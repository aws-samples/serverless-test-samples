/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved
 *
 * SPDX-License-Identifier: MIT-0
 */

using System.Collections.Generic;
using System.Net;
using System.Text.Json;
using System.Threading.Tasks;

using UnicornReservationSystem.Tests.Integration.Fixtures;

using Xunit;

namespace UnicornReservationSystem.Tests.Integration;

[Collection("Environment")]
public class LocationTests : IClassFixture<LocationFixture>
{
	private readonly EnvironmentFixture _environmentFixture;
	private readonly LocationFixture _locationFixture;

	public LocationTests(EnvironmentFixture environmentFixture, LocationFixture locationFixture)
	{
		_environmentFixture = environmentFixture;
		_locationFixture = locationFixture;
	}

	[Fact]
	public async Task Api_ConnectivityCheck_Returns200()
	{
		var response = await _locationFixture.UnicornApi.GetAsync("locations/");

		Assert.True(response.IsSuccessStatusCode);
		Assert.Equal(HttpStatusCode.OK, response.StatusCode);
	}

	[Fact]
	public async Task Api_GetCorrectLocations_ReturnsLocations()
	{
		var response = await _locationFixture.UnicornApi.GetAsync("locations/");
		var content = await response.Content.ReadAsStringAsync();
		var result = JsonSerializer.Deserialize<Dictionary<string, string[]>>(content);

		Assert.True(response.IsSuccessStatusCode);
		Assert.Contains(_locationFixture.UniqueTestLocation, result["locations"]);
	}

	[Fact]
	public async Task Api_IncorrectLocationsUrl_ReturnsError()
	{
		var response = await _locationFixture.UnicornApi.GetAsync("incorrect-locations/");
		var content = await response.Content.ReadAsStringAsync();
		var result = JsonSerializer.Deserialize<Dictionary<string, string>>(content);

		Assert.False(response.IsSuccessStatusCode);
		Assert.Equal(HttpStatusCode.Forbidden, response.StatusCode);
		Assert.Equal("Missing Authentication Token", result["message"].ToString());
	}
}
