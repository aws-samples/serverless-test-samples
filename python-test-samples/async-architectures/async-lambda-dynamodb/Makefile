PIP ?= pip3

target:
	$(info ${HELP_MESSAGE})
	@exit 0

clean: ##=> Deletes current build environment and latest build
	$(info [*] Who needs all that anyway? Destroying environment....)
	rm -rf ./.aws-sam/ ./venv/

checkOSDependencies:
	python3 --version || grep "3.9" || (echo "Error: Requires Python 3.9" && exit 1)

all: clean build

install: checkOSDependencies
	${PIP} install virtualenv
	python3 -m venv venv

deps:
	source ./venv/bin/activate && ${PIP} install -r tests/integration/requirements.txt

build: ##=> Same as package except that we don't create a ZIP
	source ./venv/bin/activate && sam build --use-container

deploy.g: ##=> Guided deploy that is typically run for the first time only
	source ./venv/bin/activate &&  sam build --use-container
	source ./venv/bin/activate &&  sam deploy --guided

deploy: ##=> Deploy app using previously saved SAM CLI configuration
	source ./venv/bin/activate &&  sam build --use-container
	source ./venv/bin/activate &&  sam deploy

deploy.p: ##=> Deploy app to a production environment
	source ./venv/bin/activate && sam deploy --parameter-overrides EnvType=prod

test: check-stack-name
	source ./venv/bin/activate && AWS_SAM_STACK_NAME=$(AWS_SAM_STACK_NAME) && python3 -m pytest -s tests/integration -v

check-stack-name:
ifndef AWS_SAM_STACK_NAME
	$(error usage: make AWS_SAM_STACK_NAME=<your-aws-stack-name> test)
endif

delete: 
	sam delete

#############
#  Helpers  #
#############

define HELP_MESSAGE

	Usage: make <command>

	Commands:

	build     Build Lambda function dependencies
	deploy.g  Deploy guided (for initial deployment)
	deploy    Deploy subsequent changes

	install   Install Pipenv, application and dev dependencies defined in Pipfile
	shell     Spawn a virtual environment shell
	deps      Install project dependencies locally
	test      Run integration test against cloud environment (requires AWS_SAM_STACK_NAME variable) 

	clean     Cleans up local build artifacts including zip files
	delete    Delete stack from AWS

endef
