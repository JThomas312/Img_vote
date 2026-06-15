# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 13:55:37 2026

@author: j.thomas
"""

#general imports
from sqlalchemy import delete

from sqlalchemy.orm import Session

#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local imports
from img_vote.Models.POCO import CriterionPOCO, PrerequisitePOCO, CategoryPOCO


#read-only 
def get_category_prerequisites(catId, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(PrerequisitePOCO, CriterionPOCO).join(CriterionPOCO, PrerequisitePOCO.criterion == CriterionPOCO.id).filter(PrerequisitePOCO.category == catId)
        
        queriedAnswer = query.all()
        
        #0: prerequisite, 1: criterion
        
        answer = []
        
        for ans in queriedAnswer:
            answer.append((ans[0].criterion, ans[1].name))
    
    finally:
        session.close()
    
    return answer

#CRUD
def new_prerequisite(catId, name, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CriterionPOCO).filter(CriterionPOCO.name == name).filter(CriterionPOCO.category != catId)
        crit = query.one_or_none()
        if crit != None:
            
            newPrerequisite = PrerequisitePOCO(catId, crit.id)
            
            session.add(newPrerequisite)
            
            session.commit()
            
            answer = crit.id
        
        else:
            answer = None
            
    finally:
        session.close()
    
    return answer
    
def delete_prerequisite(catId, critId, engine):

    session = Session(engine)  
    
    try:
        deleteStmt = delete(PrerequisitePOCO).where(PrerequisitePOCO.category == catId).where(PrerequisitePOCO.criterion == critId)
        
        session.execute(deleteStmt)
        
        session.commit()
        
    finally:
        session.close()
    
def delete_category_prerequisite(catId, engine):

    session = Session(engine)  
    
    try:
        deleteStmt = delete(PrerequisitePOCO).where(PrerequisitePOCO.category == catId)
        
        session.execute(deleteStmt)
        
        session.commit()
        
    finally:
        session.close()
    
def delete_prerequisite_from_category_criteria(catId, engine):

    session = Session(engine)  
    
    try:
        query = session.query(CriterionPOCO.id).where(CriterionPOCO.category == catId)
        answer = query.all()
        
        for ans in answer:
            deleteStmt = delete(PrerequisitePOCO).where(PrerequisitePOCO.criterion == ans[0])
            session.execute(deleteStmt)
        
        deleteStmt = delete(PrerequisitePOCO).where(PrerequisitePOCO.category == catId)
        
        session.execute(deleteStmt)
        
        session.commit()
        
    finally:
        session.close()
    
def delete_prerequisite_from_criterion(critId, engine):

    session = Session(engine)  
    
    try:
        deleteStmt = delete(PrerequisitePOCO).where(PrerequisitePOCO.criterion == critId)

        session.execute(deleteStmt)

        session.commit()
        
    finally:
        session.close()

#one-time data creation
def clear_all_prerequisites(study_id, engine):
    
    session = Session(engine)
    
    try:
        
        categories = session.query(CategoryPOCO.id).filter(CategoryPOCO.study == study_id).all()
        categoryIds = [x.id for x in categories]
        
        deleteStmt = delete(PrerequisitePOCO).where(PrerequisitePOCO.category.in_(categoryIds))
        
        session.execute(deleteStmt)
        session.commit()
    
    finally:
        session.close()
