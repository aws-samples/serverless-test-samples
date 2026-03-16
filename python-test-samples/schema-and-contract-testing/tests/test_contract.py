# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Customer(BaseModel):
    """Class representing a customer"""
    customerId: str = Field(
        ..., examples=['577af109-1f19-4d0a-9c56-359f44ca0034'], title='Customerid'
    )
    firstName: str = Field(..., examples=['Jane'], title='Firstname')
    lastName: str = Field(..., examples=['Doe'], title='Lastname')
    address: str = Field(
        ..., examples=['2 Park St, Sydney, NSW 2000, Australia'], title='Address'
    )

    @field_validator('address')
    @classmethod
    def address_has_four_fields(cls, address_value: str) -> str:
        """Function to validate address field"""
        if len(address_value.split(',')) != 4:
            raise ValueError("Address must have four fields separated by ','.")
        return address_value