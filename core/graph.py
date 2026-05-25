"""
Artist Collaboration Network Analysis Module

This module implements the `ArtistGraph` class using an Adjacency Map structure.
It parses music metadata to construct an undirected network where artists represent
nodes and collaborative tracks represent edges.

Key Capabilities:
    - Automatic graph construction parsing multi-artist string combinations.
    - Pathfinding (Shortest Path) using Breadth-First Search (BFS).
    - Separation metrics (degrees of separation/max-depth constraints).
    - Group isolation and cluster identification via Connected Components.
    - Network centrality rankings (Top K most collaborative artists).
"""


from collections import defaultdict, deque


class ArtistGraph:
    """
    Manages a graph of artist collaborations using an Adjacency Map structure.
    Nodes: Artist Names
    Edges: Undirected connection if they appeared on the same track.
    """

    def __init__(self, database):
        self._db = database
        # Uses a dictionary where keys are artists, and values are sets of collaborators
        self._graph = defaultdict(set)
        self._built = False

    def build_graph(self):
        """
        Constructs the graph from the database records (O(N) where N is number of songs).
        """
        self._graph.clear()

        # Helper to ensure artist names are consistently stripped of whitespace
        def normalize_name(name):
            return name.strip() if name else None

        for record in self._db._data.values():
            if record is None:
                continue

            main_artist = normalize_name(record.get("artist_name"))
            feat_str = record.get("featured_artists", "")

            if not main_artist:
                continue

            # Start with a set of all artists involved in this song
            collaborators = {main_artist}

            # Add featured artists to the set
            for raw_name in feat_str.split("|"):
                name = normalize_name(raw_name)
                if name and name != main_artist:
                    collaborators.add(name)

            # Create edges between all pairs in the collaboration set
            # This ensures if Artist A featured B, and B featured C on the same track, A, B, and C are all linked.
            collaborators_list = list(collaborators)
            for i in range(len(collaborators_list)):
                for j in range(i + 1, len(collaborators_list)):
                    artist1 = collaborators_list[i]
                    artist2 = collaborators_list[j]

                    # Add undirected edge to the Adjacency Map
                    self._graph[artist1].add(artist2)
                    self._graph[artist2].add(artist1)

        self._built = True

    def _ensure_built(self):
        """Lazy loader to build graph only when needed."""
        if not self._built:
            self.build_graph()

    def neighbors(self, artist):
        """Returns a sorted list of artists who have collaborated with the given artist (O(1))."""
        self._ensure_built()
        return sorted(list(self._graph.get(artist, [])))

    def degree(self, artist):
        """Returns the number of collaborators for an artist (O(1))."""
        self._ensure_built()
        return len(self._graph.get(artist, []))

    def bfs(self, start, max_depth=None):
        """
        Performs Breadth-First Search to find distances from a start artist (O(V+E)).
        Returns a dictionary {artist: distance}.
        """
        self._ensure_built()
        # Normalization is key here as keys in the graph are normalized
        start = start.strip() if start else None
        if not start or start not in self._graph:
            return {}

        dist = {start: 0}
        q = deque([start])

        while q:
            u = q.popleft()
            d = dist[u]

            if max_depth is not None and d >= max_depth:
                continue

            for v in self._graph[u]:
                if v not in dist:
                    dist[v] = d + 1
                    q.append(v)
        return dist

    def shortest_path(self, source, target):
        """
        Finds the shortest path of collaborations between two artists using BFS (O(V+E)).
        Returns a list of artist names: [source, ..., target].
        """
        self._ensure_built()
        source = source.strip() if source else None
        target = target.strip() if target else None

        if source not in self._graph or target not in self._graph:
            return []

        if source == target:
            return [source]

        q = deque([source])
        parent = {source: None}
        visited = {source}

        while q:
            u = q.popleft()

            for v in self._graph[u]:
                if v not in visited:
                    visited.add(v)
                    parent[v] = u
                    q.append(v)

                    if v == target:
                        # Reconstruct path
                        path = [v]
                        while parent[path[-1]] is not None:
                            path.append(parent[path[-1]])
                        path.reverse()
                        return path
        return []

    def connected_components(self):
        """Returns a list of lists, where each inner list is a group of connected artists (O(V+E))."""
        self._ensure_built()
        visited = set()
        components = []

        for node in list(self._graph.keys()):
            if node in visited:
                continue

            comp = []
            q = deque([node])
            visited.add(node)

            while q:
                u = q.popleft()
                comp.append(u)

                for v in self._graph[u]:
                    if v not in visited:
                        visited.add(v)
                        q.append(v)
            components.append(sorted(comp))

        return components

    def top_k_by_degree(self, k=10):
        """Returns the top K most connected artists (O(V log V))."""
        self._ensure_built()
        degrees = [(artist, len(neigh)) for artist, neigh in self._graph.items()]
        degrees.sort(key=lambda x: x[1], reverse=True)
        return degrees[:k]
