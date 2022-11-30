# to install whisper :
# pip install git+https://github.com/openai/whisper.git

import whisper

model = whisper.load_model("tiny")
print("MODEL LOADED")

# load audio and pad/trim it to fit 30 seconds
audio = whisper.load_audio("/home/mathieu/Dev/PYTHON/newjarvis-server/out.wav")
audio = whisper.pad_or_trim(audio)

# make log-Mel spectrogram and move to the same device as the model
mel = whisper.log_mel_spectrogram(audio).to(model.device)

# decode the audio
options = whisper.DecodingOptions(fp16=False)
result = whisper.decode(model, mel, options)

# print the recognized text
print(result.text)