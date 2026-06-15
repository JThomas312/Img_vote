#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 28 16:15:24 2025

@author: jacques
"""

#general imports
import os.path

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
from img_vote.Models.DataModels import CriterionDataModel, CriterionForCaseDataModel, DiagnosisDataModel
from img_vote.Models.POCO import CasePOCO, AnswerPOCO, CriterionPOCO, AnswerCriterionPOCO, CategoryPOCO, PrerequisitePOCO
from img_vote.dal.AnswerDal import get_all_answers
from img_vote.dal.AnswerDal import get_user_answers

     
#read-only
def get_criterion_by_id(identifier, engine):
    
    session = Session(engine)
    
    try:
        criterionPOCO = session.get(CriterionPOCO, identifier)
        
        criterion = CriterionDataModel(criterionPOCO.id, criterionPOCO.name, criterionPOCO.tutorial_path, criterionPOCO.category, criterionPOCO.is_trust)
        
    finally:        
        session.close()
    
    return criterion

def is_answer_done(userId, caseId, engine):
    
    session = Session(engine)
    
    #criterion category 2 is one of
    yes_no_category = 1
    one_of_category = 2
    numerical_value_category = 3
    unanswered_value = -1
    unanswered_trust_value = 0
    true_value = 1
    
    try:
        # prefiltered query with all necessary joins
        query0 = session.query(CasePOCO, AnswerPOCO, CriterionPOCO, AnswerCriterionPOCO, CategoryPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).join(CategoryPOCO, CriterionPOCO.category == CategoryPOCO.id).filter(CasePOCO.id == caseId).filter(AnswerPOCO.reviewer == userId)
        
        categories = session.query(CategoryPOCO).all()
        #0: case, 1:answer, 2: criterion, 3:answercriterion, 4: category
        for category in categories:
            
            mandatory = True
            
            if category.optional:
                mandatory = False
                prerequisites = session.query(PrerequisitePOCO.criterion).filter(PrerequisitePOCO.category == category.id).all()
                #check if all prerequisites are checked
                for prerequisite in prerequisites:
                    prerequisitesQuery = query0.filter(CriterionPOCO.id == prerequisite.criterion).filter(AnswerCriterionPOCO.value == true_value)
                    if session.query(prerequisitesQuery.exists()).scalar():
                        mandatory = True
                        
            if mandatory:
                if category.type == yes_no_category or category.type == numerical_value_category:
                    #check if any criterion is still unanswered
                    unanswered_query = query0.filter(CategoryPOCO.id == category.id).filter(AnswerCriterionPOCO.value == unanswered_value).filter(CriterionPOCO.is_trust == False)
                    if session.query(unanswered_query.exists()).scalar():
                        return False
                
                if category.type == one_of_category:
                    #check if any criterion has been chosen
                    answered_query = query0.filter(CategoryPOCO.id == category.id).filter(AnswerCriterionPOCO.value == true_value).filter(CriterionPOCO.is_trust == False)
                    if not session.query(answered_query.exists()).scalar():
                        return False
                
                if category.has_trust:
                    #check if trust criterion was left unanswered
                    trust_query1 = query0.filter(CategoryPOCO.id == category.id).filter(AnswerCriterionPOCO.value == unanswered_trust_value).filter(CriterionPOCO.is_trust == True)
                    trust_query2 = query0.filter(CategoryPOCO.id == category.id).filter(AnswerCriterionPOCO.value == unanswered_value).filter(CriterionPOCO.is_trust == True)
                    exists1 = session.query(trust_query1.exists()).scalar()
                    exists2 = session.query(trust_query2.exists()).scalar()
                    if exists1 or exists2:
                        return False
    
    finally:
        session.close()        
    
    return True

def get_criteria_for_case(userId, caseId, catId, engine):

    session = Session(engine)

    try:
        query = session.query(CasePOCO, AnswerPOCO, CriterionPOCO, AnswerCriterionPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CriterionPOCO.category == catId).filter(AnswerPOCO.reviewer == userId).filter(CasePOCO.id == caseId).order_by(CriterionPOCO.category, CriterionPOCO.id)
    
        queriedAnswers = query.all()
    
    
        answer = []
    
        # 0: Case, 1: Answer, 2: Criterion, 3: AnswerCriterion
        for queriedAnswer in queriedAnswers:
            answer.append(CriterionForCaseDataModel(queriedAnswer[2].id, queriedAnswer[2].name, queriedAnswer[3].value, queriedAnswer[2].category, queriedAnswer[2].is_trust, queriedAnswer[2].tutorial_path))
    
    finally:
        session.close()

    return answer


def get_diagnosis_for_case(userId, caseId, engine):
    
    session = Session(engine)
    #criterion type 2 is diagnosis
    diagnosis_type = 2    
    
    try:
        query = session.query(CasePOCO, AnswerPOCO, CriterionPOCO, AnswerCriterionPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CasePOCO.id == caseId).filter(AnswerPOCO.reviewer == userId).filter(CriterionPOCO.type == diagnosis_type).order_by(CriterionPOCO.id)
    
        queriedAnswer = query.all()
        
        #0: Case, 1: Answer, 2: Criterion, 3: AnswerCriterion   
        
        answer = CriterionForCaseDataModel(queriedAnswer[0][0].path)
        
        for i in range(len(queriedAnswer)):
            answer.criteria.append((queriedAnswer[i][2].type, queriedAnswer[i][2].name, queriedAnswer[i][3].value, queriedAnswer[i][2].tutorial_path, queriedAnswer[i][2].id))
    
    finally:
        session.close()
    
    return answer

def get_all_criteria(study_id, engine):
    
    session = Session(engine)

    try:
        criteria = []
        
        categories = session.query(CategoryPOCO.id).filter(CategoryPOCO.study == study_id).all()
        categoryIds = [x.id for x in categories]
        
        criteriaQuery = session.query(CriterionPOCO).filter(CriterionPOCO.category.in_(categoryIds))
        criteria = criteriaQuery.all()

    finally:
        session.close()

    return criteria

def get_all_criteria_no_diagnosis(engine):
    
    session = Session(engine)
    
    try:
        diagnosis_type = 0
        trust_category = 3
        
        query = session.query(CriterionPOCO).filter(CriterionPOCO.type != diagnosis_type).filter(CriterionPOCO.category != trust_category)
        ans = query.all()
        
        critNoDiag = []
        
        for i in range(len(ans)):
            critNoDiag.append(DiagnosisDataModel(ans[i].id, ans[i].name))
    
    finally:
        session.close()
    
    return critNoDiag

def get_gold_standard_criteria(study_id, engine):
    
    session = Session(engine)

    try:
        query = session.query(CriterionPOCO.id, CriterionPOCO.name).join(CategoryPOCO, CriterionPOCO.category == CategoryPOCO.id).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.has_gold_standard == True)
        answer = query.all()
        
    finally:
        session.close()
    
    return answer

def get_gold_standard_dict(study_id, engine):
    
    session = Session(engine)

    try:
        query = session.query(CriterionPOCO.id, CriterionPOCO.name).join(CategoryPOCO, CriterionPOCO.category == CategoryPOCO.id).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.has_gold_standard == True)
        criteria = query.all()
        
        criteriaDict = dict()
     
        for criterion in criteria:
            criteriaDict[criterion[1]] = criterion[0]
        
    finally:
        session.close()
    
    return criteriaDict

#CRUD
def create_criterion(name, tutorial_path, category, is_trust, malignancy, engine):
    
    session = Session(engine)
    
    try:
        newCrit = CriterionPOCO(name, tutorial_path, category, is_trust, malignancy)
        if (newCrit.tutorial_path == None):
            newCrit.tutorial_path = tutorial_path
            
        session.add(newCrit)
        session.commit()
        
        answer = newCrit.id
    
    finally:        
        session.close()
        
    return answer
    
def update_criterion(crit_id, crit_name, crit_malignancy, engine):
    
    session = Session(engine)
    
    try:
        updatestmt = update(CriterionPOCO).where(CriterionPOCO.id == crit_id).values(name=crit_name, malignancy=crit_malignancy)
    
        session.execute(updatestmt)
    
        session.commit()
    
    finally:        
        session.close()
    
def update_criterion_malignancy(crit_id, crit_malignancy, engine):
    
    session = Session(engine)
    
    try:
        updatestmt = update(CriterionPOCO).where(CriterionPOCO.id == crit_id).values(malignancy=crit_malignancy)
    
        session.execute(updatestmt)
    
        session.commit()
    
    finally:        
        session.close()

def update_criteria_path(study_id, path, engine):
    
    session = Session(engine)
    
    try:    
        no_tutorial = session.query(CriterionPOCO.id).join(CategoryPOCO, CriterionPOCO.category == CategoryPOCO.id).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.has_tutorial == False).all()
        
        for no_tuto in no_tutorial:
        
            updatestmt = update(CriterionPOCO).where(CriterionPOCO.id == no_tuto.id).values(tutorial_path='')
            
            session.execute(updatestmt)
        
        has_tutorial = session.query(CriterionPOCO, CategoryPOCO).join(CategoryPOCO, CriterionPOCO.category == CategoryPOCO.id).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.has_tutorial == True).all()
        
        #0: Criterion, 1: Category
        
        for answer in has_tutorial:
            tutorial_path = os.path.join(path, answer[1].name, answer[0].name)
            updatestmt = update(CriterionPOCO).where(CriterionPOCO.id == answer[0].id).values(tutorial_path=tutorial_path)
            session.execute(updatestmt)
        
        session.commit()
        
    finally:
        session.close()

def clear_malignant_criteria_in_non_malignant_category(study_id, engine):
    
    session = Session(engine)
    
    try:
        
        query = session.query(CriterionPOCO, CategoryPOCO).join(CategoryPOCO, CriterionPOCO.category == CategoryPOCO.id).filter(CategoryPOCO.study == study_id).filter(CriterionPOCO.malignancy == True).filter(CategoryPOCO.has_malignancy == False)
        queriedAnswer = query.all()
        
        #0: criterion, 1: category
        
        for ans in queriedAnswer:
            updatestmt = update(CriterionPOCO).where(CriterionPOCO.id == ans[0].id).values(malignancy=False)
            session.execute(updatestmt)
        
        session.commit()
        
    finally:
        session.close()

def erase_criterion(identifier, engine):
    
    session = Session(engine)
    
    try:
        deleteStmt = delete(CriterionPOCO).where(CriterionPOCO.id == identifier)
        
        session.execute(deleteStmt)
        session.commit()
        
    finally:
        session.close()
    
def erase_category_criteria(identifier, engine):
    
    session = Session(engine)
    
    try:
        deleteStmt = delete(CriterionPOCO).where(CriterionPOCO.category == identifier)
        
        session.execute(deleteStmt)
        session.commit()

    finally:    
        session.close()

def create_answer_to_criterion(answer, criterion, engine):
    
    session = Session(engine)
    
    try:
        newAnsCrit = AnswerCriterionPOCO(answer, criterion)
        session.add(newAnsCrit)
        session.commit()

    finally:        
        session.close()

def save_Criterion(user, case, critName, newValue, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(AnswerCriterionPOCO, AnswerPOCO, CriterionPOCO).join(AnswerPOCO, AnswerCriterionPOCO.answer == AnswerPOCO.id).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CriterionPOCO.name == critName).filter(AnswerPOCO.study_case == case).filter(AnswerPOCO.reviewer == user)
        ansCrit = query.one_or_none()[0]
        updatestmt = update(AnswerCriterionPOCO).where(AnswerCriterionPOCO.answer == ansCrit.answer).where(AnswerCriterionPOCO.criterion == ansCrit.criterion).values(value=newValue)
    
        session.execute(updatestmt)
    
        session.commit()
    
    finally:        
        session.close()

def safeguard_Criterion(user, case, critId, newValue, engine):
    
    session = Session(engine)
     
    try:
        query = session.query(AnswerCriterionPOCO, AnswerPOCO, CriterionPOCO).join(AnswerPOCO, AnswerCriterionPOCO.answer == AnswerPOCO.id).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CriterionPOCO.id == critId).filter(AnswerPOCO.study_case == case).filter(AnswerPOCO.reviewer == user)
        
        result = query.one_or_none()
        
        if result is None:
            return
        
        ansCrit = result[0]
                
        updatestmt = update(AnswerCriterionPOCO).where(AnswerCriterionPOCO.answer == ansCrit.answer).where(AnswerCriterionPOCO.criterion == ansCrit.criterion).values(value=newValue)
    
        session.execute(updatestmt)
    
        session.commit()
        
    finally:
        session.close()


def undo_all_but_one(userId, case, criterionId, value, category, engine):
    
    session = Session(engine)
    
    try:
        false_value = 0
        
        query = session.query(AnswerCriterionPOCO, AnswerPOCO, CriterionPOCO).join(AnswerPOCO, AnswerCriterionPOCO.answer == AnswerPOCO.id).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CriterionPOCO.category == category).filter(AnswerPOCO.reviewer == userId).filter(AnswerPOCO.study_case == case).filter(CriterionPOCO.id != criterionId).filter(CriterionPOCO.is_trust == False)
        ansCrit = query.all()
    
        # 0: answerCriterion, 1: answer, 2: criterion
        ansId = ansCrit[0][1].id
        
        for ans in ansCrit:
            
            updatestmt = update(AnswerCriterionPOCO).where(AnswerCriterionPOCO.answer == ansId).where(AnswerCriterionPOCO.criterion == ans[2].id).values(value=false_value)
            session.execute(updatestmt)
        
        
        updatestmt = update(AnswerCriterionPOCO).where(AnswerCriterionPOCO.answer == ansId).where(AnswerCriterionPOCO.criterion == criterionId).values(value=value)
        session.execute(updatestmt)
        
        session.commit()
     
    finally:
        session.close()
    
    
#one-time data creation
def create_trust_criteria(study_id, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO).filter(CategoryPOCO.has_trust == True).filter(CategoryPOCO.study == study_id).order_by(CategoryPOCO.id)
        
        answer = query.all()
        
        for ans in answer:
            newCrit = CriterionPOCO(ans.name + '_trust_scale', '', ans.id, True, False)
                
            if (newCrit.tutorial_path == None):
                newCrit.tutorial_path = ''
                
            session.add(newCrit)
            
        session.commit()
        
    finally:
        session.close()

def create_na_criteria(study_id, engine):
    
    session = Session(engine)
    
    one_of_category = 2
    
    try:
        query = session.query(CategoryPOCO).filter(CategoryPOCO.has_na == True).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.type == one_of_category).order_by(CategoryPOCO.id)
        
        answer = query.all()
        
        for ans in answer:
            newCrit = CriterionPOCO('na', '', ans.id, False, False)
                
            if (newCrit.tutorial_path == None):
                newCrit.tutorial_path = ''
                
            session.add(newCrit)
            
        session.commit()
        
    finally:
        session.close()

def remove_trust_criteria(study_id, engine):
    
    session = Session(engine)
    
    try:
        relevant_categories = session.query(CategoryPOCO.id).filter(CategoryPOCO.study == study_id).all()
        relevant_ids = [x.id for x in relevant_categories]
        deleteStmt = delete(CriterionPOCO).where(CriterionPOCO.category.in_(relevant_ids)).where(CriterionPOCO.is_trust == True)
        
        session.execute(deleteStmt)
        session.commit()
        
    finally:
        session.close()

def remove_na_criteria(study_id, engine):
    
    session = Session(engine)
    
    try:
        relevant_categories = session.query(CategoryPOCO.id).filter(CategoryPOCO.study == study_id).all()
        relevant_ids = [x.id for x in relevant_categories]
        deleteStmt = delete(CriterionPOCO).where(CriterionPOCO.category.in_(relevant_ids)).where(CriterionPOCO.name == 'na')
        
        session.execute(deleteStmt)
        session.commit()
        
    finally:
        session.close()

def create_all_answer_to_criterion(study_id, engine):
        
    answers = get_all_answers(study_id, engine)
    criteria = get_all_criteria(study_id, engine)
    
    session = Session(engine)
    
    try:
        for i in range(len(answers)):
            for j in range(len(criteria)):
                newAnsCrit = AnswerCriterionPOCO(answers[i].id, criteria[j].id)
                session.add(newAnsCrit)
    
        session.commit()

    finally:
        session.close()

def create_user_answer_to_criterion(study_id, userId, engine):
        
    answers = get_user_answers(userId, engine)
    criteria = get_all_criteria(study_id, engine)
    
    session = Session(engine)
    
    try:
        for i in range(len(answers)):
            for j in range(len(criteria)):
                newAnsCrit = AnswerCriterionPOCO(answers[i].id, criteria[j].id)
                session.add(newAnsCrit)
        
        session.commit()

    finally:        
        session.close()

def clear_all_criteria(study_id, engine):
    
    session = Session(engine)
    
    try:
        
        categories = session.query(CategoryPOCO.id).filter(CategoryPOCO.study == study_id)
        categoryIds = [x.id for x in categories]
        
        deleteStmt = delete(CriterionPOCO).where(CriterionPOCO.category.in_(categoryIds))
        
        session.execute(deleteStmt)
        session.commit()
    
    finally:
        session.close()
    
