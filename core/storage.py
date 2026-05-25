"""
Storage Module

This module serves as the central data management hub. It
defines the `Database` class, which handles data ingestion from CSV sources,
maintains primary record storage via a hash map, and integrates with
`IndexAVLTree` to manage secondary attribute indexes.

Key Capabilities:
    - O(1) primary key lookups using unique record identifiers.
    - O(log n) secondary attribute lookups via AVL Tree structures.
    - Highly efficient range queries over indexed attributes.
"""

import csv
import os
from PROJECT.core.indexing import IndexAVLTree


class Database:
    """
    Manages data ingestion, storage, and indexing using a Dictionary structure.
    """

    def __init__(self):
        """
        Initializes the database.

        self._data: A dictionary storing raw data.
                    Key: song_id (UUID string)
                    Value: The record dictionary (e.g., {'song_title': '...', ...})

        self._indexes: A dictionary to store and manage all created indexes.
                       The key is the attribute name (e.g., 'release_year')
                       and the value is the IndexAVLTree object.
        """
        self._data = {}
        self._indexes = {}

    def load_data(self, csv_relative_path):
        """
        Implements the data ingestion pipeline.
        Loads data from CSV and stores it in the internal `self._data` dictionary
        using 'song_id' as the key.
        """
        file_path = os.path.join(os.path.dirname(__file__), '..', csv_relative_path)
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        row['release_year'] = int(row['release_year'])
                        row['duration_ms'] = int(row['duration_ms'])
                    except ValueError:
                        continue

                    # Store the raw data record using song_id as the primary key
                    if 'song_id' in row:
                        record_id = row['song_id']
                        self._data[record_id] = row

            print(f"Data ingestion complete. Loaded {len(self._data)} records.")
        except Exception as e:
            print(f"An error occurred during data ingestion: {e}")

    def build_index(self, attribute_name):
        """
        Builds an AVL Tree index for a specified attribute.

        Iterates over all records in `self._data` and inserts the
        song_id (UUID) into the `IndexAVLTree` keyed by the attribute value.
        """
        if not self._data:
            print(f"Error: Cannot build index. Load data first.")
            return

        print(f"Building index for attribute: '{attribute_name}'...")

        # Create a new, empty index tree for this attribute
        index = IndexAVLTree()

        # Iterate over the dictionary items to get both ID and Record
        for record_id, record in self._data.items():
            key = record.get(attribute_name)

            if key is not None:
                # The 'key' is the attribute value (e.g., 1990)
                # The 'value' stored in the tree is the song_id (UUID)
                index.insert_value(key, record_id)

        # Store the newly built index
        self._indexes[attribute_name] = index
        print(f"Index for '{attribute_name}' is built and ready.")

    def get_record_by_id(self, record_id):
        """
        Retrieves a raw data record using its song_id (O(1) lookup).
        """
        return self._data.get(record_id)

    def search_by_attribute(self, attribute, key):
        """
        Performs an efficient lookup using a pre-built index.
        Returns a list of full record dictionaries.
        """
        index = self._indexes.get(attribute)
        if index is None:
            print(f"Error: No index found for '{attribute}'. Build index first.")
            return []
        # Use the AVL tree's get() method to find the list of song_ids
        record_ids = index.get(key)
        if record_ids is None:
            return []
        results = [self.get_record_by_id(rid) for rid in record_ids]
        return [res for res in results if res is not None]

    def range_query(self, attribute, start_key, end_key):
        """
        Performs an efficient range query using the AVL index.
        Returns a list of full record dictionaries.
        """
        index = self._indexes.get(attribute)
        if index is None:
            print(f"Error: No index found for '{attribute}'. Build index first.")
            return []

        results = []
        # `sub_map` returns an iterable of (key, value) entries
        # where value is the list of song_ids.
        for entry in index.sub_map(start_key, end_key):
            record_ids = entry.get_value()
            for rid in record_ids:
                rec = self.get_record_by_id(rid)
                if rec is not None:
                    results.append(rec)

        return results
