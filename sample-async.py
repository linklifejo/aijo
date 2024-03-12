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
        return x+y
    loop = asyncio.get_running_loop()
    partial_func = partial(add, x, y)
    result = await loop.run_in_executor(None, partial_func)
    return result
    

def main():
    result = run_async(add(3, 4))  # run_async의 반환 값을 result에 저장
    print(result)  # 결과 출력

if __name__ == "__main__":
    main()
                