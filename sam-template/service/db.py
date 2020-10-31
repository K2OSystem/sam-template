import base64
import json
import os
import re
import random
import string

import boto3

from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta

from decimal import Decimal
from boto3.dynamodb.types import Binary


# セッションタイムアウト期間（分）
SESSION_EXPIRE = 120
# アクセストークンタイムアウト期間（分）
ACCESS_TOKEN_EXPIRE = 100

ddb = None

# DynamoDBの設定。local用に環境変数によってendpoint切替
def dynamodb():
    global ddb
    if ddb != None:
        return ddb

    if os.environ['ENV'] == 'local':
        # print('local db')
        ddb = boto3.resource('dynamodb', endpoint_url=os.environ['ENDPOINT'])
    else:
        # print('prod db')
        ddb = boto3.resource('dynamodb')

    return ddb


# Dynamoデータ→JSON変換
def default(obj) -> object:
    if isinstance(obj, Decimal):
        if int(obj) == obj:
            return int(obj)
        else:
            return float(obj)
    elif isinstance(obj, Binary):
        return obj.value
    elif isinstance(obj, bytes):
        return obj.decode()
    elif isinstance(obj, set):
        return list(obj)
    try:
        return str(obj)
    except Exception:
        return None



def randomname(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


# Company
def find_company_all():
    table = dynamodb().Table('Company')
    res = table.scan()

    return res['Items']

def find_company(id):
    table = dynamodb().Table('Company')
    res = table.query(
        KeyConditionExpression=Key('id').eq(int(id))
    )

    return res['Items']

def find_company_by_url_param(param):
    table = dynamodb().Table('Company')
    res = table.query(
        IndexName="access_url-index",
        KeyConditionExpression=Key('access_url').eq(str(param))
    )

    return res['Items']

def put_company(name, code, limit_count=0, take_start=None, take_end=None, created=None, id=None, access_url=None):
    if created is None:
        created=str(datetime.now())
    if take_start is None:
        take_start=str(datetime.now())
    if take_end is None:
        take_end=str(datetime.now())
    if id is None:
        # シーケンス取得
        id = next_id('Company')
        # print(id)

    # 企業アクセスコード生成
    if access_url is None:
        for i in range(5):
            access_url = randomname(8)

            # 生成コードが未使用であることを確認
            company = find_company_by_url_param(access_url)
            if len(company) == 0:
                break
        else:
            raise ValueError('access url dupulicated')

    table = dynamodb().Table('Company')
    ret = table.put_item(
        Item={
            'id': id,
            'code': code,
            'name': name,
            'access_url': access_url,
            'limit_count': limit_count,
            'take_start': take_start,
            'take_end': take_end,
            'created': created,
            'updated': None,
        },
        ConditionExpression='attribute_not_exists(id) or attribute_not_exists(code)',
    )

    return id

def update_company(name, code, limit_count=0, take_start=None, take_end=None, updated=None, id=None, access_url=None):
    if updated is None:
        updated = datetime.now()
    if id is None:
        # シーケンス取得
        id = next_id('Company')
    # 企業アクセスコード生成
    if access_url is None:
        for i in range(5):
            access_url = randomname(8)

            # 生成コードが未使用であることを確認
            company = find_company_by_url_param(access_url)
            if len(company) == 0:
                break
        else:
            raise ValueError('access url dupulicated')
    if take_start is None:
        take_start = datetime.now()
    if take_end is None:
        take_end = datetime.now() + timedelta(weeks=24)

    table = dynamodb().Table('Company')
    res = table.update_item(
        Key = {'id': int(id)},
        UpdateExpression = "SET #name = :name, code = :code, limit_count = :limit, take_start = :s, take_end = :e, access_url = :url, updated = :u",
        ExpressionAttributeNames = {
            '#name': 'name'
        },
        ExpressionAttributeValues = {
            ":code": code,
            ":name": name,
            ":limit": limit_count,
            ":s": str(take_start),
            ":e": str(take_end),
            ":url": access_url,
            ":u": str(updated)
        },
        ReturnValues = "UPDATED_NEW"
    )

    return res


# CompanyStaff
def find_company_staff(company_id, email):
    table = dynamodb().Table('CompanyStaff')
    res = table.query(
        KeyConditionExpression=Key('company_id').eq(
            company_id) & Key('email').eq(email)
    )
    # return res['Items']
    return res['Items']

def find_company_staff_by_token(company_id, token):
    table = dynamodb().Table('CompanyStaff')
    res = table.query(
        IndexName="access_token-index",
        KeyConditionExpression=Key('company_id').eq(
            company_id) & Key('access_token').eq(token)
    )
    return res['Items']


def list_company_staff(company_id):
    table = dynamodb().Table('CompanyStaff')
    res = table.query(
        IndexName="company_id-index",
        KeyConditionExpression=Key('company_id').eq(company_id)
    )
    return res['Items']

def put_company_staff(email, name, company_id, token=None, token_expire=None, id=None, created=None):
    if created is None:
        created=str(datetime.now())
    if id is None:
        # シーケンス取得
        id = next_id('CompanyStaff')

    table = dynamodb().Table('CompanyStaff')
    table.put_item(
        Item={
            'company_id': company_id,
            'email': email,
            'id': id,
            'name': name,
            'access_token': token,
            'token_expire': token_expire,
            'created': created,
            'updated': None,
        },
        ConditionExpression='attribute_not_exists(id) or attribute_not_exists(email)',
    )

    return id

def update_company_staff(company_id, email, name, token=None, token_expire=None, id=None, updated=None):
    if updated is None:
        updated = str(datetime.now())
    if id is None:
        # シーケンス取得
        id = next_id('CompanyStaff')
    if token_expire is None:
        # システム時間を設定
        token_expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    expire = int(token_expire.timestamp())

    table = dynamodb().Table('CompanyStaff')
    res = table.update_item(
        Key = {'company_id': int(company_id), 'email': str(email)},
        UpdateExpression = "SET id = :id, #name = :name, access_token = :t, token_expire = :e, updated = :u",
        ExpressionAttributeNames = {
            '#name': 'name'
        },
        ExpressionAttributeValues = {
            ":id": id,
            ":name": name,
            ":t": token,
            ":e": expire,
            ":u": updated
        },
        ReturnValues = "UPDATED_NEW"
    )

    return res

def update_company_staff_token(company_id, email, token, expire=None):
    if expire is None:
        # システム時間を設定
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)

    updated = expire
    expire = int(expire.timestamp())

    table = dynamodb().Table('CompanyStaff')
    res = table.update_item(
        Key={'company_id': company_id, 'email': email},
        UpdateExpression="set access_token = :t, token_expire = :e, updated = :u",
        ExpressionAttributeValues={
            ":t": token,
            ":e": expire,
            # ":u": str(datetime.now())
            ":u": str(updated)
        },
        ReturnValues="UPDATED_NEW"
    )

    return res



