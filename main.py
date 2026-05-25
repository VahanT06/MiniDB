from PROJECT.core.storage import Database
from PROJECT.core.query_engine import QueryEngine
import os


def main():
    """
    Main function to run the MiniDB demonstration.
    Updated to support Dictionary-based storage (UUIDs).
    """

    # Initialize & Ingest
    print("\n=== 1. Data Ingestion & Storage ===")
    db = Database()

    # Path relative to project root
    DATA_PATH = 'dataset/songs_dataset.csv'

    # Check if file exists before loading to avoid confusion
    if not os.path.exists(DATA_PATH):
        print(f"Error: Dataset not found at {DATA_PATH}. Please run generator.py first.")
        return

    db.load_data(DATA_PATH)

    if not db._data:
        print("Data loading failed or empty. Exiting.")
        return

    # We can't use index 0 anymore because keys are UUIDs.
    # We grab the first key from the dictionary to show an example.
    first_uuid = next(iter(db._data))
    print("Data loaded successfully.")
    print(f"Total Records: {len(db._data)}")
    print("Example record (fetched by UUID):")
    print(db.get_record_by_id(first_uuid))

    # Indexing
    print("\n=== 2. Building AVL Indexes ===")
    # We build indexes on fields we plan to search
    db.build_index('release_year')
    db.build_index('artist_name')

    # Initialize the Query Engine (which uses these indexes)
    qe = QueryEngine(db)

    # Search
    print("\n=== 3. Search (AVL Lookup) ===")
    test_year = 1999
    print(f"Searching for songs released in {test_year}...")

    # This uses the AVL tree to find UUIDs, then gets records from the Dictionary
    results = qe.search('release_year', test_year)
    print(f"Found {len(results)} songs.")

    # Show first 3 results
    for song in results[:3]:
        print(f"  - [{song['song_id']}] {song['song_title']} ({song['artist_name']})")

    # Range Query
    print("\n=== 4. Range Query ===")
    start_year = 2000
    end_year = 2005
    print(f"Searching for songs between {start_year} and {end_year} (exclusive)...")

    range_results = qe.range_search('release_year', start_year, end_year)
    print(f"Found {len(range_results)} songs.")

    if range_results:
        print("Sample result:")
        print(f"  - {range_results[0]['release_year']}: {range_results[0]['song_title']}")

    # Insertion
    print("\n=== 5. Insertion (Create) ===")
    new_record = {
        # Note: We don't necessarily need to provide an ID; query_engine can generate one.
        # But we provide one here for clarity.
        "song_id": "TEST-RECORD-001",
        "song_title": "Data Structures Anthem",
        "artist_name": "The Algorithms",
        "featured_artists": "AVL Tree",
        "album_title": "O(log N) Beats",
        "release_year": 2025,
        "duration_ms": 180000,
        "genre": "Techno"
    }

    # This inserts into the Dictionary AND updates the AVL indexes (Year, Artist)
    new_id = qe.insert(new_record)
    print(f"Inserted new record with ID: {new_id}")

    # Verify it exists in the index
    print("Verifying via Search...")
    check = qe.search('artist_name', "The Algorithms")
    print(check)

    # Update
    print("\n=== 6. Update (Modify) ===")
    # Let's change the year from 2025 to 1990.
    # This requires removing the pointer from the '2025' AVL node
    # and adding it to the '1990' AVL node.

    print(f"Updating year for {new_id} to 1990...")
    qe.update(new_id, {"release_year": 1990})

    # Verify the update
    updated_record = db.get_record_by_id(new_id)
    print(f"Record after update: {updated_record['song_title']}, Year: {updated_record['release_year']}")

    # Verify the INDEX was updated (search for 1990 should find it now)
    search_1990 = qe.search('release_year', 1990)
    found_in_index = any(s['song_id'] == new_id for s in search_1990)
    print(f"Is record found in the 1990 Index? {found_in_index}")

    # Deletion
    print("\n=== 7. Deletion ===")
    print(f"Deleting record {new_id}...")
    qe.delete(new_id)

    # Verify deletion from Storage
    if db.get_record_by_id(new_id) is None:
        print("Success: Record removed from Storage (Dictionary).")
    else:
        print("Fail: Record still exists in Storage.")

    # Verify deletion from Index
    # Searching for 'The Algorithms' should now return empty
    deleted_check = qe.search('artist_name', "The Algorithms")
    if not deleted_check:
        print("Success: Record removed from Artist Index.")
    else:
        print("Fail: Record still referenced in Index.")

    # Boolean Logic
    print("\n=== 8. Advanced Query (AND / OR) ===")
    print("Query: Artist='Daft Punk' OR Year=1999")
    party_criteria = [
        ('artist_name', 'Daft Punk'),
        ('release_year', 1999)
    ]

    party_results = qe.compound_search(party_criteria, operator="OR")

    print(f"Found {len(party_results)} matches.")
    for song in party_results[:5]:
        print(f"  - [{song['release_year']}] {song['song_title']} ({song['artist_name']})")

    specific_criteria = [
        ('artist_name', 'Amanda Gallegos'),
        ('release_year', 1999)
    ]

    specific_results = qe.compound_search(specific_criteria, operator="AND")

    print(f"Found {len(specific_results)} matches.")
    for song in specific_results:
        print(f"  - {song['song_title']} by {song['artist_name']} ({song['release_year']})")


if __name__ == "__main__":
    main()
