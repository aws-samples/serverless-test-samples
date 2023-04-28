# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Customer(BaseModel):
    """Class representing a customer"""
    customerId: str = Field(
        ..., examples=['577af109-1f19-4d0a-9c56-359f44ca0034'], title='Customerid'
    )
    firstName: str = Field(..., examples=['Jane'], title='Firstname')
    lastName: str = Field(..., examples=['Doe'], title='Lastname')
    address: str = Field(..., examples=['2 Park St'], title='Address')
    city: Optional[str] = Field('', examples=['Sydney'], title='City')
    state: Optional[str] = Field('', examples=['NSW'], title='State')
    country: Optional[str] = Field('', examples=['Australia'], title='Country')
    postcode: Optional[str] = Field('', examples=['2066'], title='Postcode')
