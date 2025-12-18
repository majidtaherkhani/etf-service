from slowapi import Limiter
from starlette.requests import Request

def get_real_user_ip(request: Request):
    """
    Retrieves the real IP address of the user.
    Essential for deployments (Vercel, Docker, AWS) where the direct
    connection comes from a load balancer/proxy.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    
    return request.client.host or "127.0.0.1"

limiter = Limiter(key_func=get_real_user_ip, default_limits=["30/hour"])