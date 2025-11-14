from flask import Flask, render_template, request, jsonify, send_from_directory
from google import genai
from google.genai import types
from pydub import AudioSegment
import os
import wave
from datetime import datetime

app = Flask(__name__)

# === CONFIG ===
API_KEY = "AIzaSyCFNCywzuKK6h_USZ9qTgnugmvZq-4Y55A"
OUTPUT_FOLDER = "tts_output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Utility Functions ===
def save_pcm_to_wav(pcm_bytes, wav_path):
    """Save PCM byte data as WAV file"""
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm_bytes)

def generate_tts_audio(client, text, voice_name, temperature, tone=None):
    """Generate audio with optional tone"""
    if tone:
        text = f"Say this in {tone} tone: {text}"

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=text,
        config=types.GenerateContentConfig(
            temperature=temperature,
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            ),
        ),
    )

    return response.candidates[0].content.parts[0].inline_data.data

# === ROUTES ===
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tts_output/<path:filename>")
def serve_audio(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route("/generate", methods=["POST"])
def generate_tts():
    """Main TTS handler for single & multi-speaker"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data received"}), 400

    mode = data.get("mode", "single")
    temperature = float(data.get("temperature", 0.7))
    temp_str = str(temperature).replace('.', '_')
    client = genai.Client(api_key=API_KEY)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # === SINGLE MODE ===
    if mode == "single":
        text = data.get("text", "").strip()
        voice_name = data.get("voice_name", "").strip()
        tone = data.get("tone", "").strip()

        if not text:
            return jsonify({"error": "Please enter text"}), 400

        pcm_data = generate_tts_audio(client, text, voice_name, temperature, tone)

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

        if not s1_text and not s2_text:
            return jsonify({"error": "Both speakers have empty text"}), 400

        segments = []
        speaker_names = []

        # Speaker 1
        if s1_text:
            pcm1 = generate_tts_audio(client, s1_text, s1_voice, temperature, s1_tone)
            wav1 = os.path.join(OUTPUT_FOLDER, f"s1_{s1_voice}_{timestamp}.wav")
            save_pcm_to_wav(pcm1, wav1)
            segments.append(AudioSegment.from_wav(wav1))
            speaker_names.append(s1_voice)

        # Speaker 2
        if s2_text:
            pcm2 = generate_tts_audio(client, s2_text, s2_voice, temperature, s2_tone)
            wav2 = os.path.join(OUTPUT_FOLDER, f"s2_{s2_voice}_{timestamp}.wav")
            save_pcm_to_wav(pcm2, wav2)
            segments.append(AudioSegment.from_wav(wav2))
            speaker_names.append(s2_voice)

        if not segments:
            return jsonify({"error": "No valid speaker input"}), 400

        # Merge segments
        combined_audio = AudioSegment.empty()
        for seg in segments:
            combined_audio += seg

        base = f"{'_and_'.join(speaker_names)}_temp{temp_str}_{timestamp}"
        wav_path = os.path.join(OUTPUT_FOLDER, f"{base}.wav")
        mp3_path = os.path.join(OUTPUT_FOLDER, f"{base}.mp3")

        combined_audio.export(wav_path, format="wav")
        combined_audio.export(mp3_path, format="mp3", bitrate="192k")

        return jsonify({
            "status": "success",
            "wav_path": f"/tts_output/{base}.wav",
            "mp3_path": f"/tts_output/{base}.mp3"
        })

    else:
        return jsonify({"error": "Invalid mode"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)