# CompanyDomain
def find_company_domain(company_id, domain):
    table = dynamodb().Table('CompanyDomain')
    res = table.query(
        KeyConditionExpression=Key('company_id').eq(
            company_id) & Key('domain').eq(domain)
    )
    return res['Items']

def list_company_domain(company_id):
    table = dynamodb().Table('CompanyDomain')
    res = table.query(
        IndexName="company_id-index",
        KeyConditionExpression=Key('company_id').eq(company_id)
    )
    return res['Items']

def update_company_domain(company_id, domain, id=None, updated=None):
    if updated is None:
        updated=str(datetime.now())
    if id is None:
        # シーケンス取得
        id = next_id('CompanyDomain')
    # print(id)

    table = dynamodb().Table('CompanyDomain')
    table.update_item(
        Key = {'domain': domain, 'company_id': company_id},
        UpdateExpression = "SET id = :id, updated = :updated",
        ExpressionAttributeValues = {
            ":id": str(id),
            ":updated": updated,
        },
        # ConditionExpression='attribute_not_exists(id) and attribute_not_exists(domain)',
        ReturnValues="UPDATED_NEW"
    )

    return id


# Student
def find_student(company_id, email):
    table = dynamodb().Table('Student')
    res = table.query(
        KeyConditionExpression=Key('company_id').eq(
            company_id) & Key('email').eq(str(email))
    )
    return res['Items']

def find_student_by_id(company_id, id):
    table = dynamodb().Table('Student')

    try:
        res = table.query(
            IndexName="company_id-id-index",
            KeyConditionExpression=Key('company_id').eq(
                company_id) & Key('id').eq(id)
        )
    except:
        return []

    return res['Items']

def count_student(company_id):
    table = dynamodb().Table('Student')
    res = table.query(
        IndexName="company_id-index",
        KeyConditionExpression=Key('company_id').eq(company_id),
        Select='COUNT'
    )
    # print(res)
    return int(res['Count'])

def list_student(company_id):
    table = dynamodb().Table('Student')
    res = table.query(
        IndexName="company_id-index",
        KeyConditionExpression=Key('company_id').eq(
            company_id)
    )
    return res['Items']

def find_student_by_serial_code(serial_code):
    table = dynamodb().Table('Student')
    res = table.query(
        IndexName="serial_code-index",
        KeyConditionExpression=Key('serial_code').eq(
            serial_code)
    )
    return res['Items']

def put_student(company_id, email, name='', serial_code='-', employee_no='', score='', department_name='', id=None, created=None):
    if created is None:
        created=str(datetime.now())

    if id is None:
        id = next_id('Student')

    table = dynamodb().Table('Student')
    table.put_item(
        Item={
            'email': str(email),
            'company_id': company_id,
            'id': id,
            'name': name,
            'serial_code': serial_code,
            'employee_no': employee_no,
            'score': score,
            'department_name': department_name,
            'created': created,
            'updated': '',
        }
    )

    return id


