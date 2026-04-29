#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 18:29:44 2025

@author: jacques
"""

class UserDataModel():
    userId: int
    name: str
    login: str
    admin: bool
    remaining_cases: int
    
    def __init__(self, userId, name, login, admin, remaining_cases):
        self.userId = userId
        self.name = name
        self.login = login
        self.admin = admin
        self.remaining_cases = remaining_cases
        
class UserForLogDataModel():
    login: str
    hashPass: str
    
    def __init__(self, login, hashPass):
        self.login = login
        self.hashPass = hashPass
        
class CaseDataModel():
    caseId: int
    path: str
    name: str
    
    def __init__(self, caseId, path, name):
        self.caseId = caseId
        self.path = path
        self.name = name

class CaseAnsDataModel():
    caseId: int
    name: str
    completed: bool
    
    def __init__(self, caseId, name, completed):
        self.caseId = caseId
        self.name = name
        self.completed = completed
        
class UserHomeDataModel():
    userId: int
    name: str
    remaining_cases: int
    cases: list((int, str, bool))
    
    def __init__(self, userId, name):
        self.userId = userId
        self.name = name
        self.remaining_cases = 0
        self.cases = []
    
class CriterionDataModel():
    critId: int
    name: str
    tutorial_path: str
    critCategory: int 
    isTrust: bool
    
    def __init__(self, critId, name, tutorial_path, category, trust):
        self.critId = critId
        self.name = name
        self.tutorial_path = tutorial_path
        self.critCategory = category
        self.isTrust = trust
 
class DiagnosisDataModel():
    diagId: int
    name: str
    
    def __init__(self, diagId, name):
        self.diagId = diagId
        self.name = name
 
class CategoryDataModel():
     catId: int
     name: str
     catType: int
     hasTutorial: bool
     hasTrust: bool
     hasNA: bool
     optional: bool
     prerequisites: list(int) #ids of criterions to display category
     
     def __init__(self, catId, name, catType, hasTutorial, hasTrust, hasNA, optional, prerequisites = []):
         self.catId = catId
         self.name = name
         self.catType = catType
         self.hasTutorial = hasTutorial
         self.hasTrust = hasTrust
         self.hasNA = hasNA
         self.optional = optional
         self.prerequisites = prerequisites

class CategoryCreationDataModel():
     name: str
     catType: int
     hasTutorial: bool
     hasTrust: bool
     hasNA: bool
     optional: bool
     hasGoldStandard: bool
     hasMalignancy: bool
     
     def __init__(self):
         self.optional = False
         self.hasGoldStandard = False
         self.hasMalignancy = False

class CategoryWithCriteriaDataModel():
     catId: int
     name: str
     catType: int
     hasTutorial: bool
     hasTrust: bool
     hasNA: bool
     optional: bool
     criteria: list(int, str) #ids and names of criterions from the category
     
     def __init__(self, catId, name, catType, hasTutorial, hasTrust, hasNA, optional):
         self.catId = catId
         self.name = name
         self.catType = catType
         self.hasTutorial = hasTutorial
         self.hasTrust = hasTrust
         self.hasNA = hasNA
         self.optional = optional
         self.criteria = []

class CategoryWithCriteriaAndPrerequisitesDataModel():
     catId: int
     name: str
     catType: int
     hasTutorial: bool
     hasTrust: bool
     hasNA: bool
     optional: bool
     hasGoldStandard: bool
     hasMalignancy: bool
     criteria: list(int, str, bool) #ids, names and malignancies of criterions from the category
     prerequisites: list(int, str) # ids and names of prerequisites for the category
     
     def __init__(self, catId, name, catType, hasTutorial, hasTrust, hasNA, optional, hasGoldStandard, hasMalignancy):
         self.catId = catId
         self.name = name
         self.catType = catType
         self.hasTutorial = hasTutorial
         self.hasTrust = hasTrust
         self.hasNA = hasNA
         self.optional = optional
         self.hasGoldStandard = hasGoldStandard
         self.hasMalignancy = hasMalignancy
         self.criteria = []
         self.prerequisites = []
    
class CriterionForCaseDataModel():
    critId: int
    name: str
    value: int
    category: int
    isTrust: bool
    path_to_tutorial: str
    
    def __init__(self, critId, name, value, category, isTrust, path_to_tutorial):
        self.critId = critId
        self.name = name
        self.value = value
        self.category = category
        self.isTrust = isTrust
        self.path_to_tutorial = path_to_tutorial
        
    
class CriteriaForCase():
    path: str #path to image folder
    categories: list(CategoryDataModel)
    criteria: list(CriterionForCaseDataModel)
    
    def __init__(self, path):
        self.path = path
        self.categories = []
        self.criteria = []
 
class CriterionExtractdataModel():
    name: str
    value: int    
    
    def __init__(self, name, value):
        self.name = name
        self.value = value
 
class CategoryExtractDataModel():
    name: str
    catType: int
    criteria: list(CriterionExtractdataModel)
    diagnosis: str
    confidence: int
    
    def __init__(self, name, catType, confidence = -1, diagnosis = '', criteria = []):
        self.name = name
        self.catType = catType
        self.diagnosis = diagnosis
        self.confidence = confidence
        self.criteria = criteria
 
class FinalExtractDataModel():
    case: str
    reviewer: str
    categories: list[CategoryExtractDataModel]
    reviewer_gold_standard_answer: str
    gold_standard_confidence: int
    gold_standard_answer: str
    gold_standard_comparison: bool
    reviewer_gold_standard_malignancy: str
    gold_standard_malignancy: str
    gold_standard_malignancy_comparison: bool
    
    def __init__(self, case, reviewer, reviewer_gold_standard_answer = '', gold_standard_confidence = -1, gold_standard_answer = '', gold_standard_comparison = False, reviewer_gold_standard_malignancy = '', gold_standard_malignancy = '', gold_standard_malignancy_comparison = False, categories = []):
        self.case = case
        self.reviewer = reviewer
        self.reviewer_gold_standard_answer = reviewer_gold_standard_answer
        self.gold_standard_confidence = gold_standard_confidence
        self.gold_standard_answer = gold_standard_answer
        self.gold_standard_comparison = gold_standard_comparison
        self.reviewer_gold_standard_malignancy = reviewer_gold_standard_malignancy
        self.gold_standard_malignancy = gold_standard_malignancy
        self.gold_standard_malignancy_comparison = gold_standard_malignancy_comparison
        self.categories = categories
        
    
    
    