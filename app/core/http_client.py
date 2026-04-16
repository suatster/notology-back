import httpx

client = httpx.AsyncClient(
    timeout=5.0,
    verify=False 
)

def get_http_client() -> httpx.AsyncClient:
    return client
