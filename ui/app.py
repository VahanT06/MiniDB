"""
MiniDB

This module implements the primary graphical user interface (GUI) using Streamlit.
It bundles all underlying backend services (AVL indexing storage, the Boolean
query engine, Graph network analysis pipelines, and statistical analytics engines)
into a cohesive, web-based control panel.

Features:
    - Operational Dashboard
    - Multi-Strategy Search Engine (Simple, Range, and Boolean mapping)
    - Network Graph Topology Visualizer (Degrees of separation / path-finding)
    - Analytical Plotly Visualizations (Pie charts and trend scatters)
    - Dynamic Mutation Manager (In-memory CRUD validations)

Execution:
    Ensure you are in the directory of your UI and run the following command in terminal:
    $ streamlit run app.py
"""

import base64
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import random
import sys

# Absolute import setup
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_PARENT_DIR = os.path.abspath(os.path.join(APP_DIR, "..", ".."))
sys.path.insert(0, PROJECT_PARENT_DIR)

from PROJECT.core.storage import Database
from PROJECT.core.query_engine import QueryEngine
from PROJECT.core.graph import ArtistGraph
from PROJECT.core.analytics import Analytics

# Streamlit Page Config
st.set_page_config(
    page_title="MiniDB Pro",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Background helpers
@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_png_as_page_bg(os.path.join(APP_DIR, "background.jpg"))

# CSS Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #0E1117;
        border: 1px solid #262730;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF4B4B;
    }
    .metric-label {
        font-size: 1rem;
        color: #FAFAFA;
    }
