"""
KG-Based Explainer - Generate explanations purely from Knowledge Graph analysis
No LLM required, uses graph structure and patterns to explain recommendations
"""

import os
import csv
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict, Counter


class KGBasedExplainer:
    """
    Generate detailed explanations based on Knowledge Graph analysis
    No LLM required - uses graph patterns, paths, and entity relationships
    """
    
    def __init__(self):
        self.entity_to_name = {}
        self.entity_to_topics = defaultdict(list)
        self.entity_to_levels = {}
        self._load_dataset()
    
    def _load_dataset(self):
        """Load mappings and KG data from dataset files"""
        try:
            # Determine paths
            base_dir = os.path.dirname(os.path.abspath(__file__))
            dataset_dir = os.path.join(base_dir, '../../dataset')
            
            kg_path = os.path.join(dataset_dir, 'cpp.kg')
            link_path = os.path.join(dataset_dir, 'cpp.link')
            item_path = os.path.join(dataset_dir, 'cpp.item')
            
            # 1. Load mappings: Entity ID -> Item ID -> Name
            item_id_to_name = {}
            if os.path.exists(item_path):
                with open(item_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter='\t')
                    next(reader, None) # Skip header
                    for row in reader:
                        if len(row) >= 3:
                            item_id, _, name = row[0], row[1], row[2]
                            item_id_to_name[item_id] = name

            entity_to_item_id = {}
            if os.path.exists(link_path):
                with open(link_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter='\t')
                    next(reader, None) # Skip header
                    for row in reader:
                        if len(row) >= 2:
                            item_id, entity_id = row[0], row[1]
                            entity_to_item_id[entity_id] = item_id
            
            # Create Entity -> Name mapping
            for entity_id, item_id in entity_to_item_id.items():
                if item_id in item_id_to_name:
                    self.entity_to_name[entity_id] = item_id_to_name[item_id]
            
            # 2. Load KG data: Entity -> Topics/Levels
            if os.path.exists(kg_path):
                with open(kg_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter='\t')
                    next(reader, None) # Skip header
                    for row in reader:
                        if len(row) >= 3:
                            head, relation, tail = row[0], row[1], row[2]
                            if relation == 'has_topic':
                                self.entity_to_topics[head].append(tail)
                            elif relation == 'has_level':
                                self.entity_to_levels[head] = tail

        except Exception as e:
            print(f"Error loading dataset for explainer: {str(e)}")

    def explain_recommendations(
        self,
        student_code: str,
        recommendations: List[Dict],
        kg_contexts: List[Dict] = None
    ) -> str:
        """
        Generate comprehensive explanation from KG analysis
        
        Args:
            student_code: Student ID
            recommendations: List of recommended items with metadata
            kg_contexts: List of KG explanation data for each item
        
        Returns:
            Detailed markdown explanation
        """
        # If no KG context passed, we can still use our loaded KG data
        # But we need the entity IDs from the recommendations
        
        # Analyze KG patterns
        analysis = self._analyze_kg_patterns(recommendations, kg_contexts)
        
        # Build explanation sections
        explanation = self._build_explanation(student_code, recommendations, analysis)
        
        return explanation
    
    def _get_entity_id(self, item_id: str) -> Optional[str]:
        # Helper to reverse look up entity id (not implemented efficiently, but dataset is small)
        # Actually recommendations usually come with 'id' which might be Item ID or Entity ID depending on the system.
        # Looking at previous files, it seems recommendations have 'id' matching the item_id in cpp.item.
        return None

    def _analyze_kg_patterns(self, recommendations: List[Dict], kg_contexts: List[Dict]) -> Dict:
        """Analyze patterns in KG data"""
        analysis = {
            'topics': [],
            'levels': [],
            'topic_progression': [],
            'level_progression': [],
            'shared_connections': defaultdict(int),
            'path_patterns': [],
            'topic_clusters': defaultdict(list),
            'item_details': [] # details for each item
        }
        
        # If kg_contexts is None or empty, create dummy list
        ctx_iter = kg_contexts if kg_contexts else [{} for _ in recommendations]
        
        for i, (rec, ctx) in enumerate(zip(recommendations, ctx_iter)):
            # Try to find entity ID. 
            # Strategy: 
            # 1. Check if 'id' in rec is an Entity ID (starts with E)
            # 2. Check if we can find it via name or other metadata?
            # actually, typically recs have the ID from the dataset.
            # In cpp.link: item_id (numeric) -> entity_id (E...)
            
            # Let's assume rec['id'] might be the Item ID (e.g. "1", "2").
            # But in the KG explainer usage, we might get specific dicts.
            
            # For now, let's rely on what we can find.
            # If we loaded the KG, we can augment the info.
            
            rec_id = str(rec.get('id', ''))
            
            # Try to resolve topics and name
            topics = []
            level = ''
            name = rec.get('name', '') # Fallback to rec name
            
            # Check if we have mapped this item/entity
            # If rec_id looks like "E1", it's entity ID. If "1", it's item ID.
            entity_id = None
            if rec_id.startswith('E'):
                entity_id = rec_id
            else:
                # Try to find entity ID for this item ID (we loaded Entity->Name, but not Item->Entity explicitly in self vars,
                # but we can infer or pass it. 
                # Let's check our loaded entity_to_name to start with)
                # Reverse lookup ID:
                # Actually, simpler: self.entity_to_name keys are Entity IDs.
                # Do we have item_id mapping? 
                # Let's assume rec['id'] is compatible.
                pass
            
            # Note: The provided `kg_contexts` typically contains `head_id` which IS the entity ID
            if ctx and 'head_id' in ctx:
                entity_id = ctx['head_id']
            elif not entity_id:
                # Fallback: try to match simple ID
                # In cpp.link, 1 -> E1.
                candidate_e = f"E{rec_id}"
                if candidate_e in self.entity_to_name or candidate_e in self.entity_to_topics:
                    entity_id = candidate_e

            if entity_id:
                # Get real name
                if entity_id in self.entity_to_name:
                    name = self.entity_to_name[entity_id]
                
                # Get topics from KG
                if entity_id in self.entity_to_topics:
                    topics = self.entity_to_topics[entity_id]
                
                # Get level
                if entity_id in self.entity_to_levels:
                    level = self.entity_to_levels[entity_id]
            
            # Fallback to metadata in ctx if KG lookup failed
            if not topics and ctx:
                meta_topic = ctx.get('metadata', {}).get('topic')
                if meta_topic:
                    topics = [meta_topic]
            
            if not level and ctx:
                level = ctx.get('metadata', {}).get('level', '')

            # Store details
            clean_topics = [t.replace('T_', '').replace('_', ' ') for t in topics]
            clean_level = level.replace('L_', 'Level ') if level else 'Unknown'
            
            analysis['item_details'].append({
                'name': name,
                'topics': clean_topics,
                'level': clean_level,
                'entity_id': entity_id
            })

            # Add to aggregates
            for t in topics:
                analysis['topics'].append(t)
                analysis['topic_clusters'][t].append(i + 1) # Position 1-based
            
            if level:
                analysis['levels'].append(level)
            
            # Analyze shared entities (from ctx - these are neighbors)
            if ctx:
                shared_entities = ctx.get('shared_entities', [])
                for entity in shared_entities:
                    shared_topics = entity.get('shared', {}).get('topics', [])
                    shared_levels = entity.get('shared', {}).get('levels', [])
                    
                    for t in shared_topics:
                        analysis['shared_connections'][f"topic:{t}"] += 1
                    for l in shared_levels:
                        analysis['shared_connections'][f"level:{l}"] += 1

                # Analyze paths
                paths = ctx.get('paths_from_history', [])
                for path in paths:
                    path_str = path.get('path_string', '')
                    if path_str:
                        analysis['path_patterns'].append(path_str)
        
        # Detect progressions
        analysis['topic_progression'] = self._detect_progression(analysis['topics'])
        analysis['level_progression'] = self._detect_level_progression(analysis['levels'])
        
        return analysis
    
    def _detect_progression(self, items: List[str]) -> Dict:
        """Detect if there's a progression pattern"""
        counter = Counter(items)
        most_common = counter.most_common(3)
        
        return {
            'dominant': most_common[0][0] if most_common else None,
            'count': most_common[0][1] if most_common else 0,
            'diversity': len(counter),
            'distribution': dict(counter)
        }
    
    def _detect_level_progression(self, levels: List[str]) -> Dict:
        """Detect level progression (e.g., L_1 -> L_2 -> L_3)"""
        if not levels:
            return {
                'has_progression': False,
                'is_uniform': False,
                'range': (0, 0),
                'levels': []
            }
        
        # Extract level numbers
        level_nums = []
        for level in levels:
            try:
                num = int(level.split('_')[1]) if '_' in level else 0
                level_nums.append(num)
            except:
                continue
        
        if not level_nums:
            return {
                'has_progression': False,
                'is_uniform': False,
                'range': (0, 0),
                'levels': []
            }
        
        is_increasing = all(level_nums[i] <= level_nums[i+1] for i in range(len(level_nums)-1))
        is_same = len(set(level_nums)) == 1
        
        return {
            'has_progression': is_increasing and not is_same,
            'is_uniform': is_same,
            'range': (min(level_nums), max(level_nums)),
            'levels': level_nums
        }
    
    def _build_explanation(self, student_code: str, recommendations: List[Dict], analysis: Dict) -> str:
        """Build comprehensive explanation from analysis"""
        
        sections = []
        
        # Header
        sections.append(f"# Giải thích gợi ý cho sinh viên {student_code}\n")
        
        # 1. Overview
        sections.append("## 1. Tổng quan\n")
        topic_prog = analysis['topic_progression']
        if topic_prog['dominant']:
            dominant_topic = topic_prog['dominant'].replace('T_', '').replace('_', ' ')
            sections.append(
                f"Hệ thống gợi ý **{len(recommendations)} bài tập** tập trung chủ yếu vào chủ đề "
                f"**{dominant_topic}** ({topic_prog['count']} liên kết).\n"
            )
        else:
             sections.append(f"Hệ thống gợi ý **{len(recommendations)} bài tập** để bạn luyện tập.\n")
        
        if topic_prog['diversity'] > 1:
            other_topics = [t.replace('T_', '').replace('_', ' ') 
                          for t in topic_prog['distribution'].keys() 
                          if t != topic_prog['dominant']]
            if other_topics:
                sections.append(
                    f"Ngoài ra còn có các chủ đề liên quan: {', '.join(other_topics[:3])}.\n"
                )
        
        # 2. Detailed Breakdown with Names and Topics
        sections.append("\n## 2. Chi tiết các bài tập\n")
        for i, detail in enumerate(analysis['item_details']):
            name = detail['name'] if detail['name'] else f"Bài {i+1}"
            topics_str = ', '.join(detail['topics']) if detail['topics'] else "Tổng hợp"
            level = detail['level']
            sections.append(f"- **{name}**: Chủ đề *{topics_str}* ({level})\n")

        # 3. Why these recommendations? (Using explicit KG relations)
        sections.append("\n## 3. Tại sao gợi ý những bài này?\n")
        sections.append("Dựa trên phân tích Knowledge Graph (quan hệ `has_topic`, `has_level`):\n\n")
        
        # Group reasons by topic
        topic_clusters = analysis['topic_clusters']
        if topic_clusters:
            for topic, indices in topic_clusters.items():
                t_name = topic.replace('T_', '').replace('_', ' ')
                idx_str = ', '.join([f"bài {i}" for i in indices])
                sections.append(f"- **Chủ đề {t_name}**: Được tìm thấy qua quan hệ `has_topic` trong KG, giúp củng cố kiến thức về {t_name}.\n")
        
        # Level analysis
        level_prog = analysis['level_progression']
        if level_prog['has_progression']:
             sections.append(f"- **Lộ trình độ khó**: Bài tập được sắp xếp theo độ khó tăng dần (Level {level_prog['range'][0]} -> {level_prog['range'][1]}).\n")
        elif level_prog['is_uniform']:
             sections.append(f"- **Độ khó phù hợp**: Tập trung rèn luyện kỹ năng ở mức độ Level {level_prog['levels'][0]}.\n")
        
        # 4. Connectedness (Shared Entities)
        if analysis['shared_connections']:
             sections.append("\n## 4. Mối liên hệ bài tập\n")
             sections.append("Các bài tập có sự liên kết chặt chẽ trong đồ thị tri thức:\n")
             
             # Top shared topics
             topic_conns = [(k.replace('topic:T_', '').replace('_', ' '), v) 
                           for k, v in analysis['shared_connections'].items() if k.startswith('topic:')]
             topic_conns.sort(key=lambda x: -x[1])
             
             for t_name, count in topic_conns[:2]:
                 sections.append(f"- **{count}** cặp bài tập cùng chia sẻ chủ đề **{t_name}**.\n")

        return ''.join(sections)
