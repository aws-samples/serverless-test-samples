/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved
 *
 * SPDX-License-Identifier: MIT-0
 */

using Xunit;

namespace UnicornReservationSystem.Tests.Integration.Fixtures;

/// <summary>
/// This class has no code, and is never created. Its purpose is simply
/// to be the place to apply [CollectionDefinition] and all the
/// ICollectionFixture&lt;T&gt; interfaces.
/// </summary>
[CollectionDefinition("Environment")]
public class EnvironmentCollection : ICollectionFixture<EnvironmentFixture>;
