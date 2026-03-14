from redis import Redis

from nutri.settings import get_settings


settings = get_settings()


redis_conn = Redis.from_url(url=settings.redis_url)
