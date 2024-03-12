import asyncio
import io
from gtts import gTTS
from pygame import mixer
import speech_recognition as sr
import time
import audio



# 재생 상태를 관리하는 전역 변수
is_playing = False

async def text_to_speech(text, lang='ko'):
    global is_playing

    # mixer 초기화
    if not mixer.get_init():
        mixer.init()

    # TTS 생성 및 재생
    tts = gTTS(text=text, lang=lang)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    mixer.music.load(mp3_fp)
    mixer.music.play()
    is_playing = True

    # 음성 재생 상태를 체크하고 필요할 때 재생을 중지
    while is_playing and mixer.music.get_busy():
        await asyncio.sleep(0.1)  # 비동기적으로 대기

    # 재생이 끝났거나 중지되면 mixer 정리
    mixer.music.stop()
    mixer.quit()
    is_playing = False

async def stop_to_speech():
    global is_playing
    is_playing = False  # 재생 상태를 False로 설정하여 재생 중지
async def handle_voice_command():
    success, prompt = await speech_to_text()  # 음성 인식을 비동기적으로 실행
    if success:
        if '종료' in prompt:
            await stop_to_speech()
            # '종료' 명령이 인식되면, 애플리케이션에서 특정 메시지를 표시
            return True, "종료"
        else:
            # 다른 음성 명령이 인식되면, 해당 명령을 처리
            return True, f"{prompt}"
    else:
        # 음성 인식 실패
        return False, "음성 인식에 실패했습니다."
# async def stop_to_speech():
#     global is_playing
#     if is_playing and mixer.get_init():
#         mixer.music.stop()
#         # mixer.mixer.quit()
#         is_playing = False
        
async def speech_to_text():
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

    # 스레드 풀을 사용하여 동기 함수를 비동기적으로 실행하고, 결과를 반환합니다.
    success, result = await loop.run_in_executor(None, sync_speech_to_text)
    return success, result  

