#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 28 14:49:10 2025

@author: jacques
"""

#general imports
from sqlalchemy import select
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
from img_vote.Models.Enums import CriterionValue
from img_vote.Models.DataModels import CaseAnsDataModel, CaseLearnDataModel, RemarksDataModel
from img_vote.Models.POCO import ReviewerPOCO, CasePOCO, AnswerPOCO, AnswerCriterionPOCO, CriterionPOCO, CategoryPOCO, PrerequisitePOCO
        
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

def get_user_answers(userId, engine):
    
    session = Session(engine)
    
    answers = []
    
    try:
        answersQuery = select(AnswerPOCO).filter(AnswerPOCO.reviewer == userId)
        answersPOCO = session.execute(answersQuery).all()
        
        for i in range(len(answersPOCO)):
            answers.append(answersPOCO[i][0]) #no time to investigate all(), mayhap later
    
    finally:
        session.close()

    return answers

def get_answer_name(userId, caseId, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(AnswerPOCO.name).filter(AnswerPOCO.reviewer == userId).filter(AnswerPOCO.study_case == caseId).one_or_none()
        answer = query.name
        
    finally:
        session.close()
    
    return answer

def get_case_by_answer_name(answerName, userId, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(AnswerPOCO.study_case).filter(AnswerPOCO.name == answerName).filter(AnswerPOCO.reviewer == userId)
        answer = query.one_or_none()
        if answer == None:
            answer = -1
        else:
            answer = answer[0]

    finally:
        session.close()
    
    return answer

def get_cases_and_answers(userId, engine):
    
    session = Session(engine)
    
    casesAns = []
    
    try:    
        query = session.query(CasePOCO, AnswerPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).filter(AnswerPOCO.reviewer == userId).order_by(CasePOCO.id)
        
        queriedAns = query.all()
        #0: Case, 1: Answer
        
        for i in range(len(queriedAns)):
            casesAns.append(CaseAnsDataModel(queriedAns[i][0].id, queriedAns[i][1].name, queriedAns[i][1].completed))
    
    finally:
        session.close()
        
    return casesAns

def get_answer_remarks(userId, caseId, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(AnswerPOCO.remarks).filter(AnswerPOCO.reviewer == userId).filter(AnswerPOCO.study_case == caseId)
        ans = query.one_or_none()
        if ans.remarks == None:
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

def get_cases_and_learn(userId, engine):
    
    session = Session(engine)
    
    casesAns = []
    
    try:    
        query = session.query(CasePOCO, AnswerPOCO, AnswerCriterionPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).filter(AnswerPOCO.reviewer == userId).order_by(CasePOCO.id)
        
        queriedAns = query.all()
        #0: Case, 1: Answer, 2: AnswerCriterion
        
        for i in range(len(queriedAns)):
            if queriedAns[i][0].gold_standard == queriedAns[i][2].criterion:
                casesAns.append(CaseLearnDataModel(queriedAns[i][0].id, queriedAns[i][1].name, queriedAns[i][2].value == CriterionValue.true.value))
    
    finally:
        session.close()
        
    return casesAns

def get_answer_to_case(userId, caseId, engine):
    
    session = Session(engine)
    
    answer = ''
    
    try:
        query = session.query(AnswerPOCO, AnswerCriterionPOCO, CriterionPOCO, CategoryPOCO).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).join(CategoryPOCO, CriterionPOCO.category == CategoryPOCO.id).filter(AnswerPOCO.reviewer == userId).filter(AnswerPOCO.study_case == caseId).filter(CategoryPOCO.has_gold_standard).filter(AnswerCriterionPOCO.value == CriterionValue.true.value)
        ans = query.one_or_none()
        
        #0: answer, 1: answerCriterion, 2: criterion, 3: category
        
        if ans == None:
            answer = 'unanswered'
        else:
            answer = ans[2].name
            
    finally:
        session.close()
        
    return answer

#CRUD
def save_remarks(userId, caseId, value, engine):
    
    session = Session(engine)
    
    try:
        updatestmt = update(AnswerPOCO).where(AnswerPOCO.reviewer == userId).where(AnswerPOCO.study_case == caseId).values(remarks=value)
        session.execute(updatestmt)
        session.commit()
        
    finally:
        session.close()

def update_answer_status(userId, caseId, done, engine):
    
    session = Session(engine)
    
    try:
        ans = session.query(AnswerPOCO).filter(AnswerPOCO.reviewer == userId).filter(AnswerPOCO.study_case == caseId).one_or_none()
    
        databaseUpdated = False
        
        if ans != None and (ans.completed != done):
            updatestmt = update(AnswerPOCO).where(AnswerPOCO.reviewer == userId).where(AnswerPOCO.study_case == caseId).values(completed=done)
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

def create_user_answers(study_id, userId, case_per_rev, engine):
    
    session = Session(engine)
    
    try:    
        cases = session.query(CasePOCO.id).filter(CasePOCO.study == study_id).all()
        
        caseIds = [i.id for i in cases]
        
        shuffle(caseIds)
        
        
        for i in range(case_per_rev):
            name = str(i + 1)
            newAns = AnswerPOCO(caseIds[i], userId, name)
            session.add(newAns)
                
        updatestmt = update(ReviewerPOCO).where(ReviewerPOCO.id == userId).values(remaining_cases=case_per_rev)
        session.execute(updatestmt)    
        session.commit()

    finally:
        session.close()

def erase_optional_answers(study_id, engine):
    
    session = Session(engine)
    
    try:
        #get all optional categories
        querycat = session.query(CategoryPOCO.id).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.optional == True)
        cats = querycat.all()
        
        categories = []
        
        for cat in cats:
            querypre = session.query(CriterionPOCO.id).join(PrerequisitePOCO, CriterionPOCO.id == PrerequisitePOCO.criterion).filter(PrerequisitePOCO.category == cat.id)
            prerequisites = querypre.all()
            querycrit = session.query(CriterionPOCO.id).filter(CriterionPOCO.category == cat.id)
            criteria = querycrit.all()
            #0: category, 1: prerequisites, 2: criteria
            #I don't actually need the category here it simply makes the data more human readable just incase
            categories.append((cat, prerequisites, criteria))
        
        #get all answers with optional criterion answered
        queryans = session.query(AnswerPOCO.id).join(AnswerCriterionPOCO, AnswerPOCO.id == AnswerCriterionPOCO.answer).join(CriterionPOCO, AnswerCriterionPOCO.criterion == CriterionPOCO.id).join(CategoryPOCO, CriterionPOCO.category == CategoryPOCO.id).filter(CategoryPOCO.optional == True).filter(AnswerCriterionPOCO.value != CriterionValue.unanswered.value).group_by(AnswerPOCO.id)
        answers = queryans.all()
        
        for answer in answers:
            for category in categories:
                prerequistes = [x.id for x in category[1]]
                criteria = [y.id for y in category[2]]
                prerequery = session.query(AnswerCriterionPOCO).join(AnswerPOCO, AnswerCriterionPOCO.answer == AnswerPOCO.id).filter(AnswerCriterionPOCO.answer == answer.id).filter(AnswerCriterionPOCO.value == CriterionValue.true.value).filter(AnswerCriterionPOCO.criterion.in_(prerequistes))
                ok_prerequisites = session.query(prerequery.exists()).scalar()
                if not ok_prerequisites:
                    updatestmt = update(AnswerCriterionPOCO).where(AnswerCriterionPOCO.answer == answer.id).where(AnswerCriterionPOCO.criterion.in_(criteria)).values(value=CriterionValue.unanswered.value)
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