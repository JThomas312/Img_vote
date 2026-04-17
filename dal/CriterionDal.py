#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 28 16:15:24 2025

@author: jacques
"""

#general imports
from os import getcwd
import os.path


from openpyxl import load_workbook

from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete

from sqlalchemy.orm import Session

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local imports
from img_vote.Models.DataModels import CriterionDataModel, CriterionForCaseDataModel, DiagnosisDataModel, FinalExtractDataModel
from img_vote.Models.POCO import ReviewerPOCO, CasePOCO, AnswerPOCO, CriterionPOCO, AnswerCriterionPOCO
from img_vote.dal.AnswerDal import get_all_answers
from img_vote.dal.AnswerDal import get_user_answers

     
#read-only 
def get_criterion_by_id(identifier, engine):
    
    session = Session(engine)
    
    criterionPOCO = session.get(CriterionPOCO, identifier)
    
    criterion = CriterionDataModel(criterionPOCO.id, criterionPOCO.name, criterionPOCO.tutorial_path, criterionPOCO.type, criterionPOCO.category)
    
    session.close()
    
    return criterion

def get_unfinished_criteria(userId, caseId, engine):
    
    session = Session(engine)
    
    #criterion category 2 is one of
    #diagnosis is type 0
    diagnosis_type = 0
    yes_no_category = 1
    one_of_category = 2 
    trust_category = 3 
    unanswered_value = 0
    true_value = 1
    
    # if diagnosis is not a melenoma, and trustscal was completed, consider the case done
    queryMel = session.query(CasePOCO, AnswerPOCO, CriterionPOCO, AnswerCriterionPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CasePOCO.id == caseId).filter(AnswerPOCO.reviewer == userId).filter(CriterionPOCO.type == diagnosis_type).filter(AnswerCriterionPOCO.value == true_value).filter(CriterionPOCO.category == one_of_category).filter(CriterionPOCO.name != "Melanoma")
    ansMel = session.query(queryMel.exists()).scalar()
    queryMelTrust = session.query(CasePOCO, AnswerPOCO, CriterionPOCO, AnswerCriterionPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CasePOCO.id == caseId).filter(AnswerPOCO.reviewer == userId).filter(CriterionPOCO.type == diagnosis_type).filter(AnswerCriterionPOCO.value != unanswered_value).filter(CriterionPOCO.category == trust_category)
    ansMelTrust = session.query(queryMelTrust.exists()).scalar()
    
    if ansMel :
        if ansMelTrust:
            return False
    
    
    # still need to check 
    
    query1 = session.query(CasePOCO, AnswerPOCO, CriterionPOCO, AnswerCriterionPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CasePOCO.id == caseId).filter(AnswerPOCO.reviewer == userId).filter(CriterionPOCO.category == yes_no_category).filter(AnswerCriterionPOCO.value == unanswered_value)
    query2 = session.query(CasePOCO, AnswerPOCO, CriterionPOCO, AnswerCriterionPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CasePOCO.id == caseId).filter(AnswerPOCO.reviewer == userId).filter(CriterionPOCO.type == 1).filter(CriterionPOCO.category == one_of_category).filter(AnswerCriterionPOCO.value == true_value).group_by(CriterionPOCO.category)
    query3 = session.query(CasePOCO, AnswerPOCO, CriterionPOCO, AnswerCriterionPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CasePOCO.id == caseId).filter(AnswerPOCO.reviewer == userId).filter(CriterionPOCO.type == 4).filter(CriterionPOCO.category == one_of_category).filter(AnswerCriterionPOCO.value == true_value).group_by(CriterionPOCO.category)
   
    queryTrust = session.query(CasePOCO, AnswerPOCO, CriterionPOCO, AnswerCriterionPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CasePOCO.id == caseId).filter(AnswerPOCO.reviewer == userId).filter(CriterionPOCO.type != diagnosis_type).filter(AnswerCriterionPOCO.value != unanswered_value).filter(CriterionPOCO.category == trust_category)
    ansTrust = session.query(queryTrust.exists()).scalar()
    
    ans1 = session.query(query1.exists()).scalar()
    ans2 = session.query(query2.exists()).scalar()
    ans3 = session.query(query3.exists()).scalar()
    
    
    finalAnswer = ans1 or (not ans2) or (not ans3) or (not ansTrust) or (not ansMelTrust)
    
    
    return finalAnswer

def get_criterion_for_case(userId, caseId, engine):
    
    session = Session(engine)
    #criterion category 3 is trustScale
    #trustCategory = 3    

    query = session.query(CasePOCO, AnswerPOCO, CriterionPOCO, AnswerCriterionPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CasePOCO.id == caseId).filter(AnswerPOCO.reviewer == userId).order_by(CriterionPOCO.id)
    #.filter(CriterionPOCO.category != trustCategory)

    queriedAnswer = query.all()
    
    #0: Case, 1: Answer, 2: Criterion, 3: AnswerCriterion
        
    answer = CriterionForCaseDataModel(queriedAnswer[0][0].path)
    
    for i in range(len(queriedAnswer)):
        answer.criteria.append((queriedAnswer[i][2].type, queriedAnswer[i][2].category, queriedAnswer[i][2].name, queriedAnswer[i][3].value, queriedAnswer[i][2].tutorial_path, queriedAnswer[i][2].id))
    
    session.close()
    
    return answer


def get_diagnosis_for_case(userId, caseId, engine):
    
    session = Session(engine)
    #criterion type 2 is diagnosis
    diagnosis_type = 2    

    query = session.query(CasePOCO, AnswerPOCO, CriterionPOCO, AnswerCriterionPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CasePOCO.id == caseId).filter(AnswerPOCO.reviewer == userId).filter(CriterionPOCO.type == diagnosis_type).order_by(CriterionPOCO.id)

    queriedAnswer = query.all()
    
    #0: Case, 1: Answer, 2: Criterion, 3: AnswerCriterion   
    
    answer = CriterionForCaseDataModel(queriedAnswer[0][0].path)
    
    for i in range(len(queriedAnswer)):
        answer.criteria.append((queriedAnswer[i][2].type, queriedAnswer[i][2].name, queriedAnswer[i][3].value, queriedAnswer[i][2].tutorial_path, queriedAnswer[i][2].id))
    
    session.close()
    
    return answer

def get_all_criteria(engine):
    
    session = Session(engine)
    
    criteria = []
    
    criteriaQuery = select(CriterionPOCO)
    criteriaPOCO = session.execute(criteriaQuery).all()
    
    for i in range(len(criteriaPOCO)):
        criteria.append(criteriaPOCO[i][0]) #no time to investigate all(), mayhap later

    session.close()

    return criteria

def get_all_criteria_no_diagnosis(engine):
    
    session = Session(engine)
    
    diagnosis_type = 0
    trust_category = 3
    
    query = session.query(CriterionPOCO).filter(CriterionPOCO.type != diagnosis_type).filter(CriterionPOCO.category != trust_category)
    ans = query.all()
    
    critNoDiag = []
    
    for i in range(len(ans)):
        critNoDiag.append(DiagnosisDataModel(ans[i].id, ans[i].name))
    
    session.close()
    
    return critNoDiag

def get_all_diagnosis(engine):
    
    session = Session(engine)
    
    diagnosis_type = 0
    
    query = session.query(CriterionPOCO).filter(CriterionPOCO.type == diagnosis_type)
    ans = query.all()
    
    diagnosis = []
    
    for i in range(len(ans)):
        diagnosis.append(DiagnosisDataModel(ans[i].id, ans[i].name))
    
    session.close()
    
    return diagnosis

#CRUD
def create_criterion(name, tutorial_path, critType, malignity, engine):
    
    session = Session(engine)

    newCrit = CriterionPOCO(name, tutorial_path, critType, malignity)
    if (newCrit.tutorial_path == None):
        newCrit.tutorial_path = tutorial_path
    session.add(newCrit)
    session.commit()
    
    session.close()

def create_answer_to_criterion(answer, criterion, engine):
    
    session = Session(engine)
    
    newAnsCrit = AnswerCriterionPOCO(answer, criterion)
    session.add(newAnsCrit)
    session.commit()
    
    session.close()

def save_Criterion(user, case, critName, newValue, engine):
    
    session = Session(engine)
    
    query = session.query(AnswerCriterionPOCO, AnswerPOCO, CriterionPOCO).join(AnswerPOCO, AnswerCriterionPOCO.answer == AnswerPOCO.id).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CriterionPOCO.name == critName).filter(AnswerPOCO.study_case == case).filter(AnswerPOCO.reviewer == user)
    ansCrit = query.one_or_none()[0]
    updatestmt = update(AnswerCriterionPOCO).where(AnswerCriterionPOCO.answer == ansCrit.answer).where(AnswerCriterionPOCO.criterion == ansCrit.criterion).values(value=newValue)

    session.execute(updatestmt)

    session.commit()
    
    session.close()

def safeguard_Criterion(user, case, critId, newValue, engine):
    
    session = Session(engine)
    
    query = session.query(AnswerCriterionPOCO, AnswerPOCO, CriterionPOCO).join(AnswerPOCO, AnswerCriterionPOCO.answer == AnswerPOCO.id).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CriterionPOCO.id == critId).filter(AnswerPOCO.study_case == case).filter(AnswerPOCO.reviewer == user)
    
    result = query.one_or_none()
    
    if result is None:
        return
    
    ansCrit = result[0]
            
    updatestmt = update(AnswerCriterionPOCO).where(AnswerCriterionPOCO.answer == ansCrit.answer).where(AnswerCriterionPOCO.criterion == ansCrit.criterion).values(value=newValue)

    session.execute(updatestmt)

    session.commit()
   
    session.close()


def undo_all_but_one(user, case, critId, value, critType, engine):
    
    session = Session(engine)
    
    true_value = 1
    false_value = 2
    one_of_category = 2
    
    query = session.query(AnswerCriterionPOCO, AnswerPOCO, CriterionPOCO).join(AnswerPOCO, AnswerCriterionPOCO.answer == AnswerPOCO.id).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CriterionPOCO.type == critType).filter(CriterionPOCO.category == one_of_category).filter(AnswerPOCO.study_case == case).filter(AnswerPOCO.reviewer == user)
    ansCrit = query.all()
    criterionId = int(critId)
    # 0: answerCriterion, 1: answer, 2: criterion
    for ans in ansCrit:
        currentCritId = ans[2].id
        if (currentCritId == criterionId):
            updatestmt = update(AnswerCriterionPOCO).where(AnswerCriterionPOCO.answer == ans[1].id).where(AnswerCriterionPOCO.criterion == ans[2].id).values(value=true_value)
            session.execute(updatestmt)
        else:
            updatestmt = update(AnswerCriterionPOCO).where(AnswerCriterionPOCO.answer == ans[1].id).where(AnswerCriterionPOCO.criterion == ans[2].id).values(value=false_value)
            session.execute(updatestmt)
    
    session.commit()
    
    session.close()
    
    
#one-time data creation
def create_all_criterion(engine):
    
    # load delimiting words from config file
    delimitations = []
    with open(os.path.join(getcwd(), 'persistence', 'delimitations.txt'), encoding="utf-8") as delim_file:
        for l in delim_file:
            delimitations.append(l.removesuffix('\n'))
          
    critType = -1
    trust = False
    name = ""
    typeName = ""
    
    criteriaWB = load_workbook(filename = os.path.join(getcwd(), 'data', 'WOW.xlsx'))
    criteriaWS = criteriaWB.active
    
    session = Session(engine)
    
    for i in range (1, criteriaWS.max_row + 1):
        nameCell = criteriaWS.cell(row=i, column=1)
        categoryCell = criteriaWS.cell(row=i, column=2)
        trustCell = criteriaWS.cell(row=i, column=3)
        malCell = criteriaWS.cell(row=i, column=4)
        if nameCell.value in delimitations:
            
            # add trust criterion at the end of a type
            if critType > -1 and trust:
                newCrit = CriterionPOCO(typeName, "", critType, 3, False)
                newCrit.tutorial_path = ""
                session.add(newCrit)
            
            typeName = nameCell.value

            critType +=1
            categoryName = categoryCell.value
            trust = trustCell.value == "With Trust"
            if categoryName == "One Of":
                category = 2
            if categoryName == "Multiple":
                category = 1
           
        else:
            #dirty fix, remove later
            name = nameCell.value
            tutorial_name = name
            if tutorial_name.find(">") != -1:
                tutorial_name = name.replace(">", "gt ")
            tutorial_slide_path = os.path.join(getcwd(), 'data', 'tutorial_data', delimitations[critType], tutorial_name + '.png')
            
            malignancy = (malCell.value == "Malignant")
            newCrit = CriterionPOCO(name, tutorial_slide_path, critType, category, malignancy)
            newCrit.tutorial_path = tutorial_slide_path
            session.add(newCrit)
        
        # add trust criterion at the end if need be
        if (i == criteriaWS.max_row) and trust:
            newCrit = CriterionPOCO(typeName, "", critType, 3, False)
            newCrit.tutorial_path = ""
            session.add(newCrit) 
    
    session.commit()
    
    session.close()

def create_all_answer_to_criterion(engine):
        
    answers = get_all_answers(engine)
    criteria = get_all_criteria(engine)
    
    session = Session(engine)
    
    for i in range(len(answers)):
        for j in range(len(criteria)):
            newAnsCrit = AnswerCriterionPOCO(answers[i].id, criteria[j].id)
            session.add(newAnsCrit)

    session.commit()
    
    session.close()

def create_user_answer_to_criterion(userId, engine):
        
    answers = get_user_answers(userId, engine)
    criteria = get_all_criteria(engine)
    
    session = Session(engine)
    
    for i in range(len(answers)):
        for j in range(len(criteria)):
            newAnsCrit = AnswerCriterionPOCO(answers[i].id, criteria[j].id)
            session.add(newAnsCrit)
    
    session.commit()
    
    session.close()

def clear_all_criteria(engine):
    
    session = Session(engine)
    
    deleteStmt = delete(CriterionPOCO)
    
    session.execute(deleteStmt)
    session.commit()

    session.close()
    
