# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 16:56:18 2026

@author: jacques
"""

#general modules
from natsort import natsorted
from datetime import datetime

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local modules
from img_vote.Models.ViewModels import StudiesViewModel, StudyViewModel
from img_vote.utilities.useful import generate_password

#study related
from img_vote.dal.MasterDal import get_all_studies
from img_vote.dal.MasterDal import get_study_status
from img_vote.dal.MasterDal import get_name_of_study
from img_vote.dal.MasterDal import get_review_end
from img_vote.dal.MasterDal import get_learning_end
from img_vote.dal.MasterDal import get_study_distribution
from img_vote.dal.MasterDal import update_study_status
from img_vote.dal.MasterDal import update_study_review_end
from img_vote.dal.MasterDal import update_study_learning_end
from img_vote.dal.MasterDal import update_study_name
from img_vote.dal.MasterDal import update_study_distribution

def get_studies():
    
    studiesDM = get_all_studies()
    
    studiesVM = StudiesViewModel()
    
    for studyDM in studiesDM:
        studiesVM.studies.append(StudyViewModel(studyDM.id, studyDM.name))
        studiesVM.studies_to_show = True
    
    studiesVM.studies = natsorted(studiesVM.studies, lambda x: x.name)
    
    return studiesVM

def get_status(studyId):
    
    status = get_study_status(studyId)
    
    if status == None:
        status = 'stopped'
    
    return status

def update_status(studyId, new_status):
    
    update_study_status(studyId, new_status)

def get_remaining_review_days(studyId):
    
    study_end = get_review_end()
    
    if study_end != None:
        remaining_days = (study_end - datetime.today()).days
    else:
        remaining_days = -1
    
    return remaining_days

def get_remaining_learning_days(studyId):
    
    study_end = get_learning_end()
    
    if study_end != None:
        remaining_days = (study_end - datetime.today()).days
    else:
        remaining_days = -1
    
    return remaining_days
  
def set_study_review_end(studyId, endresponse, keep=True):
    
    if keep:
        deadline = datetime.strptime(endresponse, '%Y-%m-%d')
        
    else:
        deadline = ''
    
    update_study_review_end(deadline, keep)
  
def set_study_learning_end(studyId, endresponse, keep=True):
    
    if keep:
        deadline = datetime.strptime(endresponse, '%Y-%m-%d')
        
    else:
        deadline = ''
    
    update_study_learning_end(deadline, keep)

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
