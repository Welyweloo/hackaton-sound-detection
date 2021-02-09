import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import audioop
import csv
import wave
import matplotlib.pyplot as plt
from IPython.display import Audio
from scipy.io import wavfile
import scipy.signal

# Load the model.
model = hub.load('https://tfhub.dev/google/yamnet/1')


# Find the name of the class with the top score when mean-aggregated across frames.
def class_names_from_csv(class_map_csv_text):
  """Returns list of class names corresponding to score vector."""
  class_names = []
  with tf.io.gfile.GFile(class_map_csv_text) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      class_names.append(row['display_name'])

  return class_names


def stereo_to_mono(wavsamplefile):
    stereo = wave.open(wavsamplefile, 'rb')
    mono_filename = "{0}-mono.wav".format(wavsamplefile.replace('.wav',''))
    mono = wave.open(mono_filename, 'wb')
    mono.setparams(stereo.getparams())
    mono.setnchannels(1)
    mono.writeframes(audioop.tomono(stereo.readframes(float('inf')), stereo.getsampwidth(), 1, 1))
    mono.close()

    return mono_filename


def ensure_sample_rate(original_sample_rate, waveform,
                       desired_sample_rate=16000):
  """Resample waveform if required."""
  if original_sample_rate != desired_sample_rate:
    desired_length = int(round(float(len(waveform)) /
                               original_sample_rate * desired_sample_rate))
    waveform = scipy.signal.resample(waveform, desired_length)
  return desired_sample_rate, waveform


class_map_path = model.class_map_path().numpy()
class_names = class_names_from_csv(class_map_path)

wav_file_name = stereo_to_mono('/home/aurelie/Documents/Hackaton/ie_shot_gun-luminalace-770179786.wav')
#wav_file_name = '/src/miaow_16k.wav'

#wav_file_name = stereo_to_mono('/home/aurelie/Documents/Hackaton/recorded_sounds/2.wav')
sample_rate, wav_data = wavfile.read(wav_file_name, 'rb')
sample_rate, wav_data = ensure_sample_rate(sample_rate, wav_data)

# Show some basic information about the audio.
duration = len(wav_data)/sample_rate
print(f'Sample rate: {sample_rate} Hz')
print(f'Total duration: {duration:.2f}s')
print(f'Size of the input: {len(wav_data)}')

# Listening to the wav file.
#Audio(wav_data, rate=sample_rate)
waveform = wav_data / tf.int16.max
scores, embeddings, spectrogram = model(waveform)
scores_np = scores.numpy()
spectrogram_np = spectrogram.numpy()
infered_class = class_names[scores_np.mean(axis=0).argmax()]

print(f'The main sound is: {infered_class}')
