/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved
 *
 * SPDX-License-Identifier: MIT-0
 */

using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.DocumentModel;
using Amazon.S3;
using Amazon.S3.Model;

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

using UnicornReservationSystem.Tests.Integration.Fixtures;

using Xunit;

namespace UnicornReservationSystem.Tests.Integration;

[Collection("Environment")]
public class FileProcessorTests : IAsyncLifetime
{
	private readonly EnvironmentFixture _environmentFixture;
	private readonly AmazonDynamoDBClient _dynamoDbClient;
	private readonly AmazonS3Client _s3Client;

	private readonly Guid _postFix;
	private readonly string _testUnicorn;
	private readonly string _testLocation;

	/// <summary>
	/// We also seed the DynamoDB Table for the test
	/// </summary>
	/// <param name="environmentFixture"></param>
	public FileProcessorTests(EnvironmentFixture environmentFixture)
	{
		_environmentFixture = environmentFixture;
		_dynamoDbClient = new AmazonDynamoDBClient();
		_s3Client = new AmazonS3Client();

		// Create a random postfix for the id's to prevent data collisions between tests
		// Using unique id's per unit test will isolate test data
		// Use this id in all test data values or artifacts
		_postFix = Guid.NewGuid();
		_testUnicorn = $"TEST_UNI_{_postFix}";
		_testLocation = $"TEST_LOC_{_postFix}";
	}

	public Task InitializeAsync() => Task.CompletedTask;

	/// <summary>
	/// Test that given an S3 file, the Unicorn is created in DynamoDB
	/// In a real-world scenario, we would test variations and failure modes as well
	/// </summary>
	[Fact]
	public async Task Workflow_S3Upload_ReturnsNewUnicorn()
	{
		var table = Table.LoadTable(_dynamoDbClient, _environmentFixture.DynamoDbTable);
		Document existingTestUnicorn = await table.GetItemAsync(_testUnicorn);
		Assert.True(existingTestUnicorn is null, "Data exists before test, invalid starting state");

		// Seed the S3 bucket with test data
		// Note the uniqueness of the test data and S3 key to prevent collisions with actual data:
		// both the postfix and the exact test name are part of the filename.
		var testData = $"""
				                "Unicorn Name","Unicorn Location"
				                "{_testUnicorn}","{_testLocation}"

				                """;
		var testDataKey = $"INTEGRATION_TEST/TEST{_postFix}.test_file_processor_happy_path.csv";
		var s3Request = new PutObjectRequest
		{
			BucketName = _environmentFixture.UnicornInventoryBucket,
			Key = testDataKey,
			ContentBody = testData
		};
		_ = await _s3Client.PutObjectAsync(s3Request);

		// Create a search object to contain the search parameters
		List<Document> searchResults = [];

		// Poll for processing completion
		var pollMaxTime = TimeSpan.FromSeconds(30);
		var pollCompleteSeconds = TimeSpan.Zero;
		while (pollCompleteSeconds < pollMaxTime)
		{
			// Perform the search to see if the file processor has finished
			Search tableSearch = table.Query(new QueryFilter("PK", QueryOperator.Equal, _testUnicorn));
			searchResults = await tableSearch.GetNextSetAsync();
			if (searchResults.Count == 0)
			{
				/* There are better ways to wait for an async event to finish than "Sleep"
				 * https://ardalis.com/thread-sleep-in-tests-is-evil/
				 * https://www.meziantou.net/automated-ui-tests-an-asp-net-core-application-with-playwright-and-xunit.htm
				 */
				Thread.Sleep(TimeSpan.FromSeconds(1));
				pollCompleteSeconds = pollCompleteSeconds.Add(TimeSpan.FromSeconds(1));
			}
			else
			{
				break;
			}
		}

		// Happy Path Checks: 1 item found within a good timeframe, data is as expected.
		// Using Assert.True for most of these checks as they allow for user messages to be added to test output

		Assert.True(searchResults.Count > 0, "Item not found after time allowed for processing.");
		Assert.True(pollCompleteSeconds < TimeSpan.FromSeconds(2), $"Unicorns should be fast!  Took too long: {pollCompleteSeconds}");
		Assert.True(searchResults.Count == 1, "More than one item found after insert of data");
		Assert.True(searchResults[0]["PK"].AsString() == _testUnicorn, $"Table PK is not set to the Unicorn Name: {searchResults[0]["PK"].AsString()} expected {_testUnicorn}");
		Assert.True(searchResults[0]["LOCATION"].AsString() == _testLocation, $"Table LOCATION is not set to the Unicorn Location: {searchResults[0]["LOCATION"].AsString()} expected {_testLocation}");
		Assert.Contains(["IN_TRAINING", "AVAILABLE"], status => status.Contains(searchResults[0]["STATUS"].AsString()));
	}

	public async Task DisposeAsync()
	{
		// Remove the test unicorn
		var table = Table.LoadTable(_dynamoDbClient, _environmentFixture.DynamoDbTable);
		Document testUnicorn = await table.GetItemAsync(_testUnicorn);
		if (testUnicorn is not null)
		{
			await table.DeleteItemAsync(testUnicorn);
		}

		// And the test location from the locations list
		DynamoDBEntry testLocationEntry = DynamoDBEntryConversion.V2.ConvertToEntry(_testLocation);
		DynamoDBList locations = null;
		var pollMaxTime = TimeSpan.FromSeconds(30);
		var pollCompleteSeconds = TimeSpan.Zero;

		// The LOCATIONS#LIST value was being subjected to eventual consistently delays
		// This loop repeatedly retrieves the LOCATIONS#LIST key until our _testLocation is present
		// or the timeout has elapsed
		while (pollCompleteSeconds < pollMaxTime)
		{
			Document locationsList = await table.GetItemAsync("LOCATION#LIST");
			locations = locationsList["LOCATIONS"].AsDynamoDBList();
			var indexUpdated = locations?.AsArrayOfString().Contains(_testLocation) ?? false;
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

		locations?.Entries.Remove(testLocationEntry);
		await table.PutItemAsync(new Document
		{
			["PK"] = "LOCATION#LIST",
			["LOCATIONS"] = locations
		});

		_dynamoDbClient?.Dispose();
		_s3Client?.Dispose();
	}
}