def update_student(company_id, email, name='', serial_code='-', employee_no='', score='', department_name=''):
    """生徒情報更新
        id, createdは更新しない

    Args:
        company_id (int): 企業ID（キー）
        email (string): 生徒メールアドレス（キー）
        name (str, optional): 氏名. Defaults to ''.
        serial_code (str, optional): シリアルコード. Defaults to '-'.
        employee_no (str, optional): 識別ID. Defaults to ''.
        score (str, optional): TOEICスコア. Defaults to ''.
        department_name (str, optional): 部署名. Defaults to ''.

    Returns:
        [type]: [description]
    """

    table = dynamodb().Table('Student')
    res = table.update_item(
        Key={'email': str(email), 'company_id': company_id},
        UpdateExpression="SET #name = :name, serial_code = :serial_code, employee_no = :employee_no, department_name = :department_name, score = :score, updated = :updated",
        ExpressionAttributeNames={
            '#name': 'name'
        },
        ExpressionAttributeValues={
            ":name": name,
            ":employee_no": employee_no,
            ":department_name": department_name,
            ":score": score,
            ":serial_code": serial_code,
            ':updated': str(datetime.now()),
        },
        ReturnValues="UPDATED_NEW"
    )

    print(res['Attributes'])
    # print(res)

    return res

def update_student_serial_code(company_id, email, serial_code=''):
    """生徒情報更新（シリアルコードのみ）

    Args:
        company_id (int): 企業ID
        email (string): 生徒メールアドレス
        serial_code (string, optional): シリアルコード. Defaults to None.

    Returns:
        [type]: [description]
    """

    table = dynamodb().Table('Student')
    res = table.update_item(
        Key={'email': str(email), 'company_id': company_id},
        UpdateExpression="SET serial_code = :serial_code, updated = :updated",
        ExpressionAttributeValues={
            ":serial_code": serial_code,
            ':updated': str(datetime.now()),
        },
        ReturnValues="UPDATED_NEW"
    )

    print(str(res['Attributes']['serial_code']))

    return res


def delete_student(company_id, email):
    table = dynamodb().Table('Student')
    ret = table.delete_item(
        Key={
            'email': str(email),
            'company_id': company_id,
        }
    )

    return ret


# PreStudent
def find_pre_student(token):
    table = dynamodb().Table('PreStudent')
    res = table.query(
        KeyConditionExpression=Key('access_token').eq(token)
    )
    print('findPreStudent')
    return res['Items']


def put_pre_student(token, email, company_id, expire=None):
    """PreStudent登録

        expire未指定の場合、10分後を指定

    Args:
        token (string): アクセストークン
        email (string): メールアドレス
        company_id (int): 企業ID
        expire (datetime, optional): トークン有効期限. Defaults to None.
    """

    if expire is None:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)

    expire = int(expire.timestamp())

    table = dynamodb().Table('PreStudent')
    table.put_item(
        Item={
            'access_token': token,
            'email': str(email),
            'company_id': company_id,
            'token_expire': expire,
        }
    )


# Sequences
def next_id(table_name):
    table = dynamodb().Table('Sequences')
    res = table.update_item(
        Key={'table_name': table_name},
        UpdateExpression="ADD #name :increment",
        ExpressionAttributeNames={
            '#name': 'seq'
        },
        ExpressionAttributeValues={
            ":increment": int(1)
        },
        ReturnValues="UPDATED_NEW"
    )

    # print('table_name:' + table_name + ',sequence:' + str(res['Attributes']['seq']))

    return res['Attributes']['seq']


# Session
def find_session(id):
    table = dynamodb().Table('Session')

    try:
        res = table.query(
            KeyConditionExpression=Key('session_id').eq(id)
        )
    except:
        return []

    return res['Items']


def update_session_expire(id, expire=None):
    if expire is None:
        # システム時間を設定
        expire = datetime.now() + timedelta(minutes=SESSION_EXPIRE)

    expire = int(expire.timestamp())

    table = dynamodb().Table('Session')
    res = table.update_item(
        Key={'session_id': id},
        UpdateExpression="set expire = :e",
        ExpressionAttributeValues={
            ":e": expire
        },
        ReturnValues="UPDATED_NEW"
    )

    return res


def put_session(token, email, access_url, student_id='', expire=None, created=None):
    if expire is None:
        expire = datetime.now() + timedelta(minutes=SESSION_EXPIRE)

    if created is None:
        created = str(datetime.now())

    expire = int(expire.timestamp())

    table = dynamodb().Table('Session')
    ret = table.put_item(
        Item={
            'session_id': token,
            'email': str(email),
            'access_url': access_url,
            'student_id': student_id,
            'expire': expire,
            'created': created,
        },
        ConditionExpression='attribute_not_exists(id) or attribute_not_exists(email)',
    )
    # print(ret)
