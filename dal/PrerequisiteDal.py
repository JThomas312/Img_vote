# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 13:55:37 2026

@author: j.thomas
"""

#general imports
from os import getcwd
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
from img_vote.Models.POCO import ReviewerPOCO, CasePOCO, AnswerPOCO, CategoryPOCO, CriterionPOCO, AnswerCriterionPOCO, PrerequisitePOCO


#read-only 
def get_category_prerequisites(catId, engine):
    
    session = Session(engine)

    query = session.query(PrerequisitePOCO, CriterionPOCO).join(CriterionPOCO, PrerequisitePOCO.criterion == CriterionPOCO.id).filter(PrerequisitePOCO.category == catId)
    
    queriedAnswer = query.all()
    
    #0: prerequisite, 1: criterion
    
    answer = []
    
    for ans in queriedAnswer:
        answer.append((ans[0].criterion, ans[1].name))
    
    session.close()
    
    return answer

#CRUD
def new_prerequisite(catId, name, engine):
    
    session = Session(engine)
    
    query = session.query(CriterionPOCO).filter(CriterionPOCO.name == name).filter(CriterionPOCO.category != catId)
    
    try:
        crit = query.one_or_none()
        if crit != None:
            
            newPrerequisite = PrerequisitePOCO(catId, crit.id)
            
            session.add(newPrerequisite)
            
            session.commit()
                        
    finally:
        session.close()
    
def delete_prerequisite(catId, critId, engine):

    session = Session(engine)  
    
    try:
        deleteStmt = delete(PrerequisitePOCO).where(PrerequisitePOCO.category == catId).where(PrerequisitePOCO.criterion == critId)
        
        session.execute(deleteStmt)
        
        session.commit()
        
    finally:
        session.close()

#one-time data creation
def clear_all_prerequisites(engine):
    
    session = Session(engine)
    
    try:
        deleteStmt = delete(PrerequisitePOCO)
        
        session.execute(deleteStmt)
        session.commit()
    
    finally:
        session.close()
