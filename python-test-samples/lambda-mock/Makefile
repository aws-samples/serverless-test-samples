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
	source ./venv/bin/activate && ${PIP} install -r tests/requirements.txt

shell:
	source ./venv/bin/activate

deps:
	source ./venv/bin/activate && ${PIP} install -r tests/requirements.txt

coverage:
	source ./venv/bin/activate &&  coverage run -m unittest discover
	source ./venv/bin/activate &&  coverage html --omit "tests/*",".venv/*"

test:
	source ./venv/bin/activate &&  pytest -v --disable-socket -s tests/unit/src/

build: ##=> Same as package except that we don't create a ZIP
	source ./venv/bin/activate && sam build

deploy:
	source ./venv/bin/activate &&  sam build
	source ./venv/bin/activate &&  sam deploy

deploy.g:
	source ./venv/bin/activate &&  sam build
	source ./venv/bin/activate &&  sam deploy --guided

scan:
	source ./venv/bin/activate &&  cfn_nag_scan --input-path template.yaml
	source ./venv/bin/activate &&  pylint src/sample_lambda/*.py tests/unit/src/*.py

delete:
	source ./venv/bin/activate && sam delete

#############
#  Helpers  #
#############

define HELP_MESSAGE

	Usage: make <command>

	Commands:

	build     Build Lambda function and dependencies
	deploy.g  Deploy guided (for initial deployment)
	deploy    Deploy subsequent changes

	install   Install application and dev dependencies defined in requirements.txt
	shell     Spawn a virtual environment shell
	deps      Install project dependencies locally
	test      Run unit test locally using mocks
	coverage  Run unit test coverage reports
	scan	  Run code scanning tools

	clean     Cleans up local build artifacts and environment
	delete    Delete stack from AWS

endef
