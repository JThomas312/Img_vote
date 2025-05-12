#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 16:04:36 2025

@author: jacques
"""

from os import getcwd
from os import listdir
from random import randint

class UserHomeViewModel():
    def __init__(self):
        self.items = []
        self.remaing_items = 0
    userId: int
    items: list((str, bool))
    remaing_items: int
    
def user_for_home(username):
    usr = UserHomeViewModel()
    
    # user Id will be fetched from database when it is plugged in
    usr.userId = 42
    
    # temporary hardcoded path
    path = getcwd() + "/dummy_data/Img_data"
    files = listdir(path)
    
    #sort by id once database is plugged in
    #files.sort()
    
    #generate values until plugged to the database
    val = True    
    for file in files:
        if randint(1,2) == 1:
            val = not val
        usr.items.append((file, val))
    
    usr.remaing_items = len(usr.items) - sum(1 for x in usr.items if x[1])
    return usr
    