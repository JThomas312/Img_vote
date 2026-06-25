# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 17:12:36 2026

@author: jacques
"""

#general imports
from sqlalchemy import update
from sqlalchemy import delete

from sqlalchemy.orm import Session

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local modules
from img_vote.Models.DataModels import StudyDataModel
from img_vote.Models.POCO import StudyPOCO



#read-only
def get_all_studies(engine):
    
    session = Session(engine)
    
    try:
        studies = session.query(StudyPOCO.id, StudyPOCO.name).all()
        
        answer = [StudyDataModel(study.id, study.name) for study in studies]
    
    finally:    
        session.close()
    
    return answer

def get_study_status(study_id, engine):
    
    session = Session(engine)
    
    try:
        answer = session.query(StudyPOCO.status).filter(StudyPOCO.id == study_id).one_or_none()
        
        if answer != None:
            answer = answer.status
    
    finally:    
        session.close()
    
    return answer

def get_name_of_study(study_id, engine):
    
    session = Session(engine)
    
    try:
        answer = session.query(StudyPOCO.name).filter(StudyPOCO.id == study_id).one_or_none()
        
        if answer != None:
            answer = answer.name
    
    finally:    
        session.close()
    
    return answer

def get_review_end(study_id, engine):
    
    session = Session(engine)
    
    try:
        answer = session.query(StudyPOCO.review_end_date).filter(StudyPOCO.id == study_id).one_or_none()
        
        if answer != None:
            answer = answer.review_end_date
    
    finally:    
        session.close()
    
    return answer

def get_learning_end(study_id, engine):
    
    session = Session(engine)
    
    try:
        answer = session.query(StudyPOCO.end_date).filter(StudyPOCO.id == study_id).one_or_none()
        
        if answer != None:
            answer = answer.end_date
    
    finally:    
        session.close()
    
    return answer

def get_study_distribution(study_id, engine):
    
    session = Session(engine)
    
    try:
        ans = session.query(StudyPOCO.repartition_method, StudyPOCO.repartition_value).filter(StudyPOCO.id == study_id).one_or_none()
        answer = (ans.repartition_method, ans.repartition_value)
        
    finally:    
        session.close()
    
    return answer

def has_tutorial(study_id, engine):
    
    session = Session(engine)
    
    try:
        answer = session.query(StudyPOCO.tutorial).filter(StudyPOCO.id == study_id).one_or_none()
        
        if answer != None:
            answer = answer.tutorial

    finally:    
        session.close()
    
    return answer

def has_gold_standard(study_id, engine):
    
    session = Session(engine)
    
    try:
        answer = session.query(StudyPOCO.gold_standard).filter(StudyPOCO.id == study_id).one_or_none()
        
        if answer != None:
            answer = answer.gold_standard

    finally:    
        session.close()
    
    return answer

def has_malignancy(study_id, engine):
    
    session = Session(engine)
    
    try:
        answer = session.query(StudyPOCO.malignancy).filter(StudyPOCO.id == study_id).one_or_none()
        
        if answer != None:
            answer = answer.malignancy

    finally:    
        session.close()
    
    return answer

#CRUD
def new_study(study_name, engine):
    
    session = Session(engine)
    
    try:
        testquery = session.query(StudyPOCO).filter(StudyPOCO.name == study_name)
        name_taken = session.query(testquery.exists()).scalar()
        if not name_taken:
            new_studyPOCO = StudyPOCO(study_name, 'stopped', False, None, None, False, False, False, None, -1)
            session.add(new_studyPOCO)

            session.commit()

            answer = new_studyPOCO.id
        else:
            answer = None
    
    finally:    
        session.close()
    
    return answer
        
def update_study_status(study_id, new_status, engine):
    
    session = Session(engine)
    
    try:
        updatestmt = update(StudyPOCO).where(StudyPOCO.id == study_id).values(status=new_status)
        session.execute(updatestmt)

        session.commit()
    
    finally:    
        session.close()

def update_study_name(study_id, newname, engine):
    
    session = Session(engine)
    
    try:
        updatestmt = update(StudyPOCO).where(StudyPOCO.id == study_id).values(name=newname)
        
        session.execute(updatestmt)
        
        session.commit()
        
    finally:
        session.close()
    
def update_study_review_end(study_id, end_date, keep, engine):
    
    session = Session(engine)
    
    try:
        if keep:
            updatestmt = update(StudyPOCO).where(StudyPOCO.id == study_id).values(review_end_date=end_date)
        else:
            updatestmt = update(StudyPOCO).where(StudyPOCO.id == study_id).values(review_end_date=None)

        session.execute(updatestmt)

        session.commit()
    
    finally:    
        session.close()

def update_study_learning_end(study_id, end_date, keep, engine):
    
    session = Session(engine)
    
    try:
        if keep:
            updatestmt = update(StudyPOCO).where(StudyPOCO.id == study_id).values(end_date=end_date)
        else:
            updatestmt = update(StudyPOCO).where(StudyPOCO.id == study_id).values(end_date=None)

        session.execute(updatestmt)

        session.commit()
    
    finally:    
        session.close()

def update_study_distribution(study_id, method, value, engine):
    
    session = Session(engine)
    
    try:
        updatestmt = update(StudyPOCO).where(StudyPOCO.id == study_id).values(repartition_method=method, repartition_value=value)

        session.execute(updatestmt)

        session.commit()
    
    finally:    
        session.close()

def update_study_gold_standard(study_id, value, engine):
    
    session = Session(engine)
    
    try:
        updatestmt = update(StudyPOCO).where(StudyPOCO.id == study_id).values(gold_standard=value)

        session.execute(updatestmt)

        session.commit()
    
    finally:    
        session.close()

def update_study_malignancy(study_id, value, engine):
    
    session = Session(engine)
    
    try:
        updatestmt = update(StudyPOCO).where(StudyPOCO.id == study_id).values(malignancy=value)

        session.execute(updatestmt)

        session.commit()
    
    finally:    
        session.close()

def update_study_tutorial(study_id, value, engine):
    
    session = Session(engine)
    
    try:
        updatestmt = update(StudyPOCO).where(StudyPOCO.id == study_id).values(tutorial=value)

        session.execute(updatestmt)

        session.commit()
    
    finally:    
        session.close()

def erase_study(study_id, engine):
    
    session = Session(engine)
    
    try:
        deletestmt = delete(StudyPOCO).where(StudyPOCO.id == study_id)
        
        session.execute(deletestmt)
        
        session.commit()
        
    finally:
        session.close()

