#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 16:04:36 2025

@author: jacques
"""

#general modules
from bcrypt import gensalt, hashpw
from natsort import natsorted

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local modules
from img_vote.Models.ViewModels import UserHomeViewModel, AdminHomeViewModel, UserLearnViewModel
from img_vote.Models.Enums import StudyStatus

#user related
from img_vote.dal.MasterDal import get_reviewer_by_login
from img_vote.dal.MasterDal import get_reviewer_for_login
from img_vote.dal.MasterDal import get_users_for_admin
from img_vote.dal.MasterDal import update_password
from img_vote.dal.MasterDal import gold_standard_exists

#answer related
from img_vote.dal.MasterDal import get_cases_and_answers
from img_vote.dal.MasterDal import get_cases_and_learn

    
def user_for_home(username, studyId = None, status = None):
    
    user = get_reviewer_by_login(username)
   
    if user.admin:
        usr = AdminHomeViewModel()
        usr.userId = user.userId
        usr.userName = user.name
        if studyId != None:
            otherUsers = get_users_for_admin(user.userId, studyId)
            usr.otherUsers = []
            for otherUser in otherUsers:
                usr.otherUsers.append((otherUser.userId, otherUser.login, otherUser.name, otherUser.admin , otherUser.remaining_cases))
            
            usr.remaingUsers = sum(1 for x in usr.otherUsers if (not x[3] and not x[4] == 0))
            usr.totalUsers = sum(1 for x in usr.otherUsers if not x[3])
            
            usr.displayOthers = len(usr.otherUsers) > 0
            usr.showDeadLineAndGlobalAdvancement = (status in [StudyStatus.ongoing.value, StudyStatus.paused.value, StudyStatus.test.value])
            usr.showIndividualAdvancement = (status in [StudyStatus.ongoing.value, StudyStatus.paused.value, StudyStatus.test.value])
            usr.manageCategories = (status == StudyStatus.stopped.value)
            usr.manageUploadsAndRollbackCategories = (status == StudyStatus.categories_done.value)
            usr.manageDistributionAndRollbackUploads = (status == StudyStatus.uploads_done.value)
            usr.beginAndRollbackDistribution = (status == StudyStatus.ready.value)
            usr.targetedRollback = (status == StudyStatus.test.value)
            usr.exportRemarks = (status == StudyStatus.test.value)
            usr.pause = (status == StudyStatus.ongoing.value)
            usr.resumeAndEnd = (status == StudyStatus.paused.value)
            usr.exportData = (status in [StudyStatus.ended.value, StudyStatus.paused.value, StudyStatus.test.value])
            usr.manageDownloads = (status in [StudyStatus.ended.value, StudyStatus.paused.value, StudyStatus.test.value, StudyStatus.ongoing.value])
            usr.clearUserAndData = (status == StudyStatus.ended.value)
            usr.allowUserDeletion = (status != StudyStatus.ongoing.value)
        
        return usr
    
    usr = UserHomeViewModel()
    
    usr.userId = user.userId
    usr.userName= user.name
    usr.study = user.study
   
    casesAns = get_cases_and_answers(usr.userId)
       
    for caseAns in casesAns:
        usr.items.append((caseAns.caseId, caseAns.name, caseAns.completed))
    
    usr.items = natsorted(usr.items, lambda x : x[1])
        
    usr.remainingItems = len(usr.items) - sum(1 for x in usr.items if x[2])
    
    return usr

def user_for_learning(userId, userName, studyName, remainingDays):
    
    caseLearn = get_cases_and_learn(userId)
    
    viewModel = UserLearnViewModel()
    viewModel.userId = userId
    
    for caseLearnItem in caseLearn:
        viewModel.items.append((caseLearnItem.caseId, caseLearnItem.name, caseLearnItem.correct))
    
    viewModel.items = natsorted(viewModel.items, lambda x : x[1])
    
    viewModel.userName = userName
    viewModel.studyName = studyName
    viewModel.remainingDays = remainingDays
    viewModel.correctAnswers = sum(1 for x in viewModel.items if x[2])
    viewModel.totalAnswers = len(viewModel.items)
    
    return viewModel

def user_for_login(username):
    
    usr = get_reviewer_for_login(username)
    
    return usr

def modify_password(userId, newPass):
    
    s = gensalt()
    hashPass = hashpw(newPass.encode('utf-8'), s).decode('utf-8')
    update_password(userId, hashPass)


