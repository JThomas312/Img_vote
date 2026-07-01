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
    unanswered_trust = 0

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
    

