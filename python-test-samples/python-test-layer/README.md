# Python AWS Lambda Layer Test Demonstration

## Introduction

This project expands on the [python-test-intro](../python-test-intro/README.md) introductory example, and adds [Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/invocation-layers.html) to the sample Lambda function to demonstrate test approaches.

---

## Unit Test of Layers

When creating unit tests, create a separate test harnesses for each layer to test its functionality, as seen in [tests/unit/mock_test_samplecodelayer.py](tests/unit/mock_test_samplecodelayer.py).  

When running in the unit tests for the Lambda function, the layer modules are not available to the Lambda function as they would be in a deployed Lambda runtime environment.  To accomodate this in the unit test code, add the path of the layers in the unit test before importing the lambda hander, as seen on lines 6:8 of [tests/unit/mock_test_samplelambda.py](tests/unit/mock_test_samplelambda.py):

```python
sys.path.append("src/sampleCodeLayer/python")
sys.path.append("src/sampleSchemaLayer/python")
from src.sampleLambda import app
```

In the unit test for the Lambda function, the layer is patched and not re-tested, as coverage is provided in the test for the layer.  As seen in [tests/unit/mock_test_samplelambda.py](tests/unit/mock_test_samplelambda.py) line 13, you can patch the layer and mock it's return value.

To run the unit tests:

```bash
# Change current directory to the python-test-layer sub-project
cd python-test-samples/python-test-layer

# install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r tests/requirements.txt

# run Lambda layer unit tests with mocks
python3 -m pytest -s tests/unit/mock_test_samplecodelayer.py -v

# run Lambda function unit tests with patched layer
python -m pytest -s tests/unit/mock_test_samplelambda.py -v
```

---

## Other Testing

Using Lambda layers does not affect the other tests, as the layer functionality is implicitly tested with the invokation of the Lambda function. 
