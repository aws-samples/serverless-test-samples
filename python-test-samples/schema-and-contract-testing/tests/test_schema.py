# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import pytest
from tests.context import CustomerModel
from pydantic import ValidationError

# v1.0.0 represents the current schema in use and is the baseline to detect breaking changes
# v1.1.0 to v1.4.0 represent changes from v1.0.0

# utility method to instantiate customer model 1.0.0 with event passed as
# parameter

def instantiate_customer(schema_version):
    sample_event_file = f"events/customerCreated-event-{schema_version}.json"
    with open(sample_event_file, "r") as f:
        new_schema_event = json.load(f)
        return CustomerModel(**new_schema_event)

# by default, Pydantic models ignore additional fields passed in
# any optional or mandatory new fields is not considered breaking schema change

def test_adding_optional_element_backward_compatible():
    customer = instantiate_customer("1.1.0")
    with pytest.raises(AttributeError):
        assert customer.email == "jane@example.com", "Adding optional email field is not a breaking change"

# any optional or mandatory new fields is not considered breaking schema change

def test_adding_required_element_backward_compatible():
    customer = instantiate_customer("1.2.0")
    with pytest.raises(AttributeError):
        assert customer.name == "Jane Doe", "Adding mandatory name field is not a breaking change"

# missing mandatory field will raise a validation error

def test_removing_required_element_not_backward_compatible():
    with pytest.raises(Exception) as e_info:
        customer = instantiate_customer("1.3.0")
    assert e_info.type == ValidationError
    assert "field required" in str(e_info.value)
    assert "firstName" in str(e_info.value)
    assert "lastName" in str(e_info.value)

# schema test cannot catch changes to business logic
# in this case, the custoner address value was changed from a full address to just a street number
# this business logic change does not impact schema of event and hence
# test passes

def test_changing_business_logic_existing_field_backward_compatible():
    customer = instantiate_customer("1.4.0")
    assert customer.address == "2 Park St", "Passing the street address instead of full address is not breaking schema change"
