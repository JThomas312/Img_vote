# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 11:11:37 2026

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

#local imports
from img_vote.Models.DataModels import CategoryDataModel, CategoryCreationDataModel, CategoryWithCriteriaDataModel, CategoryWithCriteriaAndPrerequisitesDataModel
from img_vote.Models.POCO import CategoryPOCO, CriterionPOCO, PrerequisitePOCO


#read-only 
def get_category_by_id(identifier, engine):
    
    session = Session(engine)
    
    try:
        categoryPOCO = session.get(CategoryPOCO, identifier)
        
        category = CategoryDataModel(categoryPOCO.id, categoryPOCO.name, categoryPOCO.type, categoryPOCO.has_tutorial, categoryPOCO.has_trust, categoryPOCO.has_na, categoryPOCO.optional)
    
    finally:
        session.close()
    
    return category

def get_categories(study_id, engine):
    
    session = Session(engine)
    
    categoriesDM = []
    
    try:
        categories = session.query(CategoryPOCO).filter(CategoryPOCO.study == study_id).order_by(CategoryPOCO.id).all()
        
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

def get_na_tutorial_one_of_categories(study_id, engine):
    
    session = Session(engine)
    
    one_of_type = 2
    
    categoriesDM = []
    
    try:
        categories = session.query(CategoryPOCO).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.has_na == True).filter(CategoryPOCO.has_tutorial == True).filter(CategoryPOCO.type == one_of_type).order_by(CategoryPOCO.id).all()
        
        for category in categories:
            cDM = CategoryDataModel(category.id, category.name, category.type, category.has_tutorial, category.has_trust, category.has_na, category.optional, [])
            categoriesDM.append(cDM)
            
    finally:
        session.close()

    return categoriesDM

def categories_with_criteria(study_id, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO, CriterionPOCO).outerjoin(CriterionPOCO, CategoryPOCO.id == CriterionPOCO.category).filter(CategoryPOCO.study == study_id).order_by(CategoryPOCO.id, CriterionPOCO.id)
        
        #0: category, 1:criterion
        queriedAnswer = query.all()
        
        answer = []
        currentCategory = -1
        currentDataModel = None
        
        for ans in queriedAnswer:
            if (ans[0].id != currentCategory):
                if (currentCategory != -1):
                    answer.append(currentDataModel)
                currentCategory = ans[0].id
                currentDataModel = CategoryWithCriteriaDataModel(ans[0].id, ans[0].name, ans[0].type, ans[0].has_tutorial, ans[0].has_trust, ans[0].has_na, ans[0].optional, ans[0].has_gold_standard, ans[0].has_malignancy)
            if ans[1] != None and not ans[1].is_trust:
                currentDataModel.criteria.append((ans[1].id, ans[1].name))
        
        #avoid off by one
        if currentDataModel != None:
            answer.append(currentDataModel)
    
    finally:
        session.close()
    
    return answer

def category_with_criteria_and_prerequisites(catId, engine):
    
    session = Session(engine)
    
    try:
        query1 = session.query(CategoryPOCO, CriterionPOCO).outerjoin(CriterionPOCO, CategoryPOCO.id == CriterionPOCO.category).filter(CategoryPOCO.id == catId).order_by(CategoryPOCO.id, CriterionPOCO.id)
        query2 = session.query(CriterionPOCO, PrerequisitePOCO).join(PrerequisitePOCO, CriterionPOCO.id == PrerequisitePOCO.criterion).filter(PrerequisitePOCO.category == catId)
        
        #0: category, 1: criterion
        queriedAnswer1 = query1.all()
        #0: criterion, 1: prerequisite
        queriedAnswer2 = query2.all()
        
        
        answer = queriedAnswer1[0]
        categoryDataModel = CategoryWithCriteriaAndPrerequisitesDataModel(answer[0].id, answer[0].name, answer[0].type, answer[0].has_tutorial, answer[0].has_trust, answer[0].has_na, answer[0].optional, answer[0].has_gold_standard, answer[0].has_malignancy)
        
        for ans in queriedAnswer1:
            if ans[1] != None and not ans[1].is_trust:
                categoryDataModel.criteria.append((ans[1].id, ans[1].name, ans[1].malignancy))
        
        for ans in queriedAnswer2:
            categoryDataModel.prerequisites.append((ans[0].id, ans[0].name))
    
    finally:
        session.close()
        
    return categoryDataModel

def at_least_one_other_mandatory_category(study_id, identifier, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.optional == False).filter(CategoryPOCO.id != identifier)
        
        ans = session.query(query.exists()).scalar()
        
    finally:
        session.close()
        
    return ans

def at_least_one_mandatory_category(study_id, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.optional == False)
        
        ans = session.query(query.exists()).scalar()
        
    finally:
        session.close()
        
    return ans

