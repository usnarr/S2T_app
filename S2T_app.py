import pyaudio
import wave
import subprocess
import os
import threading
import time

# Settings for recording
chunk = 1024
sample_format = pyaudio.paInt16
channels = 1
fs = 44100
chunk_seconds = 3 
total_seconds = 20  
whisper_path = "path to your whisper"
output_dir = "path to the folder where u want to store the recordings and files produced by whisper"
p = pyaudio.PyAudio()
tmp_dir = "tmp"
stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)

# Function to save chunk
def save_chunk(frames, filename):
    filepath = os.path.join(tmp_dir, filename)
    wf = wave.open(filepath, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    return filepath

# Function to transcribe audio
def transcribe_audio(filepath):
    #cmd = [whisper_path, filepath, "--model", "small", "--task", "transcribe",  "--output_dir", output_dir]  # automatically detects language
    cmd = [whisper_path, filepath, "--model", "small", "--task", "transcribe", "--language", "Polish", "--output_dir", output_dir]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

# Main recording loop
try:
    counter = 0
    start_time = time.time()
    while time.time() - start_time < total_seconds:
        frames = []
        print("Recording chunk")
        for _ in range(0, int(fs / chunk * chunk_seconds)):
            data = stream.read(chunk)
            frames.append(data)

        chunk_filename = f"chunk_output_{counter}.wav"
        filepath = save_chunk(frames, chunk_filename)

        threading.Thread(target=transcribe_audio, args=(filepath,)).start()

        counter += 1

except KeyboardInterrupt:
    print("Recording stopped")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()