import streamlit as st
from melodygenerator import MelodyGenerator
from preprocess import SEQUENCE_LENGTH
import matplotlib.pyplot as plt
import music21 as m21
from midi2audio import FluidSynth
import os
import subprocess
import time
import pretty_midi
import numpy as np
import soundfile as sf



# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Melody Generator", layout="centered")


import json

with open("mapping.json", "r") as f:
    mapping = json.load(f)

valid_notes = set(mapping.keys())

# ------------------ UI STYLE ------------------
st.markdown("""
<style>
.main { background-color: #0e1117; }

h1 {
    text-align: center;
    color: #00ffd5;
}

div.stButton > button {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border-radius: 10px;
    height: 45px;
    width: 100%;
    font-size: 16px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

def show_sequence_box(title, sequence):
    st.markdown(f"""
    <div style="
        background:#161b22;
        padding:15px;
        border-radius:12px;
        border:1px solid #30363d;
        margin-bottom:15px;
    ">
        <h6 style="margin-bottom:8px;">{title}</h6>
        <div style="
            font-family:monospace;
            font-size:13px;
            color:#c9d1d9;
            line-height:1.6;
            max-height:120px;
            overflow-y:auto;
            white-space:pre-wrap;
            word-break:break-word;
        ">
            {sequence}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<h1 style='text-align: center; margin-bottom:5px;'>
 MelodAI
</h1>

<p style='text-align: center; font-size:18px; color:#ccc; margin-top:-5px;'>
AI-based melody generation using LSTM
</p>

<hr style='margin-top:8px; margin-bottom:30px;'>
""", unsafe_allow_html=True)

# ------------------ PATH ------------------
BASE_DIR = os.path.dirname(__file__)

FLUIDSYNTH_PATH = r"C:\Users\DELL\Desktop\fluidsynth\bin\fluidsynth.exe"
SOUNDFONT_PATH = r"C:\Users\DELL\Desktop\fluidsynth\FluidR3_GM.sf2"

# ------------------ LOAD MODEL ------------------
@st.cache_resource
def load_model():
    return MelodyGenerator()

# ------------------ MIDI → WAV ------------------






def midi_to_wav(midi_file, wav_file):
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_file)

        # synthesize audio
        audio = midi_data.synthesize()

        # save wav
        sf.write(wav_file, audio, 44100)

        if os.path.exists(wav_file):
            print("✅ WAV created:", wav_file)
            return True
        else:
            print("❌ WAV NOT CREATED")
            return False

    except Exception as e:
        print("Error:", e)
        return False
    """try:
        subprocess.run(command, check=True)
        return os.path.exists(wav_file)
    except:
        return False"""

# ------------------ SCORE ------------------
def score_melody(melody):
    try:
        # remove rests
        notes = [n for n in melody if n not in ["_", "r", "/"]]

        if len(notes) == 0:
            return 0

        pitches = [int(n) for n in notes]

        # 🎯 UNIQUE VARIETY
        unique_ratio = len(set(pitches)) / len(pitches)

        # 🎯 REPETITION CONTROL (FIXED)
        repetition = (len(pitches) - len(set(pitches))) / len(pitches)

        # 🎯 FINAL SCORE
        score = (unique_ratio * 70) + ((1 - repetition) * 30)

        return round(score, 2)

    except Exception as e:
        print("Score error:", e)
        return 0
# ------------------ READABLE NOTES ------------------
def midi_to_note_name(melody):
    readable = []
    for symbol in melody:
        if symbol == "_":
            readable.append("_")
        else:
            try:
                p = m21.pitch.Pitch()
                p.midi = int(symbol)
                readable.append(p.nameWithOctave)
            except:
                readable.append(str(symbol))
    return " ".join(readable)

def clean_melody(melody):
    cleaned = []
    for n in melody:
        try:
            if n not in ["_", "r", "/"]:
                int(n)
                cleaned.append(n)
            else:
                cleaned.append(n)
        except:
            continue
    return cleaned

# ------------------ PIANO ROLL ------------------
def plot_piano_roll(melody, title=""):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 2.5))

    # 🎨 Dark theme
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')

    time_val = 0
    step = 0.25
    start_time = None
    current_note = None

    for symbol in melody:

        if symbol == "_" or symbol == "r":
            time_val += step
            continue

        try:
            note = int(symbol)
        except:
            continue

        if current_note is None:
            current_note = note
            start_time = time_val

        elif note != current_note:
            duration = time_val - start_time
            ax.barh(
                current_note,
                duration,
                left=start_time,
                height=0.5,
                color="#197E1E"  # 🔥 consistent color
            )
            current_note = note
            start_time = time_val

        time_val += step

    # Last note
    if current_note is not None:
        duration = time_val - start_time
        ax.barh(current_note, duration, left=start_time, height=0.5, color="#197E1E")

    # 🎯 Labels
    ax.set_title(title, color="white", fontsize=10)
    ax.set_xlabel("Time (steps)", color="white", fontsize=9)
    ax.set_ylabel("Pitch (MIDI)", color="white", fontsize=9)

    # 🎯 Grid (important)
    ax.grid(True, linestyle="--", alpha=0.2)

    # 🎯 Tick styling
    ax.tick_params(colors='white', labelsize=8)

    # 🎯 Remove borders
    for spine in ax.spines.values():
        spine.set_visible(False)

    return fig
# ------------------ ORIGINAL SONG ------------------
st.subheader("🎵 Reference Melody")

song_choice = st.selectbox("Choose Song", ["Twinkle", "Happy Birthday"])

if song_choice == "Twinkle":
    original_file = os.path.join(BASE_DIR, "twinkle.mid")
else:
    original_file = os.path.join(BASE_DIR, "happy.mid")

if st.button("▶ Play Original Song"):
    if midi_to_wav(original_file, "original.wav"):
        st.audio("original.wav")

st.markdown("<br>", unsafe_allow_html=True)
# ------------------ INPUT ------------------
st.subheader("🎯 Generate Melody")

seed = st.text_input("Enter Seed", placeholder="e.g: 60 _ 60 _ 67 _")

if "generated" not in st.session_state:
    st.session_state.generated = False

if "last_seed" not in st.session_state:
    st.session_state.last_seed = ""
if seed != st.session_state.last_seed:
    st.session_state.generated = False
    st.session_state.last_seed = seed
    st.session_state.pop("melodies", None)
    st.session_state.pop("scores", None)

# ------------------ GENERATE ------------------
if st.button("🚀 Generate Melody"):
    
    st.session_state.generated = False


    invalid=False
    seed_list = seed.split("_")

    for note in seed_list:
        note = note.strip()

        if note == "":
            continue

        if note not in valid_notes and note not in ["r"] and note != " ":
            st.error(f"❌ Invalid note: {note}")
            st.info("✔ Please enter valid notes( e.g.,60-72)")
            invalid=True
            break
    if invalid:
        st.session_state.generated = False
        st.stop()

    mg = load_model()

    progress = st.progress(0)
    status = st.empty()

    status.text("Starting melody generation...")

    melodies = []
    temps = [0.3, 0.8, 1.2]
    labels = ["Safe", "Balanced", "Creative"]

    for i in range(3):

        status.text(f" Generating {labels[i]} melody...")

        melody = mg.generate_melody(
            seed,
            num_steps=100,
            max_sequence_length=SEQUENCE_LENGTH,
            temperature=temps[i]
        )

        melody = clean_melody(melody)
        melodies.append(melody)

        progress.progress((i + 1) * 30)

    

    status.text(" Preparing audio files...")
    # SAVE + CONVERT
    for i in range(3):
        mg.save_melody(melodies[i], file_name=f"mel{i+1}.mid")
        midi_to_wav(f"mel{i+1}.mid", f"mel{i+1}.wav")

    
    progress.progress(100)
    
    

    # 🔥 VARIATIONS
    melody1 = mg.generate_melody(seed, 100, SEQUENCE_LENGTH, 0.3)
    melody2 = mg.generate_melody(seed, 100, SEQUENCE_LENGTH, 0.8)
    melody3 = mg.generate_melody(seed, 100, SEQUENCE_LENGTH, 1.2)

    melody1 = clean_melody(melody1)
    melody2 = clean_melody(melody2)
    melody3 = clean_melody(melody3)

    # 🔥 SCORES
    score1 = score_melody(melody1)
    score2 = score_melody(melody2)
    score3 = score_melody(melody3)

    # SAVE
    mg.save_melody(melody1, file_name="mel1.mid")
    mg.save_melody(melody2, file_name="mel2.mid")
    mg.save_melody(melody3, file_name="mel3.mid")
    

    midi_to_wav("mel1.mid", "mel1.wav")
    midi_to_wav("mel2.mid", "mel2.wav")
    midi_to_wav("mel3.mid", "mel3.wav")

    st.session_state.generated = True
    st.session_state.melodies = [melody1, melody2, melody3]
    st.session_state.scores = [score1, score2, score3]
    st.session_state.seed = seed

    status.empty()


# ------------------ OUTPUT ------------------
if st.session_state.get("generated",False) and "melodies" in st.session_state and "scores" in st.session_state:
    st.success("🎉 Melodies generated successfully!")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.subheader("🎼 Generated Melody Variations")

    labels = ["Stable (Low)", "Balanced (Medium)", "Explorative (High)"]

    cols = st.columns(3)
    best_index = st.session_state.scores.index(max(st.session_state.scores))

    for i in range(3):
        with cols[i]:

            is_best = (i == best_index)

            with st.container():
                
                # 🎯 HEADER
                st.markdown(f"""
                <div style="text-align:center;
                display:flex; flex-direction:column; align-items:center; justify-content:center">
                    <h6 style="margin-bottom:5px; text-align: center; margin-left:30px">{labels[i]}</h6>
                    <p style="color:#9aa4b2; margin-top:-10px;">
                        Score: {st.session_state.scores[i]:.2f}
                    </p>
                    
                </div>
                """, unsafe_allow_html=True)

                # 🎧 AUDIO
                if os.path.exists(f"mel{i+1}.wav"):
                    st.audio(f"mel{i+1}.wav")

                # 📊 GRAPH (clean size)
                fig = plot_piano_roll(st.session_state.melodies[i])
                fig.set_size_inches(5.5, 2.5)
                st.pyplot(fig)

                # ⬇️ DOWNLOAD
                with open(f"mel{i+1}.mid", "rb") as f:
                    st.download_button(
                        "⬇ Download",
                        f,
                        file_name=f"melody_{i+1}.mid",
                        use_container_width=True
                    )

                st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
    #"This system generates three melody variations from the same seed using temperature to control randomness. "
    #"Lower values produce stable sequences, while higher values introduce more variation.\n\n"
    #"The score reflects variation and repetition balance, not musical correctness.\n\n"
    #"The piano roll visualizes melody as Pitch vs Time, where horizontal bars represent notes and their duration."
    
    #------best melody---
    for i in range(3):
        with cols[i]:
            if i==best_index:
                st.success("✅ Best Melody")

    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🎹 Melody Note Representation")
    st.markdown("<h6>Input Sequence</h6>", unsafe_allow_html=True)
    
    show_sequence_box(
        "Input Seed",

        " ".join(midi_to_note_name(st.session_state.seed.split()))
    )

    #st.subheader("🎼 Generated Sequence Notes")
    #for i in range(3):
    #   st.markdown(f"**Variation {i+1} ({labels[i]})**")
    #   st.write(midi_to_note_name(st.session_state.melodies[i]))

    st.markdown("<h6>Generated Sequence</h6>", unsafe_allow_html=True)

    show_sequence_box(
        "Variation 1 (Stable - Low)",
        " ".join(midi_to_note_name(st.session_state.melodies[0]))
    )

    show_sequence_box(
        "Variation 2 (Balanced - Medium)",
        " ".join(midi_to_note_name(st.session_state.melodies[1]))
    )

    show_sequence_box(
        "Variation 3 (Explorative - High)",
        " ".join(midi_to_note_name(st.session_state.melodies[2]))
    )

    



    #'''st.markdown("""
    #### 🔍 Observation
    #- 3 variations generated using different temperature values  
    #- Score evaluates # melody quality (variation + repetition)  
    #- User can compare and choose best output  
    #""")'''