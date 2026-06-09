#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 15:08:18 2025

@author: jacques
"""

from flask import Flask
from flask import redirect
from flask import url_for
from flask import request
from flask import render_template
from flask import session
from flask import jsonify
from flask import send_file

from flask_session import Session
from cachelib.file import FileSystemCache

from flask_wtf.csrf import CSRFProtect

from datetime import datetime

from os import getcwd
import os.path
from bcrypt import checkpw

from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename

from utilities.useful import sanitize

from controller.UserController import user_for_home
from controller.UserController import user_for_login
from controller.UserController import modify_password
from controller.UserController import study_has_gold_standard
from controller.UserController import user_for_learning

from controller.AdminController import create_user
from controller.AdminController import delete_user
from controller.AdminController import regenerate_password
from controller.AdminController import find_name_and_login
from controller.AdminController import categories_for_editing
from controller.AdminController import category_for_editing
from controller.AdminController import create_empty_category
from controller.AdminController import update_category
from controller.AdminController import delete_category
from controller.AdminController import check_category
from controller.AdminController import check_categories
from controller.AdminController import categories_rollback
from controller.AdminController import delete_criterion
from controller.AdminController import save_criterion
from controller.AdminController import save_criterion_malignancy
from controller.AdminController import change_criterion
from controller.AdminController import save_prerequisite
from controller.AdminController import change_prerequisite
from controller.AdminController import optional_category_allowed
from controller.AdminController import gold_standard_category_allowed
from controller.AdminController import upload_status
from controller.AdminController import unzip_and_move
from controller.AdminController import move
from controller.AdminController import remove_case_images
from controller.AdminController import remove_tutorial_images
from controller.AdminController import remove_case_data
from controller.AdminController import check_uploads_and_create_cases
from controller.AdminController import upload_rollback
from controller.AdminController import data_for_distribution
from controller.AdminController import handle_distribution
from controller.AdminController import distribution_rollback
from controller.AdminController import clear_data
from controller.AdminController import get_data_for_export
from controller.AdminController import get_data_to_download
from controller.AdminController import get_result_file
from controller.AdminController import remove_result_file
from controller.AdminController import remove_all_result_files
from controller.AdminController import get_remarks_for_export
from controller.AdminController import clear_optional_answers

from controller.CaseController import caseForDisplay
from controller.CaseController import caseForLearning
from controller.CaseController import safeguardProgress
from controller.CaseController import safeguardDiagnosis
from controller.CaseController import safeguardRemarks
from controller.CaseController import criterion_for_tutorial
from controller.CaseController import checkProgress

UPLOAD_FOLDER = os.path.join(getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'zip'}

app = Flask(__name__)
pkfile = open(os.path.join(getcwd(), 'private_key.txt'), encoding="utf-8")
pkcontent = pkfile.read()
pk = pkcontent.removeprefix('-----BEGIN RSA PRIVATE KEY-----\n').removesuffix('\n-----END RSA PRIVATE KEY-----\n')
app.secret_key = pk
pkfile.close()

csrf = CSRFProtect(app)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SESSION_TYPE"] = "cachelib"
SESSION_SERIALIZATION_FORMAT = 'json'
SESSION_CACHELIB = FileSystemCache(threshold=500, cache_dir=os.path.join(getcwd(), "sessions"))
app.config.from_object(__name__)
# Initialize Flask-Session
Session(app)

@app.route("/")
def index():
    if 'username' in session:
        return redirect(url_for('user_home'))
    else:
        return redirect(url_for('login'))

@app.route('/login/', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error, logout=False)


@app.route('/logout/', methods=['POST', 'GET'])
def logout():
    error = None
    logout = True
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
            logout = False
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    session.clear()
    return render_template('login.html', error=error, logout=logout)

@app.route('/user_home/', methods=['GET'])
def user_home():    
    if 'username' in session:
        (user, study_name) = user_for_home(session["username"])
        with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
            status = fr.read().replace('\n', '')
        if (status != 'stopped') and status != 'ended':
            try:
                with open(os.path.join(getcwd(), 'persistence', 'study_end.txt'), 'r', encoding="utf-8") as f:
                   try:
                       study_end = datetime.strptime(f.read(), '%Y-%m-%d')
                       remaining_days = (study_end - datetime.today()).days
                   except:
                       remaining_days = -1
            except FileNotFoundError:
                remaining_days = -1
        else:
            remaining_days = -1
        if user.admin:
            remaing_users = user.remaing_users
            total_users = user.total_users
            otherUsers = user.otherUsers
            display_others = len(otherUsers) > 0
            return render_template('admin_home.html', remaining_days=remaining_days, username=user.name, studyname=study_name, study_status=status, remaing_users=remaing_users, total_users=total_users, otherUsers=otherUsers, display_others=display_others)
        else:   
            if status == 'ongoing' or status == 'test':
                items = user.items
                remaining_items = user.remaing_items             
                return render_template('user_home.html', username=user.name, studyname=study_name, remaining_items=remaining_items, remaining_days=remaining_days, items=items)
            else:
                if status == 'ended' and study_has_gold_standard():
                    learnViewModel = user_for_learning(user.userId)
                    return render_template('user_learning.html', username=user.name, studyname=study_name, correct_answers=learnViewModel.correct_answers, total_answers=learnViewModel.total_answers, items=learnViewModel.items)
                else:
                    return render_template('study_ended.html', username=user.name)
    else:
        return(redirect(url_for('login')))

@app.route('/category_configuration/', methods=['GET'])
def category_configuration():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                status_error = None
                deletion_error = None
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status != 'stopped':
                    status_error = 'Categories are already locked, current status is: ' + status 
                pending_categories = categories_for_editing()
                return render_template('category_configuration.html', status_error=status_error, deletion_error=deletion_error, categories=pending_categories)                        
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/add_category/', methods=['GET'])
def add_category():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status != 'stopped':
                    return(redirect(url_for('category_configuration')))                
                category_id = create_empty_category()
                return(redirect('/edit_category/' + str(category_id)))                       
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))



@app.route('/edit_category/<categoryId>', methods=['GET', 'POST'])
def edit_category(categoryId):
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                error = None
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status != 'stopped':
                    return(redirect(url_for('category_configuration')))
                optional_allowed = optional_category_allowed(categoryId)
                gold_standard_allowed = gold_standard_category_allowed(categoryId)
                if request.method == 'GET':
                    categoryViewModel = category_for_editing(categoryId)
                    return render_template('category_edition.html', category=categoryViewModel, error=error, formError=None, optional_allowed=optional_allowed, gold_standard_allowed=gold_standard_allowed)
                    
                if request.method == 'POST':
                    answer = (request.form).copy()
                    answer.pop('csrf_token')
                    formError = check_category(categoryId, answer)
                    if formError != None:
                        categoryViewModel = category_for_editing(categoryId)
                        return render_template('category_edition.html', category=categoryViewModel, error=error, formError=formError, optional_allowed=optional_allowed, gold_standard_allowed=gold_standard_allowed)
                    return(redirect(url_for('category_configuration')))
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/finish_category_configuration/', methods=['GET'])
def finish_category_configuration():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status != 'stopped':
                    return(redirect(url_for('category_configuration')))
                (errors, incorrect_categories) = check_categories()
                if len(errors) > 0 or len(incorrect_categories) > 0:
                    return render_template('category_errors.html', errors=errors, incorrect_categories=incorrect_categories, nb_incorrect_categories=len(incorrect_categories))                        
                with open(os.path.join(getcwd(), 'persistence/study_status.txt'), 'w', encoding="utf-8") as fw:
                    fw.write('categories_done')
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/rollback_categories/', methods=['GET'])
def rollback_categories():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status == 'categories_done':
                    if request.method == 'GET':
                        categories_rollback()
                        with open(os.path.join(getcwd(), 'persistence/study_status.txt'), 'w', encoding="utf-8") as fw:
                            fw.write('stopped')
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/manage_uploads/', methods=['GET', 'POST'])
def manage_uploads():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status != 'categories_done':
                    return(redirect(url_for('user_home')))
                if request.method == 'GET':
                    uploadStatusVM = upload_status()
                    return render_template('manage_uploads.html', upload_status=uploadStatusVM, errors=None)
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))
    
@app.route('/upload_case_images/', methods=['GET', 'POST'])
def upload_case_images():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status != 'categories_done':
                    return(redirect(url_for('user_home')))
                
                if request.method == 'GET':
                    return render_template('upload_case_images.html', errors=None)
                
                if request.method == 'POST':
                    # check if the post request has the file part
                    if 'file' not in request.files:
                        return redirect(request.url)
                    file = request.files['file']
                    # If the user does not select a file, the browser submits an
                    # empty file without a filename.
                    if file.filename == '':
                        return redirect(request.url)
                    if file and allowed_file(file.filename):
                        save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'case_images.zip')
                        file.save(save_path)
                        problems = unzip_and_move(save_path, 'case')
                        if problems != None:
                            return render_template('upload_case_images.html', errors=problems)
                    return redirect(url_for('manage_uploads'))
                    
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))
    
@app.route('/upload_tutorial_images/', methods=['GET', 'POST'])
def upload_tutorial_images():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status != 'categories_done':
                    return(redirect(url_for('user_home')))
                
                if request.method == 'GET':
                    return render_template('upload_tutorial_images.html')
                
                if request.method == 'POST':
                    # check if the post request has the file part
                    if 'file' not in request.files:
                        return redirect(request.url)
                    file = request.files['file']
                    # If the user does not select a file, the browser submits an
                    # empty file without a filename.
                    if file.filename == '':
                        return redirect(request.url)
                    if file and allowed_file(file.filename):
                        save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'tutorial_images.zip')
                        file.save(save_path)
                        problems = unzip_and_move(save_path, 'tutorial')
                        if problems != None:
                            return render_template('upload_case_images.html', errors=problems)
                    return redirect(url_for('manage_uploads'))
                
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/upload_case_data/', methods=['GET', 'POST'])
def upload_case_data():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status != 'categories_done':
                    return(redirect(url_for('user_home')))
                
                if request.method == 'GET':
                    return render_template('upload_case_data.html')
                
                if request.method == 'POST':
                    # check if the post request has the file part
                    if 'file' not in request.files:
                        return redirect(request.url)
                    file = request.files['file']
                    # If the user does not select a file, the browser submits an
                    # empty file without a filename.
                    if file.filename == '':
                        return redirect(request.url)
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = 'case_data.' + filename.rsplit('.', 1)[1]
                        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename.rsplit('.', 1)[0])
                        file.save(save_path)
                        move(save_path, os.path.join(getcwd(), 'data', filename))
                    return redirect(url_for('manage_uploads'))
                
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/delete_case_images/', methods=['GET'])
def delete_case_images():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status != 'categories_done':
                    return(redirect(url_for('user_home')))
                remove_case_images()
                return redirect(url_for('manage_uploads'))

        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/delete_tutorial_images/', methods=['GET'])
def delete_tutorial_images():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status != 'categories_done':
                    return(redirect(url_for('user_home')))
                remove_tutorial_images()
                return redirect(url_for('manage_uploads'))

        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/delete_case_data/', methods=['GET'])
def delete_case_data():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status != 'categories_done':
                    return(redirect(url_for('user_home')))
                remove_case_data()
                return redirect(url_for('manage_uploads'))

        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/finish_uploading/', methods=['GET'])
def finish_uploading():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status == 'categories_done':
                    errors = check_uploads_and_create_cases()
                    if errors != None:
                        uploadStatusVM = upload_status()
                        return render_template('manage_uploads.html', upload_status=uploadStatusVM, errors=errors)
                    with open(os.path.join(getcwd(), 'persistence/study_status.txt'), 'w', encoding="utf-8") as fw:
                        fw.write('uploads_done')
                return redirect(url_for('user_home'))

        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/rollback_uploads/')
def rollback_uploads():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status == 'uploads_done':
                    upload_rollback()
                    with open(os.path.join(getcwd(), 'persistence/study_status.txt'), 'w', encoding="utf-8") as fw:
                        fw.write('categories_done')

        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/manage_reviewer_distribution/', methods=['GET', 'POST'])
def manage_reviewer_distribution():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status == 'uploads_done':
                    if request.method == 'GET':
                        viewModel = data_for_distribution()
                        return render_template('manage_reviewer_distribution.html', VM=viewModel)
                    if request.method == 'POST':    
                        distribution_method = request.form['distribution']
                        reviewer_per_case = request.form['reviewer_per_case']
                        cases_per_reviewer = request.form['cases_per_reviewer']
                        percentage = request.form['percentage']
                        handle_distribution(distribution_method, reviewer_per_case, cases_per_reviewer, percentage)
                        with open(os.path.join(getcwd(), 'persistence/study_status.txt'), 'w', encoding="utf-8") as fw:
                            fw.write('ready')
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/rollback_distribution/', methods=['GET'])
def rollback_distribution():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status == 'ready':
                    if request.method == 'GET':
                        distribution_rollback()
                        with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'w', encoding="utf-8") as fw:
                            fw.write('uploads_done')
        return(redirect(url_for('user_home'))) 
    else:
        return(redirect(url_for('login')))

@app.route('/begin_study/', methods=['GET', 'POST'])
def begin_study():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                error = None
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if request.method == 'GET':
                    if status != 'ready':
                        error = 'Study has already begun, current status is: ' + status 
                    return render_template('study_begining.html', error=error, nameError=None, ansError=None, test=False)
                if request.method == 'POST':
                    if status == 'ready':
                        nameError = None
                        dateError = None
                        
                        name = request.form['study_name']
                        endresponse = request.form['study_end']
                        
                        if name == '':
                            nameError = 'Your study needs a name\n'
                        if endresponse == '':
                            dateError = 'You study needs an endDate'
                        
                        if nameError != None or dateError != None:
                            return render_template('study_begining.html', error=None, nameError=nameError, dateError=dateError, test=False)
                        
                        endDate = datetime.strptime(endresponse, '%Y-%m-%d')
                        
                        with open(os.path.join(getcwd(), 'persistence', 'study_end.txt'), 'w', encoding="utf-8") as fw:
                            fw.write(endDate.strftime('%Y-%m-%d'))
                        
                        with open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'w', encoding="utf-8") as fw:
                            fw.write(name)
                            
                        with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'w', encoding="utf-8") as fw:
                            fw.write('ongoing')
                            
        return(redirect(url_for('user_home'))) 
    else:
        return(redirect(url_for('login')))

@app.route('/begin_testing/', methods=['GET', 'POST'])
def begin_testing():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                error = None
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if request.method == 'GET':
                    if status != 'ready':
                        error = 'Study has already begun, current status is: ' + status 
                    return render_template('study_begining.html', error=error, nameError=None, dateError=None, test=True)
                if request.method == 'POST':
                    if status == 'ready':
                        nameError = None
                        dateError = None
                        
                        name = request.form['study_name']
                        endresponse = request.form['study_end']
                        
                        if name == '':
                            nameError = 'Your study needs a name\n'
                        if endresponse == '':
                            dateError = 'You study needs an endDate'
                        
                        if nameError != None or dateError != None:
                            return render_template('study_begining.html', error=None, nameError=nameError, dateError=dateError, test=True)
                        
                        endDate = datetime.strptime(endresponse, '%Y-%m-%d')
                        
                        with open(os.path.join(getcwd(), 'persistence', 'study_end.txt'), 'w', encoding="utf-8") as fw:
                            fw.write(endDate.strftime('%Y-%m-%d'))
                        
                        with open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'w', encoding="utf-8") as fw:
                            fw.write(name)
                            
                        with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'w', encoding="utf-8") as fw:
                            fw.write('test')
                            
        return(redirect(url_for('user_home'))) 
    else:
        return(redirect(url_for('login')))

@app.route('/test_rollback/<step>', methods=['GET'])
def test_rollback(step):
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status == 'test':
                    if request.method == 'GET':
                        with open(os.path.join(getcwd(), 'persistence', 'study_end.txt'), 'w', encoding="utf-8") as fw:
                            fw.write('')
                        
                        with open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'w', encoding="utf-8") as fw:
                            fw.write('')
                        
                        if step == 'distribution':
                            distribution_rollback()
                            with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'w', encoding="utf-8") as fw:
                                fw.write('uploads_done')
                        
                        if step == 'uploads':
                            distribution_rollback()
                            upload_rollback()
                            with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'w', encoding="utf-8") as fw:
                                fw.write('categories_done')
                        
                        if step == 'categories':
                            distribution_rollback()
                            upload_rollback()
                            categories_rollback()
                            with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'w', encoding="utf-8") as fw:
                                fw.write('stopped')
                        
        return(redirect(url_for('user_home'))) 
    else:
        return(redirect(url_for('login')))

@app.route('/pause_study/')
def pause_study():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status == 'ongoing':
                    with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'w', encoding="utf-8") as fw:
                        fw.write('paused')
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/resume_study/')
def resume_study():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status == 'paused':
                    with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'w', encoding="utf-8") as fw:
                        fw.write('ongoing')
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/confirm_end/')
def confirm_end():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status == 'paused':
                    return render_template('confirm_end.html')
        return redirect(url_for('user_home'))
    else:
        return(redirect(url_for('login')))
    
@app.route('/end_study/')
def end_study():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status == 'paused':
                    with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'w', encoding="utf-8") as fw:
                        fw.write('ended')
                        clear_optional_answers()
        return(redirect(url_for('user_home')))
    else:
        return(redirect(url_for('login')))
    
@app.route('/export_data/')
def export_data():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                get_data_for_export()
        return '', 204
    else:
        return(redirect(url_for('login')))

@app.route('/manage_downloads/')
def manage_downloads():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status in ['test', 'ongoing', 'paused', 'ended']:
                    viewmodel = get_data_to_download(status)
                    return render_template('manage_downloads.html', ViewModel=viewmodel)
        return(redirect(url_for('user_home')))
    else:
        return(redirect(url_for('login')))

@app.route('/download_result_data/<filename>')
def download_result_data(filename):
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                (file_path, name) = get_result_file(filename)
                return send_file(file_path, download_name=name, as_attachment=True)
        return '', 204
    else:
        return(redirect(url_for('login')))

@app.route('/delete_result_data/<filename>')
def delete_result_data(filename):
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                remove_result_file(filename)
        return '', 204
    else:
        return(redirect(url_for('login')))

@app.route('/delete_all_results/')
def confirm_delete_all_result_files():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                return render_template('confirm_delete_result_files.html')
        return redirect(url_for('user_home'))
    else:
        return(redirect(url_for('login')))

@app.route('/delete_result_files/')
def delete_all_result_files():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                remove_all_result_files()
        return redirect(url_for('user_home'))
    else:
        return(redirect(url_for('login')))
    
@app.route('/export_remarks/')
def export_remarks():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                get_remarks_for_export()
        return '', 204
    else:
        return(redirect(url_for('login')))
    
@app.route('/confirm_clear_users/')   
def confirm_clear_users():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                return render_template('confirm_clear_users.html')
        return redirect(url_for('user_home'))
    else:
        return(redirect(url_for('login')))

@app.route('/clear_users/')   
def clear_users():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status == 'ended':
                    clear_data()
                    with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'w', encoding="utf-8") as fw:
                        fw.write('stopped')
        return redirect(url_for('user_home'))
    else:
        return(redirect(url_for('login')))    
    

@app.route('/change_password/', methods=['POST', 'GET'])
def change_password():
    if 'userId' in session:    
        error = None
        if request.method == 'POST':
            if valid_login(session['username'], request.form['oldPass']):
                if request.form['newPass'] == request.form['confirmPass']:
                    modify_password(session['userId'], request.form['newPass'])
                    return redirect(url_for('user_home'))
                else:
                    error = 'New passwords do not match'
            else:
                error = 'Invalid password'
        return render_template('change_password.html', error=error)
    else:
        return redirect(url_for('login'))

@app.route('/reset_password/<userId>')
def reset_password(userId):
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                newPass = regenerate_password(userId)
                (usrName, usrLogin) = find_name_and_login(userId)
                return render_template("password_reset.html", userName=usrName, userLogin=usrLogin, newPassword=newPass)
        return(redirect(url_for('user_home')))
    else:
        return redirect(url_for('login'))

@app.route('/confirm_delete_user/<userId>')
def confirm_user_deletion(userId):
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                (usrName, usrLogin) = find_name_and_login(userId)
                return render_template('confirm_delete_user.html', name=usrName, login=usrLogin, delid=userId)
        return(redirect(url_for('user_home')))
    else:
        return redirect(url_for('login'))
    
    
@app.route('/delete_user/<userId>')
def delete_one_user(userId):
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                delete_user(userId)
        return(redirect(url_for('user_home')))
    else:
        return redirect(url_for('login'))

@app.route('/new_user/', methods=['GET'])
def new_user():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                return render_template("new_user.html")
        return(redirect(url_for('user_home')))
    else:
        return redirect(url_for('login'))

@app.route('/new_user/', methods=['POST'])
def new_user_creation():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read()
                error = None
                login = request.form['login']
                fullname = request.form['fullname']
                admin = request.form['admin'] == '1'
                full_review = request.form['full_review'] == '1'
                password = ''
                if sanitize(fullname) and sanitize(login):
                    try:
                        password = create_user(login, fullname, admin, status, full_review)
                    except Exception as e:
                        error = f"{e}"
                else:
                    error = 'invalid user name or login'
                return render_template('user_created.html', error=error, login=login, fullname=fullname, newPass=password)
        return(redirect(url_for('user_home')))
    else:
        return redirect(url_for('login'))


@app.route('/case_display/<case>', methods=['GET'])
def case_display(case):
    if 'userId' in session:
        caseVM = caseForDisplay(session['userId'], case)
        return render_template('case_display.html', ViewModel=caseVM)
    else:
        return redirect(url_for('login'))

@app.route('/case_learning/<case>', methods=['GET'])
def case_learning(case):
    if 'userId' in session:
        with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
            status = fr.read().replace('\n', '')
        if status == 'ended':
            caseVM = caseForLearning(session['userId'], case)
            return render_template('case_learning.html', ViewModel=caseVM)
        return redirect(url_for('user_home'))
    else:
        return redirect(url_for('login'))
 
@app.route('/tutorial/<tuto>')
def display_tutorial(tuto):
    if 'userId' in session:
        img_tuto = criterion_for_tutorial(tuto)
        return render_template('tutorial.html', img_tuto=img_tuto)
    else:
        return '', 404    
 
@app.route('/safeguard_category/')
def safeguard_category():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                cat_id = int(request.args.get('cat_id'))
                value = request.args.get('value')
                field = request.args.get('field')
                
                update_category(cat_id, value, field)
                return '', 204
            
        return(redirect(url_for('user_home')))
    else:
        return redirect(url_for('login'))

@app.route('/safeguard_criterion/')
def safeguard_criterion():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                cat_id = int(request.args.get('cat_id'))
                name = request.args.get('name')
                malignancy = request.args.get('malignancy')
                crit_id = save_criterion(cat_id, name, malignancy)
                return jsonify(result=crit_id)
            
        return(redirect(url_for('user_home')))
    else:
        return redirect(url_for('login'))

@app.route('/edit_criterion/')
def edit_criterion():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                cat_id = int(request.args.get('cat_id'))
                crit_id = request.args.get('crit_id')
                name = request.args.get('name')
                malignancy = request.args.get('malignancy')
                action = request.args.get('action')
                change_criterion(cat_id, crit_id, name, malignancy, action)
                return '', 204
            
        return(redirect(url_for('user_home')))
    else:
        return redirect(url_for('login'))

@app.route('/safeguard_criterion_malignancy/')
def safeguard_criterion_malignancy():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                crit_id = int(request.args.get('crit_id'))
                malignancy = request.args.get('malignancy')
                save_criterion_malignancy(crit_id, malignancy)
                return '', 204
            
        return(redirect(url_for('user_home')))
    else:
        return redirect(url_for('login'))

@app.route('/safeguard_prerequisite/')
def safeguard_prerequisite():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                cat_id = int(request.args.get('cat_id'))
                name = request.args.get('name')
                crit_id = save_prerequisite(cat_id, name)
                return jsonify(result=crit_id)
            
        return(redirect(url_for('user_home')))
    else:
        return redirect(url_for('login'))

@app.route('/edit_prerequisite/')
def edit_prerequisite():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                cat_id = int(request.args.get('cat_id'))
                pre_id = request.args.get('pre_id')
                name = request.args.get('name')
                action = request.args.get('action')
                new_id = change_prerequisite(cat_id, pre_id, name, action)
                return jsonify(result=new_id)
            
        return(redirect(url_for('user_home')))
    else:
        return redirect(url_for('login'))
 
@app.route('/remove_category/<cat_id>')
def remove_category(cat_id):
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                delete_category(cat_id)
                return(redirect(url_for('category_configuration')))    
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))

@app.route('/remove_criterion/<crit_id>')
def remove_criterion(crit_id):
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                delete_criterion(crit_id)
                return(redirect(url_for('category_configuration')))    
        return(redirect(url_for('user_home')))    
    else:
        return(redirect(url_for('login')))    
 
@app.route('/safeguard_model/')    
def safeguard_model():
    if 'userId' in session:
        case_id = request.args.get('case_id')
        criterion_id = request.args.get('criterion_id')
        value = request.args.get('value')
        safeguardProgress(session['userId'], case_id, criterion_id, value)
        checkProgress(session['userId'], int(request.args.get('case_id')))
        return '', 204

@app.route('/safeguard_diagnosis/')    
def safeguard_diagnosis():
    if 'userId' in session:
        case_id = request.args.get('case_id')
        criterion_id = request.args.get('criterion_id')
        value = request.args.get('value')
        category = request.args.get('category')
        safeguardDiagnosis(session['userId'], case_id, criterion_id, value, category)
        checkProgress(session['userId'], int(request.args.get('case_id')))
        return '', 204

@app.route('/safeguard_remarks/')    
def safeguard_remarks():
    if 'userId' in session:
        case_id = request.args.get('case_id')
        value = request.args.get('value')
        safeguardRemarks(session['userId'], case_id, value)
        return '', 204
    
def valid_login(username, password):
    if not sanitize(username):
        return False
    user = user_for_login(username)
    if user == None:
        return False
    ePass = password.encode('utf-8')
    eHash = user.hashPass.encode('utf-8')
    return checkpw(ePass, eHash)

def log_the_user_in(username):
    (user, study_name) = user_for_home(username)
    session['username'] = username
    session['userId'] = user.userId
    session['admin'] = user.admin
    return (redirect(url_for('user_home')))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
