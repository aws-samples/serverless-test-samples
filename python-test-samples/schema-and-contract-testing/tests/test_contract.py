import json
import pytest
from tests.context import ConsumerCustomerModel
from pydantic import ValidationError

# utility method to instantiate customer model with business alidations

def instantiate_customer(schema_version):
    sample_event_file = f"events/customerCreated-event-{schema_version}.json"
    with open(sample_event_file, "r") as f:
        new_schema_event = json.load(f)
        return ConsumerCustomerModel(**new_schema_event)

# business validation for address field checks for 4 fields separated by ","
# event generated with schema 1.1.0 satisfies this, so test passes

def test_address_with_four_fields_compatible_with_business_logic():
    customer = instantiate_customer("1.1.0")
    assert customer.address == "2 Park St, Sydney, NSW 2000, Australia", "Full address value is compatible"

# business validation for address field checks for 4 fields separated by ","
# event generated with schema 1.4.0 does not satisfy this, so test fails

def test_street_name_for_address_not_compatible_with_business_logic():
    with pytest.raises(Exception) as e_info:
        customer = instantiate_customer("1.4.0")
    assert e_info.type == ValidationError
    assert "Address must have four fields separated by ','" in str(
        e_info.value)
