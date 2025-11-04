from TTS.api import TTS
import os

# Load Coqui XTTS model (supports multilingual + voice cloning)
tts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)

def generate_cloned_voice(text, ref_audio_path, output_path="tts_output/cloned_output.wav"):
    """
    Generate audio using a cloned voice from a reference audio.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    tts_model.tts_to_file(
        text=text,
        speaker_wav=ref_audio_path,
        file_path=output_path,
        language="te"  # Telugu language code
    )
    return output_path
