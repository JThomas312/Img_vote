#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 28 16:55:41 2025

@author: jacques
"""

#general imports
from datetime import datetime
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import func

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class StudyPOCO(Base):
    __tablename__ = "study"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    endDate: Mapped[datetime] = mapped_column(insert_default=func.today())
    status: Mapped[str] = mapped_column(String(20))
    has_gold_standard: Mapped[bool]
    has_malignancy: Mapped[bool]
    has_tutorial: Mapped[bool]
    repartition: Mapped[int]
    repartition_value: Mapped[int]

class ReviewerPOCO(Base):
    __tablename__ = "reviewer"
    id: Mapped[int] = mapped_column(primary_key=True)
    study: Mapped[int] = mapped_column(ForeignKey("study.id"))
    name: Mapped[str] = mapped_column(String(50))
    login: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(30))
    admin: Mapped[bool]
    full_review: Mapped[bool]
    remaining_cases: Mapped[int]
    
    def __repr__(self) -> str:
        return f"Reviewer(id={self.id!r}, name={self.name!r}, login={self.login!r}, admin={self.admin!r})"
    
    def __init__(self, name, login, password, admin, full_review):
        self.name = name
        self.login = login
        self.password = password
        self.admin = admin
        self.full_review = full_review
        self.remaining_cases = 0

class CategoryPOCO(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(primary_key=True)
    study: Mapped[int] = mapped_column(ForeignKey("study.id"))
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[int]
    has_tutorial: Mapped[bool]
    has_trust: Mapped[bool]
    has_na: Mapped[bool]
    optional: Mapped[bool]
    has_gold_standard: Mapped[bool]
    has_malignancy: Mapped[bool]
    
    def __repr__(self) -> str:
        return f"Category(id={self.id!r}, name={self.name!r}, type={self.type!r}, has_tutorial={self.has_tutorial!r}, has_trust={self.has_trust!r}, has_na={self.has_na!r}, optional={self.optional!r}, has_gold_standard={self.has_gold_standard!r}, has_malignancy={self.has_malignancy!r})"
    
    def __init__(self, name='', catType=0, has_tutorial=False, has_trust=False, has_na=False, optional=False, has_gold_standard=False, has_malignancy=False):
        self.name = name
        self.type = catType
        self.has_tutorial = has_tutorial
        self.has_trust = has_trust
        self.has_na = has_na
        self.optional = optional
        self.has_gold_standard = has_gold_standard
        self.has_malignancy = has_malignancy


class CriterionPOCO(Base):
    __tablename__ = "criterion"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    tutorial_path: Mapped[str] = mapped_column(String(200))
    category: Mapped[int] = mapped_column(ForeignKey("category.id"))
    is_trust: Mapped[bool]
    malignancy: Mapped[bool]
    
    def __repr__(self) -> str:
        return f"Criterion(id={self.id!r}, name={self.name!r}, tutorial_path={self.tutorial_path!r}, category={self.category!r})"
    
    def __init__(self, name, path, critCategory, trust, mal):
        self.name = name
        self.tutorial_path = path
        self.category = critCategory
        self.is_trust = trust
        self.malignancy = mal

class PrerequisitePOCO(Base):
    __tablename__ = "prerequisite"
    category: Mapped[int] = mapped_column(ForeignKey("category.id"), primary_key=True)
    criterion: Mapped[int] = mapped_column(ForeignKey("criterion.id"), primary_key=True)
    
    def __repr__(self) -> str:
        return f"Prerequisite(category={self.category!r}, criterion={self.criterion!r})"
    
    def __init__(self, category, criterion):
        self.category = category
        self.criterion = criterion

class CasePOCO(Base):
    __tablename__ = "study_case"
    id: Mapped[int] = mapped_column(primary_key=True)
    study: Mapped[int] = mapped_column(ForeignKey("study.id"))
    path: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(10))
    gold_standard: Mapped[int] = mapped_column(ForeignKey("criterion.id"))
    
    def __repr__(self) -> str:
        return f"Case(id={self.id!r}, path={self.path!r}, name={self.name!r})"
    
    def __init__(self, path, name, gld_std=None):
        self.path = path
        self.name = name
        self.gold_standard = gld_std

class AnswerPOCO(Base):
    __tablename__ = "answer"
    id: Mapped[int] = mapped_column(primary_key=True)
    study_case: Mapped[int] = mapped_column(ForeignKey("study_case.id"))
    reviewer: Mapped[int] = mapped_column(ForeignKey("reviewer.id"))
    name: Mapped[str] = mapped_column(String(10))
    completed: Mapped[bool]
    
    def __repr__(self) -> str:
        return f"Answer(id={self.id!r}, case={self.study_case!r}, reviewer={self.reviewer!r}, completed={self.completed!r})"
    
    def __init__(self, case, rev, name='', completed = False):
        self.study_case = case
        self.reviewer = rev
        self.name = name
        self.completed = completed
        
class AnswerCriterionPOCO(Base):
    __tablename__ = "answer_to_criterion"
    answer: Mapped[int] = mapped_column(ForeignKey("answer.id"), primary_key=True)
    criterion: Mapped[int] = mapped_column(ForeignKey("criterion.id"), primary_key=True)
    value: Mapped[int]
    
    def __repr__(self) -> str:
        return f"AnswerCriterionPOCO(answer={self.answer!r}, criterion={self.criterion!r}, value={self.value!r})"
    
    def __init__(self, answer, criterion):
        self.answer = answer
        self.criterion = criterion
        self.value = -1
        
        
        
    