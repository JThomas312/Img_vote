# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 16:27:49 2026

@author: j.thomas
"""

from enum import Enum

class CriterionValue(Enum):
    false = 0
    true = 1
    na = 2
    unanswered = -1
    unanswered_trust = 0

class CategoryType(Enum):
    yes_no = 1
    one_of = 2
    numerical_value = 3
