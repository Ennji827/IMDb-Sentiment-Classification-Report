import streamlit as st
import speech_recognition as sr
from nltk.tokenize import word_tokenize, sent_tokenize
import tempfile
import os

# === Load chatbot knowledge ===
@st.cache_data
def load_knowledge():
    with open("chatbot_knowledge.txt", "r", encoding="utf-8") as f:
        text = f.read().lower()
    return sent_tokenize(text)

chatbot_sentences = load_knowledge()

# === Simple matching chatbot logic ===
def chatbot_reply(user_input):
    user_tokens = word_tokenize(user_input.lower())
    best_match = "I'm not sure how to respond to that."
    max_overlap = 0
    for sentence in chatbot_sentences:
        tokens = word_tokenize(sentence)
        overlap = len(set(user_tokens) & set(tokens))
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = sentence
    return best_match

# === Streamlit UI ===
st.set_page_config(page_title="Voice & Text Chatbot", page_icon="🤖")
st.title("🤖 African Voice & Text Chatbot")

st.markdown("""
Type a message or upload a voice recording (WAV or MP3).  
The bot will respond based on its simple knowledge base.
""")

# === Text input ===
user_input = st.text_input("💬 Say something (text):")
if user_input:
    st.markdown(f"**You:** {user_input}")
    response = chatbot_reply(user_input)
    st.markdown(f"**Bot:** {response}")

# === Voice input ===
st.markdown("---")
st.subheader("🎤 Or upload a voice message")

audio_file = st.file_uploader("Upload WAV or MP3", type=["wav", "mp3"])

if audio_file:
    st.audio(audio_file)

    recognizer = sr.Recognizer()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_file.read())
        tmp_filename = tmp_file.name

    try:
        with sr.AudioFile(tmp_filename) as source:
            audio = recognizer.record(source)
        recognized_text = recognizer.recognize_google(audio)
        st.success(f"You said: {recognized_text}")
        st.markdown(f"**Bot:** {chatbot_reply(recognized_text)}")
    except sr.UnknownValueError:
        st.error("Could not understand the audio.")
    except sr.RequestError as e:
        st.error(f"API error: {e}")
    finally:
        os.remove(tmp_filename)
