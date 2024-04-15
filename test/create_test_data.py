import aiohttp
import asyncio
import json

async def fetch_json(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"An error occurred: {e}")


async def main():
    urls = [
        f"https://data-eng-plants-api.herokuapp.com/plants/{i}" for i in range(51)]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_json(session, url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses

if __name__ == "__main__":
    results = asyncio.run(main())
    with open(f'jsons/result.json', 'w') as f:
        json.dump(results, f)