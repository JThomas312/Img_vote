# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 16:34:34 2026

@author: j.thomas
"""

#general modules
from re import split
from re import sub
from re import match
from datetime import datetime
from os import getcwd
import os.path
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

def get_status():
    
    try:
        with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
            status = fr.read().replace('\n', '')
    except FileNotFoundError:
        fx = open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'x', encoding="utf-8")
        fx.close()
        with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'w', encoding="utf-8") as fw:
            fw.write('stopped')
        status = 'stopped'
    
    return status

def update_status(new_status):
    
    try:
        with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'w', encoding="utf-8") as fw:
            fw.write(new_status)
    except FileNotFoundError:
        fx = open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'x', encoding="utf-8")
        fx.close()
        with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'w', encoding="utf-8") as fw:
            fw.write(new_status)

def get_remaining_days():
    
    try:
        with open(os.path.join(getcwd(), 'persistence', 'study_end.txt'), 'r', encoding="utf-8") as f:
           try:
               study_end = datetime.strptime(f.read(), '%Y-%m-%d')
               remaining_days = (study_end - datetime.today()).days
           except:
               remaining_days = -1
    except FileNotFoundError:
        remaining_days = -1
    
    return remaining_days
  
def update_study_end(endresponse, keep=True):
    
    if keep:
        deadline = datetime.strptime(endresponse, '%Y-%m-%d')
        endDate = deadline.strftime('%Y-%m-%d')
    else:
        endDate = ''
    
    try:
        with open(os.path.join(getcwd(), 'persistence', 'study_end.txt'), 'w', encoding="utf-8") as fw:
            fw.write(endDate)
    except FileNotFoundError:
        fx = open(os.path.join(getcwd(), 'persistence', 'study_end.txt'), 'x', encoding="utf-8")
        fx.close()
        with open(os.path.join(getcwd(), 'persistence', 'study_end.txt'), 'w', encoding="utf-8") as fw:
            fw.write(endDate)

def get_study_name():
    
    try:
        with open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'r', encoding="utf-8") as fr:
            name = fr.read()
    except FileNotFoundError:
        fx = open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'x', encoding="utf-8")
        fx.close()
        name = ''
    
    return name

def update_study_name(name):
    
    try:
        with open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'w', encoding="utf-8") as fw:
            fw.write(name)
    except FileNotFoundError:
        fx = open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'x', encoding="utf-8")
        fx.close()
        with open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'w', encoding="utf-8") as fw:
            fw.write(name)

def get_distribution():
    
    with open(os.path.join(getcwd(), 'persistence', 'distribution.txt'), 'r', encoding="utf-8") as fr:
        method  = fr.readline().removesuffix('\n')
        case_per_r = fr.readline().removesuffix('\n')
        percentage = fr.readline().removesuffix('\n')
    
    return (method, case_per_r, percentage)
        
def update_distribution(method, case_per_r, percentage):
    
    try:
        with open(os.path.join(getcwd(), 'persistence', 'distribution.txt'), 'w', encoding="utf-8") as fw:
            fw.writelines([method, '\n', case_per_r, '\n', percentage])
    except FileNotFoundError:
        fx = open(os.path.join(getcwd(), 'persistence', 'distribution.txt'), 'x', encoding="utf-8")
        fx.close()
        with open(os.path.join(getcwd(), 'persistence', 'distribution.txt'), 'w', encoding="utf-8") as fw:
            fw.writelines([method, '\n', case_per_r, '\n', percentage])
  
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
