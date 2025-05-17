# DeepLing: AI-Powered Retirement Planner

DeepLing is a Streamlit web application designed to provide AI-powered financial guidance for retirement planning. It allows users to analyze their spending habits, incorporate savings information, and receive personalized recommendations and insights through an interactive chat interface that supports text and speech input.

## Features

*   **AI-Driven Financial Advice**: Leverages large language models (Dashscope Qwen-plus) to generate personalized retirement spending recommendations and financial insights.
*   **Spending Analysis**: Upload spending data via CSV, Excel (.xls, .xlsx), or TXT files for analysis.
*   **Savings Document Integration**: Upload savings documents (view-only) to provide context for the AI.
*   **Multiple Input Methods**:
    *   **Text Input**: Type your financial questions directly.
    *   **Live Audio Recording**: Record your questions using the microphone.
    *   **Audio File Upload**: Upload pre-recorded audio questions (supports .wav, .pcm, .mp3).
*   **Speech-to-Text**: Transcribes spoken questions into text for AI processing.
*   **Interactive Follow-up**: Generates relevant follow-up questions to guide the user through their financial planning.
*   **Data Preview**: Displays a preview of the uploaded and processed spending data.
*   **User-Friendly Interface**: Built with Streamlit for an intuitive web experience.

## Prerequisites

*   Python 3.7+
*   API Keys:
    *   **Dashscope API Key**: For accessing the Qwen-plus LLM. You need to set the `DASHSCOPE_API_KEY` environment variable or directly in the `retire_smart_app.py` script.
    *   **ASR (Automatic Speech Recognition) App Key & Token**: For the speech-to-text functionality. You need to set `ASR_APP_KEY` and `ASR_TOKEN` environment variables or directly in the `retire_smart_app.py` script.
*   The `custom_speech_recognition.py` file (or module) needs to be in the same directory as `retire_smart_app.py` or accessible in the Python path.

## Setup and Installation

1.  **Clone the repository (if applicable) or download the files.**
    ```bash
    # If it's a git repository
    # git clone <repository-url>
    # cd <repository-directory>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Keys:**
    *   Open `retire_smart_app.py`.
    *   Locate the lines for `DASHSCOPE_API_KEY`, `ASR_APP_KEY`, and `ASR_TOKEN`.
    *   Replace the placeholder values with your actual API keys.
    ```python
    DASHSCOPE_API_KEY = 'your_dashscope_api_key_here'
    # ...
    ASR_APP_KEY = "your_asr_app_key_here"
    ASR_TOKEN = "your_asr_token_here"
    ```
    Alternatively, set them as environment variables.

## Running the Application

Once the setup is complete, you can run the Streamlit application:

```bash
streamlit run retire_smart_app.py
```

This will typically open the application in your default web browser.

## Usage

1.  **Upload Spending Files**: In "Step 1", upload your spending data in CSV, XLS, XLSX, or TXT format.
2.  **Upload Savings Documents (Optional)**: In "Step 2", upload any relevant savings documents. These are view-only for the AI's context.
3.  **Ask Your Question**:
    *   **Via Speech**:
        *   Record your question directly using the "Start Recording" button.
        *   Or, upload an audio file (.wav, .pcm, .mp3) and click "Transcribe Audio to Text".
    *   **Via Text**: Type your question into the text area in "Step 3".
4.  **Generate Plan**: Click the "Generate My Retirement Plan" button.
5.  **Review & Interact**:
    *   The AI will provide a personalized recommendation and insights.
    *   A preview of your spending data (if uploaded) will be shown.
    *   The AI will suggest related follow-up questions. Click on any suggestion to get an answer.
    *   You can also type new questions based on the AI's response.

## Project Structure

```
.
├── retire_smart_app.py         # Main Streamlit application
├── custom_speech_recognition.py # Module for speech recognition (assumed)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```