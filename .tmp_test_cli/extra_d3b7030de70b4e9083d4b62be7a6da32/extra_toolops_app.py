from toolops import cache_manager
from toolops.cache import MemoryCache

async def setup():
    cache_manager.register('m1', MemoryCache(), is_default=True)