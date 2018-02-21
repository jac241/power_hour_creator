import os

from power_hour_creator import config

identity = lambda x: x

def store_results_in_settings(
        key,
        settings=config.get_persistent_settings(),
        transform=identity):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            settings.setValue(key, transform(result))
            return result
        return wrapper
    return decorator


def store_dirname_in_settings(key, settings=config.get_persistent_settings()):
    return store_results_in_settings(
        key=key, settings=settings, transform=os.path.dirname)

