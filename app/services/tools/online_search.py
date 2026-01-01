import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any
from ddgs import DDGS


_executor = ThreadPoolExecutor(max_workers=4)

def _search_sync(query: str, n_results: int, region: str) -> list[dict[str, Any]]:
    ddgs = DDGS()
    raw = ddgs.text(query=query, region=region, safesearch="off", max_results=n_results) # type: ignore
    return [
        {
            "title": item.get("title") or "",
            "link": item.get("href") or "",
            "snippet": item.get("body") or "",
        }
        for item in raw
    ]

async def search_web(query: str, n_results: int = 5, region: str = "ru-ru") -> list[dict[str, Any]]:
    loop = asyncio.get_running_loop()
    func = partial(_search_sync, query, n_results, region)
    return await loop.run_in_executor(_executor, func)