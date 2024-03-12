import streamlit as st
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from functools import partial
# 동기함수를 비동기함수로 실행하는 방법이며, 이는 기존에 존재하는 동기함수를 비동기로 실행하는데 쓰레드를 이용하는것에 주의
# 동기 함수
def sync_function(x,y):
    return x + y

# 비동기 실행 함수
async def run_sync_function_async(x,y):
    loop = asyncio.get_running_loop()
    partial_func = partial(sync_function, x, y)
    result = await loop.run_in_executor(None, partial_func)
    return result

# 비동기 작업을 실행하고 결과를 반환하는 스트림릿 컴포넌트
def async_component(key, x,y):
    # Streamlit의 캐싱 메커니즘 사용하여 비동기 작업 결과를 캐시
    @st.cache_data()
    def get_async_result(x,y):
        return asyncio.run(run_sync_function_async(x,y))

    result = get_async_result(x,y)
    st.write(f"Result for {x + y}: {result}")

# 스트림릿 앱의 메인 함수
def main():
    st.title("Async Function Demo in Streamlit")

    # 버튼을 사용하여 비동기 작업 시작
    if st.button("Run Async Task"):
        with st.spinner("Running async tasks..."):
            async_component("task1", 1,1)
            async_component("task2", 2,2)
            async_component("task3", 3,3)
        st.success("Done!")
    st.text_input('xxxx')

if __name__ == "__main__":
    main()
