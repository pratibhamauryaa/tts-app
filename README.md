Multilingual Text-to-Speech Web Application
This project is a web-based Text-to-Speech (TTS) application built using Python and Flask. It allows users to input text in English, Hindi, or a mix of both (e.g., "Hello! नमस्ते, आप कैसे हैं?"), and generates audio using the open-source Kokoro TTS model. The application detects the language of each sentence, selects appropriate voices (English: af_heart, Hindi: hf_alpha), and concatenates the audio for playback in the browser. The UI is styled with Tailwind CSS (via CDN) and includes a loading spinner during audio generation.
Features

Supports multilingual input (English and Hindi).
Automatically detects sentence-level language using langdetect.
Generates audio with Kokoro TTS (self-hosted, ~327MB model).
Responsive UI with Tailwind CSS, featuring a gradient background, card layout, and error handling.
Shows a loading spinner during audio generation.
Outputs audio as WAV, playable in the browser.

Prerequisites

Operating System: macOS, Linux, or Windows.
Python: Version 3.12 (recommended; 3.13 may cause NumPy compilation issues).
espeak-ng: Required for Kokoro's text-to-phoneme conversion.
Internet: Needed to download the Kokoro model (~327MB) on first run.

Setup Instructions

Clone or Extract the Project:

Extract the provided tts-app.zip to a directory (e.g., tts-app).


Install espeak-ng:

macOS:brew install espeak

Verify: espeak "test" (should speak "test").
Ubuntu/Debian:sudo apt update && sudo apt install espeak-ng


Windows:
Download and install from SourceForge.
Add C:\Program Files\eSpeak NG\command_line to your system PATH.




Set Up Python Environment:

Navigate to the project directory:cd tts-app


Create and activate a virtual environment:python3.12 -m venv venv
source venv/bin/activate  # macOS/Linux
# Windows: venv\Scripts\activate


Install dependencies:pip install -r requirements.txt

Note: If NumPy fails on Python 3.13, use Python 3.12 or run:pip install --only-binary=numpy numpy
pip install -r requirements.txt




Run the Application:

Navigate to the backend folder:cd backend


Start the Flask server:python app.py


The app runs on http://localhost:5001 (port 5001 avoids common conflicts).
If port 5001 is in use, check:lsof -i :5001
kill -9 <PID>


Or edit app.py to change the port (e.g., 5002).




Access the Application:

Open a browser and go to http://localhost:5001.
Enter text (e.g., "Hello! नमस्ते, आप कैसे हैं?").
Click "Generate & Play Speech" to hear the audio.



Testing the Application

Test Cases:

Mixed Language: "Hello world! Aaj ka mausam kaisa hai?" (English + Hindi).
Single Language: "Hello, how are you?" or "आज का मौसम अच्छा है।".
Empty Input: Should show a red error box: "Please enter some text!".
Network Error: Simulate by stopping the server; should show "Error: Generation failed".


Manual API Test:

Use curl to test the /tts endpoint:curl -X POST -H "Content-Type: application/json" -d '{"text":"Hello! Namaste, kaise ho?"}' http://localhost:5001/tts -o test.wav


Play test.wav to verify English (af_heart) and Hindi (hf_alpha) voices.


UI Features:

Loading Spinner: Appears in the button during audio generation (1-5 seconds).
Error Handling: Red alert box for invalid inputs or errors.
Responsive Design: Card layout with gradient background, tested on desktop and mobile.



Project Structure
tts-app/
├── backend/
│   └── app.py          # Flask app with backend and HTML frontend
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── venv/               # Virtual environment (optional, not included in zip)

Notes

Kokoro Model: Downloads automatically on first run (327MB, stored in `/.cache/huggingface/hub`).
Performance: Audio generation takes 1-5 seconds (faster with GPU; install PyTorch with CUDA if available).
Troubleshooting:
Port Conflict: Check/kill processes on port 5001 (lsof -i :5001; kill -9 <PID>).
Kokoro Download Fails: Clear cache (rm -rf ~/.cache/huggingface/hub) and retry.
espeak-ng Error: Ensure installed and in PATH.


Dependencies: No external APIs; fully self-hosted with Kokoro TTS.
UI: Uses Tailwind CSS via CDN, no additional setup needed.
