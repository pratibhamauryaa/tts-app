import re
import io
import numpy as np
from flask import Flask, request, send_file, render_template_string
from flask_cors import CORS
from kokoro import KPipeline
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
import soundfile as sf

app = Flask(__name__)
CORS(app)  # Added for potential cross-origin requests (e.g., testing)

# Language mapping: Detected lang -> Kokoro lang_code
LANG_MAP = {
    'en': 'a',  # American English
    'hi': 'h'   # Hindi
}

# Voice mapping: Detected lang -> Voice (choose natural ones)
VOICE_MAP = {
    'en': 'af_heart',  # American Female, natural
    'hi': 'hf_alpha'   # Hindi Female
}

# Global pipeline cache (reuse to avoid reloading model)
pipelines = {}

def get_pipeline(lang_code):
    if lang_code not in pipelines:
        pipelines[lang_code] = KPipeline(lang_code=lang_code, repo_id='hexgrad/Kokoro-82M')
    return pipelines[lang_code]

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Multilingual Text-to-Speech</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .spinner {
                display: none;
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-top: 4px solid #fff;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                animation: spin 1s linear infinite;
                margin-right: 8px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body class="min-h-screen bg-gradient-to-br from-blue-100 via-purple-100 to-pink-100 flex flex-col items-center justify-center p-6">
        <div class="bg-white rounded-2xl shadow-xl p-8 w-full max-w-lg">
            <h1 class="text-3xl font-bold text-center text-gray-800 mb-4">
                Multilingual Text-to-Speech
            </h1>
            <p class="text-center text-gray-600 mb-6">
                Enter text (e.g., "नमस्ते, आप कैसे हैं or hello, how are you"):
            </p>
            <input
                type="text"
                id="text"
                placeholder="Type your sentence here..."
                class="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-300 mb-4"
            />
            <button
                id="generateBtn"
                onclick="generateSpeech()"
                class="w-full py-3 rounded-lg font-semibold text-white bg-blue-600 hover:bg-blue-700 transition duration-300 flex items-center justify-center"
            >
                <span id="spinner" class="spinner"></span>
                <span id="btnText">Generate & Play Speech</span>
            </button>
            <div id="error" class="mt-4 p-3 bg-red-100 text-red-700 rounded-lg text-center hidden"></div>
            <audio id="audio" controls class="mt-6 w-full hidden"></audio>
        </div>
        <script>
            async function generateSpeech() {
                const text = document.getElementById('text').value;
                const generateBtn = document.getElementById('generateBtn');
                const spinner = document.getElementById('spinner');
                const btnText = document.getElementById('btnText');
                const errorDiv = document.getElementById('error');
                const audioElement = document.getElementById('audio');

                if (!text.trim()) {
                    errorDiv.textContent = 'Please enter some text!';
                    errorDiv.classList.remove('hidden');
                    return;
                }

                // Show spinner, disable button
                spinner.style.display = 'inline-block';
                btnText.textContent = 'Generating...';
                generateBtn.disabled = true;
                errorDiv.classList.add('hidden');
                audioElement.classList.add('hidden');

                try {
                    const response = await fetch('/tts', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    if (!response.ok) throw new Error('Generation failed');

                    const audioBlob = await response.blob();
                    const audioUrl = URL.createObjectURL(audioBlob);
                    audioElement.src = audioUrl;
                    audioElement.classList.remove('hidden');
                    audioElement.play();
                } catch (error) {
                    errorDiv.textContent = 'Error: ' + error.message;
                    errorDiv.classList.remove('hidden');
                } finally {
                    // Hide spinner, re-enable button
                    spinner.style.display = 'none';
                    btnText.textContent = 'Generate & Play Speech';
                    generateBtn.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """)

@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return 'No text provided', 400
    
    # Split into sentences (simple regex for . ! ? followed by space)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    all_audio = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Detect language
        try:
            detected_lang = detect(sentence)
        except LangDetectException:
            detected_lang = 'en'  # Default to English
        
        # Map to Kokoro settings
        lang_code = LANG_MAP.get(detected_lang, 'a')  # Default to English
        voice = VOICE_MAP.get(detected_lang, 'af_heart')
        
        # Get pipeline and generate
        pipeline = get_pipeline(lang_code)
        generator = pipeline(sentence, voice=voice)
        
        sentence_audio = []
        for _, _, chunk in generator:
            sentence_audio.append(chunk)
        
        if sentence_audio:
            sentence_audio = np.concatenate(sentence_audio)
            all_audio.append(sentence_audio)
    
    if not all_audio:
        return 'No valid audio generated', 400
    
    # Concatenate all sentence audios
    full_audio = np.concatenate(all_audio)
    
    # Save to in-memory buffer as WAV
    buffer = io.BytesIO()
    sf.write(buffer, full_audio, 24000, format='WAV')  # 24kHz sample rate for Kokoro
    buffer.seek(0)
    
    return send_file(buffer, mimetype='audio/wav', as_attachment=False, download_name='speech.wav')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)