#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 11:55:48 2025

@author: jacques
"""

from os import getcwd
from os import listdir
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
    
    #maximum and minimum values acceptable for database
    max_int_db = 1000000000
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
            
            tutorial_slide_path = criterion.path_to_tutorial
            
            try:
                slide_im = Image.open(tutorial_slide_path)
                data = io.BytesIO()
                slide_im.save(data, 'PNG')
                slide_encoded_img_data = base64.b64encode(data.getvalue())
                slide_img_data = slide_encoded_img_data.decode('utf-8')
                newCritVM.tutorial = slide_img_data
            except:
                newCritVM.tutorial = bytearray()
                
            if newCritVM.isTrust:
                newCatVM.trust_criterion = newCritVM
            else:
                criteriaVM.append(newCritVM)
        
        newCatVM.criteria = criteriaVM
        
        if category.catId == one_of_type and bool(list(filter(lambda x: x.value == trueValue or x.value == naValue, newCatVM.criteria))):
            newCatVM.unanswered = False
            
        categoriesVM.append(newCatVM)
    
    with open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'r', encoding="utf-8") as fr:
        study_name = fr.readline().removesuffix('\n')
    
    caseVM = CaseDisplayViewModel(caseDM.caseId, name, study_name, len(categoriesVM), nb_imgs=0, imgs=[], imgs_sizes=[])
    
    caseVM.categories = categoriesVM

    caseVM.criteria = criteriaVM

    path = caseDM.path
    
    img_files = listdir(path)
    img_files.sort()
    
    caseVM.nb_imgs = 0

    for img_file in img_files:
        im = Image.open(os.path.join(path, img_file))
        data = io.BytesIO()
        im.save(data, 'JPEG')
        encoded_img_data = base64.b64encode(data.getvalue())
        caseVM.imgs.append(encoded_img_data.decode('utf-8'))
        w, h = im.size
        caseVM.imgs_sizes.append((w, h))
        caseVM.nb_imgs += 1
    
    nextName = str(int(name) + 1)
    
    nextcase = get_case_by_answer_name(nextName, userId)

    caseVM.nextcase = nextcase
    
    caseVM.max_int = max_int_db
    caseVM.min_int = min_int_db
    
    return caseVM


def caseForLearning(userId, case):
    
    trueValue = 1
    naValue = 3
    one_of_type = 2
    
    
    caseDM = get_case_with_gold_standard(case)
    name = get_answer_name(userId, case)
    answer = get_answer_to_case(userId, case)
        
    
    with open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'r', encoding="utf-8") as fr:
        study_name = fr.readline().removesuffix('\n')
    
    caseVM = CaseLearningViewModel(caseDM.caseId, name, study_name, answer, caseDM.goldStandard, nb_imgs=0, imgs=[], imgs_sizes=[])
    
    path = caseDM.path
    
    img_files = listdir(path)
    img_files.sort()
    
    caseVM.nb_imgs = 0

    for img_file in img_files:
        im = Image.open(os.path.join(path, img_file))
        data = io.BytesIO()
        im.save(data, 'JPEG')
        encoded_img_data = base64.b64encode(data.getvalue())
        caseVM.imgs.append(encoded_img_data.decode('utf-8'))
        w, h = im.size
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
    try:
        slide_im = Image.open(tutorial_slide_path + '.png')
        data = io.BytesIO()
        slide_im.save(data, 'PNG')
        slide_encoded_img_data = base64.b64encode(data.getvalue())
        img_data = slide_encoded_img_data.decode('utf-8')
    except FileNotFoundError:
        try:
            slide_im = Image.open(tutorial_slide_path + '.jpeg')
            data = io.BytesIO()
            slide_im.save(data, 'JPEG')
            slide_encoded_img_data = base64.b64encode(data.getvalue())
            img_data = slide_encoded_img_data.decode('utf-8')
        except FileNotFoundError:
            try:
                slide_im = Image.open(tutorial_slide_path + '.jpg')
                data = io.BytesIO()
                slide_im.save(data, 'JPG')
                slide_encoded_img_data = base64.b64encode(data.getvalue())
                img_data = slide_encoded_img_data.decode('utf-8')
            except:
                img_data = bytearray()
    
    return(img_data)
    
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

    
def checkProgress(userId, case):
    
    done = is_answer_done(userId, case)
    
    if update_answer_status(userId, case, done):
        update_user_count(userId, done)

