import os
import music21 as m21

KERN_DATASET_PATH = "deutschl\\essen\\europa\\deutschl\\test"

# These are all the lengths of notes that are acceptable
ACCEPTABLE_DURATION = [
    0.25, # 1 time step (quarter of Quarter note length)
    0.5, 
    0.75, 
    1, # Quarter note
    1.5, 
    2, 
    3, 
    4 # Full NOte
]

# kern, MIDI, MusicXML -> m21 -> kern, MIDI, .....

# This is a boolean function that returns if a song has an acceptable length or not
def has_acceptable_durations(song, acceptable_duration):
    # The .flat function flattens the entire object into a list
    # .notesAndRests it filters out all elements that are not Notes and Rest and only keeps them
    # Now only elements we have left with in the song object are notes and rests
    for note in song.flat.notesAndRests:
        # .duration is an attribute of m21
        # If the duration quarter length is not from our accepted list, we return False
        if note.duration.quarterLength not in acceptable_duration:
            return False
        
    return True


# This function basically goes through all the files in your directory, loads the krn file, convert it into a m21 object and return it as a dataset
def load_songs_in_kern(dataset_path):
    # 1. Go through all te files in the dataset and load them with musc 21

    # This goes through all the files in a given path/folder structure
    for path, subdir, files in os.walk(dataset_path):
        songs = []

        for file in files:
            # only load kern files (filter our kern files)
            if file[-3:] == 'krn':
                # We need to pass the path of the current file we're dealing with 
                # m21 converts the krn file into a music 21 stream class and objects
                song = m21.converter.parse(os.path.join(path, file))

                # Load all the songs in an array
                songs.append(song)

        return songs

def transpose(song):
    # get key from the song 
   
    # Extracting parts from the score 
    parts = song.getElementsByClass(m21.stream.Part)

    # Once we get all the parts, we need to get all the measures present in the first part
    measures_part0 = parts[0].getElementsByClass(m21.stream.Measure)
    # The key of the song is placed in a very specific index in the object 
    key = measures_part0[0][4]

    # if we dont have the key, Estimate key using music21
    # If key is not an isntance of m21 key, that means we don't have a key
    if not isinstance(key, m21.key.Key):
        # m21 function that analyzes the key
        key = song.analyze("Key")
        
    print(key)

    # get interval for transposition
    # If we have a score with a major key, we transpose it to Cmaj
    # If we have a score with minor key, we transpose it to Amin
    if key.mode == "major":
        # This calculates the interval between the tonic and the C Pitch
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == "minor":
         interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))
    # Eg. Bmaj -> Cmaj (Difference between Bmaj and Cmaj is the interval)

    # Tranpose the song by caluculated interval
    # This tranposes the song by intervals
    transposed_song = song.transpose(interval)

    return transposed_song


def preprocess(dataset_path):
    # Load the folk songs 
    print("Loading songs...")
    songs = load_songs_in_kern(dataset_path)
    print(f"Loaded {len(songs)} songs.")

    # Iterating through each song and performing the folloing steps!
    for song in songs:
        # Filter out songs that have non acceptable durations
        if not has_acceptable_durations(song, ACCEPTABLE_DURATION):
            continue

        # Transpose songs to CMaj/Amin 
        song = transpose(song)

        # encode songs with music time series representation 

        # Save songs to a text file 

if __name__ == "__main__":
    songs = load_songs_in_kern(KERN_DATASET_PATH)
    print(f"Loaded {len(songs)} songs.")

    song = songs[0]

    print(f"Has acceptable duration? {has_acceptable_durations(song, ACCEPTABLE_DURATION)}")

    # Tranpose song 
    transposed_song = transpose(song)

    # This song is a music21 object. 
    # This will fire our song in Musescore
    song.show()
    # Display the tranposed song
    transposed_song.show()