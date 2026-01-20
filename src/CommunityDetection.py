import networkx as nx
import numpy as np
from networkx.algorithms.community import louvain_communities, greedy_modularity_communities
from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score


def get_ground_truth_communities(G: nx.Graph, label_name: str):
    """
    Extract ground truth community assignments from node attributes.
    
    Parameters
    ----------
    G : nx.Graph
        The input graph.
    label_name : str
        The node attribute representing community membership (e.g., 'dorm', 'major_index').
        
    Returns
    -------
    dict
        A dictionary mapping node ids to their community label.
    list
        List of nodes that have the attribute (in order).
    """
    communities = {}
    valid_nodes = []
    
    for node, data in G.nodes(data=True):
        if label_name in data and data[label_name] != 0:  # 0 often means missing
            communities[node] = data[label_name]
            valid_nodes.append(node)
    
    return communities, valid_nodes


def communities_to_labels(communities_list: list, nodes: list):
    """
    Convert a list of community sets to a label array for each node.
    
    """
    node_to_community = {}
    for comm_idx, community in enumerate(communities_list):
        for node in community:
            node_to_community[node] = comm_idx
    return node_to_community

def detect_communities_louvain(G: nx.Graph, seed: int = None, resolution: float = 1.0):
    """
    Detect communities using the Louvain algorithm.
    """
    communities = louvain_communities(G, seed=seed, resolution=resolution)
    communities = list(communities)
    return communities, len(communities)


def detect_communities_greedy_modularity(G: nx.Graph, resolution: float = 1.0):
    """
    Detect communities using the Greedy Modularity algorithm.
    """
    communities = greedy_modularity_communities(G, resolution=resolution)
    communities = list(communities)
    return communities, len(communities)


def compute_nmi(ground_truth_labels: list, predicted_labels: list):
    """
    Compute Normalized Mutual Information between two clusterings.
    """
    return normalized_mutual_info_score(ground_truth_labels, predicted_labels)


def compute_ari(ground_truth_labels: list, predicted_labels: list):
    """
    Compute Adjusted Rand Index between two clusterings.
    """
    return adjusted_rand_score(ground_truth_labels, predicted_labels)


def evaluate_communities(G: nx.Graph, detected_communities: list, label_name: str):
    """
    Evaluate detected communities against ground truth labels.
    """
    # Get ground truth
    ground_truth, valid_nodes = get_ground_truth_communities(G, label_name)
    
    if len(valid_nodes) == 0:
        return {'nmi': np.nan, 'ari': np.nan, 'num_communities': len(detected_communities)}
    
    # Convert detected communities to node labels
    detected_labels_dict = communities_to_labels(detected_communities, valid_nodes)
    
    # Build aligned label lists (only for nodes that have ground truth)
    y_true = []
    y_pred = []
    
    for node in valid_nodes:
        if node in detected_labels_dict:
            y_true.append(ground_truth[node])
            y_pred.append(detected_labels_dict[node])
    
    if len(y_true) == 0:
        return {'nmi': np.nan, 'ari': np.nan, 'num_communities': len(detected_communities)}
    
    # Compute metrics
    nmi = compute_nmi(y_true, y_pred)
    ari = compute_ari(y_true, y_pred)
    
    return {
        'nmi': nmi,
        'ari': ari,
        'num_communities': len(detected_communities),
        'num_ground_truth_classes': len(set(y_true))
    }


def run_louvain_evaluation(G: nx.Graph, label_name: str, seed: int = None, resolution: float = 1.0):
    """
    Run Louvain community detection and evaluate against ground truth
    """
    # Detect communities
    communities, num_communities = detect_communities_louvain(G, seed=seed, resolution=resolution)
    
    # Evaluate
    metrics = evaluate_communities(G, communities, label_name)
    metrics['algorithm'] = 'louvain'
    
    return metrics


def run_greedy_modularity_evaluation(G: nx.Graph, label_name: str, resolution: float = 1.0):
    """
    Run Greedy Modularity community detection and evaluate against ground truth.
    """
    # Detect communities
    communities, num_communities = detect_communities_greedy_modularity(G, resolution=resolution)
    
    # Evaluate
    metrics = evaluate_communities(G, communities, label_name)
    metrics['algorithm'] = 'greedy_modularity'
    
    return metrics


def run_community_detection_comparison(G: nx.Graph, label_name: str, seed: int = None):
    """
    Run both community detection algorithms and compare their performance
    """
    results = {
        'louvain': run_louvain_evaluation(G, label_name, seed=seed),
        'greedy_modularity': run_greedy_modularity_evaluation(G, label_name)
    }
    
    return results