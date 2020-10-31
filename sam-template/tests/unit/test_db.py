import json
import os

import pytest

from service import db

from datetime import datetime, timedelta


def test_find_company_all_data(monkeypatch):
    data = db.find_company_all()
    # print('data', data)
    assert len(data) > 0

def test_find_company_data(monkeypatch):
    data = db.find_company(1)
    # print('data', data)
    assert len(data) == 1

def test_find_company_staff_data(monkeypatch):
    data = db.find_company_staff(1, 'email1@gmail.com')
    # print('data', data)
    assert len(data) == 1


def test_list_company_staff_data(monkeypatch):
    data = db.list_company_staff(1)
    # print('data', data)

    assert len(data) > 1


def test_find_company_domain_data(monkeypatch):
    data = db.find_company_domain(1, 'gmail.com')
    print('data', data)
    assert len(data) == 1


def test_list_company_domain_data(monkeypatch):
    data = db.list_company_domain(1)
    print('data', data)

    assert len(data) >= 1


def test_find_student_by_id_data(monkeypatch):
    # 生徒情報取得
    data = db.find_student_by_id(1, 1)
    # print('data', data)
    assert len(data) == 1

def test_find_student_by_id_nodata(monkeypatch):
    # 生徒情報取得
    data = db.find_student_by_id(1, 0)
    # print('data', data)
    assert len(data) == 0


def test_find_student_data(monkeypatch):
    # 生徒情報取得
    data = db.find_student(1, 'student1-9@gmail.com')
    # print('data', data)
    assert len(data) == 1

def test_find_student_nodata(monkeypatch):
    # 生徒情報取得
    data = db.find_student(1, 0)
    # print('data', data)
    assert len(data) == 0

def test_count_student_data(monkeypatch):
    # 生徒情報取得
    data = db.count_student(1)
    print('data', data)

    assert data > 2

    # # 1件
    # data = db.count_student(2)
    # assert data == 1

    # 0件
    data = db.count_student(4)
    assert data == 0


def test_list_student_data(monkeypatch):
    # 生徒情報取得
    data = db.list_student(1)
    print('data', data)

    assert len(data) > 2



def test_update_company_staff_token(monkeypatch):
    try:
        data = db.update_company_staff_token(1, 'email1@gmail.com', 'TOKEN_12345')
        print('data', data)
    except Exception as e:
        print(e)
        assert False

    assert True
