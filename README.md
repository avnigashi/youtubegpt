# YoutubeGPT 📼

YoutubeGPT is a web application that utilizes OpenAI's Whisper model for speech recognition to extract transcriptions from YouTube videos. It also incorporates OpenAI's models to provide users with summarized text based on the content of the video and to analyze the trustworthiness and political bias of the video's content.

## Features

- **Video Download:** Download videos and audio from YouTube.
- **Transcription:** Transcribe audio using Whisper model.
- **Caption Retrieval:** Retrieve captions if available.
- **Summarization:** Summarize the video's content.
- **Trustworthiness Analysis:** Evaluate the trustworthiness of the video's content.
- **Political Bias Analysis:** Analyze the political bias and identify any components of propaganda.

## Installation

### Prerequisites

- Python 3.7 or higher
- Streamlit
- pytube
- youtube_transcript_api
- whisper
- requests
- re

### Clone the Repository

```bash
git clone https://github.com/avnigashi/youtubegpt.git
cd youtubegpt
pip install -r requirements.txt
streamlit run app.py
