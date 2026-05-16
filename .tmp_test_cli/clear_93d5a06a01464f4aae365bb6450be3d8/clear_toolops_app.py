from toolops import cache_manager
from toolops.cache import MemoryCache

async def setup_toolops():
    cache_manager.register('clearme', MemoryCache(), is_default=True)