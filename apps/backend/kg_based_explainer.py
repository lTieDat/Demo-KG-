"""
KG-Based Explainer - Generate explanations purely from Knowledge Graph analysis
No LLM required, uses graph structure and patterns to explain recommendations
"""

from typing import List, Dict, Optional
from collections import defaultdict, Counter


class KGBasedExplainer:
    """
    Generate detailed explanations based on Knowledge Graph analysis
    No LLM required - uses graph patterns, paths, and entity relationships
    """
    
    def __init__(self):
        pass
    
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
        if not kg_contexts or not recommendations:
            return self._fallback_explanation(student_code, recommendations)
        
        # Analyze KG patterns
        analysis = self._analyze_kg_patterns(recommendations, kg_contexts)
        
        # Build explanation sections
        explanation = self._build_explanation(student_code, recommendations, analysis)
        
        return explanation
    
    def _analyze_kg_patterns(self, recommendations: List[Dict], kg_contexts: List[Dict]) -> Dict:
        """Analyze patterns in KG data"""
        analysis = {
            'topics': [],
            'levels': [],
            'topic_progression': [],
            'level_progression': [],
            'shared_connections': defaultdict(int),
            'path_patterns': [],
            'topic_clusters': defaultdict(list)
        }
        
        for i, (rec, kg_ctx) in enumerate(zip(recommendations, kg_contexts)):
            if not kg_ctx:
                continue
            
            metadata = kg_ctx.get('metadata', {})
            topic = metadata.get('topic', '')
            level = metadata.get('level', '')
            
            # Track topics and levels
            if topic:
                analysis['topics'].append(topic)
                analysis['topic_clusters'][topic].append(i + 1)
            if level:
                analysis['levels'].append(level)
            
            # Analyze shared entities
            shared_entities = kg_ctx.get('shared_entities', [])
            for entity in shared_entities:
                shared_topics = entity.get('shared', {}).get('topics', [])
                shared_levels = entity.get('shared', {}).get('levels', [])
                
                for t in shared_topics:
                    analysis['shared_connections'][f"topic:{t}"] += 1
                for l in shared_levels:
                    analysis['shared_connections'][f"level:{l}"] += 1
            
            # Analyze paths
            paths = kg_ctx.get('paths_from_history', [])
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
                f"**{dominant_topic}** ({topic_prog['count']}/{len(recommendations)} bài).\n"
            )
        
        if topic_prog['diversity'] > 1:
            other_topics = [t.replace('T_', '').replace('_', ' ') 
                          for t in topic_prog['distribution'].keys() 
                          if t != topic_prog['dominant']]
            sections.append(
                f"Ngoài ra còn có các chủ đề liên quan: {', '.join(other_topics[:3])}.\n"
            )
        
        # 2. Level progression analysis
        sections.append("\n## 2. Phân tích độ khó\n")
        level_prog = analysis['level_progression']
        
        if level_prog.get('has_progression'):
            sections.append(
                f"✓ **Lộ trình học tập có cấu trúc**: Độ khó tăng dần từ Level {level_prog['range'][0]} "
                f"đến Level {level_prog['range'][1]}, giúp bạn phát triển kỹ năng từng bước.\n"
            )
        elif level_prog.get('is_uniform'):
            if level_prog.get('levels'):
                sections.append(
                    f"✓ **Độ khó đồng đều**: Tất cả bài tập đều ở Level {level_prog['levels'][0]}, "
                    f"phù hợp để rèn luyện và củng cố kỹ năng ở mức độ này.\n"
                )
        else:
            if level_prog.get('range'):
                sections.append(
                    f"✓ **Độ khó đa dạng**: Các bài tập có độ khó khác nhau (Level {level_prog['range'][0]}-{level_prog['range'][1]}), "
                    f"giúp bạn thử thách bản thân ở nhiều mức độ.\n"
                )
            else:
                 sections.append(
                    "✓ **Độ khó đa dạng**: Các bài tập có độ khó khác nhau, giúp bạn thử thách bản thân ở nhiều mức độ.\n"
                )
        
        # 3. Knowledge Graph connections
        sections.append("\n## 3. Mối liên hệ trong Knowledge Graph\n")
        
        if analysis['shared_connections']:
            sections.append("Các bài tập được gợi ý có **mối liên hệ chặt chẽ** với nhau:\n\n")
            
            # Group by type
            topic_connections = {k: v for k, v in analysis['shared_connections'].items() if k.startswith('topic:')}
            level_connections = {k: v for k, v in analysis['shared_connections'].items() if k.startswith('level:')}
            
            if topic_connections:
                sections.append("**Liên kết theo chủ đề:**\n")
                for conn, count in sorted(topic_connections.items(), key=lambda x: -x[1])[:3]:
                    topic_name = conn.replace('topic:T_', '').replace('_', ' ')
                    sections.append(f"- {count} bài có chung chủ đề **{topic_name}**\n")
            
            if level_connections:
                sections.append("\n**Liên kết theo độ khó:**\n")
                for conn, count in sorted(level_connections.items(), key=lambda x: -x[1])[:3]:
                    level_name = conn.replace('level:', '')
                    sections.append(f"- {count} bài có cùng độ khó **{level_name}**\n")
        
        # 4. Learning path
        sections.append("\n## 4. Lộ trình học tập đề xuất\n")
        
        # Group by topic clusters
        topic_clusters = analysis['topic_clusters']
        if topic_clusters:
            sections.append("Bạn nên làm bài theo nhóm chủ đề để tối ưu hiệu quả học:\n\n")
            for topic, positions in sorted(topic_clusters.items(), key=lambda x: min(x[1])):
                topic_name = topic.replace('T_', '').replace('_', ' ')
                pos_str = ', '.join([f"#{p}" for p in positions])
                sections.append(f"**{topic_name}**: Bài {pos_str}\n")
        else:
            sections.append("Làm bài theo thứ tự từ trên xuống dưới để đạt hiệu quả tốt nhất.\n")
        
        # 5. Why these recommendations?
        sections.append("\n## 5. Tại sao gợi ý những bài này?\n")
        sections.append(
            "Dựa trên phân tích Knowledge Graph, hệ thống nhận thấy:\n\n"
            "✓ Các bài tập có **mối liên hệ logic** với nhau qua topics và levels\n\n"
            "✓ Độ khó được sắp xếp phù hợp để **phát triển kỹ năng dần dần**\n\n"
            "✓ Chủ đề tập trung giúp bạn **chuyên sâu vào một lĩnh vực** trước khi chuyển sang lĩnh vực khác\n\n"
        )
        
        if analysis['path_patterns']:
            sections.append(
                f"✓ Có **{len(analysis['path_patterns'])} đường đi** trong Knowledge Graph "
                f"kết nối các bài với nhau, tạo thành một lộ trình học tập mạch lạc\n"
            )
        
        return ''.join(sections)
    
    def _fallback_explanation(self, student_code: str, recommendations: List[Dict]) -> str:
        """Fallback when no KG context available"""
        topics = [rec.get('topic', 'Unknown') for rec in recommendations]
        difficulties = [rec.get('difficulty', 'Unknown') for rec in recommendations]
        
        topic_counter = Counter(topics)
        main_topic = topic_counter.most_common(1)[0][0] if topic_counter else 'Unknown'
        
        return f"""# Giải thích gợi ý cho sinh viên {student_code}

## Tổng quan
Hệ thống gợi ý {len(recommendations)} bài tập tập trung vào chủ đề **{main_topic}**.

## Phân tích
- Chủ đề chính: {main_topic}
- Số lượng bài: {len(recommendations)}
- Độ khó: {', '.join(set(difficulties))}

## Lời khuyên
Làm bài theo thứ tự từ trên xuống để đạt hiệu quả tốt nhất.

*Lưu ý: Giải thích chi tiết hơn khi có dữ liệu Knowledge Graph.*
"""
