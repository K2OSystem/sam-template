import os

import pytest

from . import db_setup

@pytest.fixture(scope='session', autouse=True)
def session_fixture():
    # print("テスト全体の前処理")
    os.environ['ENV'] = 'local'
    os.environ['ENDPOINT'] = 'http://localhost:4566'
    os.environ['CORS'] = 'http://localhost:3001'

    db_setup.for_local()
    yield
    # print("テスト全体の後処理")

@pytest.fixture(scope='module', autouse=True)
def module_fixture():
    # print("モジュールの前処理")
    yield
    # print("モジュールの後処理")


@pytest.fixture(scope='class', autouse=True)
def class_fixture():
    # print("クラスの前処理")
    yield
    # print("クラスの後処理")


@pytest.fixture(scope='function', autouse=True)
def function_fixture():
    # print("関数の前処理")
    yield
    # print("関数の後処理")


@pytest.fixture(scope='module', autouse=True)
def init():
    print(os.environ['ENV'])
    # print(os.environ['ENDPOINT'])
