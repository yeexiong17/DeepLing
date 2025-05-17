import streamlit as st
import pandas as pd
import dashscope
from dashscope import Generation
from custom_speech_recognition import recognize_speech_from_bytes
from streamlit_mic_recorder import mic_recorder
from pydub import AudioSegment
import io

DASHSCOPE_API_KEY = 'sk-0cb128a3e6d14c2eb467498b3de8705f'
dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"

ASR_APP_KEY = "M5PHTh3kdqKqliKk"
ASR_TOKEN = "bbffcbadcbdc4909ba82a0fea7b0e632"

st.set_page_config(page_title="RetireSmart", layout="wide")

if 'user_prompt_content' not in st.session_state:
    st.session_state.user_prompt_content = ""

if 'live_audio_just_transcribed' not in st.session_state:
    st.session_state.live_audio_just_transcribed = False
if 'last_submitted_audio_id_for_processing' not in st.session_state:
    st.session_state.last_submitted_audio_id_for_processing = None

st.markdown("""
<style>
body {
    background: linear-gradient(to right, #d7e1ec, #f9fbfd);
}
section.main > div {
    padding: 2rem 3rem;
    background-color: #ffffffcc;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
h1, h2, h3 {
    color: #2a5d84;
}
.stTextArea textarea {
    font-size: 16px;
    background-color: rgb(38, 39, 48);
    border: 1px solid #d1d9e6;
    border-radius: 0.5rem;
    padding: 12px 15px;
    color: rgb(250, 250, 250);
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.075);
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}
.stTextArea textarea:focus {
    border-color: #457fca;
    outline: 0;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.075), 0 0 0 0.2rem rgba(69, 127, 202, 0.25);
}
.stButton>button {
    background: linear-gradient(to right, #457fca, #5691c8);
    color: white;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-size: 16px;
    font-weight: bold;
    border: none;
}
.stButton>button:hover {
    background: linear-gradient(to right, #355c7d, #6c5b7b);
}
</style>
""", unsafe_allow_html=True)

st.title("👵 RetireSmart: Your AI-Powered Retirement Planner")
st.markdown("Use AI to analyze your spending and savings. Get **beautiful**, **clear**, and **smart** financial guidance.")

st.subheader("📂 Step 1: Upload Your Spending Files")
st.caption("Accepted formats: `.csv`, `.xls`, `.xlsx`, `.txt`. Other files will be view-only.")
spending_files = st.file_uploader("Upload spending documents", type=None, accept_multiple_files=True)

st.subheader("💰 Step 2: Upload Your Savings Documents (Optional)")
savings_files = st.file_uploader("Upload savings documents (view-only)", type=None, accept_multiple_files=True)

st.subheader("🗣️ Alternative: Ask Your Question via Speech")

st.markdown("🎙️ **Record your question directly:**")
RECORDER_KEY = 'live_audio_recorder_retiresmart'
audio_info = mic_recorder(
    start_prompt="⏺️ Start Recording",
    stop_prompt="⏹️ Stop Recording",
    key=RECORDER_KEY, 
    format='wav',
    use_container_width=True
)

new_audio_available_for_submission = (
    audio_info and
    audio_info.get('bytes') and
    audio_info.get('id') and
    audio_info['id'] != st.session_state.get('last_submitted_audio_id_for_processing')
)

if new_audio_available_for_submission:
    st.session_state.last_submitted_audio_id_for_processing = audio_info['id']

    st.audio(audio_info['bytes'], format="audio/wav")
    original_audio_bytes = audio_info['bytes']
    
    if len(original_audio_bytes) > 5 * 1024 * 1024:
        st.error("Recorded audio is too large before processing (max 5MB raw). Please try a shorter recording.")
    else:
        with st.spinner("Processing recorded audio..."):
            TARGET_SAMPLE_RATE = 16000
            processed_audio_bytes = None
            try:
                audio_segment = AudioSegment.from_wav(io.BytesIO(original_audio_bytes))
                audio_segment = audio_segment.set_frame_rate(TARGET_SAMPLE_RATE)
                audio_segment = audio_segment.set_channels(1)
                final_wav_io = io.BytesIO()
                audio_segment.export(final_wav_io, format="wav")
                processed_audio_bytes = final_wav_io.getvalue()
            except Exception as e:
                st.error(f"Error during audio processing (resampling/mono conversion): {e}")

            if processed_audio_bytes:
                API_PAYLOAD_LIMIT = 2 * 1024 * 1024 
                if len(processed_audio_bytes) > API_PAYLOAD_LIMIT:
                    st.error(f"Processed audio is too large ({len(processed_audio_bytes)/(1024*1024):.2f}MB, max 2MB). Recording might be too long.")
                else:
                    transcript, error = recognize_speech_from_bytes(
                        processed_audio_bytes,
                        app_key=ASR_APP_KEY,
                        token=ASR_TOKEN,
                        input_format='wav',
                        sample_rate=TARGET_SAMPLE_RATE
                    )
                    if error:
                        st.error(f"Speech recognition error: {error}")
                    elif transcript:
                        st.session_state.user_prompt_content = transcript
                        st.session_state.live_audio_just_transcribed = True
                        st.success("Live audio transcribed successfully!")
                        if not transcript.strip(): 
                            st.info("The audio was transcribed as empty. It might have been silence or unclear audio.")
                        st.rerun()
                    else:
                        st.warning("No transcript returned from live recording. The audio might be silent or an issue occurred.")
                        st.session_state.live_audio_just_transcribed = True
                        st.rerun()

