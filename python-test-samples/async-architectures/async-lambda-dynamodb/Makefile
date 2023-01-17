BASE := $(shell /bin/pwd)
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

shell:
	$(info [*] Type the 'deactivate' command to exit this shell)
	@$(PIPENV) shell

deps:
	$(info [*] Installing pipenv project dependencies)
	@$(PIPENV) install
	@$(PIPENV) install -d

build: ##=> Same as package except that we don't create a ZIP
	sam build --use-container

deploy.g: ##=> Guided deploy that is typically run for the first time only
	sam deploy --guided

deploy: ##=> Deploy app using previously saved SAM CLI configuration
	sam deploy

deploy.p: ##=> Deploy app to a production environment
	sam deploy --parameter-overrides EnvType=prod

test: check-stack-name
	AWS_SAM_STACK_NAME=$(AWS_SAM_STACK_NAME) python -m pytest -s tests/integration -v

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
	deploy.g  Deploy for the first time
	deploy    Deploy subsequent changes

	install   Install Pipenv, application and dev dependencies defined in Pipfile
	shell     Spawn a virtual environment shell
	deps      Install project dependencies locally
	test      Run integration test against cloud environment (requires AWS_SAM_STACK_NAME variable) 

	clean     Cleans up local build artifacts including zip files
	delete    Delete stack from AWS cloud

endef
