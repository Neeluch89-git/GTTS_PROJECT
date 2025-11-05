from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import requests, os, wave, base64
from datetime import datetime

app = Flask(__name__)
CORS(app)

# === CONFIG ===
API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")  # store in Render environment
OUTPUT_FOLDER = "tts_output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === UTILITY FUNCTIONS ===
def save_pcm_to_wav(pcm_bytes, wav_path):
    """Save raw PCM bytes as WAV"""
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)        # mono
        wf.setsampwidth(2)        # 16-bit
        wf.setframerate(24000)    # 24 kHz
        wf.writeframes(pcm_bytes)

def generate_tts_audio_rest(text, voice_name="alloy", temperature=0.7, tone=None):
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

    audio_base64 = response.json()["candidates"][0]["content"]["parts"][0]["inline_data"]["data"]
    return base64.b64decode(audio_base64)

# === ROUTES ===
@app.route("/")
def index():
    return render_template("index.html")  # optional frontend

@app.route("/tts_output/<path:filename>")
def serve_audio(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404
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
            voice_name = data.get("voice_name", "alloy").strip()
            tone = data.get("tone", "").strip()

            if not text:
                return jsonify({"error": "Please enter text"}), 400

            pcm_data = generate_tts_audio_rest(text, voice_name, temperature, tone)
            base = f"{voice_name}_temp{temp_str}_{timestamp}"
            wav_path = os.path.join(OUTPUT_FOLDER, f"{base}.wav")

            save_pcm_to_wav(pcm_data, wav_path)

            return jsonify({
                "status": "success",
                "wav_path": f"/tts_output/{base}.wav"
            })

        # === MULTI SPEAKER MODE ===
        elif mode == "multi":
            s1 = data.get("speaker_1", {})
            s2 = data.get("speaker_2", {})

            segments = []
            names = []

            for s, label in [(s1, "s1"), (s2, "s2")]:
                text = s.get("text", "").strip()
                voice_name = s.get("voice", "alloy").strip()
                tone = s.get("tone", "").strip()
                if text:
                    pcm_data = generate_tts_audio_rest(text, voice_name, temperature, tone)
                    wav_file = os.path.join(OUTPUT_FOLDER, f"{label}_{timestamp}.wav")
                    save_pcm_to_wav(pcm_data, wav_file)
                    segments.append(wav_file)
                    names.append(voice_name)

            if not segments:
                return jsonify({"error": "No valid text provided"}), 400

            # Optional: just return list of WAV paths
            result = {f"{name}": path for name, path in zip(names, segments)}
            return jsonify({"status": "success", "files": result})

        else:
            return jsonify({"error": "Invalid mode"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
