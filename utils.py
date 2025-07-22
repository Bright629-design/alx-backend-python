#!/usr/bin/env python3

def access_nested_map(nested_map, path):
    for key in path:
        nested_map = nested_map[key]
    return nested_map
def memoize(method):
    """Decorator to cache method output."""
    attr_name = "_{}".format(method.__name__)

    @property
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, method(self))
        return getattr(self, attr_name)
    
    return wrapper
