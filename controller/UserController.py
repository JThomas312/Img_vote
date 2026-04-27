#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 16:04:36 2025

@author: jacques
"""

#general modules
from re import split
from os import getcwd
import os.path

from bcrypt import gensalt, hashpw

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local modules
from img_vote.Models.ViewModels import UserHomeViewModel, AdminHomeViewModel

from img_vote.dal.MasterDal import get_reviewer_by_login, get_cases_and_answers, get_users_for_admin, get_reviewer_for_login, update_password

    
def user_for_home(username):
    
    user = get_reviewer_by_login(username)

    with open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'r', encoding="utf-8") as fr:
        study_name = fr.readline().removesuffix('\n')
   
    if user.admin:
        usr = AdminHomeViewModel()
        usr.userId = user.userId
        usr.name = user.name
        otherUsers = get_users_for_admin(user.userId)
        usr.otherUsers = []
        
        for otherUser in otherUsers:
            isDone = (otherUser.remaining_cases == 0)
            usr.otherUsers.append((otherUser.userId, otherUser.login, otherUser.name, otherUser.admin , isDone))
        
        usr.remaing_users = sum(1 for x in usr.otherUsers if (not x[3] and not x[4]))
        usr.total_users = sum(1 for x in usr.otherUsers if not x[3])
        
        return (usr, study_name)
    
    
    usr = UserHomeViewModel()
    
    usr.userId = user.userId
    usr.name = user.name
   
    casesAns = get_cases_and_answers(usr.userId)
       
    for caseAns in casesAns:
        usr.items.append((caseAns.caseId, caseAns.name, caseAns.completed))
    
    usr.items = sorted(list(usr.items), key=natural_sort_key)
    
    usr.remaing_items = len(usr.items) - sum(1 for x in usr.items if x[2])
    
    return (usr, study_name)

def user_for_login(username):
    usr = get_reviewer_for_login(username)
    return usr

def modify_password(userId, newPass):
    s = gensalt()
    hashPass = hashpw(newPass.encode('utf-8'), s).decode('utf-8')
    update_password(userId, hashPass)

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
