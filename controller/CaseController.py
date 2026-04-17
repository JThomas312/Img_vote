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
from openpyxl import load_workbook

from random import randint

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local modules
from img_vote.Models.ViewModels import CaseViewModel

from img_vote.dal.MasterDal import get_case_by_id
from img_vote.dal.MasterDal import get_criterion_for_case
from img_vote.dal.MasterDal import get_diagnosis_for_case
from img_vote.dal.MasterDal import get_criterion_by_id
from img_vote.dal.MasterDal import create_all_answer_to_criterion
from img_vote.dal.MasterDal import save_Criterion
from img_vote.dal.MasterDal import safeguard_Criterion
from img_vote.dal.MasterDal import undo_all_but_one
from img_vote.dal.MasterDal import get_unfinished_criteria
from img_vote.dal.MasterDal import update_answer_status
from img_vote.dal.MasterDal import update_user_count
from img_vote.dal.MasterDal import create_all_answers
from img_vote.dal.MasterDal import create_all_criterion
from img_vote.dal.MasterDal import create_all_cases
from img_vote.dal.MasterDal import exists_case_by_id

def init_data_study_start():
    create_all_criterion()
    create_all_cases()
    create_all_answers()
    create_all_answer_to_criterion()

def caseForDisplay(userId, case):
    
    trueValue = 1
    
    criterionForCase = get_criterion_for_case(userId, case)
    caseName = get_case_by_id(case).name
     
    # load delimiting words from config file
    delimitations = []
    with open(os.path.join(getcwd(), 'persistence', 'delimitations.txt'), encoding="utf-8") as delim_file:
        for l in delim_file:
            delimitations.append(l.removesuffix('\n'))
        
    path = criterionForCase.path
    
    
    img_files = listdir(path)
    img_files.sort()

    caseVM = CaseViewModel(caseName, len(delimitations))
    
    for img_file in img_files:
        im = Image.open(os.path.join(path, img_file))
        data = io.BytesIO()
        im.save(data, 'JPEG')
        encoded_img_data = base64.b64encode(data.getvalue())
        caseVM.imgs.append(encoded_img_data.decode('utf-8'))
        w, h = im.size
        caseVM.imgs_sizes.append((w, h))
    
    unanswered = [True for a in range (len(delimitations))]
    
    for i in range (len(criterionForCase.criteria)):
        currentCriterion = criterionForCase.criteria[i]
        #currentCriterion 0: type, 1: category, 2: name, 3: value, 4: tutorial path, 5: id
        #category 2 is one of many where we need unanswered status
        if currentCriterion[1] == 2 and currentCriterion[3] == trueValue:
            unanswered[currentCriterion[0]] = False
        tutorial_slide_path = currentCriterion[4]
       
        try:
            slide_im = Image.open(tutorial_slide_path)
            data = io.BytesIO()
            slide_im.save(data, 'PNG')
            slide_encoded_img_data = base64.b64encode(data.getvalue())
            slide_img_data = slide_encoded_img_data.decode('utf-8')
            # 0: category, 1: name, 2: value, 3: image, 4: id, 5: hasTutorial
            (caseVM.criteria[currentCriterion[0]]).append((currentCriterion[1], currentCriterion[2], currentCriterion[3], slide_img_data, currentCriterion[5], True))
        except:
            (caseVM.criteria[currentCriterion[0]]).append((currentCriterion[1], currentCriterion[2], currentCriterion[3], bytearray(), currentCriterion[5], False))
    
    nextcase = 0
    
    if (exists_case_by_id(int(case) + 1)):
        nextcase = int(case) + 1
    
    return (caseVM, delimitations, unanswered, nextcase)

def caseForDiagnosis(userId, case):

    trueValue = 1
    
    criterionForCase = get_diagnosis_for_case(userId, case)
         
    # load delimiting words from config file
    delimitations = []
    with open(os.path.join(getcwd(), 'persistence', 'delim_diagnosis.txt'), encoding="utf-8") as delim_file:
        for l in delim_file:
            delimitations.append(l.removesuffix('\n'))
    
    path = criterionForCase.path
    
    
    img_files = listdir(path)
    img_files.sort()

    caseVM = CaseViewModel(len(delimitations))
    
    for img_file in img_files:
        im = Image.open(os.path.join(path, img_file))
        data = io.BytesIO()
        im.save(data, 'JPEG')
        encoded_img_data = base64.b64encode(data.getvalue())
        caseVM.imgs.append(encoded_img_data.decode('utf-8'))
        w, h = im.size
        caseVM.imgs_sizes.append((w, h))
    
    unanswered = True
    
    for i in range (len(criterionForCase.criteria)):
        currentCriterion = criterionForCase.criteria[i]
        #currentCriterion 0: type, 1: name, 2: value, 3: tutorial path, 4: id
        tutorial_slide_path = currentCriterion[3]
        if currentCriterion[2] == trueValue:
            unanswered = False
        try:
            slide_im = Image.open(tutorial_slide_path)
            data = io.BytesIO()
            slide_im.save(data, 'JPEG')
            slide_encoded_img_data = base64.b64encode(data.getvalue())
            #only one type of criterion, diagnosis, and its id is 2 so out of range
            caseVM.criteria[0].append((currentCriterion[1], currentCriterion[2], slide_encoded_img_data.decode('utf-8'), currentCriterion[4]))
        except:
            caseVM.criteria[0].append((currentCriterion[1], currentCriterion[2], bytearray(), currentCriterion[4]))
    
    nextcase = 0
    
    if (exists_case_by_id(int(case) + 1)):
        nextcase = int(case) + 1
    
    return (caseVM, delimitations, unanswered, nextcase)

    

def criterion_for_tutorial(idCriterion):
    tutorial_slide_path = get_criterion_by_id(idCriterion).tutorial_path
    slide_im = Image.open(tutorial_slide_path)
    data = io.BytesIO()
    slide_im.save(data, 'PNG')
    slide_encoded_img_data = base64.b64encode(data.getvalue())
    img_data = slide_encoded_img_data.decode('utf-8')
    return(img_data)
   
def saveProgress(userId, case, answers):
    for answer in answers:
        save_Criterion(userId, case, answer, answers[answer])
    
def safeguardProgress(userId, case, criterionId, value):
    safeguard_Criterion(userId, case, criterionId, value)
    
def safeguardDiagnosis(userId, case, criterionId, value, critType):
    undo_all_but_one(userId, case, criterionId, value, critType)
    
def checkProgress(userId, case):
    done = not get_unfinished_criteria(userId, case)
    if update_answer_status(userId, case, done):
        update_user_count(userId, done)

