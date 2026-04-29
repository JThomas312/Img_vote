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
from img_vote.Models.DataModels import CaseAnsDataModel
from img_vote.Models.POCO import ReviewerPOCO, CasePOCO, AnswerPOCO
        
#read-only
def get_answer_by_id(identifier, engine):
    
    session = Session(engine)
    
    try:
        answerPOCO = session.get(AnswerPOCO, identifier)

    finally:
        session.close()
    
    return answerPOCO

def get_all_answers(engine):
    
    session = Session(engine)
    
    try:
        answers = []
        
        answersQuery = select(AnswerPOCO)
        answersPOCO = session.execute(answersQuery).all()
        
        for i in range(len(answersPOCO)):
            answers.append(answersPOCO[i][0]) #no time to investigate all(), mayhap later
    
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

#CRUD
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

#one-time data creation
def create_all_answers(rev_per_case, engine):
    
    session = Session(engine)
    
    try:
        cases = session.query(CasePOCO.id).all()
        nb_cases = len(cases)
        full_reviewers = session.query(ReviewerPOCO.id).filter(ReviewerPOCO.admin == False).filter(ReviewerPOCO.full_review == True).all()
    
        
        for full_reviewer in full_reviewers:
            for case in cases:
                newAns = AnswerPOCO(case.id, full_reviewer.id)
                session.add(newAns)
            
        standard_reviewers = session.query(ReviewerPOCO.id).filter(ReviewerPOCO.admin == False).filter(ReviewerPOCO.full_review == False).all()
    
        if len(standard_reviewers) > 0:    
    
            ahead_group = []
            behind_group = [rev.id for rev in standard_reviewers]
            
            for i in range(nb_cases):
                for j in range(rev_per_case):
                    k = randint(0, len(behind_group) - 1)
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
        deletestmt = delete(AnswerPOCO)
        session.execute(deletestmt)
        raise e
    
    finally:
        session.close()

def create_user_answers(userId, case_per_rev, engine):
    
    session = Session(engine)
    
    try:    
        cases = session.query(CasePOCO.id).all()
        
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