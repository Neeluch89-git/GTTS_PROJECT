from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from pydub import AudioSegment
import requests, os, wave
from datetime import datetime
import base64

app = Flask(__name__)
CORS(app)

# === CONFIG ===
API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")  # store this in Render environment
OUTPUT_FOLDER = "tts_output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Path to ffmpeg (adjust if using locally)
AudioSegment.converter = r"C:\Users\Admin\Downloads\ffmpeg-8.0-essentials_build\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe"

# === UTILITY FUNCTIONS ===
def save_pcm_to_wav(pcm_bytes, wav_path):
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm_bytes)

def generate_tts_audio_rest(text, voice_name, temperature, tone=None):
    """Call Google GenAI REST API to generate TTS audio"""
    if tone:
        text = f"Say this in {tone} tone: {text}"

    url = "https://generativelanguage.googleapis.com/v1beta2/models/gemini-2.5-flash-preview-tts:generate"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": {"text": text},
        "temperature": temperature,
        "response_modalities": ["AUDIO"],
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {"voice_name": voice_name}
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"TTS API error: {response.text}")

    # The audio is base64 encoded in the response
    audio_base64 = response.json()["candidates"][0]["content"]["parts"][0]["inline_data"]["data"]
    audio_bytes = base64.b64decode(audio_base64)
    return audio_bytes

# === ROUTES ===
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tts_output/<path:filename>")
def serve_audio(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route("/generate", methods=["POST"])
def generate_tts():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data received"}), 400

    mode = data.get("mode", "single")
    temperature = float(data.get("temperature", 0.7))
    temp_str = str(temperature).replace('.', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        # === SINGLE MODE ===
        if mode == "single":
            text = data.get("text", "").strip()
            voice_name = data.get("voice_name", "").strip()
            tone = data.get("tone", "").strip()

            if not text:
                return jsonify({"error": "Please enter text"}), 400

            pcm_data = generate_tts_audio_rest(text, voice_name, temperature, tone)
            base = f"{voice_name}_temp{temp_str}_{timestamp}"
            wav_path = os.path.join(OUTPUT_FOLDER, f"{base}.wav")
            mp3_path = os.path.join(OUTPUT_FOLDER, f"{base}.mp3")

            save_pcm_to_wav(pcm_data, wav_path)
            AudioSegment.from_wav(wav_path).export(mp3_path, format="mp3", bitrate="192k")

            return jsonify({
                "status": "success",
                "wav_path": f"/tts_output/{base}.wav",
                "mp3_path": f"/tts_output/{base}.mp3"
            })

        # === MULTI SPEAKER MODE ===
        elif mode == "multi":
            s1 = data.get("speaker_1", {})
            s2 = data.get("speaker_2", {})

            s1_text = s1.get("text", "").strip()
            s2_text = s2.get("text", "").strip()
            s1_voice = s1.get("voice", "").strip()
            s2_voice = s2.get("voice", "").strip()
            s1_tone = s1.get("tone", "").strip()
            s2_tone = s2.get("tone", "").strip()

            segments = []
            names = []

            if s1_text:
                pcm1 = generate_tts_audio_rest(s1_text, s1_voice, temperature, s1_tone)
                wav1 = os.path.join(OUTPUT_FOLDER, f"s1_{timestamp}.wav")
                save_pcm_to_wav(pcm1, wav1)
                segments.append(AudioSegment.from_wav(wav1))
                names.append(s1_voice)

            if s2_text:
                pcm2 = generate_tts_audio_rest(s2_text, s2_voice, temperature, s2_tone)
                wav2 = os.path.join(OUTPUT_FOLDER, f"s2_{timestamp}.wav")
                save_pcm_to_wav(pcm2, wav2)
                segments.append(AudioSegment.from_wav(wav2))
                names.append(s2_voice)

            if not segments:
                return jsonify({"error": "No valid text provided"}), 400

            combined = AudioSegment.empty()
            for seg in segments:
                combined += seg

            base = f"{'_and_'.join(names)}_{timestamp}"
            wav_path = os.path.join(OUTPUT_FOLDER, f"{base}.wav")
            mp3_path = os.path.join(OUTPUT_FOLDER, f"{base}.mp3")

            combined.export(wav_path, format="wav")
            combined.export(mp3_path, format="mp3", bitrate="192k")

            return jsonify({
                "status": "success",
                "wav_path": f"/tts_output/{base}.wav",
                "mp3_path": f"/tts_output/{base}.mp3"
            })

        else:
            return jsonify({"error": "Invalid mode"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