def tutorial_category_exists(study_id, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.has_tutorial == True)
        
        ans = session.query(query.exists()).scalar()
        
    finally:
        session.close()
        
    return ans

def mandatory_categories_with_prerequisites(study_id, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO.id, CategoryPOCO.name).join(PrerequisitePOCO, CategoryPOCO.id == PrerequisitePOCO.category).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.optional == False)
        
        ans = query.all()
        
    finally:
        session.close()
        
    return ans

def optional_categories_without_prerequisites(study_id, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO, PrerequisitePOCO).outerjoin(PrerequisitePOCO, CategoryPOCO.id == PrerequisitePOCO.category).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.optional == True)
        
        queriedAnswer = query.all()
        
        answer = []
        
        for ans in queriedAnswer:
            if ans[1] == None:
                answer.append((ans[0].id, ans[0].name))
        
    finally:
        session.close()
    
    return answer

def categories_without_criteria(study_id, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO, CriterionPOCO).outerjoin(CriterionPOCO, CategoryPOCO.id == CriterionPOCO.category).filter(CategoryPOCO.study == study_id)
        
        queriedAnswer = query.all()
        
        answer = []
        
        for ans in queriedAnswer:
            if ans[1] == None:
                answer.append((ans[0].id, ans[0].name))
        
    finally:
        session.close()
    
    return answer

def malignant_categories_without_gold_standard(study_id, engine):

    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO.id, CategoryPOCO.name).filter(CategoryPOCO.has_malignancy == True).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.has_gold_standard == False)
        
        ans = query.all()
        
    finally:
        session.close()
        
    return ans

def other_gold_standard_exists(study_id, cat_id, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.has_gold_standard == True).filter(CategoryPOCO.id != cat_id)
        
        ans = session.query(query.exists()).scalar()
        
    finally:
        session.close()
        
    return ans

def gold_standard_exists(study_id, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.has_gold_standard == True)
        
        ans = session.query(query.exists()).scalar()
        
    finally:
        session.close()
        
    return ans

def malignancy_exists(study_id, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.has_malignancy == True)
        
        ans = session.query(query.exists()).scalar()
        
    finally:
        session.close()
        
    return ans
 
def get_gold_standards(study_id, engine):
    
    session = Session(engine)

    answer = []
    
    try:
        query = session.query(CategoryPOCO.id, CategoryPOCO.name).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.has_gold_standard == True)
        
        answer = query.all()
        
    finally:
        session.close()
        
    return answer
 
def get_gold_standard(study_id, engine):
    
    session = Session(engine)

    answer = []
    
    try:
        query = session.query(CategoryPOCO).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.has_gold_standard == True)
        
        ans = query.one_or_none()
        
        if ans != None:
            answer = CategoryCreationDataModel()
            answer.name = ans.name
            answer.catType = ans.type
            answer.hasTutorial = ans.has_tutorial
            answer.hasTrust = ans.has_trust
            answer.hasNA = ans.has_na
            answer.optional = ans.optional
            answer.hasGoldStandard = True
            answer.hasMalignancy = ans.has_malignancy
        else:
            answer = None
            
    finally:
        session.close()
        
    return answer
 
def gold_standard_in_wrong_category(study_id, engine):
    
    session = Session(engine)

    one_of_type = 2
    answer = []
    
    try:
        query = session.query(CategoryPOCO.id, CategoryPOCO.name).filter(CategoryPOCO.has_gold_standard == True).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.type != one_of_type)
        
        answer = query.all()
            
    finally:
        session.close()
        
    return answer
 
def categories_without_name(study_id, engine):
    
    session = Session(engine)
    
    try:
        query = session.query(CategoryPOCO.id, CategoryPOCO.name).filter(CategoryPOCO.study == study_id).filter(CategoryPOCO.name.regexp_match('^[ ]*$'))
        answer = query.all()
        
    finally:
        session.close()
    
    return answer

#CRUD
def new_empty_category(study_id, engine):
    
    session = Session(engine)
    
    try:
        newCat = CategoryPOCO(study_id)
        session.add(newCat)
        
        session.commit()
        
        newId = newCat.id
    
    finally:
        session.close()
    
    return newId

def update_category_value(cat_id, value, parameter, engine):
    
    session = Session(engine)
    
    try:
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
    
    finally:
        session.close()
    

def erase_category(identifier, engine):
    
    session = Session(engine)
  
    try:
        deleteStmt = delete(CategoryPOCO).where(CategoryPOCO.id == identifier)
        
        session.execute(deleteStmt)
        session.commit()
    
    finally:
        session.close()

#one-time data creation
def clear_all_categories(study_id, engine):
    
    session = Session(engine)
    
    try:
        deleteStmt = delete(CategoryPOCO).where(CategoryPOCO.study == study_id)
        
        session.execute(deleteStmt)
        session.commit()
    
    finally:
        session.close()
