#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 16:04:36 2025

@author: jacques
"""

#general modules
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
from img_vote.utilities.useful import natural_sort_key

#user related
from img_vote.dal.MasterDal import get_reviewer_by_login
from img_vote.dal.MasterDal import get_reviewer_for_login
from img_vote.dal.MasterDal import get_users_for_admin
from img_vote.dal.MasterDal import update_password

#answer related
from img_vote.dal.MasterDal import get_cases_and_answers

    
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
            usr.otherUsers.append((otherUser.userId, otherUser.login, otherUser.name, otherUser.admin , otherUser.remaining_cases))
        
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


