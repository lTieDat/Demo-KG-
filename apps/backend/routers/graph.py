from fastapi import APIRouter, HTTPException
from typing import Dict, List
import os

router = APIRouter(prefix="/graph", tags=["graph"])

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "dataset")

@router.get("/knowledge-graph")
async def get_knowledge_graph(limit: int = 10000):
    """
    Get knowledge graph data from dataset.
    Returns nodes and links for visualization.
    
    Args:
        limit: Maximum number of relationships to return (default: 10000)
    """
    try:
        # Use dataset files (no .normalized extension)
        kg_file = os.path.join(DATASET_PATH, "cpp.kg")
        item_file = os.path.join(DATASET_PATH, "cpp.item")
        link_file = os.path.join(DATASET_PATH, "cpp.link")
        
        # Read item metadata
        # Format: item_id, question_id, name, group, type (topic), level
        items_metadata = {}
        with open(item_file, 'r', encoding='utf-8') as f:
            next(f)  # Skip header
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 6:
                    item_id = parts[0]
                    question_id = parts[1]
                    name = parts[2]
                    group = parts[3]
                    topic = parts[4]  # This is the topic (type column)
                    level = parts[5]
                    items_metadata[item_id] = {
                        "question_id": question_id,
                        "name": name,
                        "group": group,
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
                
                # Extract topic name (remove T_ prefix and replace underscores with spaces)
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
            
            # Skip level_of and topic_of (reverse relationships, already handled)
            elif relation in ['level_of', 'topic_of']:
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
                            "label": metadata["question_id"],
                            "type": "item",
                            "item_id": item_id,
                            "metadata": {
                                "question_id": metadata["question_id"],
                                "name": metadata["name"],
                                "topic": topic_display,
                                "level": level_display
                            },
                            "name": f"{metadata['question_id']}: {metadata['name'][:40]}..." if len(metadata['name']) > 40 else f"{metadata['question_id']}: {metadata['name']}"
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
