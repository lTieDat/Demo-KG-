 """
Enhanced KG Explainer - KGAT/KGIN-specific explanation generation

Provides detailed, technically accurate explanations by:
1. Analyzing attention-weighted paths (KGAT technique)
2. Modeling user intents as combinations of KG relations (KGIN technique)
3. Scoring relation importance for each user
4. Generating multi-hop reasoning explanations
5. Integrating with LLM for natural language generation
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
    
    def __init__(self):
        # Data structures
        self.entity_to_name = {}
        self.entity_to_topics = defaultdict(list)
        self.entity_to_levels = {}
        self.topic_to_entities = defaultdict(list)
        self.level_to_entities = defaultdict(list)
        self.kg_triples = []  # (head, relation, tail)
        
        self._load_dataset()
    
    def _load_dataset(self):
        """Load all mappings and KG data"""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            dataset_dir = os.path.join(base_dir, '../../dataset')
            
            kg_path = os.path.join(dataset_dir, 'cpp.kg')
            link_path = os.path.join(dataset_dir, 'cpp.link')
            item_path = os.path.join(dataset_dir, 'cpp.item')
            
            # 1. Load item names
            item_id_to_name = {}
            item_id_to_topic = {}
            item_id_to_level = {}
            
            if os.path.exists(item_path):
                with open(item_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter='\t')
                    next(reader, None)  # Skip header
                    for row in reader:
                        if len(row) >= 6:
                            item_id, question_id, name, group, topic_type, level = row[:6]
                            item_id_to_name[item_id] = name
                            item_id_to_topic[item_id] = topic_type
                            item_id_to_level[item_id] = level
            
            # 2. Load entity-item mapping
            entity_to_item_id = {}
            if os.path.exists(link_path):
                with open(link_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter='\t')
                    next(reader, None)
                    for row in reader:
                        if len(row) >= 2:
                            item_id, entity_id = row[0], row[1]
                            entity_to_item_id[entity_id] = item_id
            
            # 3. Create entity -> name mapping
            for entity_id, item_id in entity_to_item_id.items():
                if item_id in item_id_to_name:
                    self.entity_to_name[entity_id] = item_id_to_name[item_id]
            
            # 4. Load full KG
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
            
            print(f"Enhanced KG Explainer loaded: {len(self.entity_to_name)} entities, {len(self.kg_triples)} triples")
            
        except Exception as e:
            print(f"Error loading dataset: {e}")
    
    def analyze_user_intents(self, user_history: List[str]) -> Dict:
        """
        KGIN-style: Model user intents as combinations of KG relations
        
        Returns:
            Dict with detected intents and their strengths
        """
        if not user_history:
            return {'intents': [], 'primary_intent': None}
        
        # Count topics and levels from history
        topic_counts = Counter()
        level_counts = Counter()
        
        for item_id in user_history:
            entity_id = f"E{item_id}" if not item_id.startswith('E') else item_id
            
            topics = self.entity_to_topics.get(entity_id, [])
            for t in topics:
                topic_counts[t] += 1
            
            level = self.entity_to_levels.get(entity_id)
            if level:
                level_counts[level] += 1
        
        # Build intents as topic+level combinations
        intents = []
        
        # Primary topic intent
        if topic_counts:
            primary_topic = topic_counts.most_common(1)[0]
            topic_clean = primary_topic[0].replace('T_', '').replace('_', ' ')
            intents.append({
                'type': 'topic_focus',
                'value': primary_topic[0],
                'name': topic_clean,
                'strength': primary_topic[1] / len(user_history),
                'description': self.TOPIC_DESCRIPTIONS.get(primary_topic[0], 'Chủ đề học tập')
            })
        
        # Level preference intent
        if level_counts:
            primary_level = level_counts.most_common(1)[0]
            level_clean = primary_level[0].replace('L_', 'Level ')
            intents.append({
                'type': 'level_preference',
                'value': primary_level[0],
                'name': level_clean,
                'strength': primary_level[1] / len(user_history),
                'description': self.LEVEL_DESCRIPTIONS.get(primary_level[0], 'Mức độ phù hợp')
            })
        
        # Detect topic progression intent
        if len(topic_counts) > 1:
            intents.append({
                'type': 'knowledge_expansion',
                'name': 'Mở rộng kiến thức',
                'strength': len(topic_counts) / max(len(user_history), 1),
                'description': f'Bạn đang học đa dạng {len(topic_counts)} chủ đề khác nhau'
            })
        
        return {
            'intents': intents,
            'primary_intent': intents[0] if intents else None,
            'topic_distribution': dict(topic_counts),
            'level_distribution': dict(level_counts)
        }
    
    def calculate_relation_importance(
        self, 
        item_id: str, 
        user_history: List[str],
        attention_weights: Optional[Dict] = None
    ) -> List[Dict]:
        """
        KGAT-style: Calculate importance of each relation for this recommendation
        
        Uses attention patterns if available, otherwise uses heuristic scoring
        """
        entity_id = f"E{item_id}" if not item_id.startswith('E') else item_id
        
        # Get user's topic/level preferences
        user_intents = self.analyze_user_intents(user_history)
        
        # Get item's relations
        item_topics = self.entity_to_topics.get(entity_id, [])
        item_level = self.entity_to_levels.get(entity_id)
        
        relations = []
        
        # Score topic relation
        topic_score = 0.0
        matching_topics = []
        for topic in item_topics:
            if topic in user_intents.get('topic_distribution', {}):
                topic_score += user_intents['topic_distribution'][topic]
                matching_topics.append(topic)
        
        if item_topics:
            topic_score = min(1.0, topic_score / max(len(user_history), 1))
            topic_name = item_topics[0].replace('T_', '').replace('_', ' ')
            relations.append({
                'relation': 'has_topic',
                'value': item_topics[0],
                'display_name': topic_name,
                'importance': topic_score,
                'reason': f'Chủ đề "{topic_name}" phù hợp với xu hướng học của bạn' if matching_topics else f'Chủ đề mới: "{topic_name}"'
            })
        
        # Score level relation
        level_score = 0.0
        if item_level:
            if item_level in user_intents.get('level_distribution', {}):
                level_score = user_intents['level_distribution'][item_level] / max(len(user_history), 1)
            level_name = item_level.replace('L_', 'Level ')
            relations.append({
                'relation': 'has_level',
                'value': item_level,
                'display_name': level_name,
                'importance': min(1.0, level_score + 0.3),  # Base importance for matching level
                'reason': self.LEVEL_DESCRIPTIONS.get(item_level, 'Độ khó phù hợp')
            })
        
        # Sort by importance
        relations.sort(key=lambda x: x['importance'], reverse=True)
        
        return relations
    
    def generate_path_explanation(
        self,
        from_item: str,
        to_item: str,
        path: List[Tuple[str, str, str]]
    ) -> str:
        """
        Generate natural language explanation for a KG path
        
        KGAT insight: Explain WHY this path matters based on attention patterns
        """
        if not path:
            return ""
        
        from_name = self.entity_to_name.get(from_item, from_item)
        to_name = self.entity_to_name.get(to_item, to_item)
        
        # Single hop: direct relation
        if len(path) == 1:
            head, rel, tail = path[0]
            rel_info = self.RELATION_SEMANTICS.get(rel, {'name': rel})
            return f"**{from_name}** {rel_info['name']} **{tail.replace('T_', '').replace('L_', 'Level ').replace('_', ' ')}**"
        
        # Two hops: typical topic/level connection
        if len(path) == 2:
            _, rel1, middle = path[0]
            _, rel2, _ = path[1]
            
            middle_clean = middle.replace('T_', '').replace('L_', '').replace('_', ' ')
            
            if 'topic' in rel1:
                return (
                    f"Bạn đã làm **{from_name}** về chủ đề **{middle_clean}**. "
                    f"Bài **{to_name}** cũng thuộc chủ đề này, giúp củng cố kiến thức."
                )
            elif 'level' in rel1:
                return (
                    f"**{from_name}** và **{to_name}** cùng ở **{middle_clean}**, "
                    f"đảm bảo độ khó phù hợp với trình độ của bạn."
                )
        
        # Longer paths
        return f"Có mối liên hệ nhiều bước giữa **{from_name}** và **{to_name}** trong đồ thị tri thức."
    
    def explain_single_recommendation(
        self,
        item_id: str,
        user_history: List[str],
        score: float = 0.0,
        attention_weights: Optional[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive explanation for a single recommendation
        
        Combines:
        1. Relation importance (KGAT attention simulation)
        2. User intent alignment (KGIN technique)
        3. Path-based reasoning
        4. Natural language synthesis
        """
        entity_id = f"E{item_id}" if not item_id.startswith('E') else item_id
        
        # Get item info
        item_name = self.entity_to_name.get(entity_id, item_id)
        item_topics = self.entity_to_topics.get(entity_id, [])
        item_level = self.entity_to_levels.get(entity_id)
        
        # Analyze user intents
        user_intents = self.analyze_user_intents(user_history)
        
        # Calculate relation importance
        relation_importance = self.calculate_relation_importance(entity_id, user_history, attention_weights)
        
        # Find connections to user history
        connections = []
        for hist_item in (user_history or [])[-5:]:
            hist_entity = f"E{hist_item}" if not hist_item.startswith('E') else hist_item
            hist_topics = self.entity_to_topics.get(hist_entity, [])
            hist_level = self.entity_to_levels.get(hist_entity)
            
            # Check for shared topics
            shared_topics = set(item_topics) & set(hist_topics)
            for topic in shared_topics:
                path = [
                    (hist_entity, 'has_topic', topic),
                    (topic, 'topic_of', entity_id)
                ]
                connections.append({
                    'from_item': hist_entity,
                    'from_name': self.entity_to_name.get(hist_entity, hist_entity),
                    'connection_type': 'topic',
                    'shared_value': topic,
                    'path': path,
                    'explanation': self.generate_path_explanation(hist_entity, entity_id, path)
                })
            
            # Check for same level
            if item_level and item_level == hist_level:
                path = [
                    (hist_entity, 'has_level', item_level),
                    (item_level, 'level_of', entity_id)
                ]
                connections.append({
                    'from_item': hist_entity,
                    'from_name': self.entity_to_name.get(hist_entity, hist_entity),
                    'connection_type': 'level',
                    'shared_value': item_level,
                    'path': path,
                    'explanation': self.generate_path_explanation(hist_entity, entity_id, path)
                })
        
        # Build explanation
        explanation = {
            'item_id': item_id,
            'entity_id': entity_id,
            'item_name': item_name,
            'score': score,
            'topic': item_topics[0] if item_topics else None,
            'topic_name': item_topics[0].replace('T_', '').replace('_', ' ') if item_topics else None,
            'topic_description': self.TOPIC_DESCRIPTIONS.get(item_topics[0], '') if item_topics else None,
            'level': item_level,
            'level_name': item_level.replace('L_', 'Level ') if item_level else None,
            'level_description': self.LEVEL_DESCRIPTIONS.get(item_level, '') if item_level else None,
            'user_intents': user_intents,
            'relation_importance': relation_importance,
            'connections': connections,
            'kgat_analysis': self._generate_kgat_analysis(relation_importance),
            'kgin_analysis': self._generate_kgin_analysis(user_intents, item_topics, item_level)
        }
        
        return explanation
    
    def _generate_kgat_analysis(self, relation_importance: List[Dict]) -> str:
        """Generate KGAT-style analysis text"""
        if not relation_importance:
            return ""
        
        lines = ["**Phân tích KGAT (Attention-weighted):**"]
        for rel in relation_importance[:2]:
            importance_pct = int(rel['importance'] * 100)
            lines.append(f"- Quan hệ `{rel['relation']}` → **{rel['display_name']}** (trọng số: {importance_pct}%)")
            lines.append(f"  _{rel['reason']}_")
        
        return "\n".join(lines)
    
    def _generate_kgin_analysis(self, user_intents: Dict, item_topics: List[str], item_level: str) -> str:
        """Generate KGIN-style intent analysis"""
        if not user_intents.get('intents'):
            return ""
        
        lines = ["**Phân tích KGIN (User Intent):**"]
        
        primary = user_intents.get('primary_intent')
        if primary:
            lines.append(f"- Xu hướng chính: **{primary['name']}** (độ mạnh: {int(primary['strength']*100)}%)")
            lines.append(f"  _{primary['description']}_")
        
        # Check if item matches intents
        for intent in user_intents['intents']:
            if intent['type'] == 'topic_focus' and item_topics:
                if intent['value'] in item_topics:
                    lines.append(f"- ✓ Bài tập này phù hợp với xu hướng chủ đề của bạn")
            elif intent['type'] == 'level_preference' and item_level:
                if intent['value'] == item_level:
                    lines.append(f"- ✓ Độ khó phù hợp với mức bạn đang luyện tập")
        
        return "\n".join(lines)
    
    def format_explanation_text(self, explanation: Dict) -> str:
        """
        Format explanation into readable markdown text
        
        Designed for display in frontend and LLM consumption
        """
        lines = []
        
        # Basic info
        lines.append(f"- **Chủ đề**: {explanation.get('topic_name', 'Không xác định')}")
        if explanation.get('topic_description'):
            lines.append(f"  _{explanation['topic_description']}_")
        
        lines.append(f"- **Độ khó**: {explanation.get('level_name', 'Không xác định')}")
        if explanation.get('level_description'):
            lines.append(f"  _{explanation['level_description']}_")
        
        # Connections (path-based reasoning)
        connections = explanation.get('connections', [])
        if connections:
            lines.append("\n🔗 **Lý do gợi ý (dựa trên KG paths):**")
            seen_explanations = set()
            for conn in connections[:3]:  # Limit to 3
                exp = conn.get('explanation', '')
                if exp and exp not in seen_explanations:
                    lines.append(f"- {exp}")
                    seen_explanations.add(exp)
        
        # KGAT analysis
        kgat = explanation.get('kgat_analysis', '')
        if kgat:
            lines.append(f"\n📊 {kgat}")
        
        # KGIN analysis
        kgin = explanation.get('kgin_analysis', '')
        if kgin:
            lines.append(f"\n🎯 {kgin}")
        
        return "\n".join(lines)
    
    def explain_recommendations(
        self,
        student_code: str,
        recommendations: List[Dict],
        user_history: List[str] = None,
        attention_data: Optional[Dict] = None
    ) -> str:
        """
        Generate comprehensive explanation for all recommendations
        
        For AI Analysis panel
        """
        sections = []
        
        # Header
        sections.append(f"# Giải thích gợi ý cho sinh viên {student_code}\n")
        
        # 1. User Intent Analysis (KGIN)
        if user_history:
            user_intents = self.analyze_user_intents(user_history)
            sections.append("## 1. Phân tích xu hướng học tập (KGIN Model)\n")
            
            if user_intents['intents']:
                for intent in user_intents['intents']:
                    strength_bar = "█" * int(intent['strength'] * 10) + "░" * (10 - int(intent['strength'] * 10))
                    sections.append(f"- **{intent['name']}**: [{strength_bar}] {int(intent['strength']*100)}%")
                    sections.append(f"  _{intent.get('description', '')}_\n")
            else:
                sections.append("_Chưa có đủ dữ liệu để phân tích xu hướng_\n")
        
        # 2. Recommendations overview
        sections.append("## 2. Danh sách bài tập gợi ý\n")
        
        # Group by topic
        topic_groups = defaultdict(list)
        for i, rec in enumerate(recommendations):
            item_id = str(rec.get('id', rec.get('external_id', '')))
            entity_id = f"E{item_id}" if not item_id.startswith('E') else item_id
            topics = self.entity_to_topics.get(entity_id, [])
            topic = topics[0] if topics else 'Unknown'
            topic_groups[topic].append((i + 1, rec))
        
        for topic, items in topic_groups.items():
            topic_name = topic.replace('T_', '').replace('_', ' ')
            topic_desc = self.TOPIC_DESCRIPTIONS.get(topic, '')
            sections.append(f"### {topic_name}")
            if topic_desc:
                sections.append(f"_{topic_desc}_\n")
            
            for rank, rec in items:
                name = rec.get('title', rec.get('name', f"Bài {rank}"))
                level = rec.get('difficulty', 'Unknown')
                sections.append(f"- **{rank}. {name}** ({level})")
            sections.append("")
        
        # 3. Technical Analysis (KGAT)
        sections.append("## 3. Phân tích kỹ thuật (KGAT Model)\n")
        sections.append("Mô hình KGAT sử dụng cơ chế attention để tính trọng số cho các quan hệ trong Knowledge Graph:\n")
        
        # Calculate aggregate relation importance
        all_relations = []
        for rec in recommendations:
            item_id = str(rec.get('id', rec.get('external_id', '')))
            rel_imp = self.calculate_relation_importance(item_id, user_history or [])
            all_relations.extend(rel_imp)
        
        # Aggregate by relation type
        rel_scores = defaultdict(list)
        for rel in all_relations:
            rel_scores[rel['relation']].append(rel['importance'])
        
        sections.append("| Quan hệ | Trọng số TB | Mô tả |")
        sections.append("|---------|-------------|-------|")
        for rel, scores in rel_scores.items():
            avg_score = sum(scores) / len(scores) if scores else 0
            rel_info = self.RELATION_SEMANTICS.get(rel, {'name': rel, 'importance_hint': ''})
            sections.append(f"| `{rel}` | {int(avg_score*100)}% | {rel_info.get('importance_hint', '')} |")
        
        sections.append("")
        
        # 4. KG Structure
        sections.append("## 4. Cấu trúc Knowledge Graph\n")
        sections.append("Đồ thị tri thức được sử dụng có cấu trúc:\n")
        sections.append("- **Entities (E)**: Các bài tập lập trình")
        sections.append("- **Topics (T)**: Các chủ đề kiến thức")
        sections.append("- **Levels (L)**: Các mức độ khó")
        sections.append("\nQuan hệ chính:")
        sections.append("- `has_topic`: Bài tập → Chủ đề")
        sections.append("- `has_level`: Bài tập → Độ khó")
        sections.append("- `topic_of`: Chủ đề → Bài tập (nghịch đảo)")
        sections.append("- `level_of`: Độ khó → Bài tập (nghịch đảo)")
        
        return "\n".join(sections)


# Factory function for easy integration
def create_enhanced_explainer() -> EnhancedKGExplainer:
    """Create and return an EnhancedKGExplainer instance"""
    return EnhancedKGExplainer()
