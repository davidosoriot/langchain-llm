import openai
import streamlit as st
import textwrap
from youtube_transcript_api import YouTubeTranscriptApi

# Leer la clave API desde el archivo
with open('apikeycash.txt', 'r') as f:
    api_key = f.read().strip()

openai.api_key = api_key

# Función para extraer el video ID de una URL de YouTube
def extract_video_id(video_url):
    """
    Extrae el ID del video desde una URL válida de YouTube.
    """
    if "v=" in video_url:
        return video_url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in video_url:
        return video_url.split("youtu.be/")[-1].split("?")[0]
    else:
        return None

# Función para obtener el transcript del video
def get_video_transcript(video_url):
    try:
        # Extraer el ID del video
        video_id = extract_video_id(video_url)
        if not video_id:
            return "Error: La URL proporcionada no es válida."
        
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en'])
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        return f"Error al obtener el transcript: {e}"

# Función para obtener la respuesta del modelo
def get_response_from_query(query, context=""):
    """
    Utiliza la API de OpenAI para obtener una respuesta basada en el contexto proporcionado.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Cambiar a "gpt-4" si tienes acceso
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{query}\n\nContext: {context}"}
            ],
            temperature=0.7,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"An error occurred: {e}"

# Interfaz de Streamlit
st.title("YouTube Assistant")

youtube_url = st.text_input("Ingrese la URL del video de YouTube:")
query = st.text_area("Haz tu pregunta sobre el video:")

if st.button("Obtener Respuesta"):
    if youtube_url and query:
        # Obtener el transcript del video
        with st.spinner("Obteniendo el transcript del video..."):
            context = get_video_transcript(youtube_url)
        
        if "Error" in context:
            st.error(context)
        else:
            with st.spinner("Generando respuesta..."):
                response = get_response_from_query(query, context)
            
            st.subheader("Respuesta:")
            st.text(textwrap.fill(response, width=85))
    else:
        st.error("Por favor, ingrese tanto la URL del video como su pregunta.")
