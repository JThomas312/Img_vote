#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 11:55:48 2025

@author: jacques
"""

import os.path

from PIL import Image
import base64
import io

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local modules
from img_vote.utilities.useful import sanitize_text, get_study_name, get_status, listdir_safe_and_sorted
from img_vote.Models.ViewModels import CategoryViewModel, CriterionViewModel, CaseDisplayViewModel, CaseLearningViewModel

#user related
from img_vote.dal.MasterDal import update_user_count

#case related
from img_vote.dal.MasterDal import get_case_by_id
from img_vote.dal.MasterDal import get_case_with_gold_standard

#answer related
from img_vote.dal.MasterDal import get_case_by_answer_name
from img_vote.dal.MasterDal import update_answer_status
from img_vote.dal.MasterDal import get_answer_to_case
from img_vote.dal.MasterDal import get_answer_remarks
from img_vote.dal.MasterDal import save_remarks

#answer related
from img_vote.dal.MasterDal import get_answer_name

#category related
from img_vote.dal.MasterDal import get_category_by_id
from img_vote.dal.MasterDal import get_categories

#criterion related
from img_vote.dal.MasterDal import get_criterion_by_id
from img_vote.dal.MasterDal import get_criteria_for_case
from img_vote.dal.MasterDal import safeguard_Criterion
from img_vote.dal.MasterDal import undo_all_but_one
from img_vote.dal.MasterDal import is_answer_done


def caseForDisplay(userId, case):
    
    trueValue = 1
    naValue = 3
    one_of_type = 2
    
    #maximum value acceptable for database
    max_int_db = 1000000000
    #numerical value MUST be positive
    min_int_db = 0
    
    caseDM = get_case_by_id(case)
    name = get_answer_name(userId, case)

    categories = get_categories()
    
    categoriesVM = []
    
    for category in categories:
            
        newCatVM = CategoryViewModel(category.catId, category.name, category.catType, category.hasTrust, category.hasTutorial, category.hasNA, category.optional, category.prerequisites)
        
        criteriaForCase = get_criteria_for_case(userId, case, category.catId)
        
        criteriaVM = []
        
        for criterion in criteriaForCase:
            
            newCritVM = CriterionViewModel(criterion.critId, criterion.name, criterion.value, criterion.isTrust)
                
            if newCritVM.isTrust:
                newCatVM.trust_criterion = newCritVM
            else:
                criteriaVM.append(newCritVM)
        
        newCatVM.criteria = criteriaVM
        
        if category.catId == one_of_type and bool(list(filter(lambda x: x.value == trueValue or x.value == naValue, newCatVM.criteria))):
            newCatVM.unanswered = False
            
        categoriesVM.append(newCatVM)
    
    study_name = get_study_name()
    
    study_status = get_status()
    
    caseVM = CaseDisplayViewModel(caseDM.caseId, name, study_name, len(categoriesVM), nb_imgs=0, imgs=[], imgs_sizes=[])
    
    caseVM.categories = categoriesVM

    caseVM.criteria = criteriaVM

    
    if study_status == 'test':
        remarks = get_answer_remarks(userId, case)
        caseVM.remarks = remarks
        caseVM.show_remarks = True
    else:
        caseVM.remarks = ''
        caseVM.show_remarks = False

    path = caseDM.path
    
    img_files = listdir_safe_and_sorted(path)
    
    caseVM.nb_imgs = 0

    for img_file in img_files:
        img_path = os.path.join(path, img_file)
        (img_data, w, h) = get_image(img_path)
        caseVM.imgs.append(img_data)
        caseVM.imgs_sizes.append((w, h))
        caseVM.nb_imgs += 1
    
    prevName = str(int(name) - 1)
    nextName = str(int(name) + 1)
    
    prevcase = get_case_by_answer_name(prevName, userId)
    nextcase = get_case_by_answer_name(nextName, userId)

    caseVM.prevcase = prevcase
    caseVM.nextcase = nextcase
    
    caseVM.max_int = max_int_db
    caseVM.min_int = min_int_db
    
    return caseVM


def caseForLearning(userId, case):

    caseDM = get_case_with_gold_standard(case)
    name = get_answer_name(userId, case)
    answer = get_answer_to_case(userId, case)
        
    study_name = get_study_name()
    
    caseVM = CaseLearningViewModel(caseDM.caseId, name, study_name, answer, caseDM.goldStandard, nb_imgs=0, imgs=[], imgs_sizes=[])
    
    path = caseDM.path
    
    img_files = listdir_safe_and_sorted(path)
    
    caseVM.nb_imgs = 0

    for img_file in img_files:
        img_path = os.path.join(path, img_file)
        (img_data, w, h) = get_image(img_path)
        caseVM.imgs.append(img_data)
        caseVM.imgs_sizes.append((w, h))
        caseVM.nb_imgs += 1
    
    prevName = str(int(name) - 1)
    nextName = str(int(name) + 1)
    
    prevcase = get_case_by_answer_name(prevName, userId)
    nextcase = get_case_by_answer_name(nextName, userId)

    caseVM.prevcase = prevcase
    caseVM.nextcase = nextcase

    return caseVM


def criterion_for_tutorial(idCriterion):
    tutorial_slide_path = get_criterion_by_id(idCriterion).tutorial_path
    
    img_data, w, h = get_image(tutorial_slide_path, True)
    
    return img_data
    
def safeguardProgress(userId, case, criterionId, value):
    safeguard_Criterion(userId, case, criterionId, value)
    
def safeguardDiagnosis(userId, case, criterionId, value, category):
    
    one_of_type = 2
    
    full_category = get_category_by_id(category)
    criterion = get_criterion_by_id(criterionId)
    
    if full_category.catType == one_of_type and not criterion.isTrust:
        undo_all_but_one(userId, case, criterionId, value, category)
        
    else:
        safeguard_Criterion(userId, case, criterionId, value)

def safeguardRemarks(userId, case, value):
    
    if sanitize_text(value):
        save_remarks(userId, case, value)
    
def checkProgress(userId, case):
    
    done = is_answer_done(userId, case)
    
    if update_answer_status(userId, case, done):
        update_user_count(userId, done)


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

