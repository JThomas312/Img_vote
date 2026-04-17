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
from flask import send_file

from flask_session import Session
from cachelib.file import FileSystemCache

from flask_wtf.csrf import CSRFProtect

from datetime import datetime

from re import match
from PIL import Image
import base64
import io
from os import getcwd
import os.path
from bcrypt import checkpw

from werkzeug.middleware.proxy_fix import ProxyFix

from markupsafe import escape
from controller.UserController import user_for_home
from controller.UserController import user_for_login
from controller.UserController import modify_password
from controller.AdminController import delete_user
from controller.AdminController import regenerate_password
from controller.AdminController import find_name_and_login
from controller.AdminController import create_user
from controller.AdminController import clear_data
from controller.AdminController import get_data_for_export
from controller.CaseController import caseForDisplay
from controller.CaseController import caseForDiagnosis
from controller.CaseController import init_data_study_start
from controller.CaseController import saveProgress
from controller.CaseController import safeguardProgress
from controller.CaseController import safeguardDiagnosis
from controller.CaseController import criterion_for_tutorial
from controller.CaseController import checkProgress


app = Flask(__name__)
# pkfile = open(os.path.join(getcwd(), 'private_key.txt'), encoding="utf-8")
# pkcontent = pkfile.read()
# pk = pkcontent.removeprefix('-----BEGIN RSA PRIVATE KEY-----\n').removesuffix('\n-----END RSA PRIVATE KEY-----\n')
pk = b'a62a3f0ecba55677e0e738b1ac3f6bb14333a9683a2de43d0146e06f95b5cdf9'
app.secret_key = pk
# pkfile.close()

csrf = CSRFProtect(app)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

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
        user = user_for_home(session["username"])
        with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
            status = fr.read().replace('\n', '')
        if (status != 'stopped') and status != 'ended':
            with open(os.path.join(getcwd(), 'persistence', 'study_end.txt'), 'r', encoding="utf-8") as f:
               try:
                   study_end = datetime.strptime(f.read(), '%Y-%m-%d')
                   remaining_days = (study_end - datetime.today()).days
               except:
                   remaining_days = -1
        else:
            remaining_days = -1
        if user.admin:
            remaing_users = user.remaing_users
            total_users = user.total_users
            otherUsers = user.otherUsers
            display_others = len(otherUsers) > 0
            return render_template('admin_home.html', remaining_days= remaining_days, username=user.name, study_status=status, remaing_users=remaing_users, total_users=total_users, otherUsers=otherUsers, display_others=display_others)
        else:   
            if status == 'ongoing':
                items = user.items
                remaining_items = user.remaing_items             
                return render_template('user_home.html', username=user.name, remaining_items=remaining_items, remaining_days=remaining_days, items=items)
            else:
                return render_template('study_ended.html', username=user.name)
    else:
        return(redirect(url_for('login')))

@app.route('/begin_study/', methods=['GET'])
def begin_study():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                error = None
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                if status != 'stopped':
                    error = 'Study has already begun, current status is: ' + status 
                return render_template('study_begining.html', error=error)
        return(redirect(url_for('user_home'))) 
    else:
        return(redirect(url_for('login')))

@app.route('/begin_study/', methods=['POST'])
def start_study():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                with open(os.path.join(getcwd(), 'persistence', 'study_status.txt'), 'r', encoding="utf-8") as fr:
                    status = fr.read().replace('\n', '')
                endDate = datetime.strptime(request.form['study_end'], '%Y-%m-%d')
                if status == 'stopped':
                    init_data_study_start()
                    with open(os.path.join(getcwd(), 'persistence', 'study_end.txt'), 'w', encoding="utf-8") as fw:
                        fw.write(endDate.strftime('%Y-%m-%d'))
                    
                    with open(os.path.join(getcwd(), 'persistence', 'study_name.txt'), 'w', encoding="utf-8") as fw:
                        fw.write(request.form['study_name'])
                        
                    with open(os.path.join(getcwd(), 'persistence/study_status.txt'), 'w', encoding="utf-8") as fw:
                        fw.write('ongoing')
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
        return(redirect(url_for('user_home')))
    else:
        return(redirect(url_for('login')))
    
@app.route('/export_data/')
def export_data():
    if 'userId' in session:
        if 'admin' in session:
            if session['admin']:
                (file_path, name) = get_data_for_export()
                return send_file(file_path, download_name=name, as_attachment=True)
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
            if valid_login(session['username'],
                           request.form['oldPass']):
                if request.form['newPass'] == request.form['confirmPass']:
                    modify_password(session['userId'], request.form['newPass'])
                    return redirect(url_for('user_home'))
                else:
                    error = 'New passwords do not match'
            else:
                error = 'Invalid password'
        # the code below is executed if the request method
        # was GET or the credentials were invalid
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
                password = ''
                if sanitize(fullname) and sanitize(login):
                    try:
                        password = create_user(login, fullname, admin, status)
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
        (caseVM, criteriaTitles, unanswered, nextcase) = caseForDisplay(session['userId'], case)
        return render_template("case_display.html", case_id=case, case_name=caseVM.name, nb_imgs=len(caseVM.imgs), imgs=caseVM.imgs, imgs_sizes=caseVM.imgs_sizes, criteria=caseVM.criteria, titles=criteriaTitles, nbTitles=len(criteriaTitles), unanswered=unanswered, nextcase=nextcase)
    else:
        return redirect(url_for('login'))
    
@app.route('/case_diagnose/<case>', methods=['GET'])
def case_diagnose(case):
    if 'userId' in session:
        (caseVM, criteriaTitles, unanswered, nextcase) = caseForDiagnosis(session['userId'], case)
        return render_template("case_diagnose.html", case_id=case, case_name=case, nb_imgs=len(caseVM.imgs), imgs=caseVM.imgs, imgs_sizes=caseVM.imgs_sizes, criteria=caseVM.criteria, titles=criteriaTitles, nbTitles=len(criteriaTitles), unanswered=unanswered, nextcase=nextcase)
    else:
        return redirect(url_for('login'))
 
@app.route('/tutorial/<tuto>')
def display_tutorial(tuto):
    if 'userId' in session:
        img_tuto = criterion_for_tutorial(tuto)
        return render_template("tutorial.html", img_tuto=img_tuto)
    else:
        return '', 404    
 
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
        critType = request.args.get('type')
        safeguardDiagnosis(session['userId'], case_id, criterion_id, value, critType)
        checkProgress(session['userId'], int(request.args.get('case_id')))
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
    user = user_for_home(username)
    session['username'] = username
    session['userId'] = user.userId
    session['admin'] = user.admin
    return (redirect(url_for('user_home')))
    
def sanitize(userinput):
    return bool(match(r'^[a-zA-Z0-9_\s]{3,20}$', userinput))

