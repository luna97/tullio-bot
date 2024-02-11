import pvporcupine
from pvrecorder import PvRecorder
import speech_recognition as sr
import pygame

# import LLMs as llm

from voice_respond import respond

import cohere
# import LLMs.LLMInterface as LLMInterface

import json
# read the config file
with open('config.json') as f:
    config = json.load(f)

class CohereLLM:#(LLMInterface):

    def __init__(self):
        # super().__init__()
        self.co = cohere.Client(config['cohere']['api_key'])
        self.history = [
                { "role": "User",
                    "message": 
                    """
                    Sei un chatbot amichevole, progettato per conversazioni informali e 
                    rilassate su vari argomenti, come se stessi parlando con un amico. 
                    Rispiondi sempre in italiano. Le risposte non devono essere troppo lunghe.
                    """
                },
        ]

    def respond_to_query(self, query):
        response = self.co.chat(
            query,
            chat_history=self.history,
        )
        self.history.append({'role': 'User', 'message': query})
        self.history.append({'role': 'Chatbot', 'message': response.text})
        return response.text

lmm = CohereLLM()

# init porcupine
porcupine = pvporcupine.create(
  access_key=config['porcupine']['access_key'],
  keyword_paths=config['porcupine']['keyword_paths'],
  model_path=config['porcupine']['model_path'],
)

# init recorder
recoder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

def play_mp3(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # wait for music to finish playing
        pygame.time.Clock().tick(10)

def after_wake_word():

    # play a sound to notify the user
    print('Playing sound...')
    play_mp3('data/wakesound.mp3')

    exit_condition = False

    while not exit_condition:

        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300

        print("Recording...")
        with sr.Microphone() as source:
            try:
                # Record the user's speech
                audio = recognizer.listen(source, timeout=5)

                print("Recording stopped, processing...")


                # Recognize speech using Google Web Speech API
                text = recognizer.recognize_google(audio, language="it-IT")
                print(f"You said: {text}")
                respond(lmm.respond_to_query(text))

            except sr.UnknownValueError:
                respond("Arrivederci!")
                exit_condition = True
                print("Empty audio, exiting...")
            except sr.RequestError as e:
                respond("Mi dispiace, non ho capito. Riprova.")
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except sr.exceptions.WaitTimeoutError:
                respond("Arrivederci!")
                print("Timeout, no speech detected.")
                exit_condition = True
            finally:
                print("Listening user input...")
                # TODO add sound for end of conversation

def listen():
    try:
        recoder.start()
        print('Listening for wake word...')

        while True:
            audio_frame = recoder.read()
            keyword_index = porcupine.process(audio_frame)
            if keyword_index == 0:
                print('Detected wake word')
                recoder.stop()
                after_wake_word()
                recoder.start()
                print('Listening for wake word...')

    except KeyboardInterrupt:
        recoder.stop()
    finally:
        porcupine.delete()
        recoder.delete()

if __name__ == "__main__":
    listen()