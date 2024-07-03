from urllib.parse import urlparse


def parse_proxies(proxies: dict):
    """Parse proxy url from dict, only support http and https proxy, not support socks5 proxy"""
    proxy_url = proxies.get('http') or proxies.get('https')
    if not proxy_url:
        return {}

    parsed = urlparse(proxy_url)
    return {
        'http_proxy_host': parsed.hostname,
        'http_proxy_port': parsed.port,
        'http_proxy_auth': (
            (parsed.username, parsed.password)
            if parsed.username and parsed.password
            else None
        ),
    }
