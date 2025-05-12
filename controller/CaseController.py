#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 11:55:48 2025

@author: jacques
"""

from os import getcwd
from os import listdir

from PIL import Image
import base64
import io
from openpyxl import load_workbook

from random import randint


class CaseViewModel():
    def __init__(self, nbCategories):
        self.imgs = []
        self.imgs_sizes = []
        self.criteria = [[] for i in range(nbCategories)]
    imgs: list()
    imgs_sizes: list((int, int))
    criteria: list(list((str, bool, bytearray)))
    
def caseForDisplay(userId, case):
    #fix path
    data_path = '/dummy_data/'
    #data_path = '/data/'
    #load delimiting words from config file
    delimitations = ['Pattern', 'Signs']
    path = getcwd() + data_path + '/Img_data/' + case
    tutorial_folder = getcwd() + data_path + '/tutorial_criteria/'
    img_files = listdir(path)

    caseVM = CaseViewModel(len(delimitations))
    
    
    #load data from database instead
    for img_file in img_files:
        im = Image.open(path + '/' + img_file)
        data = io.BytesIO()
        im.save(data, 'JPEG')
        encoded_img_data = base64.b64encode(data.getvalue())
        caseVM.imgs.append(encoded_img_data.decode('utf-8'))
        w, h = im.size
        caseVM.imgs_sizes.append((w, h))
    
    criteriaWB = load_workbook(filename = getcwd() + '/data/Criterias DPO.xlsx')
    criteriaWS = criteriaWB.active
    #end load
    
    criteriaIndex = -1
    
    currentList = []
    
    # temp value for creating dummy data until database is plugged in
    val = True
    for row in criteriaWS.iter_rows(min_row=1, max_col=1):   
        for cell in row:
            if randint(1,2) == 1:
                val = not val
            if cell.value in delimitations:
                criteriaIndex += 1
                currentList = caseVM.criteria[criteriaIndex]
            else:
                tutorial_slide_path = tutorial_folder + delimitations[criteriaIndex] + '/' + cell.value + '.jpeg'
                try:
                    slide_im = Image.open(tutorial_slide_path)
                    data = io.BytesIO()
                    slide_im.save(data, 'JPEG')
                    slide_encoded_img_data = base64.b64encode(data.getvalue())
                    currentList.append((cell.value, val, slide_encoded_img_data.decode('utf-8')))
                except:
                    currentList.append((cell.value, val, bytearray()))
                
    
    #working demo for SFP dance images
    # caseVM.criteria.append(('Jacques', True))
    # caseVM.criteria.append(('Eitan', True))
    # caseVM.criteria.append(('Maureen', False))
    # caseVM.criteria.append(('Mathilde', False))
    # caseVM.criteria.append(('Apolline', False))
    # caseVM.criteria.append(('Porté', True))
    
    return (caseVM, delimitations)
    