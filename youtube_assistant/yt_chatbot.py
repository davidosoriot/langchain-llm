import openai
import streamlit as st
import textwrap
from youtube_transcript_api import YouTubeTranscriptApi

# Read api key
with open('apikeycash.txt', 'r') as f:
    api_key = f.read().strip()

openai.api_key = api_key

# Function to extract the video ID from the youtube url
def extract_video_id(video_url):
    
    if "v=" in video_url:
        return video_url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in video_url:
        return video_url.split("youtu.be/")[-1].split("?")[0]
    else:
        return None

# Function to get the transcript
def get_video_transcript(video_url):
    try:
        # Extract video id
        video_id = extract_video_id(video_url)
        if not video_id:
            return "Error: Invalid URL."
        
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en'])
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        return f"Error obtaining the transcript: {e}"

# get openai model
def get_response_from_query(query, context=""):
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{query}\n\nContext: {context}"}
            ],
            temperature=0.7,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"An error occurred: {e}"

# Streamlit
st.title("YouTube Assistant")

youtube_url = st.text_input("Insert the Youtube URL:")
query = st.text_area("Ask something about the video:")

if st.button("Obtain answer"):
    if youtube_url and query:
        # Obtain the transcript 
        with st.spinner("Obtaining the video transcript..."):
            context = get_video_transcript(youtube_url)
        
        if "Error" in context:
            st.error(context)
        else:
            with st.spinner("Generating answer..."):
                response = get_response_from_query(query, context)
            
            st.subheader("Answer:")
            st.text(textwrap.fill(response, width=85))
    else:
        st.error("Please insert the video URL and your question.")
