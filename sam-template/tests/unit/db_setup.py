import json
import os
from datetime import datetime, timedelta, timezone

import boto3
from service import db

ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566')


def test_delete_table():
    print('delete table')
    ddb.Table('Company').delete()
    ddb.Table('CompanyStaff').delete()
    ddb.Table('CompanyDomain').delete()
    ddb.Table('PreStudent').delete()
    ddb.Table('Student').delete()
    ddb.Table('Session').delete()
    ddb.Table('Sequences').delete()


def test_create_table():
    print('create table')
    ddb.create_table(
        TableName = 'Company',
        KeySchema = [
            { "AttributeName": "id", "KeyType": "HASH" },
        ],
        AttributeDefinitions = [
            { "AttributeName": "id", "AttributeType": "N" },
            { "AttributeName": "access_url", "AttributeType": "S" },
        ],
        GlobalSecondaryIndexes = [
            {
                "IndexName": "access_url-index",
                "KeySchema": [
                    { "AttributeName": "access_url", "KeyType": "HASH" }
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": { "WriteCapacityUnits": 1, "ReadCapacityUnits": 1 }
            }
        ],
        ProvisionedThroughput = { "WriteCapacityUnits": 5, "ReadCapacityUnits": 1 }
    )

    ddb.create_table(
        TableName = 'CompanyDomain',
        KeySchema = [
            {"KeyType": "HASH", "AttributeName": "domain"},
            {"KeyType": "RANGE", "AttributeName": "company_id"}
        ],
        AttributeDefinitions = [
            {"AttributeName": "domain", "AttributeType": "S"},
            {"AttributeName": "company_id", "AttributeType": "N"}
        ],
        GlobalSecondaryIndexes = [
            {
                "IndexName": "company_id-index",
                "KeySchema": [
                    { "AttributeName": "company_id", "KeyType": "HASH" }
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": { "WriteCapacityUnits": 1, "ReadCapacityUnits": 1 }
            }
        ],
        ProvisionedThroughput = { "WriteCapacityUnits": 1, "ReadCapacityUnits": 1 }
    )

    ddb.create_table(
        TableName = 'CompanyStaff',
        KeySchema = [
            {"KeyType": "HASH", "AttributeName": "email"},
            {"KeyType": "RANGE", "AttributeName": "company_id"}
        ],
        AttributeDefinitions = [
            {"AttributeName": "email", "AttributeType": "S"},
            {"AttributeName": "company_id", "AttributeType": "N"},
            {"AttributeName": "access_token", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes = [
            {
                "IndexName": "company_id-index",
                "KeySchema": [
                    { "AttributeName": "company_id", "KeyType": "HASH" }
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": { "WriteCapacityUnits": 1, "ReadCapacityUnits": 1 }
            },
            {
                "IndexName": "access_token-index",
                "KeySchema": [
                    { "AttributeName": "access_token", "KeyType": "HASH" },
                    { "AttributeName": "company_id", "KeyType": "RANGE" },
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": { "WriteCapacityUnits": 1, "ReadCapacityUnits": 1 }
            },
        ],
        ProvisionedThroughput = { "WriteCapacityUnits": 1, "ReadCapacityUnits": 1 }
    )

    ddb.create_table(
        TableName = 'PreStudent',
        KeySchema = [
            { "AttributeName": "access_token", "KeyType": "HASH" },
        ],
        AttributeDefinitions = [
            { "AttributeName": "access_token", "AttributeType": "S" },
        ],
        ProvisionedThroughput = { "WriteCapacityUnits": 1, "ReadCapacityUnits": 1 }
    )

    ddb.create_table(
        TableName = 'Sequences',
        KeySchema = [
            { "AttributeName": "table_name", "KeyType": "HASH" },
        ],
        AttributeDefinitions = [
            { "AttributeName": "table_name", "AttributeType": "S" },
        ],
        ProvisionedThroughput = { "WriteCapacityUnits": 1, "ReadCapacityUnits": 1 }
    )

    ddb.create_table(
        TableName = 'Session',
        KeySchema = [
            { "AttributeName": "session_id", "KeyType": "HASH" },
        ],
        AttributeDefinitions = [
            { "AttributeName": "session_id", "AttributeType": "S" },
        ],
        ProvisionedThroughput = { "WriteCapacityUnits": 1, "ReadCapacityUnits": 1 }
    )

    ddb.create_table(
        TableName = 'Student',
        KeySchema = [
            {"KeyType": "HASH", "AttributeName": "email"},
            {"KeyType": "RANGE", "AttributeName": "company_id"}
        ],
        AttributeDefinitions = [
            {"AttributeName": "email", "AttributeType": "S"},
            {"AttributeName": "company_id", "AttributeType": "N"},
            {"AttributeName": "id", "AttributeType": "N"},
        ],
        GlobalSecondaryIndexes = [
            {
                "IndexName": "company_id-index",
                "KeySchema": [
                    { "AttributeName": "company_id", "KeyType": "HASH" }
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": { "WriteCapacityUnits": 1, "ReadCapacityUnits": 1 }
            },
            {
                "IndexName": "company_id-id-index",
                "KeySchema": [
                    { "AttributeName": "company_id", "KeyType": "HASH" },
                    { "AttributeName": "id", "KeyType": "RANGE" },
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": { "WriteCapacityUnits": 1, "ReadCapacityUnits": 1 }
            },
        ],
        ProvisionedThroughput = { "WriteCapacityUnits": 1, "ReadCapacityUnits": 1 }
    )


def test_data_load():
    """[summary]
    """

    print('data load')

    access_url = 'ABC'
    company_id =  1

    # UTC
    now = datetime.utcnow()
    now = datetime(now.year, now.month, now.day)

    # Company
    print('# Company')
    # 1件目はテストコードで用いるので、id、url等固定化しておく
    try:
        take_start = str(now)
        take_end = str(now + timedelta(weeks=100))
        db.put_company('テスト企業', 'TESTCOM', 50, take_start, take_end, id=1, access_url=access_url)

    except Exception as e:
        print(e)

    for i in range(2, 10):
        name = 'name ' + str(i)
        code = 'code ' + str(i)
        limit_count = 5
        take_start = str(now)
        take_end = str(now + timedelta(weeks=100))

        try:
            print('    ', name, code, limit_count, take_start, take_end, i)
            db.put_company(name, code, limit_count, take_start, take_end, id=i)
        except Exception as e:
            print(e)



    # CompanyDomain
    print('# CompanyDomain')
    for i in range(1, 10):
        try:
            db.update_company_domain(i, 'gmail.com')
            db.next_id('CompanyDomain')
        except Exception as e:
            print(e)
    

    # CompanyStaff
    print('# CompanyStaff')
    for i in range(1, 10):
        email = 'email{}@gmail.com'.format(i)
        name = 'テスト担当者{}'.format(i)
        token = 'staff{}'.format(i)
        token_expire = now + timedelta(weeks=100)
        print('    ', email, name, token, token_expire, i)
        try:
            db.update_company_staff(company_id, email, name, token, token_expire, i)
            db.next_id('CompanyStaff')
        except Exception as e:
            print(e)

        # Session
        session_token = 'sessionstaff{}'.format(i)
        try:
            db.put_session(session_token, email, access_url, student_id='', expire=token_expire)
        except Exception as e:
            print(e)


    # PreStudent, Student
    print('# PreStudent, Student')
    for i in range(1, 10):
        email = 'student1-{}@gmail.com'.format(i)
        token = 'student{}'.format(i)
        expire = now + timedelta(weeks=100)

        try:
            print('    ', token, email, company_id, expire)
            db.put_pre_student(token, email, company_id, expire)
        except Exception as e:
            print(e)

        # Student
        name = 'テスト生徒{}'.format(i)
        serial_code = '-'
        employee_no = '社員番号{}'.format(i)
        toeic = '123'
        dep = 'テスト部署'
        try:
            print('    ', company_id, email, name, serial_code, employee_no, toeic, dep, i)
            db.put_student(company_id, email, name, serial_code, employee_no, toeic, dep, i)
            db.next_id('Student')
        except Exception as e:
            print(e)

        # Session
        session_token = 'sessionstudent{}'.format(i)
        try:
            db.put_session(session_token, email, access_url, student_id=i, expire=expire)
        except Exception as e:
            print(e)


def generate_random_bytes():
    # from Crypto.Random import get_random_bytes
    # return get_random_bytes(16)
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


def for_local():
    try:
        test_delete_table()
    except Exception as e:
        print(e)

    try:
        test_create_table()
    except Exception as e:
        print(e)

    test_data_load()

def for_aws():
    # AWS環境用
    # ※別途credethialとしてDynamoDBの更新権限が必要

    os.environ['ENV'] = 'dev'
    global ddb
    # AWS環境用の場合エンドポイントの指定をなくした状態で再設定
    ddb = boto3.resource('dynamodb')

    # AWS環境はSAMでテーブルを作成するため、テーブルの作り直しを行わない。
    test_data_load()
 

if __name__ == '__main__':
    os.environ['ENV'] = 'local'
    os.environ['ENDPOINT'] = 'http://localhost:4566'

    # ローカル環境構築（テーブル）
    for_local()
    # AWS環境データ反映
    # for_aws()
