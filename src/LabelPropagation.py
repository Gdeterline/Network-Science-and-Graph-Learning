import networkx as nx
import numpy as np
from sklearn.metrics import f1_score
from collections import Counter
import random

def get_neighbors(G: nx.Graph, node):
    """
    Return the list of neighbors for a given node.

    Parameters
    ----------
    G : nx.Graph
        The input graph.
    node : hashable
        The node id.

    Returns
    -------
    list
        List of neighbor node ids.
    """
    return list(G.neighbors(node))


def get_labeled_nodes(G: nx.Graph, label_name: str):
    """
    Get all nodes that have a valid label for a given attribute.
    
    Parameters
    ----------
    G : nx.Graph
        The input graph.
    label_name : str
        The node attribute name.
        
    Returns
    -------
    list
        List of node ids that have the specified attribute.
    """
    return [n for n, data in G.nodes(data=True) if label_name in data]


def get_ground_truth_labels(G: nx.Graph, label_name: str):
    """
    Extract the ground truth labels for all nodes before any modification.

    Parameters
    ----------
    G : nx.Graph
        The original graph with all labels.
    label_name : str
        The node attribute to extract.

    Returns
    -------
    dict
        A dictionary mapping node ids to their true labels.
    """
    labels = {}
    for node, data in G.nodes(data=True):
        if label_name in data:
            labels[node] = data[label_name]
    return labels

