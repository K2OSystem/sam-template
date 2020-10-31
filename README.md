# Install
https://docs.aws.amazon.com/ja_jp/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html

## aws sam cli
``` shell
brew tap aws/tap
brew install aws-sam-cli
```

## python3
```
brew install python
```

https://www.python.org/downloads/

 
 


# build docker
ローカル環境要のサービスを構築します。
* localstack
* dynamoDB-admin
```
make up
```

### localstackの起動確認  
https://localhost:4566/  
にアクセスし、{"status": "running"}と表示されればOK

### dynamoDB-adminの確認  
http://localhost:8001/  
にアクセスし、画面が表示されればOK  


ポート番号が使われている場合は、下記ファイルのポート番号を任意の値に変更

* docker/dynamodb-admin/Dockerfile
```
 EXPOSE 任意のポート
```
* docker-compose.yml
```
 ports
  - 任意のポート:8001
```


# setting

## AWS credential
SAMのデプロイを行うためにAWSアカウントの設定を行う。

https://docs.aws.amazon.com/ja_jp/ses/latest/DeveloperGuide/create-shared-credentials-file.html



## python
``` shell
cd python

# 仮想環境設定
python3 -m venv venv
# 仮想環境有効化
source venv/bin/activate
# 環境変数登録
export PYTHONPATH=./:./service

# for Win
py -m venv venv
.\venv\Scripts\activate
$ENV:PYTHONPATH+="./;./service;"

# 以降はmac、Win同様
# pip更新（初回のみ）
python -m pip install --upgrade pip
# ローカル実行用ライブラリインストール
pip install -r requirements.txt
# UT用ライブラリインストール
pip install pytest pytest-cov

```

### ディレクトリ構成
```bash
.
├── Makefile                        <-- Make to automate build (for docker)
├── README.md                       <-- This instructions file
├── sam-template                    <-- Source code for a lambda function python
│   └── Makefile                    <-- Make to automate build (for SAM)
│   ├── hello_world                 <-- Lambda function code
│   │   ├── __init__.py
│   │   ├── app.py                  <-- Lambda function code
│   │   └── requirements.txt        <-- required lib
│   ├── service                     <-- Lambda Layer
│   │   ├── db.py                   <-- Lambda DB Utility
│   │   └── requirements.txt        <-- required lib
│   ├── tests                       <-- Unit tests
│   └── venv                        <-- virtual env
├── env.json                        <-- SAM local用 環境変数
└── template.yaml                   <-- SAM template
```


# デプロイ
## credentialの設定
aws user  


## deploy
``` shell
cd python

make build

make deploy

```

## SAM BUILD
Makefile内のPROFILEを各自のcredentialの値に変更します。  

```
make build
```

## SAM DEPLOY
```
make deploy
```

以下サービスがデプロイされます。
* CloudFormation
* API Gateway
  * オーソライザー
* Lambda
  * アプリケーション
  * レイヤー
* DynamoDB

## Cleanup
AWSへデプロイした場合、のクリア方法  
1．AWSのコンソールから削除  
1-1.コンソールにサインインし、CloudFormationのページを開く
1-2.スタックのページを開く
1-3.該当のスタック名を選択し、画面上部にある「削除」をクリック
  デプロイされた関連するAWSサービスの内容がすべて削除されます。

2．CLIによるコマンドでの削除  

```
cd python
make clean
```


## テストデータ登録
``` shell
# テストデータ登録（テーブルの削除、作成、データ登録）
python tests/unit/db_setup.py 

# dynamoDB-adminにアクセスし、テーブルおよびデータが入っていることを確認できます。  
http://localhost:8001/
```



## SAM ローカルテスト
以下のコマンドでローカル環境にAPI Gateway、Lambdaの環境がデプロイされます。
```
make local
```

APIへのアクセス例
```
http://127.0.0.1:3000/1/staff/auth
```

CTRL+C で停止


## SAM ローカルログ
```
sam logs -n HelloWorldFunction --stack-name sample-serverless-backend --tail
```


## ローカル Unit Test
``` shell
cd python
# 実施済みであれば下記は不要
python -m venv venv
pip install -r requirements.txt

# テスト用ライブラリインストール
pip install pytest pytest-cov
# テストデータ登録
python tests/unit/db_setup.py 

# テスト実施
make test
```

## ローカル UTカバレッジ
```
pip install pytest-cov

pytest tests/ -v -s --cov=hello_world --cov-report=html
```
