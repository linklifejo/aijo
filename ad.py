import asyncio
import io
from gtts import gTTS
from pygame import mixer
import speech_recognition as sr
import time

is_playing = False
async def _text_to_speech(text, lang='ko'):
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
        mixer.init()
        is_playing = False
        
async def _speech_to_text_async():
    # 비동기 함수 내에서 실행될 동기 코드
    def sync_speech_to_text():
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                # 오디오를 듣고 인식
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                # 오디오를 텍스트로 변환
                if audio:
                    text = r.recognize_google(audio, language='ko-KR')
                    if text:
                        return True, text
            except sr.WaitTimeoutError:
                return False, 'timeout'
            except sr.UnknownValueError:
                return False, 'unknown'
            except sr.RequestError as e:
                return False, 'error'

    # 현재 실행 중인 이벤트 루프를 가져옵니다.
    loop = asyncio.get_running_loop()

    # 스레드 풀을 사용하여 동기 함수를 비동기적으로 실행합니다.
    return await loop.run_in_executor(None, sync_speech_to_text)
# 비동기 작업을 Streamlit에서 실행하기 위한 래퍼 함수
def speech_to_text():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(_speech_to_text_async())
def stop_to_speech():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_stop_to_speech())
def text_to_speech(text):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_text_to_speech(text))

