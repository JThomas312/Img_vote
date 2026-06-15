#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 18:34:27 2025

@author: jacques
"""

class StudyViewModel():
    id: int
    name: str
    
    def __init__(self, id, name):
        self.id = id
        self.name = name

class StudiesViewModel():
    studies_to_show: bool
    studies: list(StudyViewModel)
    
    def __init__(self):
        self.studies_to_show = False
        self.studies = []

class UserHomeViewModel():
    userId: int
    study: int
    name: str
    items: list((int, str, bool)) #id, name, completed
    remaing_items: int
    admin: bool
    demographics_answered: bool
    def __init__(self):
        self.items = []
        self.remaing_items = 0
        self.admin = False
        self.demographics_answered = True #edit once demographics are implemented
  
class AdminHomeViewModel():
    userId: int
    name: str
    otherUsers: list((int, str, str, bool, int)) #id, login, name, admin, remaining cases
    remaing_users: int
    total_users: int
    admin: bool
    def __init__(self):
        self.otherUsers = []
        self.remaing_users = 0
        self.admin = True

class UserLearnViewModel():
    userId: int
    name: str
    items: list((int, str, bool)) #id, name, correct
    correct_answers: int
    total_answers: int
    def __init__(self):
        self.items = []
        self.correct_answers = 0
        self.total_answers = 0
        self.admin = False

# ViewModels for admins before study
class CriterionEditingViewModel():
    id: int
    name: str
    malignancy: bool
    def __init__(self, crit_id, name, malignancy=False):
        self.id = crit_id
        self.name = name
        self.malignancy = malignancy
    
class CategoryConfigurationViewModel():
    id: int
    name: str
    type: int
    has_tutorial: bool
    has_trust: bool
    has_NA: bool
    optional: bool
    has_gold_standard: bool
    has_malignancy: bool
    criteria: list(CriterionEditingViewModel)
    def __init__(self, cat_id, name, cat_type, has_trust, has_tutorial, has_NA, optional, has_gold_standard, has_malignancy):
        self.id = cat_id
        self.name = name
        self.type = cat_type
        self.has_trust = has_trust
        self.has_tutorial = has_tutorial
        self.has_NA = has_NA
        self.has_gold_standard = has_gold_standard
        self.has_malignancy = has_malignancy
        self.optional = optional
        self.criteria = []
  
class PrerequisiteEditingViewModel():
    id: int #id of the criterion
    name:str
    def __init__(self, pre_id, name):
        self.id = pre_id
        self.name = name
  
class CategoryEditingViewModel():
    id: int
    name: str
    type: int
    has_trust: bool
    has_tutorial: bool
    has_NA: bool
    optional: bool
    has_gold_standard: bool
    has_malignancy: bool
    criteria: list(CriterionEditingViewModel)
    prerequisites: list(PrerequisiteEditingViewModel)
    def __init__(self, cat_id, name, cat_type, has_trust, has_tutorial, has_NA, optional, has_gold_standard, has_malignancy):
        self.id= cat_id
        self.name = name
        self.type = cat_type
        self.has_trust = has_trust
        self.has_tutorial = has_tutorial
        self.has_NA = has_NA
        self.optional = optional
        self.has_gold_standard = has_gold_standard
        self.has_malignancy = has_malignancy
        self.criteria = []
        self.prerequisites = []

class UploadStatusViewModel():
    case_images_uploaded: bool
    tutorial_images_needed: bool
    tutorial_images_uploaded: bool
    case_data_needed: bool
    case_data_uploaded: bool

class ReviewerDistributionViewmodel():
    nb_cases: int
    nb_reviewers: int
    nb_full_reviewers: int
    def __init__(self, nb_cases=0, nb_reviewers=0, nb_full_reviewers=0):
        self.nb_cases = nb_cases
        self.nb_reviewers = nb_reviewers
        self.nb_full_reviewers = nb_full_reviewers
        
class CriterionViewModel():
    id: int
    name: str
    value: int
    isTrust: bool
    def __init__(self, critId, name, value, isTrust):
        self.id = critId
        self.name = name
        self.value = value
        self.isTrust = isTrust

# ViewModels for admins during study
class ManageDownloadsViewModel():
    errors: str
    files_to_show: bool
    files: list(str)
    def __init__(self):
        self.errors = ''
        self.files_to_show = False
        self.files = []

# ViewModels for user pages during study
class CategoryViewModel():
    cat_id: int
    name: str
    type: int
    has_trust: bool
    has_tutorial: bool
    has_NA: bool
    optional: bool
    prerequisites: list(int)
    criteria: list(CriterionViewModel)
    trust_criterion: CriterionViewModel
    unanswered: bool
    def __init__(self, cat_id, name, cat_type, has_trust, has_tutorial, has_NA, optional, prerequisites=[], criteria=[], trust_criterion=None, unanswered=True):
        self.cat_id = cat_id
        self.name = name
        self.type = cat_type
        self.has_trust = has_trust
        self.has_tutorial = has_tutorial
        self.has_NA = has_NA
        self.optional = optional
        self.prerequisites = prerequisites
        self.criteria = criteria
        self.trust_criterion = trust_criterion
        self.unanswered = unanswered
    
class CaseDisplayViewModel():
    case_id: int
    case_name: str
    study_name: str
    nb_imgs: int 
    imgs: list()
    imgs_sizes: list((int, int))
    categories: list(CategoryViewModel)
    max_int: int
    min_int: int
    show_remarks : int
    remarks: str
    prevcase: int
    nextcase: int
    def __init__(self, case_id, case_name, study_name, show_remarks=False, remarks='', nb_categories=0, nb_imgs=0, imgs=[], imgs_sizes=[]):
        self.case_id = case_id
        self.case_name = case_name
        self.study_name = study_name
        self.show_remarks = show_remarks
        self.remarks = remarks
        self.nb_categories = nb_categories
        self.nb_imgs = nb_imgs
        self.imgs = imgs
        self.imgs_sizes = imgs_sizes
        self.categories = []
    
class CaseLearningViewModel():
    case_id: int
    case_name: str
    study_name: str
    nb_imgs: int 
    imgs: list()
    imgs_sizes: list((int, int))
    answer: str
    correct_answer: str
    prevcase: int
    nextcase: int
    def __init__(self, case_id, case_name, study_name, answer, correct_answer, nb_imgs=0, imgs=[], imgs_sizes=[]):
        self.case_id = case_id
        self.case_name = case_name
        self.study_name = study_name
        self.answer = answer
        self.correct_answer = correct_answer
        self.nb_imgs = nb_imgs
        self.imgs = imgs
        self.imgs_sizes = imgs_sizes