if st.session_state.get('live_audio_just_transcribed', False):
    st.session_state.live_audio_just_transcribed = False

st.markdown("---")
st.markdown("📂 **Or, upload an audio file:**")
audio_file = st.file_uploader("Upload an audio file (e.g., .wav, .pcm, .mp3)", type=['wav', 'pcm', 'mp3'])
if audio_file is not None:
    if st.button("🎤 Transcribe Audio to Text"):
        with st.spinner("Transcribing audio..."):
            audio_bytes = audio_file.getvalue()
            file_extension = audio_file.name.split('.')[-1].lower()
            input_format = 'pcm'
            sample_rate = 16000
            audio_bytes_to_send = None

            if file_extension == 'wav':
                input_format = 'wav'
                audio_bytes_to_send = audio_bytes
            elif file_extension == 'pcm':
                input_format = 'pcm'
                audio_bytes_to_send = audio_bytes
            elif file_extension == 'mp3':
                try:
                    st.write("Converting MP3 to WAV for ASR...")
                    audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
                    audio_segment = audio_segment.set_channels(1).set_frame_rate(16000)
                    wav_io = io.BytesIO()
                    audio_segment.export(wav_io, format="wav")
                    audio_bytes_to_send = wav_io.getvalue()
                    input_format = 'wav'
                    st.write("MP3 converted to WAV successfully.")
                except Exception as convert_e:
                    st.error(f"Error converting MP3: {convert_e}")
                    audio_bytes_to_send = None
            else:
                st.warning(f"Unsupported file extension for direct ASR: .{file_extension}. Trying as PCM.")
                input_format = 'pcm'
                audio_bytes_to_send = audio_bytes

            if audio_bytes_to_send:
                API_PAYLOAD_LIMIT = 2 * 1024 * 1024
                if len(audio_bytes_to_send) > API_PAYLOAD_LIMIT:
                    st.error(f"Processed audio is too large ({len(audio_bytes_to_send)/(1024*1024):.2f}MB, max 2MB).")
                else:
                    transcript, error = recognize_speech_from_bytes(
                        audio_bytes_to_send,
                        app_key=ASR_APP_KEY,
                        token=ASR_TOKEN,
                        input_format=input_format,
                        sample_rate=sample_rate
                    )

                    if error:
                        st.error(f"Speech recognition error from uploaded file: {error}")
                    elif transcript:
                        st.session_state.user_prompt_content = transcript
                        st.success("Uploaded audio transcribed successfully!")
                        if not transcript.strip():
                            st.info("The audio (uploaded) was transcribed as empty.")
                        st.rerun()
                    else:
                        st.warning("No transcript returned from uploaded file. The audio might be silent or an issue occurred.")
            elif file_extension == 'mp3' and not audio_bytes_to_send:
                 st.info("Transcription from MP3 was skipped due to conversion error.")

st.subheader("📝 Step 3: Ask Your Retirement Question")

st.text_area(
    "Example: How can I budget for medical expenses after retirement?", 
    height=150, 
    key="user_prompt_content"
)

def convert_file_to_dataframe(file):
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        elif file.name.endswith((".xls", ".xlsx")):
            return pd.read_excel(file)
        elif file.name.endswith(".txt"):
            return pd.read_csv(file, delimiter="\t", header=None)
        else:
            return pd.DataFrame({"FileName": [file.name], "Note": ["Unsupported format (view-only)"]})
    except Exception as e:
        return pd.DataFrame({"FileName": [file.name], "Error": [str(e)]})

def summarize_spending(files):
    combined_data = pd.DataFrame()
    for file in files:
        df = convert_file_to_dataframe(file)
        combined_data = pd.concat([combined_data, df], ignore_index=True)
    return combined_data

st.markdown("---")
if st.button("💬 Generate My Retirement Plan"):
    current_user_question = st.session_state.get("user_prompt_content", "")
    
    if not (spending_files and current_user_question.strip()):
        st.warning("Please upload at least one spending file and enter your question.")
    else:
        with st.spinner("AI is working on your plan..."):
            try:
                combined_spending_df = summarize_spending(spending_files)

                if not combined_spending_df.empty:
                    csv_text_summary = combined_spending_df.head(20).to_csv(index=False)
                else:
                    csv_text_summary = "No structured data extracted."

                full_prompt = f"""
User Question: {current_user_question}

User Spending Summary (first 20 rows, CSV-style):
{csv_text_summary}

The user uploaded {len(savings_files)} savings documents (view-only).

Please provide:

1. A personalized retirement spending recommendation.
2. Insights about spending patterns based on the uploaded data.
"""

                messages = [
                    {
                        'role': 'system',
                        'content': (
                            "You are a helpful retirement financial assistant. "
                            "Use the user's past spending and uploaded savings context to generate personalized advice."
                        )
                    },
                    {'role': 'user', 'content': full_prompt}
                ]

                response = dashscope.Generation.call(
                    api_key=DASHSCOPE_API_KEY,
                    model="qwen-plus",
                    messages=messages,
                    result_format='message'
                )

                answer = response.output.choices[0].message.content

                st.markdown("### 🧠 Personalized Recommendation:")
                st.success(answer)

                if not combined_spending_df.empty:
                    st.markdown("### 📊 Uploaded Spending Data (Preview):")
                    st.dataframe(combined_spending_df.head(20))
                else:
                    st.info("No structured spending data found.")

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")