
#🎼 MelodAI – AI Melody Generator
MelodAI is an AI-based melody generation system that uses an LSTM neural network to generate new musical sequences from a given seed. The system produces multiple variations, evaluates them, and provides audio playback and visualization.

#🚀 Features
🎵 Generate melodies from user-defined seed
🎛️ Three variations:
Stable (Low randomness)
Balanced (Medium randomness)
Explorative (High randomness)
⭐ Automatic scoring (variation vs repetition)
🎧 Audio playback (MIDI → WAV)
📊 Piano roll visualization (Pitch vs Time)
⬇️ Download generated MIDI files
🎯 Best melody selection

#📂Project Structure
MelodAI/
│
├── app.py                # Streamlit UI
├── melodygenerator.py   # Melody generation logic
├── preprocess.py        # Data preprocessing
├── train.py             # Model training
├── mapping.json         # Symbol → integer mapping
├── model.h5             # Trained model
│
├── mel1.mid / .wav      # Generated outputs
├── mel2.mid / .wav
├── mel3.mid / .wav
│
└── dataset/             # Processed dataset

#⚙️ Tech Stack
Python
TensorFlow / Keras
music21
pretty_midi
Streamlit
NumPy
