import re
import importlib.util
import logging


def split_text(text):
    return re.findall(r'\S+\s*', text)


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
