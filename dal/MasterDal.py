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
import img_vote.dal.UserDal as UserDal
import img_vote.dal.CaseDal as CaseDal
import img_vote.dal.AnswerDal as AnswerDal
import img_vote.dal.CriterionDal as CriterionDal

metadata_obj = MetaData()

database_credentials_file = open(os.path.join(getcwd(), 'persistence/database_credentials.txt'))
orm_driver = database_credentials_file.readline().removesuffix('\n')
usrname = database_credentials_file.readline().removesuffix('\n')
passw = database_credentials_file.readline().removesuffix('\n')
db_host = database_credentials_file.readline().removesuffix('\n')
db_name = database_credentials_file.readline().removesuffix('\n')

database_credentials_file.close()

url_object = URL.create(
    orm_driver,
    username=usrname,
    password=passw,  # plain (unescaped) text
    host=db_host,
    database=db_name,
)

engine = create_engine(url_object)

#UserDal
def get_reviewer_by_id(identifier):
    return UserDal.get_reviewer_by_id(identifier, engine)

def get_reviewer_by_login(login):
    return UserDal.get_reviewer_by_login(login, engine)

def get_reviewer_for_login(login):
    return UserDal.get_reviewer_for_login(login, engine)

def get_users_for_admin(identifier):
    return UserDal.get_users_for_admin(identifier, engine)

def create_reviewer(name, login, password, admin):
    return UserDal.create_reviewer(name, login, password, admin, engine)

def delete_reviewer_by_id(identifier):
    return UserDal.delete_reviewer_by_id(identifier, engine)

def delete_reviewer_by_login(login):
    return UserDal.delete_reviewer_by_login(login, engine)

def clear_non_admin_users():
    return UserDal.clear_non_admin_users(engine)

def update_password(userId, newPassword):
    return UserDal.update_password(userId, newPassword, engine)

def advance_user_count(userId):
    return UserDal.advance_user_count(userId, engine)


#CaseDal
def get_case_by_id(identifier):
    return CaseDal.get_case_by_id(identifier, engine)

def get_all_cases():
    return CaseDal.get_all_cases(engine)

def exists_case_by_id(identifier):
    return CaseDal.exists_case_by_id(identifier, engine)

def create_case(path, name, gld_std):
    return CaseDal.create_case(path, name, gld_std, engine)

def extract_all_data():
    return CaseDal.extract_all_data(engine)

def create_all_cases():
    return CaseDal.create_all_cases(engine)

def clear_all_cases():
    return CaseDal.clear_all_cases(engine)

#AnswerDal
def get_answer_by_id(identifier):
    return AnswerDal.get_answer_by_id(identifier, engine)

def get_cases_and_answers(userId):
    return AnswerDal.get_cases_and_answers(userId, engine)

def mark_answer_done(userId, caseId):
    return AnswerDal.mark_answer_done(userId, caseId, engine)

def create_all_answers():
    return AnswerDal.create_all_answers(engine)
    
def create_user_answers(userId):
    return AnswerDal.create_user_answers(userId, engine)

#CriterionDal
def get_criterion_by_id(identifier):
    return CriterionDal.get_criterion_by_id(identifier, engine)

def get_criterion_for_case(userId, caseId):
    return CriterionDal.get_criterion_for_case(userId, caseId, engine)

def get_diagnosis_for_case(userId, caseId):
    return CriterionDal.get_diagnosis_for_case(userId, caseId, engine)

def get_all_criteria():
    return CriterionDal.get_all_criteria(engine)

def get_all_criteria_no_diagnosis():
    return CriterionDal.get_all_criteria_no_diagnosis(engine)

def get_all_diagnosis():
    return CriterionDal.get_all_diagnosis()

def create_all_criterion():
    return CriterionDal.create_all_criterion(engine)
    
def create_all_answer_to_criterion():
    return CriterionDal.create_all_answer_to_criterion(engine)
    
def create_user_answer_to_criterion(userId):
    return CriterionDal.create_user_answer_to_criterion(userId, engine)

def clear_all_criteria():
    return CriterionDal.clear_all_criteria(engine)

def save_Criterion(user, case, critName, newValue):
    return CriterionDal.save_Criterion(user, case, critName, newValue, engine)
    
def safeguard_Criterion(user, case, critId, newValue):
    return CriterionDal.safeguard_Criterion(user, case, critId, newValue, engine)    
    
def undo_all_but_one(user, case, critId, value, critType):
    return CriterionDal.undo_all_but_one(user, case, critId, value, critType, engine)    

def get_unfinished_criteria(userId, caseId):
    return CriterionDal.get_unfinished_criteria(userId, caseId, engine)

