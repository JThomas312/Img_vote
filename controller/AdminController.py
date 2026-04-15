#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 19:33:36 2025

@author: jacques
"""

#general imports
import random
import string
from bcrypt import gensalt, hashpw

from openpyxl import Workbook
from os import getcwd
import os.path
from re import sub

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local modules
from img_vote.Models.DataModels import UserDataModel
from img_vote.Models.ViewModels import UserHomeViewModel, CriterionEditingViewModel, CategoryConfigurationViewModel, CategoryEditingViewModel, PrerequisiteEditingViewModel

from img_vote.dal.MasterDal import get_reviewer_by_login, create_reviewer, delete_reviewer_by_id, update_password, get_reviewer_by_id, clear_non_admin_users
from img_vote.dal.MasterDal import create_all_cases, clear_all_cases, extract_all_data
from img_vote.dal.MasterDal import create_criterion, update_criterion, erase_criterion, erase_category_criteria, create_all_criterion, create_all_answer_to_criterion, create_user_answer_to_criterion, get_all_criteria_no_diagnosis, clear_all_criteria
from img_vote.dal.MasterDal import create_user_answers
from img_vote.dal.MasterDal import get_category_by_id, new_empty_category, erase_category, categories_with_criteria, category_with_criteria_and_prerequisites, update_category_value, at_least_one_other_mandatory_category, gold_standard_exists
from img_vote.dal.MasterDal import new_prerequisite, delete_prerequisite


def find_name_and_login(userId):
    usr = get_reviewer_by_id(userId)
    usrName = usr.name
    usrLogin = usr.login
    return (usrName, usrLogin)


def create_user(login, name, admin, status):
    existing = get_reviewer_by_login(login)
    if ((not admin) and (status == 'ended')):
        raise Exception('While the study is ended only administrator users can be created')
    elif existing != None:
        raise Exception('User already exists with login ' + login)
    else:
        password = generate_password()
        s = gensalt()
        hashPass = hashpw(password.encode('utf-8'), s).decode('utf-8')
        revId = create_reviewer(name, login, hashPass, admin)
        if status != 'stopped':
            create_user_answers(revId)
            create_user_answer_to_criterion(revId)
    return password

def categories_for_editing():
    categoriesDMs = categories_with_criteria()
    categoriesVMs = []
    for categoryDM in categoriesDMs:
        currentCategoryVM = CategoryConfigurationViewModel(categoryDM.catId, categoryDM.name, categoryDM.catType, categoryDM.hasTrust, categoryDM.hasTutorial, categoryDM.hasNA, categoryDM.optional)
        for crit in categoryDM.criteria:
            currentCategoryVM.criteria.append(CriterionEditingViewModel(crit[0], crit[1]))
        categoriesVMs.append(currentCategoryVM)
    return categoriesVMs   

def category_for_editing(catId):
    categoryDM = category_with_criteria_and_prerequisites(catId)
    categoryVM = CategoryEditingViewModel(categoryDM.catId, categoryDM.name, categoryDM.catType, categoryDM.hasTrust, categoryDM.hasTutorial, categoryDM.hasNA, categoryDM.optional, categoryDM.hasGoldStandard, categoryDM.hasMalignancy)
    
    for criterion in categoryDM.criteria:
        categoryVM.criteria.append(CriterionEditingViewModel(criterion[0], criterion[1], criterion[2]))
    
    for prerequisite in categoryDM.prerequisites:
        categoryVM.prerequisites.append(PrerequisiteEditingViewModel(prerequisite[0], prerequisite[1]))

    return categoryVM 

def create_empty_category():
    newId = new_empty_category()
    return newId

def update_category(cat_id, value, parameter):
    val = value
    param = parameter
    #this way if either the DAL of front changes parameter, only this needs to be updated --> no dependency between front and DAL
    if parameter == 'name':
        param = 'name'
    if parameter == 'type':
        val = int(value)
        param = 'type'
    if parameter == 'tutorial':
        param = 'tutorial'
    if parameter == 'trust':
        param = 'tutorial'
    if parameter == 'na':
        param = 'tutorial'
    if parameter == 'optional':
        param = 'optional'
    if parameter == 'gold_standard':
        param = 'gold_standard'
    if parameter == 'malignancy':
        param ='malignancy'
    if (value == 'true'):
        val = True
    if (value == 'false'):
        val = False
        
    update_category_value(cat_id, val, param)
    return

def save_criterion(cat_id, name, malignancy):
    
    category_name = get_category_by_id(cat_id).name
    tutorial_slide_path = os.path.join(getcwd(), 'data', 'tutorial_data', category_name, name + '.png')
    mal = malignancy == 'true'
    create_criterion(name, tutorial_slide_path, cat_id, False, mal)

def change_criterion(cat_id, crit_id, name, malignancy, action):
    if action == 'remove':
        erase_criterion(crit_id)    
    if action == 'edit':
        mal = malignancy == 'true'
        update_criterion(crit_id, name, mal)

def save_prerequisite(cat_id, name):
    new_prerequisite(cat_id, name)

def change_prerequisite(cat_id, crit_id, name, action):
    
    if action == 'remove':
        delete_prerequisite(cat_id, crit_id)    
    if action == 'edit':
        delete_prerequisite(cat_id, crit_id)    
        new_prerequisite(cat_id, name)
        

def delete_category(cat_id):
    erase_category_criteria(cat_id)
    erase_category(cat_id)

def delete_criterion(crit_id):
    erase_criterion(crit_id)

def optional_category_allowed(categoryId):
    allowed = at_least_one_other_mandatory_category(categoryId)
    return allowed

def gold_standard_category_allowed(categoryId):
    allowed = not gold_standard_exists(categoryId)
    return allowed

def get_data_for_export():

    wb = Workbook()
    ws = wb.active
    ws.title = "Study_data"
    
    with open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'r', encoding="utf-8") as fr:
        study_name = (fr.read()).replace('\n', '')
    
    file_name = study_name + '_study_data.xlsx'

    wb_path = os.path.join(getcwd(), 'results', file_name)
    
    criteria = get_all_criteria_no_diagnosis()
    
    finalExtract = extract_all_data()
    
    nbCriteria = len(criteria)
    
    ws.cell(row=1, column=1, value='cases')
    ws.cell(row=1, column=2, value='reviewers')
    for i in range(nbCriteria):
        ws.cell(row=1, column=i + 3, value=format_r_friendly(criteria[i].name))
    ws.cell(row=1 , column=nbCriteria + 3 , value='reviewer_diagnosis')
    ws.cell(row=1 , column=nbCriteria + 4 , value='reviewer_diagnosis_confidence')
    ws.cell(row=1 , column=nbCriteria + 5 , value='reviewer_melanoma_depth_confidence')
    ws.cell(row=1 , column=nbCriteria + 6 , value='gold_standard_diagnosis')
    ws.cell(row=1 , column=nbCriteria + 7 , value='reviewer_diagnosis_compared_to_gold_standard')
    ws.cell(row=1 , column=nbCriteria + 8 , value='reviewer_diagnosis_malignity')
    ws.cell(row=1 , column=nbCriteria + 9 , value='gold_standard_malignity')
    ws.cell(row=1 , column=nbCriteria + 10 , value='reviewer_malignity_compared_to_gold_standard')
    
    
    for i in range(len(finalExtract)):
        ws.cell(row=i + 2, column=1, value=finalExtract[i].case)
        ws.cell(row=i + 2, column=2, value=finalExtract[i].reviewer)
        for j in range(nbCriteria):
            ws.cell(row=i + 2, column=j + 3, value=finalExtract[i].criteria[j])
        ws.cell(row=i + 2, column=nbCriteria + 3, value=finalExtract[i].reviewer_diagnosis)
        ws.cell(row=i + 2, column=nbCriteria + 4, value=finalExtract[i].diagnosis_confidence)
        ws.cell(row=i + 2, column=nbCriteria + 5, value=finalExtract[i].depth_confidence)
        ws.cell(row=i + 2, column=nbCriteria + 6, value=finalExtract[i].gold_standard_diagnosis)
        ws.cell(row=i + 2, column=nbCriteria + 7, value=finalExtract[i].gold_standard_diagnosis_comparison)
        ws.cell(row=i + 2, column=nbCriteria + 8, value=finalExtract[i].malignant_diagnosis)
        ws.cell(row=i + 2, column=nbCriteria + 9, value=finalExtract[i].gold_standard_malignity)
        ws.cell(row=i + 2, column=nbCriteria + 10, value=finalExtract[i].gold_standard_malignity_comparison)
     
    wb.save(wb_path)
    
    return (wb_path, file_name)
    
def clear_data():
    clear_non_admin_users()
    clear_all_cases()
    clear_all_criteria()

def delete_user(userId):
    delete_reviewer_by_id(userId)
    
def regenerate_password(userId):
    newPass = generate_password()
    s = gensalt()
    hashPass = hashpw(newPass.encode('utf-8'), s).decode('utf-8')
    update_password(userId, hashPass)
    
    return newPass


def start_study():
    create_all_criterion()
    create_all_cases()
    create_all_answer_to_criterion()


def generate_password():
    length = random.randint(8, 32)
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def format_r_friendly(name):
    return sub(r'[^A-Za-z0-9_]+', "_", name).lower()
