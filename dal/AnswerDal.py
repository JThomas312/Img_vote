#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 28 14:49:10 2025

@author: jacques
"""

#general imports
from sqlalchemy import update
from sqlalchemy import delete

from random import randint, shuffle

from sqlalchemy.orm import Session

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local imports
from img_vote.models.Enums import CriterionValue
from img_vote.models.DataModels import CaseAnsDataModel, CaseLearnDataModel, RemarksDataModel
from img_vote.models.POCO import ReviewerPOCO, CasePOCO, AnswerPOCO, AnswerCriterionPOCO, CriterionPOCO, CategoryPOCO, PrerequisitePOCO
        
#read-only
def get_answer_by_id(identifier, engine):
    
    session = Session(engine)
    
    try:
        answerPOCO = session.get(AnswerPOCO, identifier)

    finally:
        session.close()
    
    return answerPOCO

def get_all_answers(study_id, engine):
    
    session = Session(engine)
    
    try:
        answers = []
        
        cases = session.query(CasePOCO.id).filter(CasePOCO.study == study_id).all()
        caseIds = [x.id for x in cases]
        
        answersQuery = session.query(AnswerPOCO).filter(AnswerPOCO.study_case.in_(caseIds))
        answers = answersQuery.all()
    
    finally:
        session.close()

    return answers

def get_user_answers(user_id, engine):
    
    session = Session(engine)
    
    answers = []
    
    try:
        answersQuery = session.query(AnswerPOCO).filter(AnswerPOCO.reviewer == user_id)
        answersPOCO = answersQuery.all()
        
        for i in range(len(answersPOCO)):
            answers.append(answersPOCO[i]) #no time to investigate all(), mayhap later
    
    finally:
        session.close()

    return answers

def get_answer_name(user_id, caseId, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(AnswerPOCO.name).filter(AnswerPOCO.reviewer == user_id).filter(AnswerPOCO.study_case == caseId).one_or_none()
        answer = query.name
        
    finally:
        session.close()
    
    return answer

def get_case_by_answer_name(answerName, user_id, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(AnswerPOCO.study_case).filter(AnswerPOCO.name == answerName).filter(AnswerPOCO.reviewer == user_id)
        answer = query.one_or_none()
        if answer is None:
            answer = -1
        else:
            answer = answer[0]

    finally:
        session.close()
    
    return answer

def get_cases_and_answers(user_id, engine):
    
    session = Session(engine)
    
    casesAns = []
    
    try:    
        query = session.query(CasePOCO, AnswerPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).filter(AnswerPOCO.reviewer == user_id).order_by(CasePOCO.id)
        
        queriedAns = query.all()
        #0: Case, 1: Answer
        
        for i in range(len(queriedAns)):
            casesAns.append(CaseAnsDataModel(queriedAns[i][0].id, queriedAns[i][1].name, queriedAns[i][1].completed))
    
    finally:
        session.close()
        
    return casesAns

def get_answer_remarks(user_id, caseId, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(AnswerPOCO.remarks).filter(AnswerPOCO.reviewer == user_id).filter(AnswerPOCO.study_case == caseId)
        ans = query.one_or_none()
        if ans.remarks is None:
            answer = ''
        else:
            answer = ans.remarks
        
    finally:
        session.close()
    
    return answer

def get_all_remarks(study_id, engine):
    
    session = Session(engine)
    
    answer = []
    
    try:
        query = session.query(AnswerPOCO.remarks, ReviewerPOCO.name, CasePOCO.name).join(ReviewerPOCO, AnswerPOCO.reviewer == ReviewerPOCO.id).join(CasePOCO, AnswerPOCO.study_case == CasePOCO.id).filter(ReviewerPOCO.study == study_id).order_by(AnswerPOCO.study_case, AnswerPOCO.reviewer)
        queriedAns = query.all()
        for ans in queriedAns:
            #0:Answer, 1: Reviewer, 2: Case
            answer.append(RemarksDataModel(ans[2], ans[1], ans[0]))
        
    finally:
        session.close()
        
    return answer

def get_cases_and_learn(user_id, engine):
    
    session = Session(engine)
    
    casesAns = []
    
    try:    
        query = session.query(CasePOCO, AnswerPOCO, AnswerCriterionPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).filter(AnswerPOCO.reviewer == user_id).order_by(CasePOCO.id)
        
        queriedAns = query.all()
        #0: Case, 1: Answer, 2: AnswerCriterion
        
        for i in range(len(queriedAns)):
            if queriedAns[i][0].gold_standard == queriedAns[i][2].criterion:
                casesAns.append(CaseLearnDataModel(queriedAns[i][0].id, queriedAns[i][1].name, queriedAns[i][2].value == CriterionValue.true.value))
    
    finally:
        session.close()
        
    return casesAns

def get_answer_to_case(user_id, caseId, engine):
    
    session = Session(engine)
    
    answer = ''
    
    try:
        query = session.query(AnswerPOCO, AnswerCriterionPOCO, CriterionPOCO, CategoryPOCO).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).join(CategoryPOCO, CriterionPOCO.category == CategoryPOCO.id).filter(AnswerPOCO.reviewer == user_id).filter(AnswerPOCO.study_case == caseId).filter(CategoryPOCO.has_gold_standard).filter(AnswerCriterionPOCO.value == CriterionValue.true.value)
        ans = query.one_or_none()
        
        #0: answer, 1: answerCriterion, 2: criterion, 3: category
        
        if ans is None:
            answer = 'unanswered'
        else:
            answer = ans[2].name
            
    finally:
        session.close()
        
    return answer

#CRUD
def save_remarks(user_id, caseId, value, engine):
    
    session = Session(engine)
    
    try:
        updatestmt = update(AnswerPOCO).where(AnswerPOCO.reviewer == user_id).where(AnswerPOCO.study_case == caseId).values(remarks=value)
        session.execute(updatestmt)
        session.commit()
        
    finally:
        session.close()

def update_optional_answers(user_id, case, criterionId, category, engine):
    
    session = Session(engine)
    
    try:
        if category is not None:
            
            query = session.query(AnswerCriterionPOCO, AnswerPOCO, CriterionPOCO).join(AnswerPOCO, AnswerCriterionPOCO.answer == AnswerPOCO.id).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).filter(CriterionPOCO.category == category).filter(AnswerPOCO.reviewer == user_id).filter(AnswerPOCO.study_case == case).filter(CriterionPOCO.is_trust == False)
            ansCrit = query.all()
            # 0: answerCriterion, 1: answer, 2: criterion
            idsLeft = [ans[2].id for ans in ansCrit]
            
        else:
            idsLeft = [criterionId]
            
        answer_id = session.query(AnswerPOCO).filter(AnswerPOCO.study_case == case, AnswerPOCO.reviewer == user_id).one_or_none().id
        
        
        while(len(idsLeft) > 0):
            
            currentId = idsLeft.pop(0)
            
            relevant_categories_query = session.query(CategoryPOCO, PrerequisitePOCO).join(CategoryPOCO, PrerequisitePOCO.category == CategoryPOCO.id).filter(PrerequisitePOCO.criterion == currentId)
            relevant_categories = relevant_categories_query.all()
            
            #0: category, 1: prerequisite
            for category in relevant_categories:
                prerequisites_fulfilled_query = session.query(AnswerCriterionPOCO, PrerequisitePOCO).join(PrerequisitePOCO, AnswerCriterionPOCO.criterion == PrerequisitePOCO.criterion).filter(AnswerCriterionPOCO.answer == answer_id).filter(PrerequisitePOCO.category == category[0].id).filter(AnswerCriterionPOCO.value == CriterionValue.true.value)
                prerequisites_fulfilled = session.query(prerequisites_fulfilled_query.exists()).scalar()
                
                if not prerequisites_fulfilled:
                    
                    criteria_to_uncheck_query = session.query(CriterionPOCO).filter(CriterionPOCO.category == category[0].id)
                    criteria_to_uncheck = criteria_to_uncheck_query.all()
                    criteria_to_uncheck_ids = [crit.id for crit in criteria_to_uncheck]
                    
                    idsLeft.extend(criteria_to_uncheck_ids)
                    
                    updatestmt = update(AnswerCriterionPOCO).filter(AnswerCriterionPOCO.answer == answer_id).filter(AnswerCriterionPOCO.criterion.in_(criteria_to_uncheck_ids)).values(value=CriterionValue.unanswered.value)
                    
                    session.execute(updatestmt)
                    session.commit()
                    
    
    finally:
        session.close()

def update_answer_status(user_id, caseId, done, engine):
    
    session = Session(engine)
    
    try:
        ans = session.query(AnswerPOCO).filter(AnswerPOCO.reviewer == user_id).filter(AnswerPOCO.study_case == caseId).one_or_none()
    
        databaseUpdated = False
        
        if ans is not None and (ans.completed != done):
            updatestmt = update(AnswerPOCO).where(AnswerPOCO.reviewer == user_id).where(AnswerPOCO.study_case == caseId).values(completed=done)
            session.execute(updatestmt)
            session.commit()
            session.close()
            databaseUpdated = True
            #returns wether the database was updated

    finally:    
        session.close()

    return databaseUpdated

#one-time data manipulation
def create_all_answers(study_id, rev_per_case, engine):
    
    session = Session(engine)
    
    try:
        # if any answer already exists for the study, it means this function has already been called, do not do anything
        failsafe_query = session.query(AnswerPOCO, CasePOCO).join(CasePOCO, AnswerPOCO.study_case == CasePOCO.id).filter(CasePOCO.study == study_id)
        if session.query(failsafe_query.exists()).scalar():
            return 'answers already exist'
        
        cases = session.query(CasePOCO.id).filter(CasePOCO.study == study_id).all()
        nb_cases = len(cases)
        full_reviewers = session.query(ReviewerPOCO.id).filter(ReviewerPOCO.study == study_id).filter(ReviewerPOCO.admin == False).filter(ReviewerPOCO.full_review == True).all()
    
        
        for full_reviewer in full_reviewers:
            for case in cases:
                newAns = AnswerPOCO(case.id, full_reviewer.id)
                session.add(newAns)
            
        standard_reviewers = session.query(ReviewerPOCO.id).filter(ReviewerPOCO.study == study_id).filter(ReviewerPOCO.admin == False).filter(ReviewerPOCO.full_review == False).all()
    
        if len(standard_reviewers) > 0:    
    
            ahead_group = []
            behind_group = [rev.id for rev in standard_reviewers]
            
            for i in range(nb_cases):
                already_attributed = []
                for j in range(rev_per_case):
                    k = randint(0, len(behind_group) - 1)
                    while (behind_group[k] in already_attributed):
                        k = randint(0, len(behind_group) - 1)
                    already_attributed.append(behind_group[k])
                    newAns = AnswerPOCO(cases[i].id, behind_group[k])
                    session.add(newAns)
                    ahead_group.append(behind_group[k])
                    behind_group.pop(k)
                    if len(behind_group) == 0:
                        behind_group = ahead_group.copy()
                        ahead_group = []
        
        total_reviewers = []
        total_reviewers.extend(full_reviewers)
        total_reviewers.extend(standard_reviewers)
        
        
        for reviewer in total_reviewers:
            
            counter = 0
            assigned_cases = session.query(AnswerPOCO.study_case).filter(AnswerPOCO.reviewer == reviewer.id).all()
            shuffle(assigned_cases)
            
            for i in range(len(assigned_cases)):
                name = str(i + 1)
                updateans = update(AnswerPOCO).where(AnswerPOCO.reviewer == reviewer.id).where(AnswerPOCO.study_case == assigned_cases[i].study_case).values(name=name)
                session.execute(updateans)
                counter += 1
            
            updatestmt = update(ReviewerPOCO).where(ReviewerPOCO.id == reviewer.id).values(remaining_cases=counter)
                
            session.execute(updatestmt)
    
        session.commit()
    
    except Exception as e:
        caseIds = [x.id for x in cases]
        deletestmt = delete(AnswerPOCO).where(AnswerPOCO.study_case.in_(caseIds))
        session.execute(deletestmt)
        raise e
    
    finally:
        session.close()
    
    return None

def create_user_answers(study_id, user_id, case_per_rev, engine):
    
    session = Session(engine)
    
    try:    
        cases = session.query(CasePOCO.id).filter(CasePOCO.study == study_id).all()
        
        caseIds = [i.id for i in cases]
        
        shuffle(caseIds)
        
        
        for i in range(case_per_rev):
            name = str(i + 1)
            newAns = AnswerPOCO(caseIds[i], user_id, name)
            session.add(newAns)
                
        updatestmt = update(ReviewerPOCO).where(ReviewerPOCO.id == user_id).values(remaining_cases=case_per_rev)
        session.execute(updatestmt)    
        session.commit()

    finally:
        session.close()

def clear_all_answers(study_id, engine):
    
    session = Session(engine)
    
    try:
        ans = session.query(AnswerPOCO.id).join(ReviewerPOCO, AnswerPOCO.reviewer == ReviewerPOCO.id).filter(ReviewerPOCO.study == study_id).all()
        
        ans = [x.id for x in ans]
        
        deleteStmt = delete(AnswerCriterionPOCO).where(AnswerCriterionPOCO.answer.in_(ans))
        
        session.execute(deleteStmt)
        session.commit()
        
        deleteStmt = delete(AnswerPOCO).where(AnswerPOCO.id.in_(ans))
        
        session.execute(deleteStmt)
        session.commit()
        
    finally:
        session.close()