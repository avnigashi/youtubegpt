import os
import requests
import json
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import whisper
import re

# Import Streamlit
import streamlit as st

@st.cache_resource
def load_model():
    # Load the Whisper model for speech recognition
    model = whisper.load_model("base")
    return model

def extract_video_id(url):
    video_id = url.split("v=")[-1]
    return video_id

def create_result_dirs(video_id):
    base_dir = os.path.join("results", video_id)
    os.makedirs(base_dir, exist_ok=True)
    return base_dir

def save_video(url):
    video_id = extract_video_id(url)
    result_dir = create_result_dirs(video_id)
    
    video_path = os.path.join(result_dir, "video.mp4")
    
    if not os.path.exists(video_path):
        youtube_obj = YouTube(url)
        youtube_obj = youtube_obj.streams.get_highest_resolution()
        try:
            youtube_obj.download(output_path=result_dir, filename="video.mp4")
        except:
            raise Exception("An error has occurred while downloading the video")
        print("Download completed successfully")
    
    return video_path

def save_audio(url):
    video_id = extract_video_id(url)
    result_dir = create_result_dirs(video_id)
    audio_path = os.path.join(result_dir, "audio.mp3")
    
    if not os.path.exists(audio_path):
        video = YouTube(url)
        audio = video.streams.filter(only_audio=True).first()
        audio.download(output_path=result_dir, filename="audio.mp3")
    
    return audio_path

def get_caption_text(url):
    video_id = extract_video_id(url)
    result_dir = create_result_dirs(video_id)
    caption_path = os.path.join(result_dir, "captions.txt")
    
    if (os.path.exists(caption_path)):
        with open(caption_path, "r") as f:
            return f.read()
    
    try:
        captions = YouTubeTranscriptApi.get_transcript(video_id)
        caption_text = " ".join([caption['text'] for caption in captions])
        with open(caption_path, "w") as f:
            f.write(caption_text)
        return caption_text
    except NoTranscriptFound:
        return None

def audio_to_transcript(video_id):
    result_dir = create_result_dirs(video_id)
    audio_path = os.path.join(result_dir, "audio.mp3")
    transcript_path = os.path.join(result_dir, "transcript.txt")
    
    if os.path.exists(transcript_path):
        with open(transcript_path, "r") as f:
            return f.read()

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at path: {audio_path}")

    model = load_model()
    result = model.transcribe(audio_path)
    transcript = result["text"]
    with open(transcript_path, "w") as f:
        f.write(transcript)
    return transcript

def analyze_video_content(transcript, title, description):
    url = "http://host.docker.internal:11434/api/generate"

    payload = {
        "model": "llama3",
        "prompt": f"""Evaluate the trustworthiness and political bias of the following text on a scale from 0 to 100, where 0 indicates very untrustworthy and 100 indicates very trustworthy. The text is from a YouTube video titled '{title}' with the following description: '{description}'. 
        Assess factors such as factual accuracy, logical consistency, presence of credible sources, tone and language used, and any potential bias. Additionally, consider the quality of the presenter or interviewee (expertise, credibility) and the interviewer if applicable (impartiality, questioning style). 
        Evaluate if the content is balanced, if multiple perspectives are represented, and if there are any misleading or inaccurate statements. 
        Be vigilant to identify any attempts to manipulate the viewer by presenting one-sided or misleading narratives, and ensure that the analysis considers the broader context of the information presented. 

        Also, analyze the political bias of the text. Explain if it has components of political propaganda to influence the user. Highlight key attributes such as clarity and precision, coherence and consistency, evidence-based arguments, moral and ethical foundations, practical feasibility, consideration of consequences, empathy and understanding, communication skills, openness to dialogue and criticism, and integrity and authenticity. 
        Ensure that the analysis does not fall into sarcasm. Categorize it as 'left', 'right', 'center', 'far left', 'far right', or 'propaganda'. 
        Additionally, evaluate the presenter's or interviewee's quality (expertise, credibility) and the interviewer's impartiality (if applicable). 
        Assess if the content is balanced and if multiple perspectives are represented. Be vigilant to identify and critique any attempts to manipulate the viewer by presenting one-sided or misleading narratives, such as negatively portraying a specific group to influence opinions about political matters:

        {transcript}

        Provide the analysis in the following structured format:
        1. **Trustworthiness Score**: [Score from 0 to 100]
        2. **Political Bias**: 
            - Category: [left/right/center/far left/far right/propaganda]
        3. **Components of Propaganda**: 
            - [List any propaganda components if present]
        4. **Key Attributes**:
            - **Clarity and Precision**: [Description]
            - **Coherence and Consistency**: [Description]
            - **Evidence-Based Arguments**: [Description]
            - **Moral and Ethical Foundations**: [Description]
            - **Practical Feasibility**: [Description]
            - **Consideration of Consequences**: [Description]
            - **Empathy and Understanding**: [Description]
            - **Communication Skills**: [Description]
            - **Openness to Dialogue and Criticism**: [Description]
            - **Integrity and Authenticity**: [Description]
        5. **Quality of Presenter/Interviewee**: 
            - [Evaluate expertise and credibility]
        6. **Quality of Interviewer (if applicable)**: 
            - [Evaluate impartiality and questioning style]
        7. **Overall Assessment**: 
            - [Summarize the overall findings]\n""",
        "options": {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        },
        "stream": False
    }

    response = requests.post(url, data=json.dumps(payload))
    response_data = response.json()
    response_text = response_data['response']

    trustworthiness_score = 0
    try:
        trustworthiness_score = int(re.search(r'\b\d{1,3}\b', response_text).group())
    except (ValueError, AttributeError) as e:
        print(f"Error parsing trustworthiness score: {e}")

    return response_text, trustworthiness_score
