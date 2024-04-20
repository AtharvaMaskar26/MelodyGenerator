import streamlit as st

from melodygenerator import MelodyGenerator
from melodygenerator import SEQUENCE_LENGTH

st.header("🎹 Harmon AI")
st.text("Deep Learning based Melody Generator build using RNN & LSTM")

def save_melody_file(mg):
    mg.save_melody(melody)
    st.caption("File has been saved in your directory, you can open it using any MIDI playing software like MuseScore.")

with st.form("melody-form"):
    # Creating an instance of melody generator class 
    mg = MelodyGenerator()

    seed_melody = st.text_input("Enter a seed phrase: ")
    temperature = st.slider("Adjust temperature: ", 0.0, 1.0)

    submitted = st.form_submit_button("Generate Melody")

    if submitted: 
        melody = mg.generate_melody(seed_melody, 500, SEQUENCE_LENGTH, temperature)

        save_melody_file(mg)