#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 28 16:55:41 2025

@author: jacques
"""

#general imports
from sqlalchemy import String
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class ReviewerPOCO(Base):
    __tablename__ = "reviewer"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    login: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(30))
    admin: Mapped[bool]
    remaining_cases: Mapped[int]
    
    def __repr__(self) -> str:
        return f"Reviewer(id={self.id!r}, name={self.name!r}, login={self.login!r}, admin={self.admin!r})"
    
    def __init__(self, name, login, password, admin):
        self.name = name
        self.login = login
        self.password = password
        self.admin = admin
        self.remaining_cases = 0

class CategoryPOCO(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[int]
    trust: Mapped[int]

class CriterionPOCO(Base):
    __tablename__ = "criterion"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    tutorial_path: Mapped[str] = mapped_column(String(200))
    type: Mapped[int]
    category: Mapped[int]
    malignity: Mapped[bool]
    
    def __repr__(self) -> str:
        return f"Criterion(id={self.id!r}, name={self.name!r}, tutorial_path={self.tutorial_path!r}, type={self.type!r})"
    
    def __init__(self, name, path, critType, critCategory, mal):
        self.name = name
        self.path = path
        self.type = critType
        self.category = critCategory
        self.malignity = mal

class CasePOCO(Base):
    __tablename__ = "study_case"
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(10))
    gold_standard: Mapped[int] = mapped_column(ForeignKey("criterion.id"))
    
    def __repr__(self) -> str:
        return f"Case(id={self.id!r}, path={self.path!r}, name={self.name!r})"
    
    def __init__(self, path, name, gld_std):
        self.path = path
        self.name = name
        self.gold_standard = gld_std

class AnswerPOCO(Base):
    __tablename__ = "answer"
    id: Mapped[int] = mapped_column(primary_key=True)
    study_case: Mapped[int] = mapped_column(ForeignKey("study_case.id"))
    reviewer: Mapped[int] = mapped_column(ForeignKey("reviewer.id"))
    completed: Mapped[bool]
    
    def __repr__(self) -> str:
        return f"Answer(id={self.id!r}, case={self.study_case!r}, reviewer={self.reviewer!r}, completed={self.completed!r})"
    
    def __init__(self, case, rev):
        self.study_case = case
        self.reviewer = rev
        
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
        self.value = 0
        
        
        
    