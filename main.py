from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
from pydub import AudioSegment
from datetime import datetime
import wave
import os

# === CONFIG ===
GOOGLE_API_KEY = "AIzaSyD7qMkVZublTcKUt1wle6BbP4D8CG5su-k"  # Your Google AI key
FASTAPI_KEY = "neelu-secret-key-0602"  # Your own authentication key
OUTPUT_FOLDER = "tts_output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === APP ===
app = FastAPI(title="FastAPI Google TTS")

# Serve static audio files
app.mount("/tts_output", StaticFiles(directory=OUTPUT_FOLDER), name="tts_output")

# === Middleware for API key verification ===
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    # Skip root endpoint
    if request.url.path == "/":
        return await call_next(request)

    # Check API key in header
    api_key = request.headers.get("X-API-KEY")
    if api_key != FASTAPI_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-KEY")

    response = await call_next(request)
    return response

# === Utility function ===
def save_pcm_to_wav(pcm_bytes, wav_path):
    """Convert PCM byte data to WAV"""
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm_bytes)

def generate_tts_audio(client, text, voice_name, temperature, tone=None):
    """Generate speech using Google Gemini TTS"""
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
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
                )
            ),
        ),
    )

    return response.candidates[0].content.parts[0].inline_data.data

# === ROUTES ===
@app.get("/")
async def root():
    return {"message": "FastAPI TTS is running!"}

@app.post("/generate")
async def generate_tts(request: Request):
    """Generate text-to-speech from Google Gemini"""
    data = await request.json()

    mode = data.get("mode", "single")
    text = data.get("text", "").strip()
    voice_name = data.get("voice_name", "alloy").strip()
    temperature = float(data.get("temperature", 0.7))
    tone = data.get("tone", None)

    if not text:
        return JSONResponse({"error": "Text input required"}, status_code=400)

    client = genai.Client(api_key=GOOGLE_API_KEY)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_str = str(temperature).replace('.', '_')

    # Generate PCM and convert to audio
    pcm_data = generate_tts_audio(client, text, voice_name, temperature, tone)
    base_name = f"{voice_name}_temp{temp_str}_{timestamp}"
    wav_path = os.path.join(OUTPUT_FOLDER, f"{base_name}.wav")
    mp3_path = os.path.join(OUTPUT_FOLDER, f"{base_name}.mp3")

    save_pcm_to_wav(pcm_data, wav_path)
    AudioSegment.from_wav(wav_path).export(mp3_path, format="mp3", bitrate="192k")

    return {
        "status": "success",
        "wav_path": f"/tts_output/{base_name}.wav",
        "mp3_path": f"/tts_output/{base_name}.mp3"
    }

# === Run app ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=7860, reload=True)
