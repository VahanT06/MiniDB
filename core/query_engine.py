"""
Query Engine Module

Implements the full Query Engine for MiniDB:
- search
- range search
- insertion
- deletion
- update (modification)

Works together with:
- Database (raw storage + index directory)
- IndexAVLTree (AVL tree supporting duplicate values)
"""

import uuid


class QueryEngine:
    """
    Implements the full Query Engine for MiniDB .
    """

    def __init__(self, database):
        """
        Initialize with a Database object.
        """
        self._db = database

    def search(self, attribute, key):
        """
        Search using an AVL index.
        """
        if attribute not in self._db._indexes:
            return []
        return self._db.search_by_attribute(attribute, key)

    def range_search(self, attribute, start_key, end_key):
        """
        Range search using AVL index.
        """
        if attribute not in self._db._indexes:
            return []
        return self._db.range_query(attribute, start_key, end_key)

    def insert(self, record):
        """
        Insert record into hash map storage and update all indexes.
        Return the new song_id (UUID).
        """
        # Ensure the record has a unique ID
        if 'song_id' not in record:
            record['song_id'] = str(uuid.uuid4())

        record_id = record['song_id']

        # Insert into Storage (Dictionary) - O(1)
        # If the ID exists, this will overwrite
        self._db._data[record_id] = record

        # Update Indexes - O(M * log N) where M is number of indexed attributes
        for attr, index in self._db._indexes.items():
            key = record.get(attr)
            if key is not None:
                # We insert the UUID (record_id) into the AVL tree
                index.insert_value(key, record_id)

        return record_id

    def delete(self, record_id):
        """
        Deletes a record from storage and removes its references from all indexes.
        Returns True if successful, False if record_id not found.
        """
        # Check existence in Storage - O(1)
        record = self._db._data.get(record_id)
        if record is None:
            return False

        # Remove pointers from AVL Indexes
        # We need the record data to know which tree nodes to clean up.
        for attr, index in self._db._indexes.items():
            key = record.get(attr)
            if key is None:
                continue

            # Get the list of UUIDs associated with this attribute value
            values_list = index.get(key)

            if values_list and record_id in values_list:
                # Remove this specific UUID from the list
                values_list.remove(record_id)

                # If the list becomes empty, we remove the node from the AVL tree entirely
                # to keep the tree clean.
                if len(values_list) == 0:
                    index.remove(key)

        # Delete from Storage - O(1)
        del self._db._data[record_id]
        return True

    def update(self, record_id, updated_fields: dict):
        """
        Update a record and adjust indexes for any modified indexed attributes.
        """
        # Fetch the existing record (O(1))
        record = self._db._data.get(record_id)
        if record is None:
            return False

        # Update indexes (only for attributes that are indexed)
        for attr, index in self._db._indexes.items():
            if attr not in updated_fields:
                continue  # attribute not being updated

            old_key = record.get(attr)
            new_key = updated_fields[attr]

            if old_key == new_key:
                continue  # no change

            # Remove old pointer
            values_list = index.get(old_key)
            if values_list and record_id in values_list:
                values_list.remove(record_id)
                if len(values_list) == 0:
                    index.remove(old_key)

            # Insert new pointer
            index.insert_value(new_key, record_id)

        # Update the record stored in memory
        record.update(updated_fields)

        return True

    def compound_search(self, criteria: list, operator: str):
        """
        Performs a boolean search (AND / OR) across multiple attributes.

        Args:
            criteria (list): A list of tuples
            operator (str): 'AND' (Intersection) or 'OR' (Union)

        Returns:
            list: A list of full record dictionaries.
        """
        if not criteria:
            return []
        result_ids = None

        for attribute, value in criteria:
            # Check if index exists
            if attribute not in self._db._indexes:
                print(f"Warning: No index for '{attribute}'. Skipping this criterion.")
                continue

            index = self._db._indexes[attribute]

            # Get the list of UUIDs from the AVL Tree
            # We convert the list to a Python 'set' for fast operations
            ids_list = index.get(value)
            current_ids = set(ids_list) if ids_list else set()

            # Combine with previous results
            if result_ids is None:
                # First iteration: just load the first set
                result_ids = current_ids
            else:
                if operator.upper() == "OR":
                    # Union: Add new IDs to the pile
                    result_ids = result_ids.union(current_ids)
                elif operator.upper() == "AND":
                    # Intersection: Keep only IDs present in BOTH sets
                    result_ids = result_ids.intersection(current_ids)

        # If result_ids is still None (e.g., no valid indexes found), return empty
        if not result_ids:
            return []

        # Convert UUIDs back to full records
        final_records = []
        for rid in result_ids:
            rec = self._db.get_record_by_id(rid)
            if rec:
                final_records.append(rec)

        return final_records
