import aiohttp
import asyncio
import time
from transform import transform


async def fetch_json(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"An error occurred: {e}")



async def main():
    while True:
        current_time = time.time()

        seconds_until_next_minute = 60 - (current_time % 60)

        # await asyncio.sleep(seconds_until_next_minute)

        start_time = time.time()

        urls = [
            f"https://data-eng-plants-api.herokuapp.com/plants/{i}" for i in range(51)
        ]

        async with aiohttp.ClientSession() as session:
            tasks = [fetch_json(session, url) for url in urls]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        print(transform(responses))

        

        print(time.time() - start_time)
asyncio.run(main())

