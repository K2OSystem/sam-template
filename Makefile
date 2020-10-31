.PHONY: build

STACK_NAME ?= --stack-name sample-template
PROFILE ?= --profile sam-user
DEBUG ?= --debug


## docker 
up:
	docker-compose up -d --build

kill:
	docker-compose kill

reload: kill up

## docker-clean: docker remove all containers in stack
clean:
	docker-compose rm -fv --all
	docker-compose down --rmi local --remove-orphans


## local dynamodb

local-db-delete:
	aws dynamodb delete-table   --endpoint-url http://localhost:4566 --table-name Company
	aws dynamodb delete-table   --endpoint-url http://localhost:4566 --table-name CompanyDomain
	aws dynamodb delete-table   --endpoint-url http://localhost:4566 --table-name CompanyStaff
	aws dynamodb delete-table   --endpoint-url http://localhost:4566 --table-name PreStudent
	aws dynamodb delete-table   --endpoint-url http://localhost:4566 --table-name Sequences
	aws dynamodb delete-table   --endpoint-url http://localhost:4566 --table-name Session
	aws dynamodb delete-table   --endpoint-url http://localhost:4566 --table-name Student

local-db-create:
	aws dynamodb create-table --endpoint-url http://localhost:4566 --cli-input-json file://./docker/dynamodb/table/Company.json
	aws dynamodb create-table --endpoint-url http://localhost:4566 --cli-input-json file://./docker/dynamodb/table/CompanyDomain.json
	aws dynamodb create-table --endpoint-url http://localhost:4566 --cli-input-json file://./docker/dynamodb/table/CompanyStaff.json
	aws dynamodb create-table --endpoint-url http://localhost:4566 --cli-input-json file://./docker/dynamodb/table/PreStudent.json
	aws dynamodb create-table --endpoint-url http://localhost:4566 --cli-input-json file://./docker/dynamodb/table/Sequences.json
	aws dynamodb create-table --endpoint-url http://localhost:4566 --cli-input-json file://./docker/dynamodb/table/Session.json
	aws dynamodb create-table --endpoint-url http://localhost:4566 --cli-input-json file://./docker/dynamodb/table/Student.json

	aws dynamodb list-tables  --endpoint-url http://localhost:4566
	: # aws dynamodb describe-table --endpoint-url http://localhost:4566 --table-name Music
	: # aws dynamodb put-item --endpoint-url http://localhost:4566 --table-name SampleTable --item '{"Id": {"S": "test"}, "Column1": {"S": "test1"}, "Column2": {"S": "test2"}, "Column3": {"S": "test3"}}'

local-data:
	aws dynamodb batch-write-item --endpoint-url http://localhost:4566 --request-items file://./docker/dynamodb/data/Data_Company.json
	aws dynamodb batch-write-item --endpoint-url http://localhost:4566 --request-items file://./docker/dynamodb/data/Data_CompanyDomain.json
	aws dynamodb batch-write-item --endpoint-url http://localhost:4566 --request-items file://./docker/dynamodb/data/Data_CompanyStaff.json
	aws dynamodb batch-write-item --endpoint-url http://localhost:4566 --request-items file://./docker/dynamodb/data/Data_PreStudent.json
	aws dynamodb batch-write-item --endpoint-url http://localhost:4566 --request-items file://./docker/dynamodb/data/Data_Sequences.json
	aws dynamodb batch-write-item --endpoint-url http://localhost:4566 --request-items file://./docker/dynamodb/data/Data_Session.json
	aws dynamodb batch-write-item --endpoint-url http://localhost:4566 --request-items file://./docker/dynamodb/data/Data_Student.json

local-db-init: local-db-delete local-db-create local-data


aws-data:
	aws dynamodb batch-write-item --request-items file://./docker/dynamodb/data/Data_Company.json $(PROFILE) --region ap-northeast-1
	aws dynamodb batch-write-item --request-items file://./docker/dynamodb/data/Data_CompanyDomain.json $(PROFILE) --region ap-northeast-1
	aws dynamodb batch-write-item --request-items file://./docker/dynamodb/data/Data_CompanyStaff.json $(PROFILE) --region ap-northeast-1
	aws dynamodb batch-write-item --request-items file://./docker/dynamodb/data/Data_PreStudent.json $(PROFILE) --region ap-northeast-1
	aws dynamodb batch-write-item --request-items file://./docker/dynamodb/data/Data_Sequences.json $(PROFILE) --region ap-northeast-1
	aws dynamodb batch-write-item --request-items file://./docker/dynamodb/data/Data_Session.json $(PROFILE) --region ap-northeast-1
	aws dynamodb batch-write-item --request-items file://./docker/dynamodb/data/Data_Student.json $(PROFILE) --region ap-northeast-1
