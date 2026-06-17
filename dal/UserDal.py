#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 15:05:05 2025

@author: jacques
"""

#general imports
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete

from sqlalchemy.orm import Session

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local modules
from img_vote.Models.DataModels import UserDataModel
from img_vote.Models.DataModels import UserForLogDataModel
from img_vote.Models.POCO import ReviewerPOCO, AnswerPOCO, AnswerCriterionPOCO



#read-only
def get_reviewer_by_id(identifier, engine):
    
    session = Session(engine)
    
    try:
        revPOCO = session.query(ReviewerPOCO).filter(ReviewerPOCO.id == identifier).one_or_none()
        
        rev = UserDataModel(revPOCO.id, revPOCO.study, revPOCO.name, revPOCO.login, revPOCO.admin, revPOCO.remaining_cases)
    
    finally:    
        session.close()
    
    return rev

def get_reviewer_by_login(login, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(ReviewerPOCO).filter(ReviewerPOCO.login == login)
        
        revPOCO = query.one_or_none()
        
        if revPOCO == None:
            return None
        
        rev = UserDataModel(revPOCO.id, revPOCO.study, revPOCO.name, revPOCO.login, revPOCO.admin, revPOCO.remaining_cases)
    
    finally:        
        session.close()
    
    return rev


def get_reviewer_for_login(login, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(ReviewerPOCO).filter(ReviewerPOCO.login == login)
    
        revPOCO = query.one_or_none()
    
        if revPOCO == None:
            return None
    
        rev = UserForLogDataModel(revPOCO.login, revPOCO.password)
    
    finally:        
        session.close()
    
    return rev

def get_users_for_admin(identifier, study_id, engine):
    
    session = Session(engine)

    try:
        users = []
    
        reviewerQuery = select(ReviewerPOCO).where(ReviewerPOCO.study == study_id).where(ReviewerPOCO.admin == False).where(ReviewerPOCO.id != identifier).order_by(ReviewerPOCO.remaining_cases, ReviewerPOCO.id)
        reviewerPOCO = session.execute(reviewerQuery).all()
    
        for i in range(len(reviewerPOCO)):
            users.append(UserDataModel(reviewerPOCO[i][0].id, reviewerPOCO[i][0].study, reviewerPOCO[i][0].name, reviewerPOCO[i][0].login, reviewerPOCO[i][0].admin, reviewerPOCO[i][0].remaining_cases))
    
        adminQuery = select(ReviewerPOCO).where(ReviewerPOCO.admin == True).where(ReviewerPOCO.id != identifier).order_by(ReviewerPOCO.id)
        adminPOCO = session.execute(adminQuery).all()
    
        for i in range(len(adminPOCO)):
            users.append(UserDataModel(adminPOCO[i][0].id, adminPOCO[i][0].study, adminPOCO[i][0].name, adminPOCO[i][0].login, adminPOCO[i][0].admin, adminPOCO[i][0].remaining_cases))
    
    finally:
        session.close()

    return users

def get_all_non_admin_reviewers(study_id, engine):
    
    session = Session(engine)

    try:
        users = []
    
        userQuery = select(ReviewerPOCO).where(ReviewerPOCO.study == study_id).where(ReviewerPOCO.admin != True)
        userPOCO = session.execute(userQuery).all()
    
        for i in range(len(userPOCO)):
            users.append(UserDataModel(userPOCO[i][0].id, userPOCO[i][0].study, userPOCO[i][0].name, userPOCO[i][0].login, userPOCO[i][0].admin, userPOCO[i][0].remaining_cases))
    
    finally:
        session.close()

    return users
 
def count_all_reviewers(study_id, full, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(ReviewerPOCO).filter(ReviewerPOCO.study == study_id).filter(ReviewerPOCO.full_review == full).filter(ReviewerPOCO.admin == False)
            
        answer = query.count()
    
    finally:
        session.close()
    
    return answer
   
#CRUD    
def update_user_count(user_id, done, engine):
    
    session = Session(engine)
    
    try:
        ans = session.query(ReviewerPOCO).filter(ReviewerPOCO.id == user_id).one_or_none()
        
        increment = 0
        
        if done:
            increment = -1
        else:
            increment = 1
        
        if ans != None:
            updatestmt = update(ReviewerPOCO).where(ReviewerPOCO.id == user_id).values(remaining_cases=ans.remaining_cases + increment)
        
            session.execute(updatestmt)
    
            session.commit()
    
    finally:
        session.close()

def create_reviewer(name, login, password, study_id, full_review, engine):
    
    session = Session(engine)
    
    try:
        newReviewer = ReviewerPOCO(name, login, password, study=study_id, full_review=full_review)
        session.add(newReviewer)
        session.commit()
        
        rev_id = newReviewer.id
    
    finally:        
        session.close()
    
    return rev_id

def create_admin(name, login, password, engine):
    
    session = Session(engine)
    
    try:
        newReviewer = ReviewerPOCO(name, login, password, admin=True)
        session.add(newReviewer)
        session.commit()
        
        rev_id = newReviewer.id
    
    finally:        
        session.close()
    
    return rev_id
    
def update_password(user_id, newPassword, engine):
    
    session = Session(engine)
    
    try:
        updatestmt = update(ReviewerPOCO).where(ReviewerPOCO.id == user_id).values(password=newPassword)
       
        session.execute(updatestmt)
    
        session.commit()

    finally:
        session.close()

def delete_reviewer_by_id(identifier, engine):
    
    session = Session(engine)
    
    try:
        rev = session.query(ReviewerPOCO).filter(ReviewerPOCO.id == identifier).one()
        
        ans = session.query(AnswerPOCO.id).filter(AnswerPOCO.reviewer == identifier).all()
        
        ans_ids = [a[0] for a in ans]
        
        deleteACstmt = delete(AnswerCriterionPOCO).where(AnswerCriterionPOCO.answer.in_(ans_ids))
        deleteAnsstmt = delete(AnswerPOCO).where(AnswerPOCO.reviewer == identifier)
        
        session.execute(deleteACstmt)
        session.execute(deleteAnsstmt)
        
        session.delete(rev)
        session.commit()
    
    finally:
        session.close()

def delete_reviewer_by_login(login, engine):
    
    session = Session(engine)
    
    try:
        rev = session.query(ReviewerPOCO).filter(ReviewerPOCO.login == login).one()
        
        identifier = rev.id
        
        ans = session.query(AnswerPOCO.id).filter(AnswerPOCO.reviewer == identifier).all()
        
        ans_ids = [a[0] for a in ans]
        
        deleteACstmt = delete(AnswerCriterionPOCO).where(AnswerCriterionPOCO.answer.in_(ans_ids))
        deleteAnsstmt = delete(AnswerPOCO).where(AnswerPOCO.reviewer == identifier)
        
        session.execute(deleteACstmt)
        session.execute(deleteAnsstmt)
        
        session.delete(rev)
        session.commit()
    
    finally:        
        session.close()
    
def clear_non_admin_users(study_id, engine):
    
    session = Session(engine)
    
    try:
        revs = session.query(ReviewerPOCO).filter(ReviewerPOCO.study == study_id).filter(ReviewerPOCO.admin == False).all()
        
        for rev in revs:
            ans = session.query(AnswerPOCO.id).filter(AnswerPOCO.reviewer == rev.id).all()
            
            ans_ids = [a[0] for a in ans]
            
            
            deleteACstmt = delete(AnswerCriterionPOCO).where(AnswerCriterionPOCO.answer.in_(ans_ids))
            deleteAnsstmt = delete(AnswerPOCO).where(AnswerPOCO.reviewer == rev.id)
            
            session.execute(deleteACstmt)
    
            session.execute(deleteAnsstmt)
            
            session.delete(rev)
    
        session.commit()

    finally:
        session.close()
