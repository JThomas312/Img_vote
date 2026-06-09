# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 16:34:34 2026

@author: j.thomas
"""

#general modules
from re import split
from re import sub
from re import match

import random
import string

def generate_password():
    length = random.randint(8, 32)
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def format_r_friendly(name):
    return sub(r'[^A-Za-z0-9_]+', "_", name).lower()

def sanitize(userinput):
    return bool(match(r'^[a-zA-Z0-9_\s]{3,50}$', userinput))

def sanitize_text(userinput):
    return bool(match(r'^[a-zA-Z0-9À-ÿ,.:;?!_()\s]*$', userinput))

def natural_sort_key(item):                                              # ERG added
    """
    Robust key for natural sorting:
    - extracts a name from tuple/list/dict/object/string,
    - splits into text / number chunks and returns a tuple where numbers are ints.
    """
    # 1) get a string name from various possible item shapes
    if isinstance(item, (list, tuple)):
        # prefer the second element if present (id, name, status)
        if len(item) > 1:
            name = str(item[1])
        else:
            name = str(item[0])
    elif isinstance(item, dict):
        name = str(item.get('name') or item.get('label') or next(iter(item.values())))
    else:
        # object or plain string
        name = str(getattr(item, 'name', None) or getattr(item, 'case_name', None) or item)

    # 2) split on digit groups and build key: text parts as lowercase, digit parts as ints
    parts = split(r'(\d+)', name)
    key = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.lower())
    return tuple(key)
