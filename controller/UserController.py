#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 16:04:36 2025

@author: jacques
"""

#general modules
from bcrypt import gensalt, hashpw

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local modules
from img_vote.Models.ViewModels import UserHomeViewModel, AdminHomeViewModel, UserLearnViewModel
from img_vote.utilities.useful import natural_sort_key, get_study_name

#user related
from img_vote.dal.MasterDal import get_reviewer_by_login
from img_vote.dal.MasterDal import get_reviewer_for_login
from img_vote.dal.MasterDal import get_users_for_admin
from img_vote.dal.MasterDal import update_password
from img_vote.dal.MasterDal import gold_standard_exists

#answer related
from img_vote.dal.MasterDal import get_cases_and_answers
from img_vote.dal.MasterDal import get_cases_and_learn

    
def user_for_home(username):
    
    user = get_reviewer_by_login(username)
    
    try:
        study_name = get_study_name()
    except FileNotFoundError:
        study_name = ''
   
    if user.admin:
        usr = AdminHomeViewModel()
        usr.userId = user.userId
        usr.name = user.name
        otherUsers = get_users_for_admin(user.userId)
        usr.otherUsers = []
        for otherUser in otherUsers:
            usr.otherUsers.append((otherUser.userId, otherUser.login, otherUser.name, otherUser.admin , otherUser.remaining_cases))
        
        usr.remaing_users = sum(1 for x in usr.otherUsers if (not x[3] and not x[4] == 0))
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

def user_for_learning(userId):
    
    caseLearn = get_cases_and_learn(userId)
    
    viewModel = UserLearnViewModel()
    
    
    for caseLearnItem in caseLearn:
        viewModel.items.append((caseLearnItem.caseId, caseLearnItem.name, caseLearnItem.correct))
    
    viewModel.items = sorted(list(viewModel.items), key=natural_sort_key)
    
    viewModel.correct_answers = sum(1 for x in viewModel.items if x[2])
    viewModel.total_answers = len(viewModel.items)
    
    return viewModel

def study_has_gold_standard():
    return gold_standard_exists()

def user_for_login(username):
    usr = get_reviewer_for_login(username)
    return usr

def modify_password(userId, newPass):
    s = gensalt()
    hashPass = hashpw(newPass.encode('utf-8'), s).decode('utf-8')
    update_password(userId, hashPass)


