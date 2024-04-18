"""Script containing functions for pulling data from the Plants API asynchronously. """

import asyncio

import aiohttp


async def fetch_json(session, url):
    """Makes an asynchronous call to an API using the provided endpoint."""
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"An error occurred: {e}")


async def fetch_data_from_endpoints(urls: list[str]):
    """Returns data from the provided endpoint URLs. Calls to the API are asynchronous."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_json(session, url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses
