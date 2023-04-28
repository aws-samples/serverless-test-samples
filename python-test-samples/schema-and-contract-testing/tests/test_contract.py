import json
import pytest
from pydantic import ValidationError
from tests.context import ConsumerCustomerModel

def instantiate_customer(schema_version):
    """utility method to instantiate customer model with business alidations"""
    sample_event_file = f"events/customerCreated-event-{schema_version}.json"
    with open(sample_event_file, "r", encoding="utf-8") as event:
        new_schema_event = json.load(event)
        return ConsumerCustomerModel(**new_schema_event)


def test_address_with_four_fields_compatible_with_business_logic():
    """
    business validation for address field checks for 4 fields separated by ","
    event generated with schema 1.1.0 satisfies this, so test passes
    """
    customer = instantiate_customer("1.1.0")
    assert customer.address == "2 Park St, Sydney, NSW 2000, Australia", "Full address compatible"


def test_street_name_for_address_not_compatible_with_business_logic():
    """
    business validation for address field checks for 4 fields separated by ","
    event generated with schema 1.4.0 does not satisfy this, so test fails
    """
    with pytest.raises(Exception) as e_info:
        customer = instantiate_customer("1.4.0")
    assert e_info.type == ValidationError
    assert "Address must have four fields separated by ','" in str(
        e_info.value)
