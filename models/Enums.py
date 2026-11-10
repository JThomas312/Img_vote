# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 16:27:49 2026

@author: j.thomas
"""

from enum import Enum

#values for criteria, dependency to the database
class CriterionValue(Enum):
    false = 0
    true = 1
    na = 2
    unanswered = -1

#type of category, dependency to the database
class CategoryType(Enum):
    yes_no = 1
    one_of = 2
    numerical_value = 3

#type of action, dependency to the front (category edition)
class Action(Enum):
    remove = 'remove'
    edit = 'edit'
 
#possible statuses for a study, dependency to the database
class StudyStatus(Enum):
    stopped = 'stopped'
    categories_done = 'categories_done'
    uploads_done = 'uploads_done'
    ready = 'ready'
    test = 'test'
    ongoing = 'ongoing'
    paused = 'paused'
    ended = 'ended'
    
class DemographicsVal(Enum):
    
    female = 1
    male = 2
    other = 3
    lessThanAYear = 1
    oneToThreeYears = 2
    threeToTenYears = 3
    moreThanTenYears = 4
    never = 1
    severalAYear = 2
    severalAMonth = 3
    severalAWeek = 4
    everyDay = 5