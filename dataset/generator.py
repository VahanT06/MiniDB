"""
Mock Music Dataset Generator Module

This module orchestrates the generation of synthetic, high-volume music metadata
saved directly to a CSV schema. It relies on the `faker` library combined with
localized data pooling techniques to guarantee realistic relational patterns—such
as repeating artists, shared album naming conventions, and interconnected graph
cliques via featured artist properties.

Prerequisites:
    $ pip install faker
"""


import csv
import random
import uuid
from faker import Faker

NUM_RECORDS = 1_000_000
OUTPUT_FILE = 'songs_dataset.csv'

# Create smaller, realistic pools of data to pull from.
# This ensures data is relational (e.g., artists reappear).
NUM_ARTISTS = 7_000
NUM_ALBUM_WORDS = 2_000
GENRE_POOL = [
    'Pop', 'Rock', 'Hip-Hop', 'Electronic', 'R&B', 'Jazz',
    'Classical', 'Country', 'Reggae', 'Blues', 'Metal', 'Folk',
    'Techno', 'Indie', 'Alternative', 'Punk', 'Funk', 'Soul'
]

fake = Faker()

artist_pool = [fake.name() for _ in range(NUM_ARTISTS)]
album_word_pool = [fake.word().capitalize() for _ in range(NUM_ALBUM_WORDS)]

# Data Generation
records = []
for _ in range(NUM_RECORDS):

    # Basic Attributes
    song_id = str(uuid.uuid4())
    song_title = " ".join(fake.words(nb=random.randint(2, 5))).capitalize()

    # Relational/Categorical Attributes (from pools)
    artist_name = random.choice(artist_pool)
    album_title = f"{random.choice(album_word_pool)} {random.choice(album_word_pool)}"
    genre = random.choice(GENRE_POOL)

    # Numeric Attributes (for Range/Analytics)
    release_year = random.randint(1970, 2025)
    duration_ms = random.randint(120000, 360000)  # 2 to 6 minutes

    # Graph Attribute (Relational)
    # Create featured artists. Most songs have 0, some have 1 or 2.
    # This creates the graph edges 
    featured_artists_list = []
    num_features = random.choices([0, 1, 2], weights=[0.75, 0.20, 0.05], k=1)[0]

    if num_features > 0:
        # Select from artists who are NOT the main artist
        possible_features = [a for a in artist_pool if a != artist_name]
        if len(possible_features) >= num_features:
            featured_artists_list = random.sample(possible_features, num_features)

    # Store the list as a pipe-delimited string in the CSV
    featured_artists_str = "|".join(featured_artists_list)

    # Add record to our list
    records.append({
        'song_id': song_id,
        'song_title': song_title,
        'artist_name': artist_name,
        'featured_artists': featured_artists_str,
        'album_title': album_title,
        'release_year': release_year,
        'duration_ms': duration_ms,
        'genre': genre
    })

# CSV Writing
try:
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        # Define fieldnames based on the 8 attributes 
        fieldnames = [
            'song_id', 'song_title', 'artist_name', 'featured_artists',
            'album_title', 'release_year', 'duration_ms', 'genre'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(records)

    print(f"Successfully created {OUTPUT_FILE}!")

except IOError as e:
    print(f"Error writing to file: {e}")

if __name__ == "__main__":
    pass
