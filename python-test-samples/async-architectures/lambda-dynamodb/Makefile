BASE := $(shell /bin/pwd)
CODE_COVERAGE = 72
PIPENV ?= pipenv

#############
#  SAM vars	#
#############

target:
	$(info ${HELP_MESSAGE})
	@exit 0

clean: ##=> Deletes current build environment and latest build
	$(info [*] Who needs all that anyway? Destroying environment....)
	rm -rf ./.aws-sam/

all: clean build

install:
	$(info [*] Installing pipenv)
	@pip install pipenv --upgrade
	$(MAKE) dev

dev:
	$(info [*] Installing pipenv project dependencies)
	@$(PIPENV) install
	@$(PIPENV) install -d

shell:
	@$(PIPENV) shell

build: ##=> Same as package except that we don't create a ZIP
	sam build --use-container

deploy.guided: ##=> Guided deploy that is typically run for the first time only
	sam deploy --guided

deploy: ##=> Deploy app using previously saved SAM CLI configuration
	sam deploy

deploy.prod: ##=> Deploy app to a production environment
	sam deploy --parameter-overrides EnvType=prod

invoke: ##=> Run SAM Local function with a given event payload
	@sam local invoke TextTransformer --event events/putObject.json

unit-test: ##=> Run pytest
	POWERTOOLS_METRICS_NAMESPACE="MyServerlessApplication" $(PIPENV) run python -m pytest --cov . --cov-report term-missing --cov-fail-under $(CODE_COVERAGE) tests/ -vv

integration-test: check-stack-name
	AWS_SAM_STACK_NAME=$(AWS_SAM_STACK_NAME) python -m pytest -s tests/integration -v

check-stack-name:
ifndef AWS_SAM_STACK_NAME
	$(error usage: make AWS_SAM_STACK_NAME=<your-aws-stack-name> integration-test)
endif

ci: ##=> Run full workflow - Install deps, build deps, and deploy
	$(MAKE) dev
	$(MAKE) build
	$(MAKE) deploy

hurry: ##=> Run full workflow for the first time
	$(MAKE) install
	$(MAKE) build
	$(MAKE) deploy.guided

#############
#  Helpers  #
#############

define HELP_MESSAGE
	Environment variables to be aware of or to hardcode depending on your use case:

	NETWORK
		Default: ""
		Info: Docker Network to connect to when running Lambda function locally

	Common usage:

	...::: Installs Pipenv, application and dev dependencies defined in Pipfile :::...
	$ make install

	...::: Builds Lambda function dependencies:::...
	$ make build

	...::: Deploy for the first time :::...
	$ make deploy.guided

	...::: Deploy subsequent changes :::...
	$ make deploy

	...::: Run Pytest under tests/ with pipenv :::...
	$ make unit-test

	...::: Run integration test against cloud resources :::...
	$ make AWS_SAM_STACK_NAME=<your-aws-stack-name> integration-test

	...::: Spawn a virtual environment shell :::...
	$ make shell

	...::: Cleans up the environment - Deletes Virtualenv, ZIP builds and Dev env :::...
	$ make clean

	...::: Run full workflow from installing Pipenv, dev and app deps, build, and deploy :::...
	$ make ci

	Advanced usage:

endef
