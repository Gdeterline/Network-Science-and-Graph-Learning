from abc import ABC
from abc import abstractmethod
import networkx as nx
import numpy as np
import progressbar

class LinkPrediction(ABC):
    def __init__(self, graph):
        """
        Constructor

        Parameters
        ----------
        graph : Networkx graph
        """
        self.graph = graph
        self.N = len(graph)

    def neighbors(self, v):
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
        neighbors_list = self.graph.neighbors(v)
        return list(neighbors_list)

    @abstractmethod
    def fit(self):
        raise NotImplementedError("Fit must be implemented")
    
class CommonNeighbors(LinkPrediction):
    def __init__(self, graph):
        super(CommonNeighbors, self).__init__(graph)

    def fit(self):
        scores = {}
        nodes = list(self.graph.nodes())
        bar = progressbar.ProgressBar(maxval=len(nodes))
        bar.start()
        
        for i, u in enumerate(nodes):
            neighbors_u = set(self.neighbors(u))
            for v in nodes[i+1:]:
                # Only compute for non-edges
                if not self.graph.has_edge(u, v):
                    neighbors_v = set(self.neighbors(v))
                    score = len(neighbors_u.intersection(neighbors_v))
                    scores[(u, v)] = score
            bar.update(i+1)
        
        bar.finish()
        
        return scores

class Jaccard(LinkPrediction):
    def __init__(self, graph):
        super(Jaccard, self).__init__(graph)

    def fit(self):
        scores = {}
        nodes = list(self.graph.nodes())
        bar = progressbar.ProgressBar(maxval=len(nodes))
        bar.start()
        for i, u in enumerate(nodes):
            neighbors_u = set(self.neighbors(u))
            for v in nodes[i+1:]:
                if not self.graph.has_edge(u, v):
                    neighbors_v = set(self.neighbors(v))
                    
                    intersection = neighbors_u.intersection(neighbors_v)
                    union = neighbors_u.union(neighbors_v)
                    
                    if len(union) == 0:
                        score = 0.0
                    else:
                        score = len(intersection) / len(union)
                    
                    scores[(u, v)] = score
            bar.update(i+1)
            
        bar.finish()
        
        return scores

class AdamicAdar(LinkPrediction):
    def __init__(self, graph):
        super(AdamicAdar, self).__init__(graph)

    def fit(self):
        scores = {}
        nodes = list(self.graph.nodes())
        bar = progressbar.ProgressBar(maxval=len(nodes))
        bar.start()
        for i, u in enumerate(nodes):
            neighbors_u = set(self.neighbors(u))
            for v in nodes[i+1:]:
                if not self.graph.has_edge(u, v):
                    neighbors_v = set(self.neighbors(v))
                    intersection = neighbors_u.intersection(neighbors_v)
                    
                    score = 0
                    for w in intersection:
                        degree = self.graph.degree(w)
                        if degree > 1:
                            score += 1 / np.log(degree)
                            
                    scores[(u, v)] = score
            bar.update(i+1)
            
        bar.finish()
        
        return scores