</style>
""", unsafe_allow_html=True)

# Initialization
@st.cache_resource
def load_database():
    db = Database()
    db.load_data("dataset/songs_dataset.csv")
    db.build_index("release_year")
    db.build_index("artist_name")
    return db

@st.cache_resource
def initialize_system():
    db = load_database()
    db.build_index("genre")
    qe = QueryEngine(db)

    with st.spinner("Constructing Artist Collaboration Graph..."):
        graph = ArtistGraph(db)
        graph.build_graph()

    analytics = Analytics(db)
    return db, qe, graph, analytics

db, qe, graph, analytics = initialize_system()
if not db:
    st.stop()

# Sidebar Navigation
with st.sidebar:
    st.title("MiniDB Menu")
    st.markdown("Explore the song database with ease. Select an operation from below.")
    st.markdown("---")

    page = st.sidebar.selectbox(
        "Operation",
        [
            "Dashboard",
            "Search Engine",
            "Graph Explorer",
            "Analytics",
            "Data Manager"
        ]
    )

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:12px; color:gray; line-height:1.3;">
            Developed by <span style="color:#2ca02c; font-weight:bold;">
            Milena Mkrtumyan, Aram Bakhchagulyan, Vahan Tonoyan
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

# Pages
if page == "Dashboard":
    st.markdown(
        "<h1 style='color: SeaShell;'>MiniDB – Songs System</h1>",
        unsafe_allow_html=True
    )
    col1, col2, col3, col4 = st.columns(4)

    total_records = len(db._data)
    total_artists = len({rec["artist_name"] for rec in db._data.values()})
    min_year = min(rec["release_year"] for rec in db._data.values())
    max_year = max(rec["release_year"] for rec in db._data.values())

    with col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value" style="color:Ivory; font-size:1.8rem;">{total_records:,}</div>'
            f'<div class="metric-label">Total Songs</div></div>',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value" style="color:Ivory;">{total_artists:,}</div>'
            f'<div class="metric-label">Unique Artists</div></div>',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value" style="color:Ivory;">{int(min_year)}</div>'
            f'<div class="metric-label">Oldest Track</div></div>',
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value" style="color:Ivory;">{int(max_year)}</div>'
            f'<div class="metric-label">Newest Track</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("### Random Data Sample")
    if len(db._data) > 0:
        sample_ids = random.sample(list(db._data.keys()), min(5, len(db._data)))
        sample_data = [db.get_record_by_id(i) for i in sample_ids]
        st.dataframe(pd.DataFrame(sample_data), width='stretch')
    else:
        st.info("No data loaded.")

elif page == "Search Engine":
    st.title("Advanced Search")
    tab1, tab2, tab3 = st.tabs(["Simple Search", "Range Search", "Boolean Builder (AND/OR)"])

    # Simple Search
    with tab1:
        col_s1, col_s2 = st.columns([1, 3])
        with col_s1:
            search_attr = st.selectbox("Search By", ["artist_name", "release_year", "genre"])
        with col_s2:
            search_val = st.text_input("Value", placeholder="e.g., Adele")
            if search_attr == "release_year" and search_val:
                try:
                    search_val = int(search_val)
                except:
                    pass

        if st.button("Search", key="simple_btn"):
            results = qe.search(search_attr, search_val.capitalize())
            st.success(f"Found {len(results)} matches.")
            if results:
                st.dataframe(pd.DataFrame(results), width='stretch')

    # Range Search
    with tab2:
        st.markdown(
            '''
            <div style="
                background-color: rgba(224, 247, 250, 0.7);  /* light blue with 50% opacity */
                color: black;                                /* text color */
                padding: 10px;
                border-radius: 5px;
            ">
                Find songs released within a specific time period.
            </div>
            ''',
            unsafe_allow_html=True
        )
        r_start, r_end = st.slider("Select Year Range", 1970, 2025, (1990, 2000))
        if st.button("Run Range Query", key="range_btn"):
            results = qe.range_search('release_year', r_start, r_end)
            st.success(f"Found {len(results)} songs between {r_start} and {r_end}.")
            if results:
                st.dataframe(pd.DataFrame(results), width='stretch')

    # Boolean
    with tab3:
        st.write("### Insert values below")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            artist_cond = st.text_input("Artist Name (Optional)")
        with col_b2:
            year_cond = st.number_input("Release Year (Optional)", min_value=0, value=0)
        operator = st.radio("Operator", ["OR (Either is true)", "AND (Both must be true)"], horizontal=True)
        op_code = "OR" if "OR" in operator else "AND"
        if st.button("Execute Compound Search"):
            criteria = []
            if artist_cond:
                criteria.append(('artist_name', artist_cond))
            if year_cond > 0:
                criteria.append(('release_year', year_cond))
            if not criteria:
                st.warning("Please enter at least one condition.")
            else:
                results = qe.compound_search(criteria, op_code)
                st.success(f"Found {len(results)} results.")
                if results:
                    st.dataframe(pd.DataFrame(results), width='stretch')

elif page == "Graph Explorer":
    st.title("Collaboration Network")
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("### Path Finder")
        start_artist = st.text_input("Artist A", "Daft Punk")
        end_artist = st.text_input("Artist B", "The Weeknd")
        find_path = st.button("Find Path")

        st.divider()
        st.markdown("### Artist Stats")
        stat_artist = st.text_input("Check Degree", "Adele")
        if st.button("Get Stats"):
            deg = graph.degree(stat_artist)
            neigh = graph.neighbors(stat_artist)
            if deg is None:
                st.error("Artist not found.")
            else:
                st.metric("Collaborators", deg)
                st.write(", ".join(neigh[:15]))

    with col2:
        if find_path:
            with st.spinner("Searching shortest path..."):
                path = graph.shortest_path(start_artist, end_artist)
            if path:
                st.success(f"Path Found! ({len(path)-1} degrees)")
                st.write(" → ".join(path))
                st.markdown("### Connection Chain")
                for i, artist in enumerate(path):
                    st.write(f"{i+1}. **{artist}**")
            else:
                st.error("No path found.")
        else:
            st.markdown(
                '''
                <div style="
                    background-color: rgba(224, 247, 250, 0.7);  /* light blue with 50% opacity */
                    color: black;                                /* text color */
                    padding: 10px;
                    border-radius: 5px;
                ">
                    Enter two artists to show collaboration path.
                </div>
                ''',
                unsafe_allow_html=True
            )
            st.write("### Most Connected Artists")
            top_k = graph.top_k_by_degree(10)
            df = pd.DataFrame(top_k, columns=["Artist", "Collaborations"])
            st.bar_chart(df.set_index("Artist"))

elif page == "Analytics":
    st.title("Data Analytics")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribution of Genres")
        top_genres = analytics.top_k_by_count('genre', 10)
        df_genre = pd.DataFrame(top_genres, columns=["Genre", "Count"])
        st.plotly_chart(px.pie(df_genre, names='Genre', values='Count', hole=0.4), use_container_width=False)

    with col2:
        st.subheader("Dominant Genre per Year")

        df = pd.DataFrame(db._data.values())

        grouped = df.groupby(["release_year", "genre"]).size().reset_index(name="count")

        dominant_per_year = (
            grouped.loc[grouped.groupby("release_year")["count"].idxmax()]
            .sort_values("release_year")
        )

        fig = px.scatter(
            dominant_per_year,
            x="release_year",
            y="genre",
            size="count",
            color="genre",
            hover_data=["count"],
            title="Dominant Genre Each Year",
        )

        # Connect points with lines so trend is visible
        fig.update_traces(mode="markers+lines")

        st.plotly_chart(fig, use_container_width=True)


elif page == "Data Manager":
    st.title("Data Manager")
    st.warning("Changes here affect the in-memory DB immediately.")

    action = st.selectbox("Action", ["Insert New Song", "Delete Song", "Update Record"])

    if action == "Insert New Song":
        with st.form("insert_form"):
            new_title = st.text_input("Song Title")
            new_artist = st.text_input("Artist")
            new_duration = st.text_input("Duration")
            new_album = st.text_input("Album Title")
            new_featured = st.text_input("Featured artist")
            new_year = st.number_input("Year", 1900, 2030, 2023)
            new_genre = st.selectbox("Genre", ['Pop', 'Rock', 'Hip-Hop', 'Electronic', 'R&B', 'Jazz',
                                                'Classical', 'Country', 'Reggae', 'Blues', 'Metal', 'Folk',
                                                'Techno', 'Indie', 'Alternative', 'Punk', 'Funk', 'Soul'])
            submitted = st.form_submit_button("Insert Record")

            if submitted:
                if new_title and new_artist:
                    rec = {
                        "song_title": new_title,
                        "artist_name": new_artist,
                        "featured_artists": new_featured,
                        "album_title": new_album,
                        "release_year": int(new_year),
                        "duration_ms": int(new_duration),
                        "genre": new_genre
                    }
                    new_id = qe.insert(rec)
                    st.success(f"Inserted! ID: {new_id}")
                else:
                    st.error("Title and Artist required.")

    elif action == "Update Record":
        st.subheader("Modify an Existing Song")

        update_id = st.text_input("Enter song ID to update", key="update_id_input")

        if update_id:
            record = db.get_record_by_id(update_id)

            if record is None:
                st.error("Record not found. Check the ID.")
            else:
                st.markdown(
                    '''
                    <div style="
                        background-color: rgba(224, 247, 250, 0.7);  
                        color: black;                                /* text color */
                        padding: 10px;
                        border-radius: 5px;
                    ">
                        Leave any field untouched to keep it unchanged.
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

                with st.form("update_form"):
                    up_title = st.text_input("New Title", value=record.get("song_title"))
                    up_artist = st.text_input("New Artist", value=record.get("artist_name"))
                    up_featured = st.text_input("New Featured Artists", value=record.get("featured_artists"))
                    up_album = st.text_input("New Album", value=record.get("album_title"))
                    up_year = st.number_input("New Year", 1900, 2030, value=int(record.get("release_year")))
                    up_duration = st.text_input("New Duration (ms)", value=str(record.get("duration_ms")))
                    genres = ['Pop', 'Rock', 'Hip-Hop', 'Electronic', 'R&B', 'Jazz',
                                'Classical', 'Country', 'Reggae', 'Blues', 'Metal', 'Folk',
                                'Techno', 'Indie', 'Alternative', 'Punk', 'Funk', 'Soul']
                    try:
                        default_idx = genres.index(record.get("genre"))
                    except ValueError:
                        default_idx = 0
                    up_genre = st.selectbox("New Genre", genres, index=default_idx)

                    submitted_update = st.form_submit_button("Apply Update")

                    if submitted_update:
                        updated_fields = {}

                        if up_title != record.get("song_title"):
                            updated_fields["song_title"] = up_title

                        if up_artist != record.get("artist_name"):
                            updated_fields["artist_name"] = up_artist

                        if up_duration.strip() and str(record.get("duration_ms")) != up_duration:
                            try:
                                updated_fields["duration_ms"] = int(up_duration)
                            except ValueError:
                                st.error("Duration must be a number")

                        if up_featured != record.get("featured_artists"):
                            updated_fields["featured_artists"] = up_featured

                        if up_album != record.get("album_title"):
                            updated_fields["album_title"] = up_album

                        if up_year != record.get("release_year"):
                            updated_fields["release_year"] = int(up_year)

                        if up_genre != record.get("genre"):
                            updated_fields["genre"] = up_genre

                        if updated_fields:
                            ok = qe.update(update_id, updated_fields)
                            if ok:
                                st.success("Record updated successfully!")
                            else:
                                st.error("Update failed.")
                        else:
                            st.info("No changes made.")

    elif action == "Delete Song":
        del_id = st.text_input("Enter Song ID to delete")
        if st.button("Delete"):
            if qe.delete(del_id):
                st.success(f"Record {del_id} deleted.")
            else:
                st.error("ID not found.")

