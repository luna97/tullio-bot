from pygame import mixer
import pygame
from io import BytesIO
import tempfile

from elevenlabs import set_api_key
import elevenlabs
set_api_key("4e9213ac2d4ca0e46ea76bd844a4f832")

from gtts import gTTS
import os

# TODO: Implement logic in order to use elevenlabs when possible
# if no tokens available use gTTs

def respond(text, lang='it'):
    # Use a temporary file to store the audio
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        try:
            audio_stream = elevenlabs.generate(
                text,
                voice="Charlotte",
                stream=True,
                model="eleven_multilingual_v2"
            )
            elevenlabs.stream(audio_stream)
        except Exception as e:
            print(e)
            print("Eleven labs not working, default back to gTTS")

            # Generate the TTS audio from the text
            voice = gTTS(text=text, lang=lang)
            voice.write_to_fp(fp)
            # You must close the file for it to be accessible for reading on some platforms
            fp.close()
            
            # if mixer is not initialized, initialize it
            mixer.init()
            mixer.music.load(fp.name)
            mixer.music.play()
            
            # Wait for the music to finish playing
            while mixer.music.get_busy():
                pygame.time.delay(100)
            
            # Delete the temporary file
            os.remove(fp.name)