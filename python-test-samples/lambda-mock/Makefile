checkOSDependencies:
	python3 --version | grep -q 3\.9 || (echo "Error: Requires Python 3.9" && exit 1)

createEnv: checkOSDependencies
	pip3 install virtualenv
	python3 -m venv venv
	source ./venv/bin/activate && pip3 install -r tests/requirements.txt

coverage:
	source ./venv/bin/activate &&  coverage run -m unittest discover
	source ./venv/bin/activate &&  coverage html --omit "tests/*",".venv/*"

unittest:
	source ./venv/bin/activate &&  pytest -v --disable-socket -s tests/unit/src/

deploy:
	source ./venv/bin/activate &&  sam build
	source ./venv/bin/activate &&  sam deploy

deploy.guided:
	source ./venv/bin/activate &&  sam build
	source ./venv/bin/activate &&  sam deploy --guided

scan:
	source ./venv/bin/activate &&  cfn_nag_scan --input-path template.yaml
	source ./venv/bin/activate &&  pylint src/sample_lambda/*.py tests/unit/src/*.py
