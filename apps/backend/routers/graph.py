from fastapi import APIRouter, HTTPException
from typing import Dict, List
import os

router = APIRouter(prefix="/graph", tags=["graph"])

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "dataset")

@router.get("/knowledge-graph")
async def get_knowledge_graph(limit: int = 10000):
    """
    Get knowledge graph data from normalized dataset.
    Returns nodes and links for visualization.
    
    Args:
        limit: Maximum number of relationships to return (default: 10000)
    """
    try:
        # Use normalized dataset files
        kg_file = os.path.join(DATASET_PATH, "cpp.kg.normalized")
        item_file = os.path.join(DATASET_PATH, "cpp.item.normalized")
        link_file = os.path.join(DATASET_PATH, "cpp.link")
        
        # Read item metadata from normalized file
        # Structure: item_id, type (topic), level
        items_metadata = {}
        with open(item_file, 'r', encoding='utf-8') as f:
            next(f)  # Skip header
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    item_id = parts[0]
                    topic = parts[1]  # This is the topic name
                    level = parts[2]
                    items_metadata[item_id] = {
                        "topic": topic,
                        "level": level
                    }
        
        # Read item ID to entity ID mapping
        item_to_entity = {}
        entity_to_item = {}
        with open(link_file, 'r', encoding='utf-8') as f:
            next(f)  # Skip header
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    item_id = parts[0]
                    entity_id = parts[1]
                    item_to_entity[item_id] = entity_id
                    entity_to_item[entity_id] = item_id
        
        # Read ALL KG relationships
        all_relationships = []
        with open(kg_file, 'r', encoding='utf-8') as f:
            next(f)  # Skip header
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    all_relationships.append({
                        'head': parts[0],
                        'relation': parts[1],
                        'tail': parts[2]
                    })
        
        # Process relationships
        nodes_set = set()
        links = []
        entity_info = {}
        processed_pairs = set()  # Track processed pairs to avoid duplicates from bidirectional edges
        
        for rel in all_relationships:
            head_id = rel['head']
            relation = rel['relation']
            tail_id = rel['tail']
            
            # Process has_topic relationships
            if relation == 'has_topic':
                nodes_set.add(head_id)
                nodes_set.add(tail_id)
                
                # Extract topic name (normalized: single underscores)
                topic_name = tail_id.replace('T_', '').replace('_', ' ')
                entity_info[tail_id] = {'type': 'topic', 'name': topic_name}
                
                if head_id not in entity_info:
                    entity_info[head_id] = {'type': 'item'}
                
                links.append({
                    "source": head_id,
                    "target": tail_id,
                    "relation": relation,
                    "label": f"has topic: {topic_name}"
                })
            
            # Process has_level relationships (only create one edge per pair)
            elif relation == 'has_level':
                pair_key = tuple(sorted([head_id, tail_id]))
                if pair_key not in processed_pairs:
                    nodes_set.add(head_id)
                    nodes_set.add(tail_id)
                    
                    # Extract level name
                    level_name = tail_id.replace('L_', 'Level ')
                    entity_info[tail_id] = {'type': 'level', 'name': level_name}
                    
                    if head_id not in entity_info:
                        entity_info[head_id] = {'type': 'item'}
                    
                    links.append({
                        "source": head_id,
                        "target": tail_id,
                        "relation": relation,
                        "label": f"has level: {level_name}"
                    })
                    
                    processed_pairs.add(pair_key)
            
            # Skip level_of (it's the reverse of has_level, already handled)
            elif relation == 'level_of':
                continue
            
            # Process similar_to relationships
            elif relation == 'similar_to':
                nodes_set.add(head_id)
                nodes_set.add(tail_id)
                
                if head_id not in entity_info:
                    entity_info[head_id] = {'type': 'item'}
                if tail_id not in entity_info:
                    entity_info[tail_id] = {'type': 'item'}
                
                links.append({
                    "source": head_id,
                    "target": tail_id,
                    "relation": relation,
                    "label": "similar to"
                })
        
        # Create nodes with metadata
        nodes = []
        for node_id in nodes_set:
            if node_id in entity_info:
                node_type = entity_info[node_id]['type']
                
                if node_type == 'item':
                    # Get metadata from entity_to_item mapping
                    item_id = entity_to_item.get(node_id)
                    if item_id and item_id in items_metadata:
                        metadata = items_metadata[item_id]
                        # Create display name from topic
                        topic_display = metadata["topic"].replace('T_', '').replace('_', ' ') if metadata["topic"] else "Unknown"
                        level_display = metadata["level"].replace('L_', 'Level ') if metadata["level"] else "Unknown"
                        
                        nodes.append({
                            "id": node_id,
                            "label": f"{node_id}",
                            "type": "item",
                            "item_id": item_id,
                            "metadata": {
                                "topic": topic_display,
                                "level": level_display
                            },
                            "name": f"{node_id} ({topic_display[:30]}...)" if len(topic_display) > 30 else f"{node_id} ({topic_display})"
                        })
                    else:
                        nodes.append({
                            "id": node_id,
                            "label": node_id,
                            "type": "item",
                            "name": node_id
                        })
                
                elif node_type == 'topic':
                    topic_name = entity_info[node_id]['name']
                    display_name = topic_name[:50] + "..." if len(topic_name) > 50 else topic_name
                    nodes.append({
                        "id": node_id,
                        "label": display_name,
                        "type": "topic",
                        "name": topic_name
                    })
                
                elif node_type == 'level':
                    level_name = entity_info[node_id]['name']
                    nodes.append({
                        "id": node_id,
                        "label": level_name,
                        "type": "level",
                        "name": level_name
                    })
            else:
                nodes.append({
                    "id": node_id,
                    "label": node_id,
                    "type": "unknown",
                    "name": node_id
                })
        
        return {
            "nodes": nodes,
            "links": links,
            "stats": {
                "total_nodes": len(nodes),
                "total_links": len(links),
                "items": len([n for n in nodes if n["type"] == "item"]),
                "topics": len([n for n in nodes if n["type"] == "topic"]),
                "levels": len([n for n in nodes if n["type"] == "level"]),
                "similar_relations": len([l for l in links if l["relation"] == "similar_to"]),
                "has_topic_relations": len([l for l in links if l["relation"] == "has_topic"]),
                "has_level_relations": len([l for l in links if l["relation"] == "has_level"])
            }
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Dataset file not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading knowledge graph: {str(e)}")
