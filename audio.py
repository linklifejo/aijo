import asyncio
import io
from gtts import gTTS
from pygame import mixer
import speech_recognition as sr

async def _text_to_speech_async(text, lang='ko'):
    loop = asyncio.get_running_loop()

    # gTTS와 pygame mixer를 사용하는 동기 함수
    def sync_text_to_speech():
        try:
            tts = gTTS(text=text, lang=lang)
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)  # 파일 포인터를 처음으로 되돌림
            if not mixer.get_init():
                mixer.init()
            mixer.music.load(mp3_fp)  # 오디오 스트림을 메모리에서 직접 불러오기
            mixer.music.play()  # 오디오 재생

            # 오디오 재생이 끝날 때까지 대기
            while mixer.music.get_busy():
                pass

        finally:
            mixer.quit()  # 오디오 재생이 끝나면 믹서 종료

    # 스레드 풀을 사용하여 동기 함수를 비동기적으로 실행
    await loop.run_in_executor(None, sync_text_to_speech)

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
def speech_to_text():
    return asyncio.run(_speech_to_text_async())
def text_to_speech(text):
    return asyncio.run(_text_to_speech_async(text))
# 비동기 함수를 실행하는 메인 함수
def main():
    success,result = speech_to_text()
    if success:
        print(f"Recognized Text: {result}")
    else:
        print(f"Error: {result}")

    text_to_speech('안녕하세요')

if __name__ == "__main__":
    main()
