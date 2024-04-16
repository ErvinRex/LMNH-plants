import aiohttp
import asyncio


async def fetch_json(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"An error occurred: {e}")


async def fetch_data_from_endpoints(urls: list[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_json(session, url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses
