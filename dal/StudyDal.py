# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 17:12:36 2026

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
    
    finally:    
        session.close()
    
    return answer

def get_name_of_study(study_id, engine):
    
    session = Session(engine)
    
    try:
        answer = session.query(StudyPOCO.name).filter(StudyPOCO.id == study_id).one_or_none()
    
    finally:    
        session.close()
    
    return answer

def get_review_end(study_id, engine):
    
    session = Session(engine)
    
    try:
        answer = session.query(StudyPOCO.review_end_date).filter(StudyPOCO.id == study_id).one_or_none()
    
    finally:    
        session.close()
    
    return answer

def get_learning_end(study_id, engine):
    
    session = Session(engine)
    
    try:
        answer = session.query(StudyPOCO.end_date).filter(StudyPOCO.id == study_id).one_or_none()
    
    finally:    
        session.close()
    
    return answer

def get_study_distribution(study_id, engine):
    
    session = Session(engine)
    
    try:
        ans = session.query(StudyPOCO.repartition_type, StudyPOCO.repartition_value).filter(StudyPOCO.id == study_id).one_or_none()
        answer = (ans.repartition_type, ans.repartition_value)
        
    finally:    
        session.close()
    
    return answer


#CRUD
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

