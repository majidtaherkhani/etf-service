from slowapi import Limiter
from slowapi.util import get_remote_address

# key_func=get_remote_address -> Identifies user by their IP address
# default_limits=["5/minute"] -> Applies to ALL routes (optional, usually better to define per route)

limiter = Limiter(key_func=get_remote_address)
