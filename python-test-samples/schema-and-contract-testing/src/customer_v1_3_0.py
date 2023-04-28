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
    name: str = Field(..., examples=['Jane Doe'], title='Name')
    email: Optional[str] = Field('', examples=['Jane.Doe@example.com'], title='Email')
    address: str = Field(
        ..., examples=['2 Park St, Sydney, NSW 2000, Australia'], title='Address'
    )
