import torch
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from recbole.data.dataset import KnowledgeBasedDataset

def to_numpy(feat):
    if hasattr(feat, 'numpy'):
        return feat.numpy()
    if isinstance(feat, pd.Series):
        return feat.values
    return np.array(feat)

def to_tensor(feat):
    if isinstance(feat, torch.Tensor):
        return feat
    if isinstance(feat, pd.Series):
        return torch.tensor(feat.values, dtype=torch.int64)
    return torch.tensor(feat, dtype=torch.int64)

def _create_ckg_graph_patched(self, form="dgl", show_relation=False):
    import torch
    user_num = self.user_num

    kg_tensor = self.kg_feat
    inter_tensor = self.inter_feat

    head_entity = to_tensor(kg_tensor[self.head_entity_field]) + user_num
    tail_entity = to_tensor(kg_tensor[self.tail_entity_field]) + user_num

    user = to_tensor(inter_tensor[self.uid_field])
    item = to_tensor(inter_tensor[self.iid_field]) + user_num

    src = torch.cat([user, item, head_entity])
    tgt = torch.cat([item, user, tail_entity])

    if show_relation:
        ui_rel_num = user.shape[0]
        ui_rel_id = self.relation_num - 1
        kg_rel = to_tensor(kg_tensor[self.relation_field])
        ui_rel = torch.full((2 * ui_rel_num,), ui_rel_id, dtype=kg_rel.dtype)
        edge = torch.cat([ui_rel, kg_rel])

    if form == "dgl":
        import dgl
        # PATCH: Fix DGL compatibility for RecBole KGAT (preserve_nodes -> relabel_nodes)
        if not hasattr(dgl, '_edge_subgraph_patched'):
            original_edge_subgraph = dgl.edge_subgraph
            def edge_subgraph_patched(graph_in, edges_in, *args, **kwargs):
                if 'preserve_nodes' in kwargs:
                    preserve = kwargs.pop('preserve_nodes')
                    kwargs['relabel_nodes'] = not preserve
                return original_edge_subgraph(graph_in, edges_in, *args, **kwargs)
            dgl.edge_subgraph = edge_subgraph_patched
            
            # PATCH: Fix DGL compatibility for adjacency_matrix(transpose=True)
            original_adjacency_matrix = dgl.DGLGraph.adjacency_matrix
            def adjacency_matrix_patched(self_graph, *args, **kwargs):
                transpose = kwargs.pop('transpose', False)
                scipy_fmt = kwargs.pop('scipy_fmt', None)
                # Remove other legacy arguments that might be passed
                kwargs.pop('ctx', None)
                
                res = original_adjacency_matrix(self_graph, *args, **kwargs)
                if transpose:
                    res = res.t()
                
                if scipy_fmt:
                    import scipy.sparse as sp
                    # Modern DGL can return a SparseMatrix object or a torch sparse tensor
                    # Handle DGL SparseMatrix
                    if hasattr(res, 'coo'):
                        coo_res = res.coo()
                        if len(coo_res) == 3:
                            row, col, values = coo_res
                        else:
                            row, col = coo_res
                            values = torch.ones(len(row), device=row.device)
                            
                        mat = sp.coo_matrix((values.detach().cpu().numpy(), 
                                            (row.detach().cpu().numpy(), col.detach().cpu().numpy())), 
                                            shape=res.shape)
                        return mat.asformat(scipy_fmt)
                    # Handle Torch Sparse Tensor
                    elif hasattr(res, 'is_sparse') and res.is_sparse:
                        indices = res.indices().detach().cpu().numpy()
                        values = res.values().detach().cpu().numpy()
                        mat = sp.coo_matrix((values, (indices[0], indices[1])), shape=res.shape)
                        return mat.asformat(scipy_fmt)
                    else:
                        # Fallback
                        try:
                            return sp.coo_matrix(res.detach().cpu().numpy()).asformat(scipy_fmt)
                        except:
                            return res # Last resort return raw
                return res
            dgl.DGLGraph.adjacency_matrix = adjacency_matrix_patched
            
            dgl._edge_subgraph_patched = True
            print("INFO: Patched dgl.edge_subgraph and DGLGraph.adjacency_matrix for compatibility")

        graph = dgl.graph((src, tgt))
        if show_relation:
            graph.edata[self.relation_field] = edge
        return graph
    elif form == "pyg":
        from torch_geometric.data import Data
        edge_attr = edge if show_relation else None
        graph = Data(edge_index=torch.stack([src, tgt]), edge_attr=edge_attr)
        return graph
    else:
        raise NotImplementedError(f"Graph format [{form}] has not been implemented.")

def _create_ckg_sparse_matrix_patched(self, form="coo", show_relation=False):
    user_num = self.user_num
    hids = self.head_entities + user_num
    tids = self.tail_entities + user_num

    uids = to_numpy(self.inter_feat[self.uid_field])
    iids = to_numpy(self.inter_feat[self.iid_field]) + user_num

    ui_rel_num = len(uids)
    ui_rel_id = self.relation_num - 1

    src = np.concatenate([uids, iids, hids])
    tgt = np.concatenate([iids, uids, tids])

    if not show_relation:
        data = np.ones(len(src))
    else:
        kg_rel = to_numpy(self.kg_feat[self.relation_field])
        ui_rel = np.full(2 * ui_rel_num, ui_rel_id, dtype=kg_rel.dtype)
        data = np.concatenate([ui_rel, kg_rel])
    
    node_num = self.entity_num + self.user_num
    mat = coo_matrix((data, (src, tgt)), shape=(node_num, node_num))
    if form == "coo":
        return mat
    elif form == "csr":
        return mat.tocsr()
    else:
        raise NotImplementedError(f"Sparse matrix format [{form}] has not been implemented.")

@property
def head_entities_patched(self):
    return to_numpy(self.kg_feat[self.head_entity_field])

@property
def tail_entities_patched(self):
    return to_numpy(self.kg_feat[self.tail_entity_field])

# Apply patches
KnowledgeBasedDataset._create_ckg_graph = _create_ckg_graph_patched
KnowledgeBasedDataset._create_ckg_sparse_matrix = _create_ckg_sparse_matrix_patched
KnowledgeBasedDataset.head_entities = head_entities_patched
KnowledgeBasedDataset.tail_entities = tail_entities_patched

print("Applied RecBole KnowledgeBasedDataset patches for Series compatibility (graph + sparse + entities)")
