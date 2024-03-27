import os
import music21 as m21
import json
import numpy as np 
import tensorflow.keras as keras

MAPPING_PATH = "mapping.json"
KERN_DATASET_PATH = 'deutschl\essen\europa\deutschl\\erk'
SAVE_DIR = 'dataset'
SINGLE_FILE_DATASET = "file_dataset"
SEQUENCE_LENGTH = 64

ACCEPTABLE_DURATIONS = [
    0.25, 
    0.5, 
    0.75, 
    1, 
    1.5, 
    2, 
    3,
    4
]

def has_acceptable_durations(song, acceptable_durations):
    # Flat flattens the whole song into a list 
    # notes and rests removes all objects that aren't notes or rests
    for note in song.flat.notesAndRests:
        if note.duration.quarterLength not in acceptable_durations:
            return False
    return True

def load_songs_in_kern(dataset_path):

    songs = []

    # Go through all the files in dataset and load them with music 21
    print('1. ')
    print(dataset_path)
    
    for path, subdir, files in os.walk(dataset_path):
        for file in files:
            if file[-3:] == 'krn':
                song = m21.converter.parse(os.path.join(path, file))
                songs.append(song)
    return songs

def encode_song(song, time_stamp = 0.25):

    encoded_song = []
    for event in song.flat.notesAndRests:
        # Handle notes
        if isinstance(event, m21.note.Note):
            symbol = event.pitch.midi
        # Handle rests
        elif isinstance(event, m21.note.Rest):
            symbol = 'r'

        # Convert the note/rest into time series notation
        steps =  int(event.duration.quarterLength / time_stamp)

        for step in range(steps):
            if step == 0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")

    # Case the encoded song to a strin g
    encoded_song = " ".join(map(str, encoded_song))

    return encoded_song

     

def transpose(song):
    # get key from the song
    parts = song.getElementsByClass(m21.stream.Part)
    measures_part0 = parts[0].getElementsByClass(m21.stream.Measure)

    # Key is stored in 0, 4
    key = measures_part0[0][4]

    # estimate key using music21
    if not isinstance(key, m21.key.Key):
        key = song.analyze("key")

    print(key)

    # get interval for transposition Eg: Bmaj -> Cmaj
    if key.mode == 'major':
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch('C'))

    elif key.mode == 'minor':
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch('A'))

    # Transpose song by calculated interval
    transposed_song = song.transpose(interval)
 
    return transposed_song

def preprocess(dataset_path):
    pass 

    # Load the folk songs 
    print('Loading songs...')
    songs = load_songs_in_kern(dataset_path)
    print(f"Loaded {len(songs)} songs")

    for i, song in enumerate(songs):
        # Filter out songs that have non-acceptable durations   
        if not has_acceptable_durations(song, ACCEPTABLE_DURATIONS):
            continue
        # Transpose songs to Cmaj/Amin 
        song = transpose(song)

        # encode songs with music time series representation
        encoded_song = encode_song(song)

        # Save songs to text file 
        save_path = os.path.join(SAVE_DIR, str(i))

        with open(save_path, 'w') as fp:
            fp.write(encoded_song)

def load(file_path):
   with open(file_path, 'r') as fp:
       song = fp.read()
   return song

def create_single_file_dataset(dataset_path, file_dataset_path, sequence_length):
    new_song_delimiter = '/ ' * sequence_length
    songs = ""
 
    # Load encoded songs and add delimiters 
    for path, _, files in os.walk(dataset_path):
        for file in files:
            file_path = os.path.join(path, file)
            song = load(file_path)

            songs = songs + song + " " + new_song_delimiter
    songs = songs[:-1]

    # save string that contains all datasets
    with open(file_dataset_path, "w") as fp:
        fp.write(songs)

    return songs

def create_mapping(songs, mapping_path):
    mappings = {}

    # identify the vocabulary
    songs = songs.split()
    vocabulary = list(set(songs))

    # Create mappings 
    for i, symbol in enumerate(vocabulary):
        mappings[symbol] = i

    # Save vocabulary to a json file
    with open(mapping_path, "w") as fp:
        json.dump(mappings, fp, indent=4)
    

def convert_songs_to_int(songs):
    int_songs = []

    # Load the mappings 
    with open(MAPPING_PATH, 'r') as fp: 
        mappings = json.load(fp)

    # Cast songs string to a list 
    songs = songs.split()

    # Map songs to int
    for symbol in songs:
        int_songs.append(mappings[symbol])
    
    return int_songs

def generating_training_sequences(sequence_length):
    # Load songs and map then to int 
    songs = load(SINGLE_FILE_DATASET)
    int_songs = convert_songs_to_int(songs)
    inputs = []
    targets = []

    # generate the training sequences 
    num_sequences = len(int_songs) - sequence_length

    for i in range(num_sequences):
        inputs.append(int_songs[i:i+sequence_length])
        targets.append(int_songs[i+sequence_length])

    # one-hot encode the sequences 
    vocabulary_size = len(set(int_songs))
    inputs = keras.utils.to_categorical(inputs, num_classes=vocabulary_size)

    targets = np.array(targets)

    return inputs, targets

    

def main():
    preprocess(KERN_DATASET_PATH)
    songs = create_single_file_dataset(SAVE_DIR, SINGLE_FILE_DATASET, SEQUENCE_LENGTH)

    create_mapping(songs, MAPPING_PATH)

    # inputs, targets = generating_training_sequences(SEQUENCE_LENGTH)


if __name__ == "__main__":
    main()
