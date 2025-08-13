#!/bin/env python

import networkx as nx
import matplotlib.pyplot as plt

# Python code to reproduce the issue of bug 1

# Bug 1: https://github.com/networkx/networkx/issues/6874
class ManualGraphLoader:
    def __init__(self):
        self.G = self.create_graph_from_data()

    def create_graph_from_data(self):
        G = nx.DiGraph()
        # Add nodes
        for i in range(8):
            G.add_node(i)

        # Add edges with weights
        edges_data = [
            (0, 5, 12), (0, 7, 1), (0, 4, 6), (1, 0, -1), (2, 3, 5), (2, 7, -1), (4, 0, 12),
            (5, 4, 15), (5, 3, -16), (6, 3, 4), (6, 5, -4), (6, 4, -1), (7, 5, -8), (7, 0, 9),
            (7, 4, 7), (7, 2, 1)
        ]

        for src, tgt, weight in edges_data:
            G.add_edge(src, tgt, weight=weight)

        return G

    def compute_shortest_path_length_bellman_ford(self, source, target):
        """Computes shortest path length between source and target using Bellman-Ford algorithm."""
        try:
            return nx.bellman_ford_path_length(self.G, source=source, target=target, weight='weight')
        except nx.NetworkXNoPath:
            print(f"Bellman-Ford: No path exists between {source} and {target}.")
            return None
        except nx.NetworkXUnbounded:
            print(f"Bellman-Ford: A negative cycle exists in the graph.")
            return None

    def compute_shortest_path_length_goldberg_radzik(self, source, target):
        """Computes the shortest path length between source and target using the Goldberg-Radzik algorithm."""
        try:
            _, distance_map = nx.goldberg_radzik(self.G, source=source, weight='weight')
            return distance_map.get(target, None)
        except nx.NetworkXNoPath:
            print(f"Goldberg_Radzik: No path exists between {source} and {target}.")
            return None
        except nx.NetworkXUnbounded:
            print(f"Goldberg_Radzik: A negative cycle exists in the graph.")
            return None

    def get_graph(self):
        """Returns the manually created graph."""
        return self.G

def try_bug_1():
    graph_loader = ManualGraphLoader()
    G = graph_loader.get_graph()

    source, target = 6, 0

    shortest_path_length = graph_loader.compute_shortest_path_length_bellman_ford(source, target)
    print(f"Shortest path length between {source} and {target} using Bellman-Ford: {shortest_path_length}")

    shortest_path_length = graph_loader.compute_shortest_path_length_goldberg_radzik(source, target)
    print(f"Shortest path length between {source} and {target} using Goldberg_Radzik: {shortest_path_length}")

    try:
        cycle = nx.negative_edge_cycle(G, weight='weight')
        if cycle:
            print("The graph has a negative weight cycle.")
        else:
            print("The graph does not have a negative weight cycle.")
    except nx.NetworkXUnbounded:
        print("The graph has a negative cycle.")

if __name__ == "__main__":
    try_bug_1()
