"""
Knowledge Graph Explainer Module

Provides KG-based explanations for KGIN recommendations by:
1. Loading and parsing the KG structure from cpp.kg
2. Extracting edges (relations) for specific items
3. Finding paths between user history and recommended items
4. Formatting KG context for LLM consumption
"""

import os
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict, deque


class KGGraph:
    """Knowledge Graph structure with efficient querying capabilities"""
    
    def __init__(self, kg_file_path: str = None):
        """
        Initialize KG graph
        
        Args:
            kg_file_path: Path to cpp.kg file. If None, will search in default locations
        """
        self.edges: List[Dict[str, str]] = []
        self.head_to_edges: Dict[str, List[Dict]] = defaultdict(list)
        self.tail_to_edges: Dict[str, List[Dict]] = defaultdict(list)
        self.entity_to_edges: Dict[str, List[Dict]] = defaultdict(list)
        self.item_to_entity: Dict[str, str] = {}
        self.entity_to_item: Dict[str, str] = {}
        
        # Find and load KG file
        if kg_file_path is None:
            kg_file_path = self._find_kg_file()
        
        if kg_file_path and os.path.exists(kg_file_path):
            self.load_kg(kg_file_path)
            
            # Load links if available
            link_file = self._find_link_file(kg_file_path)
            if link_file:
                self.load_links(link_file)
        else:
            print(f"Warning: KG file not found at {kg_file_path}")
    
    def _find_kg_file(self) -> Optional[str]:
        """Find cpp.kg file in common locations"""
        base_dir = Path(__file__).parent
        possible_paths = [
            base_dir / "../../dataset/cpp.kg",
            base_dir / "dataset/cpp.kg",
            Path.cwd() / "dataset/cpp.kg",
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path.resolve())
        
        return None

    def _find_link_file(self, kg_path: str) -> Optional[str]:
        """Find cpp.link file relative to kg file"""
        kg_path_obj = Path(kg_path)
        link_path = kg_path_obj.parent / "cpp.link"
        if link_path.exists():
            return str(link_path)
        return None

    def load_links(self, link_file: str):
        """Load item-entity mapping from cpp.link"""
        print(f"Loading links from: {link_file}")
        try:
            with open(link_file, 'r', encoding='utf-8') as f:
                next(f) # Skip header
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        item_id = parts[0]
                        entity_id = parts[1]
                        self.item_to_entity[item_id] = entity_id
                        self.entity_to_item[entity_id] = item_id
            print(f"Loaded {len(self.item_to_entity)} ID mappings")
        except Exception as e:
            print(f"Error loading links: {e}")

    def load_kg(self, kg_file_path: str):
        """
        Load KG from file and build indexes for fast querying
        
        Args:
            kg_file_path: Path to cpp.kg file
        """
        print(f"Loading KG from: {kg_file_path}")
        
        with open(kg_file_path, 'r', encoding='utf-8') as f:
            # Skip header
            next(f)
            
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    head, relation, tail = parts[0], parts[1], parts[2]
                    
                    edge = {
                        'head': head,
                        'relation': relation,
                        'tail': tail
                    }
                    
                    self.edges.append(edge)
                    
                    # Build indexes for fast lookup
                    self.head_to_edges[head].append(edge)
                    self.tail_to_edges[tail].append(edge)
                    self.entity_to_edges[head].append(edge)
                    self.entity_to_edges[tail].append(edge)
        
        print(f"Loaded {len(self.edges)} edges from KG")
    
    def get_item_edges(self, item_id: str) -> List[Dict[str, str]]:
        """
        Get all edges connected to an item (both incoming and outgoing)
        
        Args:
            item_id: Item ID (e.g., 'E1', 'E42')
        
        Returns:
            List of edge dictionaries
        """
        return self.entity_to_edges.get(item_id, [])
    
    def get_item_metadata(self, item_id: str) -> Dict[str, str]:
        """
        Extract topic and level metadata for an item from KG edges
        
        Args:
            item_id: Item ID
        
        Returns:
            Dictionary with 'topic' and 'level' keys
        """
        metadata = {'topic': None, 'level': None}
        
        edges = self.get_item_edges(item_id)
        for edge in edges:
            if edge['head'] == item_id:
                if edge['relation'] == 'has_topic':
                    metadata['topic'] = edge['tail']
                elif edge['relation'] == 'has_level':
                    metadata['level'] = edge['tail']
        
        return metadata
    
    def find_shared_entities(self, item_id1: str, item_id2: str) -> Dict[str, List[str]]:
        """
        Find entities (topics, levels) shared between two items
        
        Args:
            item_id1: First item ID
            item_id2: Second item ID
        
        Returns:
            Dictionary with shared topics and levels
        """
        meta1 = self.get_item_metadata(item_id1)
        meta2 = self.get_item_metadata(item_id2)
        
        shared = {
            'topics': [],
            'levels': []
        }
        
        if meta1['topic'] and meta1['topic'] == meta2['topic']:
            shared['topics'].append(meta1['topic'])
        
        if meta1['level'] and meta1['level'] == meta2['level']:
            shared['levels'].append(meta1['level'])
        
        return shared
    
    def find_paths_bfs(
        self, 
        start_item: str, 
        end_item: str, 
        max_depth: int = 3,
        max_paths: int = 5
    ) -> List[List[Dict[str, str]]]:
        """
        Find paths between two items using BFS (optimized for speed)
        
        Args:
            start_item: Starting item ID
            end_item: Target item ID
            max_depth: Maximum path length
            max_paths: Maximum number of paths to return
        
        Returns:
            List of paths, where each path is a list of edges
        """
        if start_item == end_item:
            return []
        
        paths = []
        queue = deque([(start_item, [])])
        visited = set()
        
        while queue and len(paths) < max_paths:
            current, path = queue.popleft()
            
            if len(path) >= max_depth:
                continue
            
            # Avoid cycles
            path_key = tuple(edge['head'] + edge['relation'] + edge['tail'] for edge in path)
            if path_key in visited:
                continue
            visited.add(path_key)
            
            # Get outgoing edges from current node
            for edge in self.head_to_edges.get(current, []):
                new_path = path + [edge]
                
                if edge['tail'] == end_item:
                    paths.append(new_path)
                    if len(paths) >= max_paths:
                        break
                else:
                    queue.append((edge['tail'], new_path))
        
        return paths
    
    def format_path_string(self, path: List[Dict[str, str]]) -> str:
        """
        Format a path as a readable string
        
        Args:
            path: List of edges forming a path
        
        Returns:
            Formatted path string
        """
        if not path:
            return ""
        
        parts = [path[0]['head']]
        for edge in path:
            parts.append(f"→ {edge['relation']} →")
            parts.append(edge['tail'])
        
        return " ".join(parts)


