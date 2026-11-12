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

def generate_password():
    length = random.randint(8, 32)
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    password = sub(r'''[\\"']*''', '', password)
    return password

def format_r_friendly(name):
    return sub(r'[^A-Za-z0-9_]+', "_", name).lower()

def sanitize(userinput):
    return bool(match(r'^[a-zA-Z0-9_ /]{2,50}$', userinput))

def sanitize_login(userinput):
    return bool(match(r'^[a-zA-Z0-9_ ]{2,15}$', userinput))

def sanitize_human_name(userinput):
    return bool(match(r'^[a-zA-ZÀ-ÿ_ ]{2,50}$', userinput))

def sanitize_technical_name(userinput):
    return bool(match(r'^[a-zA-Z0-9À-ÿ,.:;?!_()\'\" /%+<>≥≤«»]{2,100}$', userinput))

def sanitize_text(userinput):
    return bool(match(r'^[a-zA-Z0-9À-ÿ,.:;?!_()\'\"\s/%+<>≥≤«»]{0,2000}$', userinput))

def sanitize_password(userinput):
    return (len(userinput) > 7 and len(userinput) < 51)

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
    
        files = [file for file in listdir(path) if not file.startswith('.') and not file.startswith('_')]
    
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

#return is the date has already passed
def is_passed(enteredDate):
    
    first = datetime.now()
    second = datetime.strptime(enteredDate, '%Y-%m-%d')
    
    return first > second

def verify_images(folder_path):
    
    possible_extensions = ['png', 'Png', 'PNG', 'jpg', 'Jpg', 'JPG',  'jpeg', 'Jpeg', 'JPEG']
    
    try :
        for folder in listdir_safe_and_sorted(folder_path):
            for img in listdir_safe_and_sorted(os.path.join(folder_path, folder)):
                img_path = os.path.join(folder_path, folder, img)
                try:
                    with Image.open(img_path) as image:
                        image.verify()
                except Exception:
                    raise Exception(' '.join(('Invalid image file', img, 'detected in folder', folder)))
                if img_path.split('.')[-1] not in possible_extensions:
                    raise Exception(' '.join(('Incorrect extension detected for image', img, 'in folder', folder)))
                
    except Exception as e:
        print(e)
        error = f'{e}'
        return error
    
    return None

def find_extension(img_path):

    definitive_path = img_path
    
    possible_extensions = ['png', 'Png', 'PNG', 'jpg', 'Jpg', 'JPG',  'jpeg', 'Jpeg', 'JPEG']

    for extension in possible_extensions:
        if os.path.exists('.'.join((img_path, extension))):
            definitive_path = '.'.join((img_path, extension))
    
    return definitive_path

def get_image_dimensions(img_path, try_extensions=False):
    
    definitive_path = img_path
    
    if try_extensions:
        possible_extensions = ['png', 'Png', 'PNG', 'jpg', 'Jpg', 'JPG',  'jpeg', 'Jpeg', 'JPEG']
    
        for extension in possible_extensions:
            if os.path.exists('.'.join((img_path, extension))):
                definitive_path = '.'.join((img_path, extension))
    
    try:
        im = Image.open(definitive_path)
        w, h = im.size
    except:
        w, h = 0, 0
        
    return (w, h)
