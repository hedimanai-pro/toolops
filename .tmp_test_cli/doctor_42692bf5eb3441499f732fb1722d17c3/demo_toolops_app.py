from toolops import build_cache_key, cache_manager
from toolops.cache import MemoryCache

async def setup_toolops():
    cache_manager.register('cli', MemoryCache(), is_default=True)
    key = build_cache_key('load_profile', {'user_id': 'alice'}, None)
    await cache_manager.set('cli', key, {'user_id': 'alice'}, 60, tags=['seed'])