class KGExplainer:
    """High-level explainer using KG structure"""
    
    def __init__(self, kg_file_path: str = None):
        """
        Initialize KG explainer
        
        Args:
            kg_file_path: Path to cpp.kg file
        """
        self.kg_graph = KGGraph(kg_file_path)
    
    def _normalize_id(self, item_id: str) -> str:
        """Ensure item ID matches KG format (starts with E)"""
        # Try lookup in loaded links
        if hasattr(self.kg_graph, 'item_to_entity') and item_id in self.kg_graph.item_to_entity:
            return self.kg_graph.item_to_entity[item_id]
            
        if item_id and not item_id.startswith('E') and item_id.isdigit():
            return f"E{item_id}"
        return item_id

    def explain_item(
        self, 
        item_id: str, 
        user_history: List[str] = None
    ) -> Dict:
        """
        Generate KG-based explanation for a single item
        
        Args:
            item_id: Item ID to explain
            user_history: List of item IDs the user has completed
        
        Returns:
            Dictionary with KG context and explanation components
        """
        # Normalize IDs
        item_id = self._normalize_id(item_id)
        if user_history:
            user_history = [self._normalize_id(hid) for hid in user_history]

        # Get item metadata
        metadata = self.kg_graph.get_item_metadata(item_id)
        edges = self.kg_graph.get_item_edges(item_id)
        
        explanation = {
            'item_id': item_id,
            'metadata': metadata,
            'edges': edges,
            'paths_from_history': [],
            'shared_entities': []
        }
        
        # Find connections to user history
        if user_history:
            for hist_item in user_history[-5:]:  # Only check recent 5 items for speed
                # Find shared entities
                shared = self.kg_graph.find_shared_entities(hist_item, item_id)
                if shared['topics'] or shared['levels']:
                    explanation['shared_entities'].append({
                        'from_item': hist_item,
                        'shared': shared
                    })
                
                # Find paths (limit to 2 paths per history item for speed)
                paths = self.kg_graph.find_paths_bfs(
                    hist_item, 
                    item_id, 
                    max_depth=3,
                    max_paths=2
                )
                
                for path in paths:
                    explanation['paths_from_history'].append({
                        'from_item': hist_item,
                        'path': path,
                        'path_string': self.kg_graph.format_path_string(path)
                    })
        
        return explanation
    
    def format_kg_context_for_llm(self, explanation: Dict, item_details: Dict = None) -> str:
        """
        Format KG explanation into natural language text with KGAT/KGIN analysis
        
        Args:
            explanation: Output from explain_item()
            item_details: Dictionary mapping item_id -> item_info (for names)
        
        Returns:
            Formatted string for display
        """
        lines = []
        
        # Try using enhanced explainer for richer context
        try:
            from enhanced_kg_explainer import EnhancedKGExplainer
            enhanced = EnhancedKGExplainer()
            
            item_id = explanation.get('item_id', '')
            user_history = []
            
            # Extract user history from shared_entities
            for shared in explanation.get('shared_entities', []):
                hist_item = shared.get('from_item')
                if hist_item and hist_item not in user_history:
                    user_history.append(hist_item)
            
            # Get enhanced explanation
            enhanced_exp = enhanced.explain_single_recommendation(
                item_id=item_id,
                user_history=user_history,
                score=explanation.get('score', 0)
            )
            
            return enhanced.format_explanation_text(enhanced_exp)
            
        except ImportError:
            pass  # Fall back to basic formatting
        except Exception as e:
            print(f"Enhanced format error, using fallback: {e}")
        
        # Legacy formatting path
        def get_name(iid):
            if not item_details:
                return iid
            
            if iid in item_details:
                return item_details[iid].get('title', iid)
            
            if hasattr(self.kg_graph, 'entity_to_item') and iid in self.kg_graph.entity_to_item:
                  numeric_id = self.kg_graph.entity_to_item[iid]
                  if numeric_id in item_details:
                       return item_details[numeric_id].get('title', iid)

            if iid.startswith('E'):
                numeric_id = iid[1:]
                if numeric_id in item_details:
                     return item_details[numeric_id].get('title', iid)
            
            return iid
        
        item_name = get_name(explanation['item_id'])
        
        # Metadata
        metadata = explanation['metadata']
        topic = "không xác định"
        level = "không xác định"
        
        if metadata['topic']:
            topic = metadata['topic'].replace('T_', '').replace('_', ' ')
        if metadata['level']:
            level = metadata['level'].replace('L_', 'Level ')
            
        lines.append(f"- **Chủ đề**: {topic}")
        lines.append(f"- **Độ khó**: {level}")
        
        # Shared entities with history
        lines.append("\n🔗 **Lý do gợi ý (KG Paths)**:")
        
        has_shared_topic = False
        if explanation['shared_entities']:
            for shared_info in explanation['shared_entities'][:3]:
                from_item = shared_info['from_item']
                from_item_name = get_name(from_item)
                shared = shared_info['shared']
                
                reasons = []
                if shared['topics']:
                    has_shared_topic = True
                    topic_clean = shared['topics'][0].replace('T_', '').replace('_', ' ')
                    reasons.append(f"cùng chủ đề **{topic_clean}**")
                
                if shared['levels']:
                    level_clean = shared['levels'][0].replace('L_', 'Level ')
                    reasons.append(f"cùng độ khó **{level_clean}**")
                
                if reasons:
                    reason_str = " và ".join(reasons)
                    lines.append(f"- Bạn đã hoàn thành bài **{from_item_name}**, bài này cũng {reason_str}.")
        
        if not has_shared_topic and metadata['topic']:
             t_clean = metadata['topic'].replace('T_', '').replace('_', ' ')
             lines.append(f"- Bài này giúp bạn rèn luyện và củng cố kiến thức về chủ đề **{t_clean}**.")
        
        # Paths
        if explanation['paths_from_history']:
            lines.append("\n🕸️ **Phân tích chi tiết từ Knowledge Graph**:")
            for path_info in explanation['paths_from_history'][:2]:
                path = path_info['path']
                # Construct a natural sentence from the path
                # Standard path: ItemA -> relation1 -> Entity -> relation2 -> ItemB
                if len(path) == 2: # 2 hops: ItemA -> rel -> Entity <- rel <- ItemB
                     # E.g. E1 -> has_topic -> T -> topic_of -> E2
                     head = get_name(path[0]['head'])
                     tail = get_name(path[1]['tail'])
                     middle = path[0]['tail'] # The shared entity
                     
                     relation1 = path[0]['relation']
                     relation2 = path[1]['relation']
                     
                     mid_text = middle.replace('T_', '').replace('L_', '').replace('_', ' ')
                     
                     if 'topic' in relation1:
                         lines.append(f"- **{head}** và **{tail}** đều thuộc chủ đề **{mid_text}**.")
                     elif 'level' in relation1:
                         lines.append(f"- **{head}** và **{tail}** đều ở mức độ khó **{mid_text}**.")
                     else:
                         lines.append(f"- Có mối liên hệ giữa **{head}** và **{tail}** qua **{mid_text}**.")
                else:
                    # Fallback for longer paths
                    raw_path = path_info['path_string']
                    # Pretty print the path but with names
                    # Replace IDs with names in the string is hard, better to reconstruct
                    # But for now let's just clean it up lightly
                    pretty_path = raw_path
                    for iid in [path[0]['head'], path[-1]['tail']]:
                        name = get_name(iid)
                        pretty_path = pretty_path.replace(iid, f"**{name}**")
                    
                    pretty_path = pretty_path.replace('T_', '').replace('_', ' ').replace('L_', 'Level ')
                    pretty_path = pretty_path.replace('has topic', 'thuộc chủ đề').replace('topic of', 'là chủ đề của')
                    pretty_path = pretty_path.replace('has level', 'có độ khó').replace('level of', 'là độ khó của')
                    pretty_path = pretty_path.replace('has topic', 'thuộc chủ đề').replace('topic of', 'là chủ đề của')
                    pretty_path = pretty_path.replace('has level', 'có độ khó').replace('level of', 'là độ khó của')
                    lines.append(f"- {pretty_path}")
        
        # Explicitly add Item -> Topic path if exists and not already covered
        if metadata['topic']:
            t_clean = metadata['topic'].replace('T_', '').replace('_', ' ')
            # Check if this simple path is already covered
            is_covered = False
            for path_info in explanation['paths_from_history']:
                # Simplistic check if topic is in path string
                if t_clean in path_info['path_string'].replace('_', ' '):
                    is_covered = True
                    break
            
            if not is_covered:
                # Add the direct path if not present sections
                if not explanation['paths_from_history']:
                     lines.append("\n🕸️ **Phân tích chi tiết từ Knowledge Graph**:")
                
                lines.append(f"- **{item_name}** → thuộc chủ đề → **{t_clean}**")
        
        if not explanation['shared_entities'] and not explanation['paths_from_history']:
             lines.append("\n(Bài tập này phù hợp với năng lực hiện tại của bạn dựa trên phân tích tổng quát)")

        return "\n".join(lines)
    
    def explain_recommendations(
        self,
        recommendations: List[Tuple[str, float]],
        user_history: List[str] = None
    ) -> List[Dict]:
        """
        Generate KG explanations for a list of recommendations
        
        Args:
            recommendations: List of (item_id, score) tuples
            user_history: List of item IDs the user has completed
        
        Returns:
            List of explanation dictionaries
        """
        explanations = []
        
        for item_id, score in recommendations:
            explanation = self.explain_item(item_id, user_history)
            explanation['score'] = score
            explanations.append(explanation)
        
        return explanations
