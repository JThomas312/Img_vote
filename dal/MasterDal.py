#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 17:58:21 2025

@author: jacques
"""

#general imports
from sqlalchemy import URL
from sqlalchemy import create_engine    
from sqlalchemy import MetaData
from os import getcwd
import os.path


#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local modules
import img_vote.dal.StudyDal as StudyDal
import img_vote.dal.UserDal as UserDal
import img_vote.dal.CaseDal as CaseDal
import img_vote.dal.AnswerDal as AnswerDal
import img_vote.dal.CategoryDal as CategoryDal
import img_vote.dal.CriterionDal as CriterionDal
import img_vote.dal.PrerequisiteDal as PrerequisiteDal

metadata_obj = MetaData()

database_credentials_file = open(os.path.join(getcwd(), 'persistence', 'database_credentials_test.txt'), encoding="utf-8")
orm_driver = database_credentials_file.readline().removesuffix('\n')
usrname = database_credentials_file.readline().removesuffix('\n')
passw = database_credentials_file.readline().removesuffix('\n')
db_host = database_credentials_file.readline().removesuffix('\n')
db_port = database_credentials_file.readline().removesuffix('\n')
db_name = database_credentials_file.readline().removesuffix('\n')

database_credentials_file.close()

url_object = URL.create(
    orm_driver,
    username=usrname,
    password=passw,  # plain (unescaped) text
    host=db_host,
    port=db_port,
    database=db_name,
)

engine = create_engine(url_object, pool_size=40, max_overflow=60, pool_timeout=30, pool_recycle=1800, pool_pre_ping=True, client_encoding="utf8")

#StudyDal
def get_all_studies():
    return StudyDal.get_all_studies(engine)

def get_study_status(study_id):
    return StudyDal.get_study_status(study_id, engine)

def get_name_of_study(study_id):
    return StudyDal.get_name_of_study(study_id, engine)

def get_review_end(study_id):
    return StudyDal.get_review_end(study_id, engine)

def get_learning_end(study_id):
    return StudyDal.get_learning_end(study_id, engine)

def get_study_distribution(study_id):
    return StudyDal.get_study_distribution(study_id, engine)

def has_tutorial(study_id):
    return StudyDal.has_tutorial(study_id, engine)

def has_gold_standard(study_id):
    return StudyDal.has_gold_standard(study_id, engine)

def has_malignancy(study_id):
    return StudyDal.has_malignancy(study_id, engine)

def new_study(study_name):
    return StudyDal.new_study(study_name, engine)

def update_study_status(study_id, new_status):
    return StudyDal.update_study_status(study_id, new_status, engine)

def update_study_name(study_id, newname):
    return StudyDal.update_study_name(study_id, newname, engine)

def update_study_review_end(study_id, end_date, keep):
    return StudyDal.update_study_review_end(study_id, end_date, keep, engine)

def update_study_learning_end(study_id, end_date, keep):
    return StudyDal.update_study_learning_end(study_id, end_date, keep, engine)

def update_study_distribution(study_id, method, value):
    return StudyDal.update_study_distribution(study_id, method, value, engine)

def update_study_gold_standard(study_id, value):
    return StudyDal.update_study_gold_standard(study_id, value, engine)

def update_study_malignancy(study_id, value):
    return StudyDal.update_study_malignancy(study_id, value, engine)

def update_study_tutorial(study_id, value):
    return StudyDal.update_study_tutorial(study_id, value, engine)

def erase_study(study_id):
    return StudyDal.erase_study(study_id, engine)

#UserDal
def get_reviewer_by_id(identifier):
    return UserDal.get_reviewer_by_id(identifier, engine)

def get_reviewer_by_login(login):
    return UserDal.get_reviewer_by_login(login, engine)

def get_reviewer_for_login(login):
    return UserDal.get_reviewer_for_login(login, engine)

def get_users_for_admin(identifier, study_id):
    return UserDal.get_users_for_admin(identifier, study_id, engine)

def count_all_reviewers(study_id, full):
    return UserDal.count_all_reviewers(study_id, full, engine)

def create_reviewer(name, login, password, study_id, full_review):
    return UserDal.create_reviewer(name, login, password, full_review, study_id, engine)

def create_admin(name, login, password):
    return UserDal.create_admin(name, login, password, engine)

def delete_reviewer_by_id(identifier):
    return UserDal.delete_reviewer_by_id(identifier, engine)

def delete_reviewer_by_login(login):
    return UserDal.delete_reviewer_by_login(login, engine)

def clear_non_admin_users(study_id):
    return UserDal.clear_non_admin_users(study_id, engine)

def update_password(userId, newPassword):
    return UserDal.update_password(userId, newPassword, engine)

def update_user_count(userId, done):
    return UserDal.update_user_count(userId, done, engine)


#CaseDal
def get_case_by_id(identifier):
    return CaseDal.get_case_by_id(identifier, engine)

def get_case_with_gold_standard(identifier):
    return CaseDal.get_case_with_gold_standard(identifier, engine)

def get_all_cases():
    return CaseDal.get_all_cases(engine)

def count_all_cases(study_id):
    return CaseDal.count_all_cases(study_id, engine)

def exists_case_by_id(identifier):
    return CaseDal.exists_case_by_id(identifier, engine)

def create_case(path, name, gld_std):
    return CaseDal.create_case(path, name, gld_std, engine)

def extract_all_data(study_id):
    return CaseDal.extract_all_data(study_id, engine)

def create_all_cases(study_id, gold_standard_dict):
    return CaseDal.create_all_cases(study_id, gold_standard_dict, engine)

def clear_all_cases(study_id):
    return CaseDal.clear_all_cases(study_id, engine)


#AnswerDal
def get_answer_by_id(identifier):
    return AnswerDal.get_answer_by_id(identifier, engine)

def get_answer_name(userId, caseId):
    return AnswerDal.get_answer_name(userId, caseId, engine)

def get_case_by_answer_name(answerName, userId):
    return AnswerDal.get_case_by_answer_name(answerName, userId, engine)

def get_cases_and_answers(userId):
    return AnswerDal.get_cases_and_answers(userId, engine)

def get_answer_remarks(userId, caseId):
    return AnswerDal.get_answer_remarks(userId, caseId, engine)

def get_all_remarks(study_id):
    return AnswerDal.get_all_remarks(study_id, engine)

def get_cases_and_learn(userId):
    return AnswerDal.get_cases_and_learn(userId, engine)

def get_answer_to_case(userId, caseId):
    return AnswerDal.get_answer_to_case(userId, caseId, engine)

def save_remarks(userId, caseId, value):
    return AnswerDal.save_remarks(userId, caseId, value, engine)

def update_answer_status(userId, caseId, done):
    return AnswerDal.update_answer_status(userId, caseId, done, engine)

def create_all_answers(study_id, rev_per_case):
    return AnswerDal.create_all_answers(study_id, rev_per_case, engine)
    
def create_user_answers(study_id, userId, case_per_rev):
    return AnswerDal.create_user_answers(study_id, userId, case_per_rev, engine)
    
def erase_optional_answers(study_id):
    return AnswerDal.erase_optional_answers(study_id, engine)
    
def clear_all_answers(study_id):
    return AnswerDal.clear_all_answers(study_id, engine)


#CategoryDal
def get_category_by_id(catId):
    return CategoryDal.get_category_by_id(catId, engine)

def get_categories(study_id):
    return CategoryDal.get_categories(study_id, engine)

def get_na_tutorial_one_of_categories(study_id):
    return CategoryDal.get_na_tutorial_one_of_categories(study_id, engine)

def categories_with_criteria(study_id):
    return CategoryDal.categories_with_criteria(study_id, engine)

def category_with_criteria_and_prerequisites(catId):
    return CategoryDal.category_with_criteria_and_prerequisites(catId, engine)

def at_least_one_other_mandatory_category(study_id, catId):
    return CategoryDal.at_least_one_other_mandatory_category(study_id, catId, engine)

def at_least_one_mandatory_category(study_id):
    return CategoryDal.at_least_one_mandatory_category(study_id, engine)

def tutorial_category_exists(study_id):
    return CategoryDal.tutorial_category_exists(study_id, engine)

def categories_without_name(study_id):
    return CategoryDal.categories_without_name(study_id, engine)

def mandatory_categories_with_prerequisites(study_id):
    return CategoryDal.mandatory_categories_with_prerequisites(study_id, engine)

def optional_categories_without_prerequisites(study_id):
    return CategoryDal.optional_categories_without_prerequisites(study_id, engine)

def categories_without_criteria(study_id):
    return CategoryDal.categories_without_criteria(study_id, engine)

def malignant_categories_without_gold_standard(study_id):
    return CategoryDal.malignant_categories_without_gold_standard(study_id, engine)

def other_gold_standard_exists(study_id, cat_id):
    return CategoryDal.other_gold_standard_exists(study_id, cat_id, engine)

def gold_standard_exists(study_id):
    return CategoryDal.gold_standard_exists(study_id, engine)

def get_gold_standards(study_id):
    return CategoryDal.get_gold_standards(study_id, engine)

def get_gold_standard(study_id):
    return CategoryDal.get_gold_standard(study_id, engine)

def gold_standard_in_wrong_category(study_id):
    return CategoryDal.gold_standard_in_wrong_category(study_id, engine)

def malignancy_exists(study_id):
    return CategoryDal.malignancy_exists(study_id, engine)

def new_empty_category(study_id):
    return CategoryDal.new_empty_category(study_id, engine)

def update_category_value(cat_id, value, parameter):
    return CategoryDal.update_category_value(cat_id, value, parameter, engine)

def erase_category(catId):
    return CategoryDal.erase_category(catId, engine)

def clear_all_categories(study_id):
    return CategoryDal.clear_all_categories(study_id, engine)


#PrerequisiteDal
def get_category_prerequisites(catId):
    return PrerequisiteDal.get_category_prerequisites(catId, engine)

def new_prerequisite(study_id, cat_id, name):
    return PrerequisiteDal.new_prerequisite(study_id, cat_id, name, engine)

def delete_prerequisite(catId, critId):
    return PrerequisiteDal.delete_prerequisite(catId, critId, engine)

def delete_category_prerequisite(catId):
    return PrerequisiteDal.delete_category_prerequisite(catId, engine)

def delete_prerequisite_from_category_criteria(catId):
    return PrerequisiteDal.delete_prerequisite_from_category_criteria(catId, engine)

def delete_prerequisite_from_criterion(critId):
    return PrerequisiteDal.delete_prerequisite_from_criterion(critId, engine)

def clear_all_prerequisites(study_id):
    return PrerequisiteDal.clear_all_prerequisites(study_id, engine)


#CriterionDal
def get_criterion_by_id(critId):
    return CriterionDal.get_criterion_by_id(critId, engine)

def get_criteria_for_case(userId, caseId, catId):
    return CriterionDal.get_criteria_for_case(userId, caseId, catId, engine)

def get_diagnosis_for_case(userId, caseId):
    return CriterionDal.get_diagnosis_for_case(userId, caseId, engine)

def get_all_criteria():
    return CriterionDal.get_all_criteria(engine)

def get_all_criteria_no_diagnosis():
    return CriterionDal.get_all_criteria_no_diagnosis(engine)

def get_all_diagnosis():
    return CriterionDal.get_all_diagnosis()

def get_gold_standard_dict(study_id):
    return CriterionDal.get_gold_standard_dict(study_id, engine)

def create_criterion(name, tutorial_path, category, is_trust, malignancy):
    return CriterionDal.create_criterion(name, tutorial_path, category, is_trust, malignancy, engine)

def update_criterion(crit_id, name, malignancy):
    return CriterionDal.update_criterion(crit_id, name, malignancy, engine)

def update_criterion_malignancy(crit_id, malignancy):
    return CriterionDal.update_criterion_malignancy(crit_id, malignancy, engine)

def update_criteria_path(study_id, path):
    return CriterionDal.update_criteria_path(study_id, path, engine)

def clear_malignant_criteria_in_non_malignant_category(study_id):
    return CriterionDal.clear_malignant_criteria_in_non_malignant_category(study_id, engine)

def erase_criterion(critId):
    return CriterionDal.erase_criterion(critId, engine)
    
def erase_category_criteria(catId):
    return CriterionDal.erase_category_criteria(catId, engine)

def create_na_criteria(study_id):
    return CriterionDal.create_na_criteria(study_id, engine)

def create_trust_criteria(study_id):
    return CriterionDal.create_trust_criteria(study_id, engine)

def remove_na_criteria(study_id):
    return CriterionDal.remove_na_criteria(study_id, engine)

def remove_trust_criteria(study_id):
    return CriterionDal.remove_trust_criteria(study_id, engine)
    
def create_all_answer_to_criterion(study_id):
    return CriterionDal.create_all_answer_to_criterion(study_id, engine)
    
def create_user_answer_to_criterion(study_id, userId):
    return CriterionDal.create_user_answer_to_criterion(study_id, userId, engine)

def clear_all_criteria(study_id):
    return CriterionDal.clear_all_criteria(study_id, engine)

def safeguard_Criterion(user, case, critId, newValue):
    return CriterionDal.safeguard_Criterion(user, case, critId, newValue, engine)    
    
def undo_all_but_one(userId, case, criterionId, value, category):
    return CriterionDal.undo_all_but_one(userId, case, criterionId, value, category, engine)    

def is_answer_done(study_id, userId, caseId):
    return CriterionDal.is_answer_done(study_id, userId, caseId, engine)
