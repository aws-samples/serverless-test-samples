// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import event_1_0_0 from '../events/event-1.0.0.json';
import event_1_2_0 from '../events/event-1.2.0.json';
import event_1_3_0 from '../events/event-1.3.0.json';

import { isAddressValid } from '../src/address-validation';

describe('Conract testing examples', () => {
  test('business logic in the producer has not changed', async () => {
    // First check the business logic on the original event.
    const initialEvent = event_1_0_0;
    let businessLogicCheck = isAddressValid(initialEvent);

    expect(businessLogicCheck).toBeTruthy();

    // Check the business logic on the new event.
    // Since the producer logic has not changed, the address format is still the same.
    // The business logic check will return the same result.
    const newEvent = event_1_2_0;
    businessLogicCheck = isAddressValid(newEvent);

    expect(businessLogicCheck).toBeTruthy();
  });

  test('changed business logic in the producer can be caught by a consumer contract test', async () => {
    // First check the business logic on the original event.
    const initialEvent = event_1_0_0;
    let businessLogicCheck = isAddressValid(initialEvent);

    expect(businessLogicCheck).toBeTruthy();

    // Check the business logic on the new event.
    // Since the producer logic has changed, the address will only contain street address now instead of a full address.
    // The business logic check will return a different result now.
    const newEvent = event_1_3_0;
    businessLogicCheck = isAddressValid(newEvent);

    expect(businessLogicCheck).toBeFalsy();
  });
});
