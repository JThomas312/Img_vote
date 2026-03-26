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
from img_vote.Models.ViewModels import UserHomeViewModel

from img_vote.dal.MasterDal import get_reviewer_by_login, create_reviewer, delete_reviewer_by_id, update_password, get_reviewer_by_id, clear_non_admin_users
from img_vote.dal.MasterDal import create_all_cases, clear_all_cases, extract_all_data
from img_vote.dal.MasterDal import create_all_criterion, create_all_answer_to_criterion, create_user_answer_to_criterion, get_all_criteria_no_diagnosis, clear_all_criteria
from img_vote.dal.MasterDal import create_user_answers
from img_vote.dal.MasterDal import extract_all_data


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
  
def get_data_for_export():

    wb = Workbook()
    ws = wb.active
    ws.title = "Study_data"
    
    with open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'r') as fr:
        study_name = (fr.read()).replace('\n', '')
    
    file_name = study_name + '_study_data.xlsx'

    wb_path = os.path.join(getcwd(), 'results', file_name)
    
    criteria = get_all_criteria_no_diagnosis()
    
    finalExtract = extract_all_data()
    
    nbCriteria = len(criteria)
    print(nbCriteria)
    
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
        print(finalExtract[i].criteria)
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
