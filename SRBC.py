import streamlit as st
import pandas as pd
from PIL import Image
img= Image.open('e.png')
# supprime streamlit de la barre
st.set_page_config(
   page_title="Song Recommendation",
   page_icon="🎧",
   layout="wide",
   initial_sidebar_state="expanded",
)

st.write('''
# Simple App to recommend music
Listen to your favorite genre of music and other music that you may like
''')
# barre laterale
st.sidebar.header('Home')
st.subheader('Application réecrite par Assi ulrich à usage non commercial')



from sklearn.neighbors import NearestNeighbors
import plotly.express as px
import streamlit.components.v1 as components

@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv("filtered_track_df.csv")
    df['genres'] = df.genres.apply(lambda x: [i[1:-1] for i in str(x)[1:-1].split(", ")])
    exploded_track_df = df.explode("genres")
    return exploded_track_df

genre_names = ['Dance Pop', 'Electronic', 'Electropop', 'Hip Hop', 'Jazz', 'K-pop', 'Latin', 'Pop', 'Pop Rap', 'R&B', 'Rock']
audio_feats = ["acousticness", "danceability", "energy", "instrumentalness", "valence", "tempo"]
exploded_track_df = load_data()


def n_neighbors_uri_audio(genre, start_year, end_year, test_feat):
   genre = genre.lower()
   genre_data = exploded_track_df[
      (exploded_track_df["genres"] == genre) & (exploded_track_df["release_year"] >= start_year) & (
                 exploded_track_df["release_year"] <= end_year)]
   genre_data = genre_data.sort_values(by='popularity', ascending=False)[:500]

   neigh = NearestNeighbors()
   neigh.fit(genre_data[audio_feats].to_numpy())

   n_neighbors = neigh.kneighbors([test_feat], n_neighbors=len(genre_data), return_distance=False)[0]

   uris = genre_data.iloc[n_neighbors]["uri"].tolist()
   audios = genre_data.iloc[n_neighbors][audio_feats].to_numpy()
   return uris, audios


st.markdown("##")
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width:500px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 300px;
        margin-left: -500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
    )
st.sidebar.button("click me!")
with st.sidebar:
   col1, col2, col3, col4 = st.columns((1.7,0.5,1,0.5))
   with col3:
      st.markdown("what's your favorite musical genre:")
      genre = st.selectbox(
         "select",
         genre_names, index=genre_names.index("Hip Hop"))
   with col1:
      st.markdown("Choisir les fonctionnalités à personnaliser:")
      start_year, end_year = st.slider(
         'Select the year range',
         1990, 2019, (2010, 2019)
      )
      acousticness = st.slider(
         'Acousticness',
         0.0, 1.0, 0.5)
      danceability = st.slider(
         'Danceability',
         0.0, 1.0, 0.5)
      energy = st.slider(
         'Energy',
         0.0, 1.0, 0.5)
      instrumentalness = st.slider(
         'Instrumentalness',
         0.0, 1.0, 0.5)
      valence = st.slider(
         'Valence',
         0.0, 1.0, 0.5)
      tempo = st.slider(
         'Tempo',
         0.0, 244.0, 118.0)

tracks_per_page = 6
test_feat = [acousticness, danceability, energy, instrumentalness, valence, tempo]
uris, audios = n_neighbors_uri_audio(genre, start_year, end_year, test_feat)

tracks = []
for uri in uris:
   track = """<iframe src="https://open.spotify.com/embed/track/{}" width="200" height="300" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>""".format(
      uri)
   tracks.append(track)

if 'previous_inputs' not in st.session_state:
   st.session_state['previous_inputs'] = [genre, start_year, end_year] + test_feat

current_inputs = [genre, start_year, end_year] + test_feat
if current_inputs != st.session_state['previous_inputs']:
   if 'start_track_i' in st.session_state:
      st.session_state['start_track_i'] = 0
   st.session_state['previous_inputs'] = current_inputs

if 'start_track_i' not in st.session_state:
   st.session_state['start_track_i'] = 0

with st.container():
   col1, col2, col3 = st.columns([3,0.5,3])
   if st.button("Recommend More Songs"):
      if st.session_state['start_track_i'] < len(tracks):
         st.session_state['start_track_i'] += tracks_per_page

   current_tracks = tracks[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
   current_audios = audios[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
   if st.session_state['start_track_i'] < len(tracks):
      for i, (track, audio) in enumerate(zip(current_tracks, current_audios)):
         if i % 2 == 0:
            with col1:
               components.html(
                  track,
                  height=500,
               )
               with st.expander("more details"):
                  df = pd.DataFrame(dict(
                     r=audio[:5],
                     theta=audio_feats[:5]))
                  fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                  fig.update_layout(height=400, width=340)
                  st.plotly_chart(fig)

         else:
            with col3:
               components.html(
                  track,
                  height=500,
               )
               with st.expander("more details"):
                  df = pd.DataFrame(dict(
                     r=audio[:5],
                     theta=audio_feats[:5]))
                  fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                  fig.update_layout(height=400, width=340)
                  st.plotly_chart(fig)
agree = st.checkbox('Check here if you liked it')

if agree:
     st.write('Great!')
