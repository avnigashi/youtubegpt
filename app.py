# Import required libraries
import streamlit as st
import openai
from pytube import YouTube  # Add this import
from model import save_video, save_audio, audio_to_transcript, get_caption_text, extract_video_id, analyze_video_content

# Get API key 
OPENAI_API_KEY = "llama"
# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Set page configuration and title for Streamlit
st.set_page_config(page_title="YoutubeGPT", page_icon="📼", layout="wide")

# Add custom CSS for styling
st.markdown("""
    <style>
    .header {
        font-size: 40px;
        font-weight: bold;
        color: #4B8BBE;
    }
    .subheader {
        font-size: 16px;
        color: #306998;
    }
    .section-header {
        font-size: 20px;
        font-weight: bold;
        color: #306998;
    }
    .content-box {
        padding: 10px;
        border-radius: 10px;
        background-color: #f9f9f9;
        box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
    }
    .scrollable-box {
        height: 200px;
        overflow-y: scroll;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 10px;
    }
    .trustworthiness-bar {
        background-color: #f0f0f0;
        border-radius: 10px;
        overflow: hidden;
    }
    .trustworthiness-bar div {
        height: 24px;
        transition: width 0.4s ease;
    }
    </style>
    """, unsafe_allow_html=True)

# Add header with title and description
st.markdown('<div class="header">📺YoutubeGPT</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">YoutubeGPT is a webapp tool that utilizes OpenAI&#39;s Whisper model for speech recognition to extract transcriptions from YouTube videos. It also incorporates GPT-3 to provide users with summarized text based on the content of the video.<br><br></div>', unsafe_allow_html=True)

# Get YouTube video URL from user
url = st.text_input('Enter URL of YouTube video:')
run_transcript = st.checkbox('Run Transcription')

if url:
    if st.button("Generate"):
        # Extract video ID
        video_id = extract_video_id(url)
        
        # Create layout with different sections
        st.markdown('<div class="section-header">Video Information</div>', unsafe_allow_html=True)
        with st.spinner('Processing...'):
            # Video display and metadata
            col1, col2 = st.columns([1, 3])
            with col1:
                st.info("Video")
                video_filename = save_video(url)
                st.video(video_filename)
            
            with col2:
                st.info("Metadata")
                video = YouTube(url)
                title = video.title
                description = video.description
                st.write(f"**Title:** {title}")
                st.write(f"**Author:** {video.author}")
                st.write(f"**Publish Date:** {video.publish_date}")
                st.write(f"**Views:** {video.views}")
                st.write(f"**Duration:** {video.length} seconds")
                st.write(f"**Description:** {description}")
                caption_text = get_caption_text(url)
                if caption_text:
                    st.write(f"**Captions:** {caption_text}")
                else:
                    st.write("**Captions:** None available. Using Whisper for transcription.")

        transcript_result = None
        st.markdown('<div class="section-header">Transcription</div>', unsafe_allow_html=True)
        try:
            audio_path = save_audio(url)  # Ensure audio is saved before transcription
            if run_transcript:
                transcript_result = audio_to_transcript(video_id)
                st.markdown(f"<div class='scrollable-box'>{transcript_result}</div>", unsafe_allow_html=True)
            elif caption_text:
                transcript_result = caption_text
                st.markdown(f"<div class='scrollable-box'>{transcript_result}</div>", unsafe_allow_html=True)
        except FileNotFoundError as e:
            st.error(str(e))
            transcript_result = None
        
        if transcript_result:
            st.markdown('<div class="section-header">Content Analysis</div>', unsafe_allow_html=True)
            analysis_text, trustworthiness_score = analyze_video_content(transcript_result, title, description)
            st.success(analysis_text)
            
            st.markdown('Trustworthiness Score</div>', unsafe_allow_html=True)
            color = f"rgb({255 - int(trustworthiness_score * 2.55)}, {int(trustworthiness_score * 2.55)}, 0)"
            st.markdown(f"""
                <div class="trustworthiness-bar">
                    <div style="width: {trustworthiness_score}%; background-color: {color};"></div>
                </div>
                <p>{trustworthiness_score}% Trustworthy</p>
                """, unsafe_allow_html=True)

# Hide Streamlit header, footer, and menu
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""

# Apply CSS code to hide header, footer, and menu
st.markdown(hide_st_style, unsafe_allow_html=True)