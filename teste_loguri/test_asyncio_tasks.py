import asyncio
import time

async def func(x: int):
    for i in range(100):
        time.sleep(x / 50)
        print(f"{x} ", end = '', flush = True)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(func(5), func(15), func(25)))
    loop.close()

if __name__ == "__main__":
    main()