# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import pytest
from pydantic import ValidationError
from tests.context import CustomerModel


def instantiate_customer(schema_version):
    """
    utility method to instantiate customer model 1.0.0 with event passed as parameter
    v1.0.0 represents the current schema in use and is the baseline to detect breaking changes
    v1.1.0 to v1.4.0 represent changes from v1.0.0
    """
    sample_event_file = f"events/customerCreated-event-{schema_version}.json"
    with open(sample_event_file, "r", encoding="utf-8") as event:
        new_schema_event = json.load(event)
        return CustomerModel(**new_schema_event)


def test_adding_optional_element_backward_compatible():
    """ 
    by default, Pydantic models ignore additional fields passed in
    any optional or mandatory new fields is not considered breaking schema change
    """
    customer = instantiate_customer("1.1.0")
    with pytest.raises(AttributeError):
        assert customer.email == "jane@example.com", "Optional email not breaking change"


def test_adding_required_element_backward_compatible():
    """any optional or mandatory new fields is not considered breaking schema change"""
    customer = instantiate_customer("1.2.0")
    with pytest.raises(AttributeError):
        assert customer.name == "Jane Doe", "New mandatory name not breaking change"


def test_removing_required_element_not_backward_compatible():
    """missing mandatory field will raise a validation error"""
    with pytest.raises(Exception) as e_info:
        customer = instantiate_customer("1.3.0")
    assert e_info.type == ValidationError
    # Updated for Pydantic v2 error message format
    error_message = str(e_info.value)
    assert "Field required" in error_message  # Pydantic v2 uses "Field required"
    assert "firstName" in error_message
    assert "lastName" in error_message


def test_changing_business_logic_existing_field_backward_compatible():
    """ 
    schema test cannot catch changes to business logic
    in this case, the custoner address value was changed from a full address to just a street number
    this business logic change does not impact schema of event and hence
    test passes
    """
    customer = instantiate_customer("1.4.0")
    assert customer.address == "2 Park St", "Street address not breaking schema change"