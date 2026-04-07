import json
import numpy as np
import tensorflow.keras as keras
import music21 as m21
from preprocess import SEQUENCE_LENGTH, MAPPING_PATH
import random

class MelodyGenerator:
    """A class that wraps the LSTM model and offers utilities to generate melodies."""

    def __init__(self, model_path="model.h5"):
        """Constructor that initialises TensorFlow model"""

        self.model_path = model_path
        self.model = keras.models.load_model(model_path)

        with open(MAPPING_PATH, "r") as fp:
            self._mappings = json.load(fp)

        self._start_symbols = ["/"] * SEQUENCE_LENGTH


    def generate_melody(self, seed, num_steps, max_sequence_length, temperature):
        """Generates a melody using the DL model and returns a midi file.

        :param seed (str): Melody seed with the notation used to encode the dataset
        :param num_steps (int): Number of steps to be generated
        :param max_sequence_len (int): Max number of steps in seed to be considered for generation
        :param temperature (float): Float in interval [0, 1]. Numbers closer to 0 make the model more deterministic.
            A number closer to 1 makes the generation more unpredictable.

        :return melody (list of str): List with symbols representing a melody
        """

        # create seed with start symbols


        seed = seed.split()
        melody = seed.copy()
        seed = self._start_symbols + seed

        seed = [self._mappings[symbol] for symbol in seed]

        
        

        for step in range(num_steps):

            seed = seed[-max_sequence_length:]

            onehot_seed = keras.utils.to_categorical(seed, num_classes=len(self._mappings))
            onehot_seed = onehot_seed[np.newaxis, ...]

            probabilities = self.model.predict(onehot_seed)[0]



            # apply temperature
            predictions = np.log(probabilities + 1e-9) / temperature
            probabilities = np.exp(predictions)
            probabilities = probabilities / np.sum(probabilities)

            # 🔥 REPETITION CONTROL
            if len(melody) > 4:
                last_note = melody[-1]
                if melody[-4:].count(last_note) >= 4:
                    if last_note in self._mappings:
                        probabilities[self._mappings[last_note]] *= 0.1

            # 🔥 STRONG ANTI-LOOP
            if len(melody) > 8:
                if melody[-4:] == melody[-8:-4]:
                    for i in range(len(probabilities)):
                        probabilities[i] *= (1 + random.random())

            # 🔥 TOP-K SAMPLING
            top_k = 10
            top_k_indices = np.argsort(probabilities)[-top_k:]
            top_k_probs = probabilities[top_k_indices]
            top_k_probs = top_k_probs / np.sum(top_k_probs)

            output_int = np.random.choice(top_k_indices, p=top_k_probs)

            seed.append(output_int)

            output_symbol = [k for k, v in self._mappings.items() if v == output_int][0]

            if output_symbol == "/":
                continue

            # 🔥 RHYTHM CONTROL
            if output_symbol == "_":
                if len(melody) > 2 and melody[-1] == "_" and melody[-2] == "_":
                    continue
            #repetition control
            
            if len(melody) > 3:
                if melody[-1] == melody[-2] == melody[-3] :
                    continue

            # jump control
            if len(melody) > 0:
                prev = melody[-1]
                if prev not in ["_", "r"] and output_symbol not in ["_", "r"]:
                    try:
                        if abs(int(output_symbol) - int(prev)) > 8:
                            continue
                    except:
                        pass




            melody.append(output_symbol)
    

            
        return melody 
    ''' 
    def _sample_with_temperature(self, probabilites, temperature):
        """Samples an index from a probability array reapplying softmax using temperature

        :param predictions (nd.array): Array containing probabilities for each of the possible outputs.
        :param temperature (float): Float in interval [0, 1]. Numbers closer to 0 make the model more deterministic.
            A number closer to 1 makes the generation more unpredictable.

        :return index (int): Selected output symbol
        """
        predictions = np.log(probabilites) / temperature
        probabilites = np.exp(predictions) / np.sum(np.exp(predictions))

        choices = range(len(probabilites)) # [0, 1, 2, 3]
        index = np.random.choice(choices, p=probabilites)

        return index '''

    def _sample_with_temperature(self, probabilities, temperature):

        # apply temperature
        predictions = np.log(probabilities + 1e-9) / temperature
        probabilities = np.exp(predictions) / np.sum(np.exp(predictions))

        # 🔥 TOP-K SAMPLING
        top_k = 5   # you can try 3, 5, 10

        # get top k indices
        top_k_indices = np.argsort(probabilities)[-top_k:]

        # get their probabilities
        top_k_probs = probabilities[top_k_indices]

        # normalize again
        top_k_probs = top_k_probs / np.sum(top_k_probs)

        # pick from top k only
        index = np.random.choice(top_k_indices, p=top_k_probs)

        return index


    def save_melody(self, melody, step_duration=0.5, format="midi", file_name="mel.mid"):
        """Converts a melody into a MIDI file

        :param melody (list of str):
        :param min_duration (float): Duration of each time step in quarter length
        :param file_name (str): Name of midi file
        :return:
        """

        # create a music21 stream
        stream = m21.stream.Stream()

        start_symbol = None
        step_counter = 1

        # parse all the symbols in the melody and create note/rest objects
        for i, symbol in enumerate(melody):

            # handle case in which we have a note/rest
            if symbol != "_" or i + 1 == len(melody):

                # ensure we're dealing with note/rest beyond the first one
                if start_symbol is not None:

                    quarter_length_duration = step_duration * step_counter # 0.25 * 4 = 1

                    # handle rest
                    if start_symbol in ["r", "_", "/"]:
                        m21_event = m21.note.Rest(quarterLength=quarter_length_duration)

                    # handle note
                    else:
                        try:
                            midi_value = int(start_symbol)
                            m21_event = m21.note.Note(midi_value, quarterLength=quarter_length_duration)
                        except:
                            continue   # 🔥 skip invalid values

                    stream.append(m21_event)

                    # reset the step counter
                    step_counter = 1

                start_symbol = symbol

            # handle case in which we have a prolongation sign "_"
            else:
                step_counter += 1
                '''
                # 🔥 YOUR CHANGE HERE
                max_steps = random.choice([2, 4, 6])

                if step_counter < max_steps:
                    step_counter += 1
                else:
                    step_counter = 1'''


        # write the m21 stream to a midi file
        stream.write(format, file_name)

"""
if __name__ == "__main__":
    mg = MelodyGenerator()
    seed = "67 _ 67 _ 67 _ _ 65 64 _ 64 _ 64 _ _"
    seed2 = "67 _ _ _ _ _ 65 _ 64 _ 62 _ 60 _ _ _"
    seed3 = "60 _ 62 _ 64 _ 65 _"
    seed4 = "72 _ 69 _ 67 _ 65 _"
    # use the different seeds also to see how model react to them
    melody = mg.generate_melody(seed, 500, SEQUENCE_LENGTH, 0.8) # try this also temperature = 1.0, 1.2,0.3,0.8
    print(melody)
    mg.save_melody(melody)"""