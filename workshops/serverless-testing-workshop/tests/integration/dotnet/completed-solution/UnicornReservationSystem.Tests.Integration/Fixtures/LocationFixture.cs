/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved
 *
 * SPDX-License-Identifier: MIT-0
 */

// More information about xUnit Class Fixtures
// https://xunit.net/docs/shared-context#class-fixture

using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.DocumentModel;

using System;
using System.Linq;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;

using Xunit;

namespace UnicornReservationSystem.Tests.Integration.Fixtures;

public class LocationFixture : IAsyncLifetime
{
	private readonly EnvironmentFixture _environmentFixture;
	private readonly AmazonDynamoDBClient _dynamoDbClient;

	public LocationFixture(EnvironmentFixture environmentFixture)
	{
		// ** Place UniqueTestLocation Code Here **
		UniqueTestLocation = $"TEST_LOC_{Guid.NewGuid()}";

		_environmentFixture = environmentFixture;
		_dynamoDbClient = new AmazonDynamoDBClient();

		// HttpClient lifecycle management best practices:
		// https://learn.microsoft.com/dotnet/fundamentals/networking/http/httpclient-guidelines#recommended-use
		UnicornApi = new HttpClient
		{
			BaseAddress = new Uri(_environmentFixture.ApiEndpoint)
		};
	}

	public string UniqueTestLocation { get; }
	public HttpClient UnicornApi { get; }

	/// <summary>
	/// Perform initialization steps
	/// </summary>
	/// <remarks>
	/// This method is implemented as part of the <see cref="IAsyncLifetime"/> interface.
	/// It is here that we use the DynamoDB module of the .NET SDK to directly upload a test location to the LOCATION#LIST
	/// entry so we can use it in our tests.
	/// </remarks>
	public async Task InitializeAsync()
	{
		// Get the LOCATION#LIST item from DynamoDB
		var table = Table.LoadTable(_dynamoDbClient, _environmentFixture.DynamoDbTable);
		Document locationList = await table.GetItemAsync("LOCATION#LIST");

		// The LOCATION#LIST is a List data type
		// https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.NamingRulesDataTypes.html#HowItWorks.DataTypes.Document.List
		// Create a new DynamoDBList object to add the test location
		var updatedLocationList = new DynamoDBList();

		// Convert the test location into a DynamoDB entry from a string
		var testLocationEntry = DynamoDBEntryConversion.V2.ConvertToEntry(UniqueTestLocation);
		if (locationList is null)
		{
			updatedLocationList.Add(testLocationEntry);
		}
		else
		{
			// If the location list already has entries, add them to the updatedLocationList
			// before we add our test location. Otherwise, the LOCATIONS attribute would be wholly
			// replaced with just the new test location, erasing the existing locations.
			updatedLocationList = locationList["LOCATIONS"].AsDynamoDBList();
			updatedLocationList.Add(testLocationEntry);
		}

		// Store the new list of locations
		await table.PutItemAsync(new Document
		{
			["PK"] = "LOCATION#LIST",
			["LOCATIONS"] = updatedLocationList
		});
	}

	/// <summary>
	/// Runs at the completion of all tests in a given class
	/// </summary>
	/// <remarks>
	/// This method is implemented as part of the <see cref="IAsyncLifetime"/> interface.
	/// It is here that we use the DynamoDB module of the .NET SDK to remove the test location from the LOCATION#LIST
	/// entry so we can clean up after the tests finish.
	/// </remarks>
	public async Task DisposeAsync()
	{
		// Convert the test location into a DynamoDB entry from a string
		DynamoDBEntry testLocationEntry = DynamoDBEntryConversion.V2.ConvertToEntry(UniqueTestLocation);
		var table = Table.LoadTable(_dynamoDbClient, _environmentFixture.DynamoDbTable);

		// Setup variables to keep track of polling
		DynamoDBList locations = null;
		var pollMaxTime = TimeSpan.FromSeconds(30);
		var pollCompleteSeconds = TimeSpan.Zero;

		// When reading from DynamoDB values are sometimes eventually consistent
		// https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html
		// This loop repeatedly retrieves the LOCATIONS#LIST key until our UniqueTestLocation is present
		// or the timeout has elapsed
		while (pollCompleteSeconds < pollMaxTime)
		{
			Document locationsList = await table.GetItemAsync("LOCATION#LIST");
			locations = locationsList["LOCATIONS"].AsDynamoDBList();
			var indexUpdated = locations?.AsArrayOfString().Contains(UniqueTestLocation) ?? false;
			if (indexUpdated)
			{
				break;
			}
			else
			{
				Thread.Sleep(TimeSpan.FromSeconds(1));
				pollCompleteSeconds = pollCompleteSeconds.Add(TimeSpan.FromSeconds(1));
			}
		}

		// Remove the UniqueTestLocation from the list retrieved from DynamoDB
		locations?.Entries.Remove(testLocationEntry);

		// Store the new list of locations
		await table.PutItemAsync(new Document
		{
			["PK"] = "LOCATION#LIST",
			["LOCATIONS"] = locations
		});

		_dynamoDbClient?.Dispose();
	}
}
