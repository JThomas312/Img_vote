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
from img_vote.Models.POCO import ReviewerPOCO, CasePOCO, AnswerPOCO, CategoryPOCO, CriterionPOCO, PrerequisitePOCO, AnswerCriterionPOCO


#read-only 
def get_category_by_id(identifier, engine):
    
    session = Session(engine)
    
    try:
        categoryPOCO = session.get(CategoryPOCO, identifier)
        
        category = CategoryDataModel(categoryPOCO.id, categoryPOCO.name, categoryPOCO.type, categoryPOCO.has_tutorial, categoryPOCO.has_trust, categoryPOCO.has_na, categoryPOCO.optional)
    finally:
        session.close()
    
    return category

def get_categories(engine):
    
    session = Session(engine)
    
    categoriesDM = []
    
    try:
        categories = session.query(CategoryPOCO).order_by(CategoryPOCO.id).all()
        
        for category in categories:
            cDM = CategoryDataModel(category.id, category.name, category.type, category.has_tutorial, category.has_trust, category.has_na, category.optional, [])
            if category.optional:
                prerequisites = session.query(PrerequisitePOCO.criterion).filter(PrerequisitePOCO.category == category.id).all()
                for prerequisite in prerequisites:
                    cDM.prerequisites.append(prerequisite.criterion)
            categoriesDM.append(cDM)
                
    finally:
        session.close()

    return categoriesDM

def at_least_one_other_mandatory_category(identifier, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO).filter(CategoryPOCO.optional == False).filter(CategoryPOCO.id != identifier)
        
        ans = session.query(query.exists()).scalar()
    finally:
        session.close()
        
    return ans

def at_least_one_mandatory_category(engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO).filter(CategoryPOCO.optional == False)
        
        ans = session.query(query.exists()).scalar()
    finally:
        session.close()
        
    return ans

def mandatory_categories_with_prerequisites(engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO.id, CategoryPOCO.name).join(PrerequisitePOCO, CategoryPOCO.id == PrerequisitePOCO.category).filter(CategoryPOCO.optional == False)
        
        ans = query.all()
    finally:
        session.close()
        
    return ans

def optional_categories_without_prerequisites(engine):
    
    session = Session(engine)
    
    try:
                
        query = session.query(CategoryPOCO, PrerequisitePOCO).outerjoin(PrerequisitePOCO, CategoryPOCO.id == PrerequisitePOCO.category).filter(CategoryPOCO.optional == True)
        
        queriedAnswer = query.all()
        
        answer = []
        
        for ans in queriedAnswer:
            if ans[1] == None:
                answer.append((ans[0].id, ans[0].name))
        
    finally:
        session.close()
    
    return answer

def categories_without_criteria(engine):
    
    session = Session(engine)
    
    try:
                
        query = session.query(CategoryPOCO, CriterionPOCO).outerjoin(CriterionPOCO, CategoryPOCO.id == CriterionPOCO.category)
        
        queriedAnswer = query.all()
        
        answer = []
        
        for ans in queriedAnswer:
            if ans[1] == None:
                answer.append((ans[0].id, ans[0].name))
        
    finally:
        session.close()
    
    return answer

def malignant_categories_in_non_gold_standard_category(engine):

    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO.id, CategoryPOCO.name).filter(CategoryPOCO.has_malignancy == True).filter(CategoryPOCO.has_gold_standard == False)
        
        ans = query.all()
    finally:
        session.close()
        
    return ans

def gold_standard_exists(cat_id, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO).filter(CategoryPOCO.has_gold_standard == True).filter(CategoryPOCO.id != cat_id)
        
        ans = session.query(query.exists()).scalar()
    finally:
        session.close()
        
    return ans
 
def get_gold_standards(engine):
    
    session = Session(engine)

    answer = []
    
    try:
        query = session.query(CategoryPOCO.id, CategoryPOCO.name).filter(CategoryPOCO.has_gold_standard == True)
        
        answer = query.all()
            
    finally:
        session.close()
        
    return answer
 
def categories_without_name(engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO.id, CategoryPOCO.name).filter(CategoryPOCO.name.regexp_match('^[ ]*$'))
        answer = session.query(query.exists()).scalar()
    finally:
        session.close()
    
    return answer

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