def remove_fraction_of_labels(G: nx.Graph, label_name: str, fraction: float, seed: int = None):
    """
    Remove a fraction of labels from the graph for a given node attribute.
    Only removes labels from nodes that actually have the attribute.

    Parameters
    ----------
    G : nx.Graph
        The input graph (will NOT be modified).
    label_name : str
        The node attribute to remove labels from.
    fraction : float
        The fraction of labeled nodes to hide (between 0 and 1).
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    G_modified : nx.Graph
        A copy of the graph with some labels removed.
    removed_nodes : list
        List of node ids whose labels were removed.
    ground_truth : dict
        Dictionary mapping removed node ids to their original labels.
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Create a copy to avoid modifying the original
    G_modified = G.copy()
    
    # Get nodes that have the label
    labeled_nodes = get_labeled_nodes(G_modified, label_name)
    
    if len(labeled_nodes) == 0:
        return G_modified, [], {}
    
    # Determine how many to remove
    num_to_remove = int(fraction * len(labeled_nodes))
    if num_to_remove == 0:
        num_to_remove = 1  # Remove at least one if fraction > 0
    
    # Randomly select nodes to remove labels from
    removed_nodes = list(np.random.choice(labeled_nodes, size=num_to_remove, replace=False))
    
    # Store ground truth before removal
    ground_truth = {node: G_modified.nodes[node][label_name] for node in removed_nodes}
    
    # Remove the labels
    for node in removed_nodes:
        del G_modified.nodes[node][label_name]
    
    return G_modified, removed_nodes, ground_truth

def label_propagation(G: nx.Graph, label_name: str, max_iterations: int = 100):
    """
    Perform Label Propagation for semi-supervised node classification.
    
    This algorithm propagates known labels to unlabeled nodes using majority 
    voting among neighbors. Labeled nodes are "clamped" (their labels never change).

    Parameters
    ----------
    G : nx.Graph
        The input graph (some nodes may have missing labels).
    label_name : str
        The node attribute to propagate.
    max_iterations : int
        Maximum number of iterations before stopping.

    Returns
    -------
    predicted_labels : dict
        A dictionary mapping ALL node ids to their predicted/known labels.
        Nodes that couldn't be labeled (isolated or in unlabeled components) 
        will have value None.
    num_iterations : int
        The number of iterations performed before convergence.
    """
    # Initialize labels: known labels are fixed, unknown are None
    labels = {}
    labeled_set = set()
    
    for node, data in G.nodes(data=True):
        if label_name in data:
            labels[node] = data[label_name]
            labeled_set.add(node)
        else:
            labels[node] = None
    
    unlabeled_nodes = [n for n in G.nodes() if n not in labeled_set]
    
    # Iterative propagation
    for iteration in range(max_iterations):
        updated = False
        
        for node in unlabeled_nodes:
            # Get labels of neighbors
            neighbor_labels = []
            for neighbor in get_neighbors(G, node):
                if labels[neighbor] is not None:
                    neighbor_labels.append(labels[neighbor])
            
            if neighbor_labels:
                # Majority voting
                label_counts = Counter(neighbor_labels)
                most_common = label_counts.most_common()
                
                # Handle ties by random selection among top labels
                max_count = most_common[0][1]
                top_labels = [lbl for lbl, cnt in most_common if cnt == max_count]
                new_label = random.choice(top_labels)
                
                if labels[node] != new_label:
                    labels[node] = new_label
                    updated = True
        
        # Check for convergence
        if not updated:
            return labels, iteration + 1
    
    return labels, max_iterations


def compute_accuracy(ground_truth: dict, predicted_labels: dict, nodes_to_evaluate: list):
    """
    Compute accuracy on the specified nodes.

    Parameters
    ----------
    ground_truth : dict
        True labels for each node.
    predicted_labels : dict
        Predicted labels for each node.
    nodes_to_evaluate : list
        List of node ids to evaluate.

    Returns
    -------
    float
        Accuracy score (between 0 and 1).
    """
    if len(nodes_to_evaluate) == 0:
        return 0.0
    
    correct = 0
    for node in nodes_to_evaluate:
        true_label = ground_truth.get(node)
        pred_label = predicted_labels.get(node)
        if true_label is not None and pred_label is not None and true_label == pred_label:
            correct += 1
    
    return correct / len(nodes_to_evaluate)


def compute_f1_score(ground_truth: dict, predicted_labels: dict, nodes_to_evaluate: list):
    """
    Compute macro-averaged F1 score on the specified nodes.

    Parameters
    ----------
    ground_truth : dict
        True labels for each node.
    predicted_labels : dict
        Predicted labels for each node.
    nodes_to_evaluate : list
        List of node ids to evaluate.

    Returns
    -------
    float
        Macro F1 score (between 0 and 1).
    """
    if len(nodes_to_evaluate) == 0:
        return 0.0
    
    # Filter out nodes with None predictions
    valid_nodes = [n for n in nodes_to_evaluate 
                   if ground_truth.get(n) is not None and predicted_labels.get(n) is not None]
    
    if len(valid_nodes) == 0:
        return 0.0
    
    y_true = [ground_truth[node] for node in valid_nodes]
    y_pred = [predicted_labels[node] for node in valid_nodes]
    
    try:
        return f1_score(y_true, y_pred, average='macro', zero_division=0)
    except Exception:
        return 0.0


def compute_mean_absolute_error(ground_truth: dict, predicted_labels: dict, nodes_to_evaluate: list):
    """
    Compute Mean Absolute Error on the specified nodes.
    
    Note: This assumes labels are numeric. For categorical labels, 
    this metric may not be meaningful.

    Parameters
    ----------
    ground_truth : dict
        True labels for each node.
    predicted_labels : dict
        Predicted labels for each node.
    nodes_to_evaluate : list
        List of node ids to evaluate.

    Returns
    -------
    float
        Mean Absolute Error.
    """
    if len(nodes_to_evaluate) == 0:
        return 0.0
    
    errors = []
    for node in nodes_to_evaluate:
        true_label = ground_truth.get(node)
        pred_label = predicted_labels.get(node)
        
        if true_label is not None and pred_label is not None:
            try:
                errors.append(abs(float(true_label) - float(pred_label)))
            except (ValueError, TypeError):
                # Skip if labels are not numeric
                continue
    
    return sum(errors) / len(errors) if errors else 0.0


def evaluate_label_propagation(ground_truth: dict, predicted_labels: dict, nodes_to_evaluate: list):
    """
    Comprehensive evaluation of label propagation predictions.

    Parameters
    ----------
    ground_truth : dict
        True labels for each node.
    predicted_labels : dict
        Predicted labels for each node.
    nodes_to_evaluate : list
        List of node ids to evaluate (typically the nodes whose labels were removed).

    Returns
    -------
    dict
        Dictionary containing:
        - 'accuracy': Classification accuracy
        - 'f1_score': Macro-averaged F1 score
        - 'mae': Mean Absolute Error (for numeric labels)
        - 'coverage': Fraction of nodes that received a prediction
    """
    # Compute coverage (how many nodes got a prediction)
    predicted_count = sum(1 for n in nodes_to_evaluate if predicted_labels.get(n) is not None)
    coverage = predicted_count / len(nodes_to_evaluate) if nodes_to_evaluate else 0.0
    
    return {
        'accuracy': compute_accuracy(ground_truth, predicted_labels, nodes_to_evaluate),
        'f1_score': compute_f1_score(ground_truth, predicted_labels, nodes_to_evaluate),
        'mae': compute_mean_absolute_error(ground_truth, predicted_labels, nodes_to_evaluate),
        'coverage': coverage
    }


def run_label_propagation_experiment(G: nx.Graph, label_name: str, fraction: float, 
                                      max_iterations: int = 100, seed: int = None):
    """
    Run a complete label propagation experiment: remove labels, propagate, evaluate.

    Parameters
    ----------
    G : nx.Graph
        The input graph with full labels.
    label_name : str
        The node attribute to test.
    fraction : float
        Fraction of labels to remove (0 to 1).
    max_iterations : int
        Maximum iterations for label propagation.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    dict
        Results dictionary containing:
        - 'metrics': Evaluation metrics (accuracy, f1, mae, coverage)
        - 'num_iterations': Number of iterations until convergence
        - 'num_removed': Number of labels that were removed
        - 'predicted_labels': The full prediction dictionary
    """
    # Step 1: Remove a fraction of labels
    G_modified, removed_nodes, ground_truth = remove_fraction_of_labels(
        G, label_name, fraction, seed=seed
    )
    
    # Step 2: Run label propagation
    predicted_labels, num_iterations = label_propagation(
        G_modified, label_name, max_iterations=max_iterations
    )
    
    # Step 3: Evaluate on the removed nodes
    metrics = evaluate_label_propagation(ground_truth, predicted_labels, removed_nodes)
    
    return {
        'metrics': metrics,
        'num_iterations': num_iterations,
        'num_removed': len(removed_nodes),
        'predicted_labels': predicted_labels,
        'ground_truth': ground_truth,
        'removed_nodes': removed_nodes
    }
    