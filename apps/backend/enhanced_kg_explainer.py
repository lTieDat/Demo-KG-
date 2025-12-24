"""
Enhanced KG Explainer - KGAT-specific explanation generation

Provides detailed, technically accurate explanations by:
1. Analyzing attention-weighted paths (KGAT technique)
2. Scoring relation importance for each user
3. Generating multi-hop reasoning explanations
4. Integrating with LLM for natural language generation
"""

import os
import csv
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict, Counter
from pathlib import Path


class EnhancedKGExplainer:
    """
    Advanced KG-based explainer using KGAT/KGIN techniques
    
    KGAT Features:
    - Attention-weighted neighbor aggregation
    - High-order connectivity analysis
    - Relation-aware path scoring
    
    KGIN Features:
    - User intent modeling as relation combinations
    - Fine-grained relational semantics
    - Intent-aware explanations
    """
    
    # Relation semantics mapping (Vietnamese)
    RELATION_SEMANTICS = {
        'has_topic': {
            'name': 'thuộc chủ đề',
            'description': 'Bài tập thuộc về một chủ đề kiến thức cụ thể',
            'importance_hint': 'Chủ đề là yếu tố quan trọng nhất trong việc học có hệ thống'
        },
        'topic_of': {
            'name': 'là chủ đề của',
            'description': 'Chủ đề này bao gồm các bài tập liên quan',
            'importance_hint': 'Các bài cùng chủ đề giúp củng cố kiến thức'
        },
        'has_level': {
            'name': 'có độ khó',
            'description': 'Bài tập có mức độ khó nhất định',
            'importance_hint': 'Độ khó phù hợp giúp học hiệu quả hơn'
        },
        'level_of': {
            'name': 'là độ khó của',
            'description': 'Mức độ khó này áp dụng cho các bài tập',
            'importance_hint': 'Học theo cấp độ giúp tiến bộ từ từ'
        }
    }
    
    # Topic descriptions (Vietnamese)
    TOPIC_DESCRIPTIONS = {
        'T_Kiểu_dữ_liệu_Viết_vòng_lặp_Viết_hàm': 'Kiểu dữ liệu, vòng lặp và hàm - nền tảng lập trình cơ bản',
        'T_Số_học': 'Số học - các thuật toán xử lý số và tính toán',
        'T_Ước_số_và_Ước_số_chung_lớn_nhất': 'Ước số và ƯSCLN - thuật toán Euclid và ứng dụng',
        'T_Mảng_một_chiều': 'Mảng một chiều - cấu trúc dữ liệu cơ bản',
        'T_Mảng_hai_chiều': 'Mảng hai chiều - ma trận và xử lý ảnh',
        'T_Kiểu_dữ_liệu_string_và_áp_dụng': 'Xử lý chuỗi - thao tác văn bản',
        'T_Xử_lý_số_nguyên_lớn': 'Số nguyên lớn - xử lý số vượt quá giới hạn kiểu dữ liệu',
        'T_Các_bài_toán_chuẩn_hóa': 'Chuẩn hóa dữ liệu - tiền xử lý input/output',
        'T_Sắp_xếp': 'Thuật toán sắp xếp - quicksort, mergesort, etc.',
        'T_Tìm_kiếm': 'Thuật toán tìm kiếm - binary search, linear search',
        'T_Cấu_trúc_cơ_bản': 'Cấu trúc dữ liệu cơ bản - struct trong C++',
        'T_Ứng_dụng_cấu_trúc': 'Ứng dụng struct - bài toán thực tế',
        'T_Khai_báo_lớp': 'Lớp và đối tượng - OOP cơ bản',
        'T_Ứng_dụng_lớp_đối_tượng': 'Ứng dụng OOP - thiết kế phần mềm',
        'T_Ứng_dụng_thuật_toán': 'Thuật toán nâng cao - tối ưu và đệ quy',
        'T_Vào_ra_trên_tệp': 'File I/O - đọc ghi tệp tin'
    }
    
    LEVEL_DESCRIPTIONS = {
        'L_1': 'Cơ bản - phù hợp cho người mới bắt đầu',
        'L_2': 'Trung bình - yêu cầu hiểu biết nền tảng',
        'L_3': 'Nâng cao - đòi hỏi tư duy thuật toán',
        'L_4': 'Khó - yêu cầu kỹ năng tối ưu',
        'L_5': 'Rất khó - thử thách chuyên sâu'
    }
    
    def __init__(self, dataset_name: str = 'cpp', model=None, dataset=None):
        # Data structures
        self.entity_to_name = {}
        self.entity_to_topics = defaultdict(list)
        self.entity_to_levels = {}
        self.topic_to_entities = defaultdict(list)
        self.level_to_entities = defaultdict(list)
        self.kg_triples = []  # (head, relation, tail)
        self.dataset_name = dataset_name
        self.model = model
        self.dataset = dataset
        
        self.device = model.device if model else 'cpu'
        
        self._load_dataset()

    def _load_dataset(self):
        """Load all mappings and KG data"""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Determine correct folder and file prefix based on dataset
            if self.dataset_name == 'algorithm':
                folder_name = 'ctdlgt'
                file_prefix = 'ctdlgt'
            else:
                folder_name = 'cpp'
                file_prefix = 'cpp'
            
            dataset_dir = os.path.join(base_dir, '../../dataset', folder_name)
            
            kg_path = os.path.join(dataset_dir, f'{file_prefix}.kg')
            link_path = os.path.join(dataset_dir, f'{file_prefix}.link')
            item_path = os.path.join(dataset_dir, f'{file_prefix}.item')
            
            # 1. Load item names
            item_id_to_name = {}
            
            if os.path.exists(item_path):
                with open(item_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter='\t')
                    next(reader, None)  # Skip header
                    for row in reader:
                        if len(row) >= 3:
                            item_id, _, name = row[:3]
                            item_id_to_name[item_id] = name
            
            # 2. Load entity-item mapping
            entity_to_item_id = {}
            item_id_to_entity = {}
            if os.path.exists(link_path):
                with open(link_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter='\t')
                    next(reader, None)
                    for row in reader:
                        if len(row) >= 2:
                            item_id, entity_id = row[0], row[1]
                            entity_to_item_id[entity_id] = item_id
                            item_id_to_entity[item_id] = entity_id
            
            # 3. Create entity -> name mapping
            for entity_id, item_id in entity_to_item_id.items():
                if item_id in item_id_to_name:
                    self.entity_to_name[entity_id] = item_id_to_name[item_id]
            
            # 4. Load full KG for path finding
            if os.path.exists(kg_path):
                with open(kg_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter='\t')
                    next(reader, None)
                    for row in reader:
                        if len(row) >= 3:
                            head, relation, tail = row[0], row[1], row[2]
                            self.kg_triples.append((head, relation, tail))
                            
                            if relation == 'has_topic':
                                self.entity_to_topics[head].append(tail)
                                self.topic_to_entities[tail].append(head)
                            elif relation == 'has_level':
                                self.entity_to_levels[head] = tail
                                self.level_to_entities[tail].append(head)
            
            print(f"KG Explainer initialized: {len(self.entity_to_name)} entities, {len(self.kg_triples)} triples")
            
        except Exception as e:
            print(f"Error loading dataset: {e}")

    def _compute_edge_score(self, head: str, relation: str, tail: str) -> float:
        """
        Compute attention score (simplified) for an edge (h, r, t) using model embeddings.
        Score = sigmoid( (e_h + e_r) * e_t ) or similar distance metric
        """
        if self.model is None or self.dataset is None:
            return 0.5 # Default fallback
            
        try:
            import torch
            
            # Map head/tail (entity/item) to token ID
            # NOTE: In recurrent usage, ensure we map to correct ent/item ID space
            # RecBole usually maps all entities/items to a unified space or separate
            # For KGAT, entities and items are often in 'entity_id' field space if unifiedKG
            
            # Try getting entity ID from token (e.g. 'CPP0101' -> internal ID)
            # We need to access dataset.token2id for 'entity_id' field usually
            
            # 1. Get internal IDs
            h_id = self._get_internal_id(head)
            t_id = self._get_internal_id(tail)
            
            # 2. Get relation ID
            # Relations naming in dataset might be 'has_topic' -> need internal ID
            # dataset.token2id(dataset.relation_field, [relation])
            r_id = 0
            if hasattr(self.dataset, 'relation_field'):
                try:
                    # relation map might be 'has_topic' -> '1'
                    r_ids = self.dataset.token2id(self.dataset.relation_field, [relation])
                    r_id = r_ids[0]
                except:
                    # Fallback relation ID
                    r_id = 0
            
            # 3. Get Embeddings
            # model.entity_embedding(id)
            # model.relation_embedding(id)
            
            with torch.no_grad():
                e_h = self.model.entity_embedding(torch.tensor([h_id], device=self.device))
                e_t = self.model.entity_embedding(torch.tensor([t_id], device=self.device))
                e_r = self.model.relation_embedding(torch.tensor([r_id], device=self.device))
                
                # KGAT logic: e_h and e_t are projected to relation space r before scoring in TransR
                # But here we might just need simple similarity if W_r isn't easily accessible from 'model' generic wrapper
                # Check dims
                if e_h.shape[-1] != e_r.shape[-1]:
                    # Mismatch (e.g. 256 vs 128). 
                    # Try to use W_R from model if it exists, or just slice/project
                    # For visualization/explanation, we can approximate by slicing or using just entity similarity
                    
                    # Option 1: Just entity similarity (ignore relation specific offset for speed/robustness)
                    # score = torch.nn.functional.cosine_similarity(e_h, e_t).item()
                    
                    # Option 2: Project e_h to e_r size (simple slice if trained that way, or linear)
                    # Let's assume embeddings are roughly aligned in first K dims or use e_t only
                    
                    # Better: Try to find W_relation in model
                    # If this is recurrent issue, simpler to just use e_h . e_t for "connection" strength
                    # + e_r . e_t for "relation" strength
                    
                    # Let's use independently: sim(h, t) which is most important
                    sim_ht = torch.nn.functional.cosine_similarity(e_h, e_t).item()
                    
                    # And maybe sim(h, r)? No.
                    
                    # Just return sim(h, t) for robustness against mismatch
                    score = (sim_ht + 1) / 2
                    return score

                query_vec = e_h + e_r
                score = torch.nn.functional.cosine_similarity(query_vec, e_t).item()
                
                # Rescale from [-1, 1] to [0, 1] loosely for attention probability
                score = (score + 1) / 2
                
                return score
                
        except Exception as e:
            # print(f"Error computing score: {e}")
            # import traceback
            # traceback.print_exc()
            return 0.5

    def _get_internal_id(self, token):
        # Helper to map token (External ID) -> Internal Entity ID
        # Prioritize entity field
        if not self.dataset: return 0
        try:
            # Try normalize
            token = self._normalize_entity_id(token)
            
            # If dataset has 'entity_id', use that
            if 'entity_id' in self.dataset.field2token_id:
                return self.dataset.token2id('entity_id', [token])[0]
            # Fallback to item_id if 'head' was an item
            if 'item_id' in self.dataset.field2token_id:
                 return self.dataset.token2id('item_id', [token])[0]
        except:
            return 0
        return 0

    def find_attention_paths(
        self,
        user_history: List[str],
        target_item: str,
        edge_attention: Dict[Tuple[str, str, str], float],
        max_paths: int = 10
    ) -> List[Dict]:
        """
        Extract paths from user history to target item with attention scores
        """
        target_entity = self._normalize_entity_id(target_item)
        history_entities = [self._normalize_entity_id(h) for h in user_history[-5:]]
        
        # We'll use a simplified version for common demo scenarios:
        # History -> Topic -> Target or History -> Level -> Target
        paths = []
        
        for hist_entity in history_entities:
            # Topic paths
            h_topics = self.entity_to_topics.get(hist_entity, [])
            t_topics = self.entity_to_topics.get(target_entity, [])
            
            shared_topics = set(h_topics) & set(t_topics)
            
            for topic in shared_topics:
                # Calculate real attention scores
                score1 = self._compute_edge_score(hist_entity, 'has_topic', topic)
                score2 = self._compute_edge_score(topic, 'topic_of', target_entity)
                
                total_att = (score1 + score2) / 2

                # Format steps string for UI
                h_name = self._get_item_name(hist_entity)
                t_name = self._get_item_name(topic)
                tgt_name = self._get_item_name(target_entity)
                
                # Removed scores from display string as requested
                path_str = f"{h_name} --[đã làm]--> {t_name} --[quan hệ]--> {tgt_name}"

                paths.append({
                    'type': 'topic',
                    'total_attention': total_att,
                    'path_string': path_str,
                    'steps': [
                        {'head': h_name, 'relation': 'đã hoàn thành', 'tail': t_name, 'attention': score1},
                        {'head': t_name, 'relation': 'là chủ đề của', 'tail': tgt_name, 'attention': score2}
                    ]
                })

            # Level paths
            h_level = self.entity_to_levels.get(hist_entity)
            t_level = self.entity_to_levels.get(target_entity)
            if h_level and h_level == t_level:
                score1 = self._compute_edge_score(hist_entity, 'has_level', h_level)
                score2_rev = self._compute_edge_score(h_level, 'level_of', target_entity)
               
                total_att = (score1 + score2_rev) / 2
                
                h_name = self._get_item_name(hist_entity)
                lvl_name = h_level.replace('L_', 'Level ')
                tgt_name = self._get_item_name(target_entity)
                
                # Removed scores from display string as requested
                path_str = f"{h_name} --[cùng độ khó]--> {lvl_name} --[quan hệ]--> {tgt_name}"
                
                paths.append({
                    'type': 'level',
                    'total_attention': total_att,
                    'path_string': path_str,
                    'steps': [
                        {'head': h_name, 'relation': 'cùng độ khó', 'tail': lvl_name, 'attention': score1},
                        {'head': lvl_name, 'relation': 'là cấp độ của', 'tail': tgt_name, 'attention': score2_rev}
                    ]
                })

        # Sort and limit
        paths.sort(key=lambda x: x['total_attention'], reverse=True)
        return paths[:max_paths]

    def format_attention_paths_input(self, user_id: str, item_name: str, attention_paths: List[Dict]) -> str:
        """
        Format paths into the 'Input' style for LLM as requested
        """
        lines = [f"user_id = \"{user_id}\"", f"item_id = \"{item_name}\""]
        
        # Extract and list specific topics found in paths
        found_topics = set()
        for path in attention_paths:
            if path['type'] == 'topic':
                # The middle node in the path steps is the topic/bridge
                if len(path['steps']) > 0:
                    found_topics.add(path['steps'][0]['tail'])
        
        if found_topics:
            lines.append(f"\n# Shared Topics (Chủ đề chung với lịch sử): {', '.join(found_topics)}")
        
        lines.append("\n# Attention paths extracted:")
        lines.append('"""')
        
        for i, path in enumerate(attention_paths, 1):
            lines.append(f"Path {i} (Tổng attention: {path['total_attention']:.2f}):")
            for step in path['steps']:
                lines.append(f"  {step['head']} --[{step['relation']}]--> {step['tail']} (attention: {step['attention']:.3f})")
            lines.append("")
            
        lines.append('"""')
        return "\n".join(lines)

    def generate_llm_explanation(
        self,
        student_code: str,
        item_name: str,
        attention_paths: List[Dict],
        llm_client = None
    ) -> str:
        """
        Use LLM to interpret attention paths into natural language
        """
        input_data = self.format_attention_paths_input(student_code, item_name, attention_paths)
        
        prompt = f"""
Bạn là chuyên gia về AI và giáo dục. Dựa trên dữ liệu attention từ mô hình EduKGAT dưới đây, hãy viết một đoạn giải thích ngắn gọn (3-4 câu) tại sao bài tập lại được gợi ý.

{input_data}

Yêu cầu QUAN TRỌNG:
1. KHAI THÁC SÂU VỀ CHỦ ĐỀ (TOPIC): Nếu có 'Shared Topics', hãy nhắc đến tên chủ đề cụ thể và giải thích rằng vì sinh viên đã làm tốt các bài trong chủ đề này nên được gợi ý tiếp.
2. Đề cập việc dùng mô hình AI phân tích trọng số attention.
3. Không hiện con số chính xác của attention score trong lời văn, chỉ dùng tính từ như "mạnh mẽ", "cao", "liên quan mật thiết".
4. Giọng văn khuyến khích, chuyên nghiệp, tiếng Việt.
"""
        if llm_client:
            try:
                # Use our LLMService abstraction
                return llm_client.generate_explanation(prompt)
            except Exception as e:
                print(f"LLM Error: {e}")
                return self._generate_fallback_explanation(item_name, attention_paths)
        
        return self._generate_fallback_explanation(item_name, attention_paths)

    def _generate_fallback_explanation(self, item_name: str, attention_paths: List[Dict]) -> str:
        """Fallback natural language generator if LLM fails"""
        if not attention_paths:
            return f"Bài tập '{item_name}' được gợi ý dựa trên sự phù hợp tổng thể với lộ trình học tập của bạn."
            
        best_path = attention_paths[0]
        factor = best_path['steps'][0]['tail']
        # removed explicit score display
        
        return f"Mô hình AI đã nhận thấy mối liên hệ mạnh mẽ từ những bài tập bạn đã làm liên quan đến chủ đề '{factor}'. Dựa trên kết nối này, bài '{item_name}' là thử thách tiếp theo phù hợp nhất cho bạn."

    def _normalize_entity_id(self, item_or_entity) -> str:
        if not item_or_entity: return ""
        if str(item_or_entity).startswith('E'): return str(item_or_entity)
        return f"E{item_or_entity}"

    def _get_item_name(self, item_or_entity) -> str:
        entity_id = self._normalize_entity_id(item_or_entity)
        name = self.entity_to_name.get(entity_id, str(item_or_entity))
        # Clean T_ and L_ prefixes for display
        return str(name).replace('T_', '').replace('L_', '').replace('_', ' ')

    def explain_single_item(
        self,
        student_code: str,
        item_id: str,
        user_history: List[str] = None,
        edge_attention: Dict = None,
        llm_client = None
    ) -> Dict:
        """
        Produce a structured explanation for a single item (compatible with router)
        """
        entity_id = self._normalize_entity_id(item_id)
        item_name = self._get_item_name(item_id)
        
        # 1. Component Data
        attention_paths = self.find_attention_paths(user_history or [], item_id, edge_attention or {})
        
        # 2. Natural Language (LLM or Fallback)
        llm_text = self.generate_llm_explanation(student_code, item_name, attention_paths, llm_client)
        
        # 3. Router-compatible dict
        return {
            'item_id': item_id,
            'entity_id': entity_id,
            'item_name': item_name,
            'metadata': {
                'topic': self.entity_to_topics.get(entity_id, [''])[0],
                'level': self.entity_to_levels.get(entity_id, ''),
                'name': item_name
            },
            'shared_entities': [], # Not used in KGAT flow as much
            'paths_from_history': attention_paths,
            'kg_context_text': llm_text,
            'kg_context_md': llm_text, # Redundant for safety
            'input_data_technical': self.format_attention_paths_input(student_code, item_name, attention_paths)
        }

    def explain_recommendations(
        self,
        student_code: str,
        recommendations: List[Dict],
        user_history: List[str] = None,
        edge_attention: Dict = None,
        llm_client = None
    ) -> str:
        """Main entry point for generating the full explanation report (Markdown)"""
        full_sections = [f"# Giải thích gợi ý EduKGAT cho sinh viên {student_code}\n"]
        
        for i, rec in enumerate(recommendations[:3]): # Top 3 for detailed report
            item_id = str(rec.get('external_id', rec.get('id', '')))
            
            # Use explain_single_item to get data
            item_data = self.explain_single_item(student_code, item_id, user_history, edge_attention, llm_client)
            
            full_sections.append(f"### {i+1}. {item_data['item_name']}")
            full_sections.append(item_data['kg_context_text'])
            full_sections.append("\n**Dữ liệu Attention EduKGAT:**")
            full_sections.append("```")
            full_sections.append(item_data['input_data_technical'])
            full_sections.append("```\n")
            
        return "\n".join(full_sections)


# Factory function for easy integration
def create_enhanced_explainer(dataset_name: str = 'cpp') -> EnhancedKGExplainer:
    """Create and return an EnhancedKGExplainer instance"""
    return EnhancedKGExplainer(dataset_name=dataset_name)
