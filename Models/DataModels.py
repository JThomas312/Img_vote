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
    
    def __init__(self, critId, name, tutorial_path, critType, category, trust):
        self.critId = critId
        self.name = name
        self.tutorial_path = tutorial_path
        self.critType = critType
        self.critCategory = category
        self.isTrust = trust
 
class DiagnosisDataModel():
    diagId: int
    name: str
    
    def __init__(self, diagId, name):
        self.diagId = diagId
        self.name = name
 
# class CriterionForCaseDataModel():
#      path: str
#      criteria: list((int, int, str, int, str, int))#type, category, name, value, path to tutorial, id
#      def __init__(self, path):
#          self.path = path
#          self.criteria = []
 
class CategoryDataModel():
     catId: int
     name: str
     catType: int
     hasTutorial: bool
     hasTrust: bool
     hasNA: bool
     optional: bool
     prerequisites: list(int, str) #ids and names of criterions to display category
     
     def __init__(self, catId, name, catType, hasTutorial, hasTrust, hasNA, optional):
         self.catId = catId
         self.name = name
         self.catType = catType
         self.hasTutorial = hasTutorial
         self.hasTrust = hasTrust
         self.hasNA = hasNA
         self.optional = optional
         self.prerequisites = []

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
    path_to_tutorial: str
    
    def __init__(self, critId, name, value, path_to_tutorial):
        self.critId = critId
        self.name = name
        self.value = value
        self.path_to_tutorial = path_to_tutorial
        
    
class CriteriaForCase():
    path: str #path to image folder
    categories: list(CategoryDataModel)
    criteria: list(CriterionForCaseDataModel)
    
    def __init__(self, path):
        self.path = path
        self.categories = []
        self.criteria = []
    
 
class FinalExtractDataModel():
    case: str
    reviewer: str
    criteria: list[int]
    reviewer_diagnosis: str
    diagnosis_confidence: int
    depth_confidence: int
    gold_standard_diagnosis: str
    gold_standard_diagnosis_comparison: bool
    malignant_diagnosis: str
    gold_standard_malignity: str
    gold_standard_malignity_comparison: bool
    
    def __init__(self, case, reviewer, criteria, reviewer_diagnosis, diag_conf, depth_conf, gold_standard_diagnosis, gold_standard_diagnosis_comparison, malignant_diagnosis, gold_standard_malignity, gold_standard_malignity_comparison):
        self.case = case
        self.reviewer = reviewer
        self.criteria = criteria
        self.reviewer_diagnosis = reviewer_diagnosis
        self.diagnosis_confidence = diag_conf
        self.depth_confidence = depth_conf
        self.gold_standard_diagnosis = gold_standard_diagnosis
        self.gold_standard_diagnosis_comparison = gold_standard_diagnosis_comparison
        self.malignant_diagnosis = malignant_diagnosis
        self.gold_standard_malignity = gold_standard_malignity
        self.gold_standard_malignity_comparison = gold_standard_malignity_comparison
        
    
    
    