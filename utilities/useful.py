# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 16:34:34 2026

@author: j.thomas
"""

#general modules
from re import sub
from re import match
from os import getcwd
from os import listdir
from os import mkdir
from os import remove
from shutil import rmtree
from shutil import copyfile
from natsort import natsorted
from datetime import datetime
import os.path
import random
import string
from PIL import Image
import base64
import io

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
    return bool(match(r'^[a-zA-Z0-9À-ÿ,.:;?!_()\'\"\s]*$', userinput))

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
  
def listdir_safe_and_sorted(path):
    
    if os.path.exists(path):
    
        files = [file for file in listdir(path) if not file.startswith('.')]
    
        return natsorted(files)
    
    return []

def safe_save(folder, filename, file):
    
    if not os.path.exists(folder):
        mkdir(folder)
    
    file.save(os.path.join(folder, filename))

def safe_worksheet_save(folder, filename, file):
    
    if not os.path.exists(folder):
        mkdir(folder)
    
    file.save_as(os.path.join(folder, filename))

def safe_remove_file(path):
    
    if os.path.exists(path):
        remove(path)

def safe_remove_folder(path):
    
    if os.path.exists(path):
        rmtree(path)

def move(ogpath, newpath):
    
    copyfile(ogpath, newpath)
    
#return if the first date come after the second date
def is_after(firstDate, secondDate):
    
    first = datetime.strptime(firstDate, '%Y-%m-%d')
    second = datetime.strptime(secondDate, '%Y-%m-%d')
    
    return first > second
    
def get_image(img_path, try_extensions=False):
    
    definitive_path = img_path
    
    if try_extensions:
        possible_extensions = ['.png', '.PNG', '.jpg', '.JPG', '.JPEG']
    
        for extension in possible_extensions:
            if os.path.exists(img_path + extension):
                definitive_path = img_path + extension
    
    try:
        im = Image.open(definitive_path)
        data = io.BytesIO()
        im.save(data, im.format)
        encoded_img_data = base64.b64encode(data.getvalue())
        img_data = encoded_img_data.decode('utf-8')
        w, h = im.size
    except:
        img_data = bytearray()
        w, h = 0, 0
        
    return (img_data, w, h)
