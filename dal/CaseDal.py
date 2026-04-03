#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 20:23:30 2025

@author: jacques
"""

#general imports
from sqlalchemy import String
from sqlalchemy import select
from sqlalchemy import delete

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy.orm import Session

from os import getcwd
from os import listdir
import os.path

from re import split
from re import sub
from openpyxl import load_workbook

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local imports
from img_vote.Models.DataModels import CaseDataModel, FinalExtractDataModel
from img_vote.Models.POCO import CasePOCO, ReviewerPOCO, CriterionPOCO, AnswerPOCO, AnswerCriterionPOCO
from img_vote.dal.CriterionDal import get_all_diagnosis
from img_vote.dal.UserDal import get_all_non_admin_reviewers


#read only     
def get_case_by_id(identifier, engine):
    
    session = Session(engine)
    
    casePOCO = session.get(CasePOCO, identifier)
    
    case = CaseDataModel(casePOCO.id, casePOCO.path, casePOCO.name)
    
    session.close()
    
    return case

def get_all_cases(engine):
    
    session = Session(engine)
    
    cases = []
    
    casesQuery = select(CasePOCO)
    casesPOCO = session.execute(casesQuery).all()
    
    for i in range(len(casesPOCO)):
        cases.append(CaseDataModel(casesPOCO[i][0].id, casesPOCO[i][0].path, casesPOCO[i][0].name)) #for some reason all() returns a tuple, interesting value in first place, see later
    
    session.close()
    
    return cases
    
def exists_case_by_id(identifier, engine):
    
    session = Session(engine)
    
    query = session.query(CasePOCO).filter(CasePOCO.id == identifier)
    ans = session.query(query.exists()).scalar()
    
    return ans


#CRUD
def create_case(path, name, gld_std, engine):
    
    session = Session(engine)

    newCase= CasePOCO(path, name, gld_std)
    
    session.add(newCase)
    session.commit()
    
    caseId = newCase.id
    
    session.close()
    
    return caseId
    
#final data extraction

def extract_all_data(engine):
    
    session = Session(engine)
    
    diagnosisType = 0
    trueValue = 1
    
    reviewers = get_all_non_admin_reviewers(engine)
    casesQuery = session.query(CasePOCO, CriterionPOCO).join(CriterionPOCO, CasePOCO.gold_standard == CriterionPOCO.id).order_by(CasePOCO.id)
    cases = session.execute(casesQuery).all()
    
    extracts = []
    
    for case in cases:
        for reviewer in reviewers:
            query = session.query(AnswerCriterionPOCO, CriterionPOCO, AnswerPOCO).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).join(AnswerPOCO, AnswerCriterionPOCO.answer == AnswerPOCO.id).where(AnswerPOCO.study_case == case[0].id).where(AnswerPOCO.reviewer == reviewer.userId).where(CriterionPOCO.type == diagnosisType).where(AnswerCriterionPOCO.value == trueValue)
            queriedAnswer = query.one_or_none()
            rev_malignity = 'na'
            rev_diag = 'na'
            
            if queriedAnswer != None:
                if queriedAnswer[1].malignity:
                    rev_malignity = 'malignant'
                else:
                    rev_malignity = 'benign'
                    
                rev_diag = format_r_friendly(queriedAnswer[1].name)
            
            diagnosis_confidence = -1
            depth_confidence = -1
            
            confidence_category = 3
            
            query = session.query(AnswerCriterionPOCO, CriterionPOCO, AnswerPOCO).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).join(AnswerPOCO, AnswerCriterionPOCO.answer == AnswerPOCO.id).where(AnswerPOCO.study_case == case[0].id).where(AnswerPOCO.reviewer == reviewer.userId).where(CriterionPOCO.category == confidence_category).where(CriterionPOCO.name == "Diagnosis")
            queriedAnswer = query.one_or_none()
            if queriedAnswer[0].value != None :
                diagnosis_confidence = queriedAnswer[0].value
            
            gld_std_name = format_r_friendly(case[1].name)
            
            if case[1].malignity:
                gld_std_malignity = 'malignant'
            else:            
                gld_std_malignity = 'benign'
            
            
            
            query = session.query(AnswerCriterionPOCO, CriterionPOCO, AnswerPOCO).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).join(AnswerPOCO, AnswerCriterionPOCO.answer == AnswerPOCO.id).where(AnswerPOCO.study_case == case[0].id).where(AnswerPOCO.reviewer == reviewer.userId).where(CriterionPOCO.category == confidence_category).where(CriterionPOCO.name == "Melanoma Depth Prediction")
            queriedAnswer = query.one_or_none()
            if queriedAnswer[0].value != None :
                depth_confidence = queriedAnswer[0].value
            
            queryCriteria = session.query(AnswerCriterionPOCO, CriterionPOCO, AnswerPOCO).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).join(AnswerPOCO, AnswerCriterionPOCO.answer == AnswerPOCO.id). where(AnswerPOCO.study_case == case[0].id).where(AnswerPOCO.reviewer == reviewer.userId).where(CriterionPOCO.type != diagnosisType).order_by(CriterionPOCO.id)
            ansCriteria = queryCriteria.all()    
            
            ansCrit = []
            
            for ansCriterion in ansCriteria:
                ansCrit.append(ansCriterion[0].value)
                
            rev_identifier = str(reviewer.userId) + '_' + format_r_friendly(reviewer.name)
            
            newExtract = FinalExtractDataModel(case[0].name, rev_identifier, ansCrit, rev_diag, diagnosis_confidence, depth_confidence, gld_std_name, rev_diag == gld_std_name, rev_malignity, gld_std_malignity, rev_malignity == gld_std_malignity)
            
            extracts.append(newExtract)
    
    return extracts

#One-time data creation
def create_all_cases(engine):
    
    session = Session(engine)
    
    criteria = get_all_diagnosis(engine)
    criteriaDict = dict()
    
    
    for criterion in criteria:
        criteriaDict[criterion.name] = criterion.diagId
    
    
    cwd = getcwd()
    path = os.path.join(cwd,'data', 'Img_data')
    wbpath = os.path.join(cwd , 'data', 'Data_WOW.xlsx')
    case_files = [file for file in listdir(path) if not file.startswith('.')]
    
    case_files = sorted(list(case_files), key=natural_sort_key)
    
    wb_obj = load_workbook(wbpath)
    sheet_obj = wb_obj.active
    
    counter = 2
    
    for case_file in case_files:
        newpath = os.path.join(path, case_file)
        newname = sheet_obj.cell(row=counter, column=1).value
        #temp hardcoded column number
        cell_value = sheet_obj.cell(row=counter, column=2).value
        gld_std_name = cell_value.removesuffix(' ')
        gld_std = criteriaDict[gld_std_name]
        newcase = CasePOCO(newpath, newname, gld_std)
        
        counter += 1
        
        session.add(newcase)
    
    
    session.commit()
     
    session.close()
     
   
def clear_all_cases(engine):
    
    session = Session(engine)
    
    deleteStmt = delete(CasePOCO)
    
    session.execute(deleteStmt)
    session.commit()

    session.close()
    
def natural_sort_key(item):                                              # ERG added
    """
    Robust key for natural sorting:
    - extracts a name from tuple/list/dict/object/string,
    - splits into text / number chunks and returns a tuple where numbers are ints.
    """
    # 1) get a string name from various possible item shapes
    if isinstance(item, (list, tuple)):
        # prefer the second element if present (id, name, status)
        if len(item) > 1:
            name = str(item[1])
        else:
            name = str(item[0])
    elif isinstance(item, dict):
        name = str(item.get('name') or item.get('label') or next(iter(item.values())))
    else:
        # object or plain string
        name = str(getattr(item, 'name', None) or getattr(item, 'case_name', None) or item)

    # 2) split on digit groups and build key: text parts as lowercase, digit parts as ints
    parts = split(r'(\d+)', name)
    key = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.lower())
    return tuple(key)  
   

def format_r_friendly(name):
    return sub(r'[^A-Za-z0-9_]+', "_", name).lower()
     