from TTS.api import TTS

# Initialize TTS with a pre-trained model
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", gpu=False)

# Synthesize speech to an audio file
tts.tts_to_file(text="Hello, this is a test with Coqui TTS.", file_path=r"TTS/output.wav")
