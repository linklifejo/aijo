import streamlit as st
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from functools import partial


def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)      

async def add(x, y):
    def add(x,y):
        z = 0
        for i in range(x,y + 1):
            z += i
        return z
    loop = asyncio.get_running_loop()
    partial_func = partial(add, x, y)
    result = await loop.run_in_executor(None, partial_func)
    return result
    

def main():
    if st.button('계산시작'):
        with st.spinner('계산중....'):
            result = run_async(add(1, 100))  # run_async의 반환 값을 result에 저장
            st.write(result)

if __name__ == "__main__":
    main()
                