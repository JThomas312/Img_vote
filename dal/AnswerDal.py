#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 28 14:49:10 2025

@author: jacques
"""

#general imports
from sqlalchemy import select
from sqlalchemy import update

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

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
    
    answerPOCO = session.get(AnswerPOCO, identifier)
        
    session.close()
    
    return answerPOCO

def get_all_answers(engine):
    
    session = Session(engine)
    
    answers = []
    
    answersQuery = select(AnswerPOCO)
    answersPOCO = session.execute(answersQuery).all()
    
    for i in range(len(answersPOCO)):
        answers.append(answersPOCO[i][0]) #no time to investigate all(), mayhap later

    session.close()

    return answers

def get_user_answers(userId, engine):
    
    session = Session(engine)
    
    answers = []
    
    answersQuery = select(AnswerPOCO).filter(AnswerPOCO.reviewer == userId)
    answersPOCO = session.execute(answersQuery).all()
    
    for i in range(len(answersPOCO)):
        answers.append(answersPOCO[i][0]) #no time to investigate all(), mayhap later

    session.close()

    return answers

def get_cases_and_answers(userId, engine):
    
    session = Session(engine)
    
    casesAns = []
    
    query = session.query(CasePOCO, AnswerPOCO).join(AnswerPOCO, CasePOCO.id == AnswerPOCO.study_case).filter(AnswerPOCO.reviewer == userId).order_by(CasePOCO.id)
    
    queriedAns = query.all()
    #0: Case, 1: Answer
    
    for i in range(len(queriedAns)):
        casesAns.append(CaseAnsDataModel(queriedAns[i][0].id, queriedAns[i][0].name, queriedAns[i][1].completed))
        
    session.close()
    
    return casesAns

#CRUD

def mark_answer_done(userId, caseId, engine):
    
    session = Session(engine)
    
    ans = session.query(AnswerPOCO).filter(AnswerPOCO.reviewer == userId).filter(AnswerPOCO.study_case == caseId).one_or_none()
    if ans != None and not ans.completed:
        updatestmt = update(AnswerPOCO).where(AnswerPOCO.reviewer == userId).where(AnswerPOCO.study_case == caseId).values(completed=True)
        session.execute(updatestmt)
        session.commit()
        session.close()
        return True
    else:
        session.close()
        return False

#one-time data creation

def create_all_answers(engine):
    
    session = Session(engine)
    cases = session.query(CasePOCO).all()
    users = session.query(ReviewerPOCO).filter(ReviewerPOCO.admin == False).all()
    for user in users:
        counter = 0
        for case in cases:
            newAns = AnswerPOCO(case.id, user.id)
            session.add(newAns)
            counter += 1
        updatestmt = update(ReviewerPOCO).where(ReviewerPOCO.id == user.id).values(remaining_cases=counter)
        session.execute(updatestmt)
        
    session.commit()
        
    session.close()

def create_user_answers(userId, engine):
    
    session = Session(engine)
    
    cases = session.query(CasePOCO).all()
    
    counter = 0
    
    for case in cases:
        newAns = AnswerPOCO(case.id, userId)
        session.add(newAns)
        counter += 1
            
    updatestmt = update(ReviewerPOCO).where(ReviewerPOCO.id == userId).values(remaining_cases=counter)
    session.execute(updatestmt)    
    session.commit()
    
    session.close()