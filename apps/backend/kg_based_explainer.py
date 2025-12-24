from enhanced_kg_explainer import EnhancedKGExplainer, create_enhanced_explainer
from services.llm_service import get_llm_service

class KGBasedExplainer:
    def __init__(self, dataset_name='cpp', model=None, dataset=None):
        self.dataset_name = dataset_name
        self.model = model
        self.dataset = dataset
        # Pass model and dataset to enhanced explainer
        self.explainer = EnhancedKGExplainer(dataset_name, model=model, dataset=dataset)
        self.llm_service = get_llm_service()
    
    def explain(self, user_id, item_id, context_size=2):
        """
        Explain the recommendation using knowledge graph paths.
        """
        user_history = []
        if self.dataset:
            try:
                # Normalize user_id to string and remove .0 if it's a float-string
                user_id_str = str(user_id)
                if user_id_str.endswith('.0'):
                    user_id_str = user_id_str[:-2]
                    
                # 1. Map student_id to user_id token
                token_id = None
                if user_id_str in self.dataset.field2token_id[self.dataset.uid_field]:
                    token_id = user_id_str
                else:
                    user_feat = self.dataset.user_feat
                    if 'student_id' in user_feat.columns:
                        # Use pandas-compatible boolean indexing instead of deprecated .nonzero()
                        mask = user_feat['student_id'] == user_id_str
                        matching_indices = mask[mask].index
                        if len(matching_indices) > 0:
                            token_id = str(user_feat[self.dataset.uid_field][matching_indices[0]])
                
                # 2. Get history if token_id found
                if token_id:
                    uid_internal = self.dataset.token2id(self.dataset.uid_field, [token_id])[0]
                    # Get interaction history
                    # Some datasets don't have uid2index, use manual mask as fallback
                    try:
                        index = self.dataset.uid2index(uid_internal)
                        # Correctly access tensor/series data
                        hist_iids = self.dataset.inter_feat[self.dataset.iid_field][index]
                        if hasattr(hist_iids, 'numpy'):
                            hist_iids = hist_iids.numpy()
                        elif hasattr(hist_iids, 'values'):
                             hist_iids = hist_iids.values
                    except (AttributeError, TypeError):
                        # Fallback: manually filter interaction table
                        mask = self.dataset.inter_feat[self.dataset.uid_field] == uid_internal
                        hist_iids = self.dataset.inter_feat[self.dataset.iid_field][mask]
                        if hasattr(hist_iids, 'numpy'):
                            hist_iids = hist_iids.numpy()
                        elif hasattr(hist_iids, 'values'):
                             hist_iids = hist_iids.values
                        
                    # Convert internal iids to external tokens
                    user_history = list(self.dataset.id2token(self.dataset.iid_field, hist_iids))
                    # Remove [PAD] if exists
                    user_history = [str(iid) for iid in user_history if iid != '[PAD]']
            except Exception as e:
                print(f"Error fetching history for explainer: {e}")

        # We delegate to the enhanced explainer which has the logic
        return self.explainer.explain_single_item(
             user_id, 
             item_id, 
             user_history=user_history,
             llm_client=self.llm_service
        )
    
    def explain_batch(self, user_id, item_ids):
        return {iid: self.explain(user_id, iid) for iid in item_ids}
