#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 18:34:27 2025

@author: jacques
"""

class UserHomeViewModel():
    userId: int
    name: str
    items: list((int, str, bool)) #id, name, completed
    remaing_items: int
    admin: bool
    def __init__(self):
        self.items = []
        self.remaing_items = 0
        self.admin = False
  
class AdminHomeViewModel():
    userId: int
    name: str
    otherUsers: list((int, str, str, bool, bool)) #id, login, name, admin, completed
    remaing_users: int
    total_users: int
    admin: bool
    def __init__(self):
        self.otherUsers = []
        self.remaing_users = 0
        self.admin = True
  
class CaseViewModel():
    imgs: list()
    imgs_sizes: list((int, int))
    criteria: list(list((int, str, int, bytearray, int, bool))) #category, name, value, image, id, hasTutorial
    def __init__(self, nbCategories):
        self.imgs = []
        self.imgs_sizes = []
        self.criteria = [[] for i in range(nbCategories)]
    
        
