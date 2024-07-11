from urllib.parse import urlparse
import re
import importlib.util
import logging


def split_text(text):
    return re.findall(r'\S+\s*', text)


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


def import_if_installed(package_name, error_message=None):
    if error_message is None:
        error_message = f'{package_name} package is not installed'

    if importlib.util.find_spec(package_name) is not None:
        try:
            return importlib.import_module(package_name)
        except ImportError as e:
            logging.warning(f'Could not import {package_name}: {e}')
            return None
    else:
        raise ImportError(error_message)
