# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import sys

# allow importing models from src folder one level up.

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '../src')))

from customer_v1_0_0_with_validation import Customer as ConsumerCustomerModel
from customer_v1_0_0 import Customer as CustomerModel
