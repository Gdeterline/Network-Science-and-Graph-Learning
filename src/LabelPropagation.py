import networkx as nx
import numpy as np
from sklearn.metrics import f1_score
import torch

def neighbors(G: nx.Graph, v):
    """
    Return the neighbors list of a node

    Parameters
    ----------
    v : int
    node id
    
    Returns
    -------
    neighbors_list : python list
    """
    neighbors_list = G.neighbors(v)
    return list(neighbors_list)

def remove_fraction_of_labels_from_graph(G: nx.Graph, label_name, fraction):
    """
    Remove a fraction of labels from the graph for a given node attribute.

    Parameters
    ----------
    label_name : str
        The node attribute to remove labels from.
    fraction : float
        The fraction of labels to remove (between 0 and 1).
    """
    # Create a copy of the graph to avoid modifying the original graph
    graph_copy = G.copy()
    
    all_nodes = list(graph_copy.nodes())
    num_to_remove = int(fraction * len(all_nodes))
    nodes_to_remove = np.random.choice(all_nodes, size=num_to_remove, replace=False)

    for node in nodes_to_remove:
        if label_name in graph_copy.nodes[node]:
            del graph_copy.nodes[node][label_name]
    G = graph_copy
    return G, nodes_to_remove

def propagate_labels(G: nx.Graph, label_name, max_iterations=100):
    """
    Perform label propagation to predict missing labels for a given node attribute using majority voting.
    
    Parameters
    ----------
    label_name : str
        The node attribute to propagate labels for.
    max_iterations : int
        The maximum number of iterations to perform.
    Returns
    -------
    labels : dict
        A dictionary mapping node ids to their predicted labels.
    """
    # Initialize labels dictionary
    labels = {}
    for node in G.nodes():
        if label_name in G.nodes[node]:
            labels[node] = G.nodes[node][label_name]
        else:
            labels[node] = None

    for iteration in range(max_iterations):
        labels_updated = labels.copy()
        for node in G.nodes():
            if labels[node] is None:
                neighbor_labels = [labels[neighbor] for neighbor in neighbors(G, node) if labels[neighbor] is not None]
                if neighbor_labels:
                    # Majority voting
                    majority_label = max(set(neighbor_labels), key=neighbor_labels.count)
                    labels_updated[node] = majority_label
        # Check for convergence
        if labels == labels_updated:
            break
        labels = labels_updated

    return labels

def evaluate_label_propagation(true_label, predicted_labels, nodes_to_evaluate):
    """
    Evaluate the accuracy of label propagation.

    Parameters
    ----------
    true_label : dict
        A dictionary mapping node ids to their true labels.
    predicted_labels : dict
        A dictionary mapping node ids to their predicted labels.
    nodes_to_evaluate : list
        A list of node ids to evaluate.

    Returns
    -------
    accuracy : float
        The accuracy of the label propagation.
    f1 : float
        The F1 score of the label propagation.
    mean_absolute_error : float
        The mean absolute error of the label propagation.
    """
    correct = 0
    total = 0
    
    # Compute accuracy only on the nodes that had their labels removed
    for node in nodes_to_evaluate:
        if true_label[node] == predicted_labels[node]:
            correct += 1
        total += 1
    accuracy = correct / total if total > 0 else 0.0
    
    # Compute the f1 score
    y_true = [true_label[node] for node in nodes_to_evaluate]
    y_pred = [predicted_labels[node] for node in nodes_to_evaluate]
    f1 = f1_score(y_true, y_pred, average='macro')
    
    # Compute the mean absolute error
    absolute_errors = []
    for node in nodes_to_evaluate:
        absolute_errors.append(abs(true_label[node] - predicted_labels[node]))
    mean_absolute_error = sum(absolute_errors) / len(absolute_errors) if absolute_errors else 0.0
    
    return accuracy, f1, mean_absolute_error
    