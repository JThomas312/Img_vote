# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 11:11:37 2026

@author: jacques
"""

#general imports
from os import getcwd
import os.path


from openpyxl import load_workbook

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
from img_vote.Models.DataModels import CategoryDataModel, CategoryWithCriteriaDataModel
from img_vote.Models.POCO import ReviewerPOCO, CasePOCO, AnswerPOCO, CategoryPOCO, CriterionPOCO, AnswerCriterionPOCO


#read-only 
def get_category_by_id(identifier, engine):
    
    session = Session(engine)
    
    categoryPOCO = session.get(CategoryPOCO, identifier)
    
    category = CategoryDataModel(categoryPOCO.id, categoryPOCO.name, categoryPOCO.type, categoryPOCO.has_tutorial, categoryPOCO.has_trust, categoryPOCO.has_na, categoryPOCO.optional)
    
    session.close()
    
    return category

def at_least_one_other_mandatory_category(identifier, engine):
    
    session = Session(engine)
    
    query = session.query(CategoryPOCO).filter(CategoryPOCO.optional == False).filter(CategoryPOCO.id != identifier)
    
    ans = session.query(query.exists()).scalar()
    
    return ans

def gold_standard_exists(cat_id, engine):
    
    session = Session(engine)
    
    query = session.query(CategoryPOCO).filter(CategoryPOCO.has_gold_standard == True).filter(CategoryPOCO.id != cat_id)
    
    ans = session.query(query.exists()).scalar()
    
    return ans
    

#CRUD
def new_empty_category(engine):
    
    session = Session(engine)
    
    newCat = CategoryPOCO()
    session.add(newCat)
    
    session.commit()
    
    newId = newCat.id
    
    session.close()
    
    return newId

def update_category_value(cat_id, value, parameter, engine):
    
    session = Session(engine)
    updatestmt = None
    
    if parameter == 'name':
        updatestmt = update(CategoryPOCO).where(CategoryPOCO.id == cat_id).values(name=value)
    if parameter == 'type':
        updatestmt = update(CategoryPOCO).where(CategoryPOCO.id == cat_id).values(type=value)
    if parameter == 'tutorial':
        updatestmt = update(CategoryPOCO).where(CategoryPOCO.id == cat_id).values(has_tutorial=value)
    if parameter == 'trust':
        updatestmt = update(CategoryPOCO).where(CategoryPOCO.id == cat_id).values(has_trust=value)
    if parameter == 'na':
        updatestmt = update(CategoryPOCO).where(CategoryPOCO.id == cat_id).values(has_na=value)
    if parameter == 'optional':
        updatestmt = update(CategoryPOCO).where(CategoryPOCO.id == cat_id).values(optional=value)
    if parameter == 'gold_standard':
        updatestmt = update(CategoryPOCO).where(CategoryPOCO.id == cat_id).values(has_gold_standard=value)
    if parameter == 'malignancy':
        updatestmt = update(CategoryPOCO).where(CategoryPOCO.id == cat_id).values(has_malignancy=value)



    session.execute(updatestmt)

    session.commit()
    
    session.close()
    

def erase_category(identifier, engine):
    
    session = Session(engine)
    
    deleteStmt = delete(CategoryPOCO).where(CategoryPOCO.id == identifier)
    
    session.execute(deleteStmt)
    session.commit()

    session.close()

#one-time data creation

