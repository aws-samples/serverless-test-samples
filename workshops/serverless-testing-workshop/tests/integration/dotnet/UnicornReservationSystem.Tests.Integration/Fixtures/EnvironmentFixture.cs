/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved
 *
 * SPDX-License-Identifier: MIT-0
 */

// More information about xUnit Collection Fixtures
// https://xunit.net/docs/shared-context#collection-fixture

using Amazon.CloudFormation;
using Amazon.CloudFormation.Model;

using System;
using System.Linq;

namespace UnicornReservationSystem.Tests.Integration.Fixtures;

public sealed class EnvironmentFixture
{
	public EnvironmentFixture()
	{

	}

	public string ApiEndpoint { get; private set; }
	public string DynamoDbTable { get; private set; }
	public string UnicornInventoryBucket { get; private set; }
}
