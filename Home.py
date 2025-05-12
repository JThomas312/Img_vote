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
from PIL import Image
import base64
import io

from markupsafe import escape
from controller.UserController import user_for_home
from controller.CaseController import caseForDisplay

app = Flask(__name__)

app.secret_key = '984af3d11405d3cf9a5a143320b8938dcc2045e35c10a38a00637b581b75bb00'


# def hello_world():
#     return "<p>Hello, World!</p>"

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
    return render_template('login.html', error=error)

@app.route('/user_home/')
def user_home():
    if 'username' in session:
        user = user_for_home(session["username"])
        items = user.items
        remaining_items = user.remaing_items
        remaining_days = 666    
        return render_template('user_home.html', username=session["username"], remaining_items=remaining_items, remaining_days=remaining_days, items=items)
    else:
        return(redirect(url_for('login')))

@app.route('/case_display/<case>', methods=['GET'])
def display_case(case):
    if 'userId' in session:
        (caseVM, criteriaTitles) = caseForDisplay(session['userId'], case)
        return render_template("case_display.html", case_name=case, nb_imgs=len(caseVM.imgs), imgs=caseVM.imgs, imgs_sizes=caseVM.imgs_sizes, criteria=caseVM.criteria, titles=criteriaTitles, nbTitles=len(criteriaTitles))
    else:
        return redirect(url_for('login'))



def valid_login(username, password):
    return True

def log_the_user_in(username):
    user = user_for_home(username)
    session['username'] = username
    session['userId'] = user.userId
    return (redirect(url_for('user_home')))
    

