import pickle
import streamlit as st
import requests
import speech_recognition as sr
import os

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url)
    data = response.json()
    poster_path = data['poster_path']
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return full_path

def get_selected_movie(movies):
    movie_list = movies['title'].values

    selected_movie = ''

    # Voice search
    if st.button("Search"):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            st.write("Speak the name of a movie or type it...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            st.write("Transcribing...")
            text = recognizer.recognize_google(audio)
            selected_movie = text
            if selected_movie in movie_list:
                st.session_state['movie_input'] = selected_movie  # Update the selectedmovie title
        except sr.UnknownValueError:
            st.write("Sorry, I could not understand your audio.")
        except sr.RequestError as e:
            st.write(f"Could not request results from Google Speech Recognition service; {e}")

    if selected_movie:
        st.success(f"Selected movie: {selected_movie}")  # Display selected movie from voice search
        return selected_movie
    else:
        selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list, key='movie_input')

        # Display movies dropdown 
        if selected_movie not in movie_list:
            st.warning("Please select a valid movie from the dropdown.")
        else:
            st.success(f"Selected movie: {selected_movie}")
        return selected_movie

def recommend(selected_movie, movies, similarity):
    index = movies[movies['title'] == selected_movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

if __name__ == "__main__":
    st.title("Movie Recommender System with Voice Search")

    # Load movies DataFrame
    movies = pickle.load(open(os.path.join('D:\mini project', 'movie_list.pkl'), 'rb'))

    # Load similarity DataFrame
    similarity = pickle.load(open(os.path.join('D:\mini project', 'similarity.pkl'), 'rb'))

    selected_movie = get_selected_movie(movies)

    # Show recommendation button
    if selected_movie!='':
        if st.button('Show Recommendation'):
            recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies, similarity)

            cols = st.columns(5)
            for i, movie_name in enumerate(recommended_movie_names):
                with cols[i]:
                    st.text(movie_name)
                    st.image(recommended_movie_posters[i])

                    