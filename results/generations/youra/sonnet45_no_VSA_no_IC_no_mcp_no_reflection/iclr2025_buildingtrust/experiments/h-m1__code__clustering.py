import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster, cophenet
from scipy.spatial.distance import squareform


class WardClusterer:
    def __init__(self, distance_matrix: np.ndarray):
        self.distance_matrix = distance_matrix
        self.linkage_matrix = None

    def fit(self, method: str = 'ward') -> np.ndarray:
        # [n-1, 4] scipy linkage format
        condensed_dist = squareform(self.distance_matrix)
        self.linkage_matrix = linkage(condensed_dist, method=method)
        return self.linkage_matrix

    def get_clusters(self, k: int) -> np.ndarray:
        # [n,] cluster assignments (1 to k)
        return fcluster(self.linkage_matrix, k, criterion='maxclust')

    def compute_cophenetic(self) -> float:
        condensed_dist = squareform(self.distance_matrix)
        return cophenet(self.linkage_matrix, condensed_dist)[0]
