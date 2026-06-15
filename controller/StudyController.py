# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 16:56:18 2026

@author: jacques
"""

#general modules
from natsort import natsorted
from datetime import datetime
from datetime import date

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local modules
from img_vote.Models.ViewModels import StudiesViewModel, StudyViewModel
# from img_vote.utilities.useful import 

#study related
from img_vote.dal.MasterDal import get_all_studies
from img_vote.dal.MasterDal import get_study_status
from img_vote.dal.MasterDal import get_name_of_study
from img_vote.dal.MasterDal import get_review_end
from img_vote.dal.MasterDal import get_learning_end
from img_vote.dal.MasterDal import get_study_distribution
from img_vote.dal.MasterDal import has_tutorial
from img_vote.dal.MasterDal import has_gold_standard
from img_vote.dal.MasterDal import has_malignancy
from img_vote.dal.MasterDal import new_study
from img_vote.dal.MasterDal import update_study_status
from img_vote.dal.MasterDal import update_study_review_end
from img_vote.dal.MasterDal import update_study_learning_end
from img_vote.dal.MasterDal import update_study_name
from img_vote.dal.MasterDal import update_study_distribution
from img_vote.dal.MasterDal import update_study_gold_standard
from img_vote.dal.MasterDal import update_study_malignancy
from img_vote.dal.MasterDal import update_study_tutorial

#category related
from img_vote.dal.MasterDal import gold_standard_exists
from img_vote.dal.MasterDal import malignancy_exists
from img_vote.dal.MasterDal import tutorial_category_exists

def get_studies():
    
    studiesDM = get_all_studies()
    
    studiesVM = StudiesViewModel()
    
    for studyDM in studiesDM:
        studiesVM.studies.append(StudyViewModel(studyDM.id, studyDM.name))
        studiesVM.studies_to_show = True
    
    studiesVM.studies = natsorted(studiesVM.studies, lambda x: x.name)
    
    return studiesVM

def create_new_study(studyName):
    
    error = None
    studyId = new_study(studyName)
    
    if studyId == None:
        error = 'Study already exists with that name'
    
    return studyId, error

def get_status(studyId):
    
    status = get_study_status(studyId)
    
    if status == None:
        status = 'stopped'
    
    return status

def update_status(studyId, newStatus):
    
    update_study_status(studyId, newStatus)

def get_remaining_review_days(studyId):
    
    study_end = get_review_end(studyId)
    
    if study_end != None:
        remaining_days = (study_end - date.today()).days
    else:
        remaining_days = -1
    
    return remaining_days

def get_remaining_learning_days(studyId):
    
    study_end = get_learning_end(studyId)
    
    if study_end != None:
        remaining_days = (study_end - date.today()).days
    else:
        remaining_days = -1
    
    return remaining_days
  
def set_study_review_end(studyId, endresponse, keep=True):
    
    if keep:
        deadline = datetime.strptime(endresponse, '%Y-%m-%d')
        
    else:
        deadline = ''

    update_study_review_end(studyId, deadline, keep)
  
def set_study_learning_end(studyId, endresponse, keep=True):
    
    if keep:
        deadline = datetime.strptime(endresponse, '%Y-%m-%d')
        
    else:
        deadline = ''
    
    update_study_learning_end(studyId, deadline, keep)

def get_study_name(studyId):
    
    name = get_name_of_study(studyId)
    
    if name == None:
        name = ''
    
    return name

def set_study_name(studyId, name):
    
    update_study_name(studyId, name)

def get_distribution(studyId):
    
    (method, value) = get_study_distribution(studyId)
    
    if method == 'all for all':
        case_per_r = -1
        percentage = -1
    if method == 'n per case':
        case_per_r = -1
        percentage = -1
    if method == 'n per reviewer':
        case_per_r = value
        percentage = -1
    if method == 'percent per reviewer':
        case_per_r = -1
        percentage = value
    
    return (method, case_per_r, percentage)
        
def set_distribution(studyId, method, case_per_r, percentage):
    
    if method == 'all for all':
        value = -1
    if method == 'n per case':
        value = -1
    if method == 'n per reviewer':
        value = case_per_r
    if method == 'percent per reviewer':
        value = percentage
    
    update_study_distribution(studyId, method, value)

def study_has_tutorial(studyId):
    
    return has_tutorial(studyId)

def study_has_gold_standard(studyId):
    
    return has_gold_standard(studyId)

def update_study_tags(studyId):
    
    gld_std = gold_standard_exists(studyId)
    update_study_gold_standard(studyId, gld_std)
    
    mal = malignancy_exists(studyId)
    update_study_malignancy(studyId, mal)
    
    tuto = tutorial_category_exists(studyId)
    update_study_tutorial(studyId, tuto)
