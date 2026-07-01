#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 19:33:36 2025

@author: jacques
"""

#general imports
from bcrypt import gensalt, hashpw

from pyexcel.sheet import Sheet
from os import getcwd
from os import remove
import os.path
from natsort import natsorted
from math import ceil
from zipfile import ZipFile
from shutil import copyfile
from re import match
from datetime import datetime
from threading import Thread
from werkzeug.utils import secure_filename


#enable imports from local modules
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

#local modules
from img_vote.utilities.useful import generate_password
from img_vote.utilities.useful import format_r_friendly
from img_vote.utilities.useful import sanitize
from img_vote.utilities.useful import listdir_safe_and_sorted
from img_vote.utilities.useful import safe_worksheet_save
from img_vote.utilities.useful import safe_remove_file
from img_vote.utilities.useful import safe_remove_folder
from img_vote.Models.Enums import Action, StudyStatus

from img_vote.Models.ViewModels import CriterionEditingViewModel, CategoryConfigurationViewModel
from img_vote.Models.ViewModels import CategoryEditingViewModel, PrerequisiteEditingViewModel, UploadStatusViewModel
from img_vote.Models.ViewModels import ReviewerDistributionViewmodel, ManageDownloadsViewModel

#study related
from img_vote.dal.MasterDal import erase_study

#user related
from img_vote.dal.MasterDal import get_reviewer_by_id, get_reviewer_by_login, count_all_reviewers, create_reviewer, create_admin
from img_vote.dal.MasterDal import delete_reviewer_by_id, update_password, clear_non_admin_users

#case related
from img_vote.dal.MasterDal import count_all_cases, extract_all_data, create_all_cases, clear_all_cases

#answer related
from img_vote.dal.MasterDal import create_all_answers, create_user_answers, get_all_remarks, erase_optional_answers

#category related
from img_vote.dal.MasterDal import get_category_by_id, categories_with_criteria, category_with_criteria_and_prerequisites
from img_vote.dal.MasterDal import at_least_one_other_mandatory_category, at_least_one_mandatory_category
from img_vote.dal.MasterDal import categories_without_name, mandatory_categories_with_prerequisites, optional_categories_without_prerequisites
from img_vote.dal.MasterDal import categories_without_criteria, malignant_categories_without_gold_standard, other_gold_standard_exists
from img_vote.dal.MasterDal import get_gold_standards, get_gold_standard, gold_standard_in_wrong_category, new_empty_category
from img_vote.dal.MasterDal import update_category_value, erase_category, clear_all_categories, get_na_tutorial_one_of_categories

#prerequisite related
from img_vote.dal.MasterDal import new_prerequisite, delete_prerequisite, delete_category_prerequisite
from img_vote.dal.MasterDal import delete_prerequisite_from_category_criteria, delete_prerequisite_from_criterion, clear_all_prerequisites

#criterion related
from img_vote.dal.MasterDal import get_gold_standard_dict
from img_vote.dal.MasterDal import create_criterion, update_criterion, update_criterion_malignancy, update_criteria_path
from img_vote.dal.MasterDal import clear_malignant_criteria_in_non_malignant_category, erase_criterion
from img_vote.dal.MasterDal import erase_category_criteria, create_na_criteria, create_trust_criteria, remove_na_criteria
from img_vote.dal.MasterDal import remove_trust_criteria, create_all_answer_to_criterion, clear_all_answers
from img_vote.dal.MasterDal import create_user_answer_to_criterion, clear_all_criteria


def find_name_and_login(userId):
    
    usr = get_reviewer_by_id(userId)
    usrName = usr.name
    usrLogin = usr.login
    
    return (usrName, usrLogin)


def create_user(studyId, login, name, admin, status, full_review, distribution=None, case_per_r=None, percentage=None):
    
    existing = get_reviewer_by_login(login)
    
    full = full_review and not admin

    answer_creation_statuses = [StudyStatus.ready.value, StudyStatus.test.value, StudyStatus.ongoing.value, StudyStatus.paused.value]
    
    
    if ((not admin) and (status == StudyStatus.ended.value)):
        raise Exception('While the study is ended only administrator users can be created')
    elif not full_review and not admin and distribution == 'n per case' and status in answer_creation_statuses:
        raise Exception('You can now only create full reviewers with your chosen distribution')
    
    elif existing != None:
        raise Exception('User already exists with login ' + login)
    
    else:
        password = generate_password()
        s = gensalt()
        hashPass = hashpw(password.encode('utf-8'), s).decode('utf-8')
        if admin:
            revId = create_admin(name, login, hashPass)
        else:
            revId = create_reviewer(studyId, name, login, hashPass, full)
    
            if status in answer_creation_statuses:
                case_per_rev = compute_case_per_rev(studyId, full, distribution, case_per_r, percentage)
                create_user_answers(studyId, revId, case_per_rev)
                create_user_answer_to_criterion(studyId, revId)
    
    return password

def categories_for_editing(studyId):
    
    categoriesDMs = categories_with_criteria(studyId)
    categoriesVMs = []
    
    for categoryDM in categoriesDMs:
        currentCategoryVM = CategoryConfigurationViewModel(categoryDM.catId, categoryDM.name, categoryDM.catType, categoryDM.hasTrust, categoryDM.hasTutorial, categoryDM.hasNA, categoryDM.optional, categoryDM.hasGoldStandard, categoryDM.hasMalignancy)
        for crit in categoryDM.criteria:
            currentCategoryVM.criteria.append(CriterionEditingViewModel(crit[0], crit[1]))
        categoriesVMs.append(currentCategoryVM)
        
    return categoriesVMs   

def category_for_editing(catId):
    
    categoryDM = category_with_criteria_and_prerequisites(catId)
    categoryVM = CategoryEditingViewModel(categoryDM.catId, categoryDM.name, categoryDM.catType, categoryDM.hasTrust, categoryDM.hasTutorial, categoryDM.hasNA, categoryDM.optional, categoryDM.hasGoldStandard, categoryDM.hasMalignancy)
    
    for criterion in categoryDM.criteria:
        categoryVM.criteria.append(CriterionEditingViewModel(criterion[0], criterion[1], criterion[2]))
    
    for prerequisite in categoryDM.prerequisites:
        categoryVM.prerequisites.append(PrerequisiteEditingViewModel(prerequisite[0], prerequisite[1]))

    return categoryVM 

def create_empty_category(studyId):
    
    newId = new_empty_category(studyId)
    
    return newId

def update_category(cat_id, value, parameter):
    
    val = value
    param = parameter
    #this way if either the DAL of front changes parameter, only this needs to be updated --> no dependency between front and DAL
    if parameter == 'name':
        if value == '' or not sanitize(value):
            return
        param = 'name'
    if parameter == 'type':
        val = int(value)
        param = 'type'
    if parameter == 'tutorial':
        param = 'tutorial'
    if parameter == 'trust':
        param = 'trust'
    if parameter == 'na':
        param = 'na'
    if parameter == 'optional':
        param = 'optional'
    if parameter == 'gold_standard':
        param = 'gold_standard'
    if parameter == 'malignancy':
        param ='malignancy'
    if (value == 'true'):
        val = True
    if (value == 'false'):
        val = False
        
    update_category_value(cat_id, val, param)
    
    return

def save_criterion(studyId, cat_id, name, malignancy):
    
    if not sanitize(name) or name == '' or name == 'na':
        return
    
    category_name = get_category_by_id(cat_id).name
    tutorial_slide_path = os.path.join(getcwd(), 'data', str(studyId), 'tutorial_data', category_name, name)
    mal = malignancy == 'true'
    crit_id = create_criterion(name, tutorial_slide_path, cat_id, False, mal)
    
    return crit_id

def change_criterion(cat_id, crit_id, name, malignancy, action):
    
    if action == Action.remove.value:
        delete_prerequisite_from_criterion(crit_id)
        erase_criterion(crit_id)
        
    if not sanitize(name) or name == '':
        return
    
    if action == Action.edit.value:
        mal = malignancy == 'true'
        update_criterion(crit_id, name, mal)

def save_criterion_malignancy(crit_id, malignancy):
    
    mal = malignancy == 'true'
    update_criterion_malignancy(crit_id, mal)

def save_prerequisite(studyId, catId, name):
    
    if not sanitize(name) or name == '':
        return
    
    critId = new_prerequisite(studyId, catId, name)
    
    return critId

def change_prerequisite(cat_id, crit_id, name, action):
    
    if not sanitize(name) or name == '':
        return
    
    if action == Action.remove.value:
        delete_prerequisite(cat_id, crit_id)
        
    if action == Action.edit.value:
        delete_prerequisite(cat_id, crit_id)
        
        return new_prerequisite(cat_id, name)
        

def delete_category(cat_id):
    
    delete_category_prerequisite(cat_id)
    delete_prerequisite_from_category_criteria(cat_id)
    erase_category_criteria(cat_id)
    erase_category(cat_id)

def delete_criterion(crit_id):
    
    delete_prerequisite_from_criterion(crit_id)
    erase_criterion(crit_id)

def check_category(cat_id, form_answers):

    if (not 'name' in form_answers) or (form_answers['name'] == '') or (not sanitize(form_answers['name'])):
        return 'Invalid category : your category must have a valid name'

    update_category(cat_id, form_answers['name'], 'name')

    if not 'type' in form_answers:
        return 'Invalid category : choosing type is mandatory'
    
    update_category(cat_id, form_answers['type'], 'type')
    
    prerequisites_ok = True
    
    if 'optional' in form_answers and form_answers['optional'] == '1':
        prerequisites_ok = False
    
    nb_answers = 0
    
    for ans in form_answers:
        if ans.find('prerequisiteField') != -1:
            val = form_answers[ans]
            if val == '':
                return 'Invalid category : one of your answers is unnamed'
            if not sanitize(val):
                return 'invalid prerequisite : ' + val + ' is not a valid name'
            prerequisites_ok = True
        if ans.find('criterionField') != -1:
            val = form_answers[ans]
            if val == '':
                return 'Invalid category : one of your answers is unnamed'
            if not sanitize(val):
                return 'invalid answer : ' + val + ' is not a valid name'
            nb_answers += 1
    
    if not prerequisites_ok:
        return 'Invalid category : an optional category needs at least one prerequisite'
    
    if form_answers['type'] == '2' and nb_answers < 2:
        return 'Invalid category : this type of category needs at least two answers'
    
    if nb_answers == 0:
        return 'Invalid category : every category needs at least one answer'
    
    return None

def check_categories(studyId):
    
    errors = []
    
    incorrect_categories = []
    unnamed_categories = categories_without_name(studyId)
    if len(unnamed_categories) > 0:
        errors.append('Some of your categories are still unnamed')
        incorrect_categories.extend(unnamed_categories)
    if not at_least_one_mandatory_category(studyId):
        errors.append('All of your categories are optional, you need at least one mandatory category')
    
    gold_standards = get_gold_standards(studyId)
    if len(gold_standards) > 1:
        errors.append('Several categories are marked as having a gold standard but only one is allowed per study')
        incorrect_categories.extend(gold_standards)
    
    wrong_gold_standards = gold_standard_in_wrong_category(studyId)
    if len(wrong_gold_standards) > 0:
        errors.append('''Your gold standard category is not of one-of type, please change it's type or remove the gold standard''')
        incorrect_categories.extend(wrong_gold_standards)
    
    mandatory_categories = mandatory_categories_with_prerequisites(studyId)
    if len(mandatory_categories) > 0:
        errors.append('Some mandatory categories have prerequisites, please remove them or make them optional')
        incorrect_categories.extend(mandatory_categories)
    
    optional_categories = optional_categories_without_prerequisites(studyId)
    if len(optional_categories) > 0:
        errors.append('Some optional categories have no prerequisites, please add at least one or make them mandatory')
        incorrect_categories.extend(optional_categories)
    
    no_criteria = categories_without_criteria(studyId)
    if len(no_criteria) > 0:
        errors.append('Some categories have no possible answer, please add at least one or delete the category')
        incorrect_categories.extend(no_criteria)
    
    malignant_categories = malignant_categories_without_gold_standard(studyId)        
    if len(malignant_categories) > 0:
        errors.append('Some categories are marked as having malignancy but not gold standard, please check them')
        incorrect_categories.extend(malignant_categories)

    unique_incorrect_categories = list(dict.fromkeys(incorrect_categories))
    
    for i in range(len(unique_incorrect_categories)):
        (identifier, name) = unique_incorrect_categories[i]
        if bool(match('^[\\s]*$', name)):
            unique_incorrect_categories[i] = (identifier, 'unnamed category')
    
    if len(errors) > 0 or len(unique_incorrect_categories) > 0:
        return (errors, unique_incorrect_categories)

    clear_malignant_criteria_in_non_malignant_category(studyId)
    
    create_na_criteria(studyId)

    update_criteria_path(studyId, os.path.join(getcwd(), 'data', str(studyId), 'tutorial_data'))
    
    create_trust_criteria(studyId)

    return ([], [])

def categories_rollback(studyId):
    
    remove_na_criteria(studyId)
    remove_trust_criteria(studyId)
    clear_uploads(studyId)

def optional_category_allowed(studyId, categoryId):
    
    allowed = at_least_one_other_mandatory_category(studyId, categoryId)
    
    return allowed

def gold_standard_category_allowed(studyId, categoryId):
    
    allowed = not other_gold_standard_exists(studyId, categoryId)
    
    return allowed

def upload_status(studyId, has_tutorial, has_gold_standard):
    
    VM = UploadStatusViewModel()
    VM.case_images_uploaded = os.path.exists(os.path.join(getcwd(), 'uploads', str(studyId), 'case_images.zip'))
    VM.tutorial_images_needed = has_tutorial
    VM.tutorial_images_uploaded = os.path.exists(os.path.join(getcwd(), 'uploads', str(studyId), 'tutorial_images.zip'))
    VM.case_data_needed = has_gold_standard
    VM.case_data_uploaded = False
    for file in listdir_safe_and_sorted(os.path.join(getcwd(), 'uploads', str(studyId))):
        if file.startswith('case_data'):
            VM.case_data_uploaded = True
    
    return VM

def unzip_and_move(studyId, path, version):
    
    if version == 'case':
        extract_path = os.path.join(getcwd(), 'data', str(studyId), 'Img_data')
    elif version == 'tutorial':
        extract_path = os.path.join(getcwd(), 'data', str(studyId), 'tutorial_data')
    else:
        return 'something went wrong'
    
    try:
        zippy = ZipFile(path)
        zippy.extractall(extract_path)
    except Exception as e:
        return e
    
    if version == 'tutorial':
        #all one of categories with tutorials and n/a enabled need the template n/a tutorial
        na_categories = get_na_tutorial_one_of_categories(studyId)
        
        for na_category in na_categories:
            copyfile(os.path.join(getcwd(), 'data', 'na.jpg'), os.path.join(getcwd(), 'data', str(studyId), 'tutorial_data', na_category.name, 'na.jpg'))
    
    return None

def remove_case_images(studyId):
    
    upload_path = os.path.join(getcwd(), 'uploads', str(studyId), 'case_images.zip')
    
    safe_remove_file(upload_path)
        
    unziped_path = os.path.join(getcwd(), 'data', str(studyId), 'Img_data')
    
    safe_remove_folder(unziped_path)

def remove_tutorial_images(studyId):
    
    upload_path = os.path.join(getcwd(), 'uploads', str(studyId), 'tutorial_images.zip')
    
    safe_remove_file(upload_path)
        
    unziped_path = os.path.join(getcwd(), 'data', str(studyId), 'tutorial_data')
    
    safe_remove_folder(unziped_path)

def remove_case_data(studyId):
    
    for filename in listdir_safe_and_sorted(os.path.join(getcwd(), 'uploads', str(studyId))):
        if filename.startswith('case_data'):
            remove(os.path.join(getcwd(), 'uploads', str(studyId), filename))
    
    for filename in listdir_safe_and_sorted(os.path.join(getcwd(), 'data', str(studyId))):
        if filename.startswith('case_data'):
            remove(os.path.join(getcwd(), 'data', str(studyId), filename))

def clear_uploads(studyId):
    
    folder_path = os.path.join(getcwd(), 'uploads', str(studyId))
    
    safe_remove_folder(folder_path)

def check_uploads_and_create_cases(studyId, has_gold_standard):
    
    if has_gold_standard:
        criteriaDict = get_gold_standard_dict(studyId)
    else:
        criteriaDict = dict()
    
    problems = create_all_cases(studyId, criteriaDict)
    
    if problems != None:
        if problems[0] == 'file name discrepancy':
            return 'Error : file ' + str(problems[1])   + ' does not correspond to case ' + problems[2] + ' in data file, please check your data and upload it again'
        if problems[0] == 'gold standard name discrepancy':
            return 'Error : name ' + str(problems[1]) + ' was encountered in your gold standard spreadsheet but is not an answer in your gold standard category'
    
    return problems

def upload_rollback(studyId):
    
    clear_all_cases(studyId)

def data_for_distribution(studyId):
    
    nb_cases = count_all_cases(studyId)
    nb_standard_reviewers = count_all_reviewers(studyId, False)
    nb_full_reviewers = count_all_reviewers(studyId, True)
    
    distributionVM = ReviewerDistributionViewmodel(nb_cases, nb_standard_reviewers + nb_full_reviewers, nb_full_reviewers)
    
    return distributionVM

def handle_distribution(studyId, method, r_per_case, case_per_r, percentage):

    rev_per_case= compute_rev_per_case(studyId, method, r_per_case, case_per_r, percentage)
    
    create_all_answers(studyId, rev_per_case)    
    create_all_answer_to_criterion(studyId)
    
    return None

def distribution_rollback(studyId):
    
    clear_all_answers(studyId)

def compute_rev_per_case(studyId, method, r_per_case, case_per_r, percentage):

    nb_cases = count_all_cases(studyId)
    nb_standard_reviewers = count_all_reviewers(studyId, False)
    nb_full_reviewers = count_all_reviewers(studyId, True)
    
    if method == 'all for all' or nb_standard_reviewers == 0:
        rev_per_case = nb_standard_reviewers
    
    if method == 'n per case':
        rev_per_case = int(r_per_case) - nb_full_reviewers
        if rev_per_case > nb_standard_reviewers:
            rev_per_case = nb_standard_reviewers
 
    if method == 'n per reviewer':
        rev_per_case = ceil(float(nb_standard_reviewers * int(case_per_r)) / float(nb_cases))
    
    if method == 'percent per reviewer':
        rev_per_case = ceil( float( nb_standard_reviewers * int( ceil( float( nb_cases * int( percentage ) ) / float(100) ) ) ) / float(nb_cases) )
    
    return rev_per_case
 
def compute_case_per_rev(studyId, full, method, case_per_r, percentage):
    
    nb_cases = count_all_cases(studyId)
    nb_standard_reviewers = count_all_reviewers(studyId, False)
    
    if full or method == 'all for all' or nb_standard_reviewers == 0:
        case_per_rev = nb_cases
 
    if method == 'n per reviewer':
        case_per_rev = case_per_r
    
    if method == 'percent per reviewer':
        case_per_rev = ceil( float( nb_cases * percentage ) / float(100) )
    
    return case_per_rev

def get_remarks_for_export(studyId, studyName):
    
    Thread(target=get_remarks_for_export_async, args=(studyId, studyName)).start()

def get_remarks_for_export_async(studyId, studyName):
    
    ws = Sheet()
    ws.title = "case_remarks"

    study_name = format_r_friendly(studyName)
    
    now = datetime.today().strftime('-%Y-%m-%d--%H-%M')
    
    file_name1 = study_name + '_remarks' + now + '.xlsx'
    file_name2 = study_name + '_remarks' + now + '.ods'
    
    folder_path = os.path.join(getcwd(), 'results', str(studyId))
    
    remarks = get_all_remarks(studyId)
    
    ws[0, 0] = 'case'
    ws[0, 1] = 'reviewer'
    ws[0, 2] = 'remarks'
    
    for i in range(len(remarks)):
        ws[i + 1, 0] = remarks[i].case
        ws[i + 1, 1] = remarks[i].reviewer
        ws[i + 1, 2] = remarks[i].remarks
    
    safe_worksheet_save(folder_path, file_name1, ws)
    safe_worksheet_save(folder_path, file_name2, ws)

def clear_optional_answers(studyId):
    
    erase_optional_answers(studyId)

def get_data_for_export(studyId, studyName):

    Thread(target=get_data_for_export_async, args=(studyId, studyName)).start()

def get_data_for_export_async(studyId, studyName):
    
    ws = Sheet()
    ws.title = "Study_data"
    
    study_name = format_r_friendly(studyName)
    
    now = datetime.today().strftime('-%Y-%m-%d--%H-%M')
    
    file_name1 = study_name + '_study_data' + now + '.xlsx'
    file_name2 = study_name + '_study_data' + now + '.ods'
    
    folder_path = os.path.join(getcwd(), 'results', str(studyId))
    
    finalExtract = extract_all_data(studyId)
    
    nbCategories = len(finalExtract[0].categories)
    
    gold_standard = get_gold_standard(studyId)
    
    one_of_category = 2
    column_increment = 0
    
    ws[0, 0] = 'cases'
    ws[0, 1] = 'reviewers'
    
    column_increment += 2
    
    for i in range(nbCategories):
        current_category = finalExtract[0].categories[i]
        if current_category.catType == one_of_category:
            ws[0, column_increment] = format_r_friendly(current_category.name)
            column_increment += 1
        else:
            for criterion in current_category.criteria:
                ws[0, column_increment] = format_r_friendly(criterion.name)
                column_increment += 1
        if current_category.confidence != -2:
            ws[0, column_increment] = format_r_friendly(format_r_friendly(current_category.name) + '_confidence')
            column_increment += 1
            
    if gold_standard != None:
        ws[0 , column_increment] = 'reviewer_gold_standard_answer'
        column_increment +=1
        if gold_standard.hasTrust:
            ws[0, column_increment] = 'gold_standard_confidence'
            column_increment +=1
        ws[0 , column_increment] = 'gold_standard_answer'
        column_increment +=1
        ws[0 , column_increment] = 'gold_standard_comparison'
        column_increment +=1
        if gold_standard.hasMalignancy:
            ws[0, column_increment] = 'reviewer_gold_standard_malignancy'
            column_increment +=1
            ws[0, column_increment] = 'gold_standard_malignancy'
            column_increment +=1
            ws[0, column_increment] = 'gold_standard_malignancy_comparison'
            column_increment +=1
    
    for i in range(len(finalExtract)):
        column_increment = 0
        ws[i + 1, 0] = finalExtract[i].case
        ws[i + 1, 1] = finalExtract[i].reviewer
        column_increment +=2
        for current_category in finalExtract[i].categories:
            if current_category.catType == one_of_category:
                ws[i + 1, column_increment] = format_r_friendly(current_category.diagnosis)
                column_increment += 1
                
            else:
                for criterion in current_category.criteria:
                    ws[i + 1, column_increment] = criterion.value
                    column_increment += 1
                    
            if current_category.confidence != -2:
                ws[i + 1, column_increment] = current_category.confidence
                column_increment += 1
        
        if gold_standard != None:
            ws[i + 1, column_increment] = format_r_friendly(finalExtract[i].reviewer_gold_standard_answer)
            column_increment +=1
            if gold_standard.hasTrust:
                ws[i + 1, column_increment] = finalExtract[i].gold_standard_confidence
                column_increment +=1
            ws[i + 1, column_increment] = format_r_friendly(finalExtract[i].gold_standard_answer)
            column_increment +=1
            ws[i + 1, column_increment] = finalExtract[i].gold_standard_comparison
            column_increment +=1
            if gold_standard.hasMalignancy:
                ws[i + 1, column_increment] = format_r_friendly(finalExtract[i].reviewer_gold_standard_malignancy)
                column_increment +=1
                ws[i + 1, column_increment] = format_r_friendly(finalExtract[i].gold_standard_malignancy)
                column_increment +=1
                ws[i + 1, column_increment] = finalExtract[i].gold_standard_malignancy_comparison
                column_increment +=1
    
    safe_worksheet_save(folder_path, file_name1, ws)
    safe_worksheet_save(folder_path, file_name2, ws)
    

def get_data_to_download(studyId, status):
    
    viewmodel = ManageDownloadsViewModel()
    
    show_remarks = status == StudyStatus.test.value
    
    files = listdir_safe_and_sorted(os.path.join(getcwd(), 'results', str(studyId)))
    
    for filename in files:
        if (show_remarks or ('_study_data' in filename)):
            viewmodel.files_to_show = True
            viewmodel.files.append(filename)

    viewmodel.files = natsorted(viewmodel.files)
    
    return viewmodel
    
def get_result_file(studyId, filename):
    
    file = secure_filename(filename)
        
    filepath = os.path.join(getcwd(), 'results', str(studyId), file)
    
    #in case an evol hides filenames from front
    return (filepath, file)

def remove_result_file(studyId, filename):
    
    file = secure_filename(filename)
    
    filepath = os.path.join(getcwd(), 'results', str(studyId), file)    
    
    safe_remove_file(filepath)

def remove_all_result_files(studyId):
    
    folder_path = os.path.join(getcwd(), 'results', str(studyId))
    
    safe_remove_folder(folder_path)

def clear_data_folder(studyId):
    
    folder_path = os.path.join(getcwd(), 'data', str(studyId))

    safe_remove_folder(folder_path)

def clear_data(studyId):

    clear_all_answers(studyId)
    clear_all_cases(studyId)
    clear_all_prerequisites(studyId)
    clear_all_criteria(studyId)
    clear_all_categories(studyId)
    clear_non_admin_users(studyId)

    remove_case_images(studyId)
    remove_tutorial_images(studyId)
    remove_case_data(studyId)
    
    remove_all_result_files(studyId)
    clear_data_folder(studyId)
    clear_uploads(studyId)
        
    erase_study(studyId)

def delete_user(userId):
    delete_reviewer_by_id(userId)
    
def regenerate_password(userId):
    newPass = generate_password()
    s = gensalt()
    hashPass = hashpw(newPass.encode('utf-8'), s).decode('utf-8')
    update_password(userId, hashPass)
    
    return newPass

