"""
Indexing AVL Tree Module

This module provides the `IndexAVLTree` class, a specialized extension of an
AVL Tree designed specifically for database-style indexing. Unlike a standard
map which overwrites values for duplicate keys, this implementation aggregates
multiple values under a single key using a list structure.

Typical use cases:
    - Indexing database records by non-unique fields (e.g., songs by release year).
    - Implementing tag search engines.
    - Grouping data items by categories.
"""

from PROJECT.core.ds_collection import AVLTreeMap


class IndexAVLTree(AVLTreeMap):
    """
    A specialized AVL Tree for indexing, inheriting from AVLTreeMap.

    This class is designed to handle non-unique keys, which is essential
    for an index. For example, many songs can have the same 'release_year'.

    Instead of overwriting the value for a key, it stores all values
    in a list.
    """

    def insert_value(self, k, v):
        """
        Inserts a new value (v) for a given key (k).

        If the key (k) is not present, it creates a new list containing (v)
        and inserts it using the parent's `put` method.

        If the key (k) is already present, it appends the new value (v) to
        the existing list of values.
        """
        # Check if the key already exists
        existing_values = self.get(k)

        if existing_values is None:
            # Key is new. We must store the value in a new list.
            # We use the parent's put() method to handle the
            # actual tree insertion and balancing.
            super().put(k, [v])
        else:
            # Key already exists. The `get` method returned a list.
            # We simply append the new value to that list.
            # The list is modified in-place, so the tree's reference
            # to it is still valid and no `put` is needed.
            existing_values.append(v)
