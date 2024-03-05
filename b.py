import asyncio
from gtts import gTTS
from pygame import mixer
import io

is_playing = False

async def text_to_speech(text, lang='ko'):
    global is_playing
    loop = asyncio.get_running_loop()

    def sync_text_to_speech():
        global is_playing
        try:
            tts = gTTS(text=text, lang=lang)
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            if not mixer.get_init():
                mixer.init()
            mixer.music.load(mp3_fp)
            mixer.music.play()
            is_playing = True

            while mixer.music.get_busy() and is_playing:
                pass

        finally:
            mixer.quit()
            is_playing = False

    await loop.run_in_executor(None, sync_text_to_speech)

async def _stop_to_speech():
    global is_playing
    if is_playing and mixer.get_init():
        mixer.music.stop()
        mixer.quit()
        is_playing = False
