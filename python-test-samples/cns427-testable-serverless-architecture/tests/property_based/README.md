# Property-Based Tests for Circular Dependency Detection

## Overview

This directory contains property-based tests for the circular dependency detection logic in the Task API. These tests were generated from formal requirements documents using Kiro's correctness testing capability and the Hypothesis library.

## What is Property-Based Testing?

Property-based testing is a testing approach where you define **properties** (invariants) that should always be true, and the testing framework automatically generates hundreds of test cases to verify those properties.

### Traditional Testing vs Property-Based Testing

**Traditional Example-Based Test:**
```python
def test_self_dependency():
    assert has_circular_dependency('task-1', 'task-1', {}) == True
```

**Property-Based Test:**
```python
@given(task_id=st.text(min_size=1))
def test_self_dependency_always_circular(task_id):
    # Property: ANY task depending on itself is circular
    assert has_circular_dependency(task_id, task_id, {}) == True
```

The property-based test automatically generates hundreds of different task IDs to verify the property holds universally.

## Test Organization

Tests are organized by requirement:

- **test_self_dependency_properties.py** - Requirement 1: Self-dependency detection
- **test_direct_cycle_properties.py** - Requirement 2: Direct two-task cycles
- **test_complex_cycle_properties.py** - Requirement 3: Complex multi-task cycles
- **test_linear_chain_properties.py** - Requirement 4: Valid linear chains
- **test_empty_graph_properties.py** - Requirement 5: Empty graph handling
- **test_validation_properties.py** - Requirement 6: Validation integration

## Properties Being Tested

### 1. Self-Dependency Properties
- **Reflexivity**: `has_circular(A, A, graph) == True` for any A and any graph
- **Independence**: Self-dependencies are detected regardless of graph state

### 2. Direct Cycle Properties
- **Symmetry**: If A→B exists, then B→A creates a cycle
- **Bidirectionality**: A→B→A is always circular

### 3. Complex Cycle Properties
- **Transitivity**: A→B→C→...→A is circular for any chain length
- **Graph Traversal**: DFS correctly identifies cycles in complex graphs

### 4. Linear Chain Properties
- **Non-circularity**: Linear chains without loops return false
- **Extensibility**: Linear chains can be extended indefinitely
- **Distinction**: System correctly distinguishes linear from circular

### 5. Empty Graph Properties
- **Permissiveness**: Empty graphs allow any dependency between different tasks
- **Self-dependency Exception**: Self-dependencies are still detected in empty graphs

### 6. Validation Properties
- **Error Handling**: CircularDependencyError raised for cycles
- **Error Messages**: Error messages include problematic dependency IDs
- **Valid Cases**: Validation passes for non-circular dependencies

## Running the Tests

### Run all property-based tests:
```bash
poetry run pytest tests/property_based/ -v
```

### Run specific test file:
```bash
poetry run pytest tests/property_based/test_self_dependency_properties.py -v
```

### Run with Hypothesis statistics:
```bash
poetry run pytest tests/property_based/ -v --hypothesis-show-statistics
```

### Run with more examples (default is 100):
```bash
poetry run pytest tests/property_based/ -v --hypothesis-seed=random
```

## Test Generation Process

These tests were generated using the following process:

1. **Requirements Analysis** - Formal requirements written in EARS format
2. **Property Identification** - Identified invariants and properties from requirements
3. **Test Generation** - Created property-based tests using Hypothesis
4. **Verification** - Ran tests to ensure comprehensive coverage

## Benefits of Property-Based Testing

### 1. Comprehensive Coverage
- Tests hundreds of input combinations automatically
- Finds edge cases you might not think of manually
- Verifies properties hold universally, not just for specific examples

### 2. Better Bug Detection
- Hypothesis automatically finds minimal failing examples
- Shrinks complex failing inputs to simplest form
- Reveals assumptions and edge cases

### 3. Living Documentation
- Properties serve as executable specifications
- Tests document what should always be true
- Requirements directly map to test properties

### 4. Regression Prevention
- Once a bug is found, Hypothesis remembers it
- Prevents regression by testing the same edge case
- Builds confidence in refactoring

## Example: How Hypothesis Finds Bugs

If there's a bug in the circular dependency detection, Hypothesis will:

1. **Generate** hundreds of random test cases
2. **Detect** the failing case
3. **Shrink** the input to the minimal failing example
4. **Report** the simplest case that breaks the property

Example output:
```
Falsifying example: test_three_task_cycle(
    task_a='550e8400-e29b-41d4-a716-446655440000',
    task_b='6ba7b810-9dad-11d1-80b4-00c04fd430c8',
    task_c='6ba7b814-9dad-11d1-80b4-00c04fd430c8'
)
```

## Realistic Test Data

Our property-based tests use the same data types as production code:

```python
# Production code (models.py)
id=str(uuid.uuid4())  # e.g., "550e8400-e29b-41d4-a716-446655440000"

# Property-based tests
task_ids = st.uuids().map(str)  # Generates same format as production
```

**Benefits:**
- Tests use realistic UUIDs instead of arbitrary strings
- More representative of actual production usage
- Hypothesis can still shrink UUIDs to simpler examples when bugs are found
- Ensures validation logic works with real UUID formats

## Integration with Requirements

Each test file maps directly to requirements:

| Test File | Requirements | Properties Tested |
|-----------|-------------|-------------------|
| test_self_dependency_properties.py | 1.1, 1.2, 1.3 | Reflexivity, Independence |
| test_direct_cycle_properties.py | 2.1, 2.2, 2.3 | Symmetry, Bidirectionality |
| test_complex_cycle_properties.py | 3.1, 3.2, 3.3, 3.4 | Transitivity, DFS traversal |
| test_linear_chain_properties.py | 4.1, 4.2, 4.3 | Non-circularity, Distinction |
| test_empty_graph_properties.py | 5.1, 5.2, 5.3 | Permissiveness, Exceptions |
| test_validation_properties.py | 6.1-6.5 | Error handling, Integration |

## Further Reading

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Property-Based Testing Introduction](https://hypothesis.works/articles/what-is-property-based-testing/)
- [Kiro Correctness Testing](https://kiro.dev/docs/specs/correctness/)


## Interpreting Hypothesis Statistics

When you run tests with `--hypothesis-show-statistics`, you get detailed information about how Hypothesis generated and executed test cases. Here's how to interpret the output:

### Example Output

```
tests/property_based/test_validation_properties.py::TestValidationIntegrationProperties::test_validation_with_complex_graph:

- during generate phase (0.10 seconds):
  - Typical runtimes: < 1ms, of which < 1ms in data generation
  - 100 passing examples, 0 failing examples, 138 invalid examples
  - Events:
    * 35.71%, invalid because: failed to satisfy assume() in test_validation_with_complex_graph (line 154)
    * 8.40%, invalid because: failed to satisfy assume() in test_validation_with_complex_graph (line 157)
    * 6.72%, invalid because: failed to satisfy assume() in test_validation_with_complex_graph (line 155)
    * 5.04%, invalid because: failed to satisfy assume() in test_validation_with_complex_graph (line 156)
  - Stopped because settings.max_examples=100
```

### Breaking Down Each Section

#### 1. Generate Phase Duration
```
during generate phase (0.10 seconds)
```
- **What it means**: Total time spent generating random inputs and running test cases
- **Good**: < 1 second per test
- **Acceptable**: 1-5 seconds per test
- **Slow**: > 5 seconds per test (may need optimization)

#### 2. Runtime Performance
```
Typical runtimes: < 1ms, of which < 1ms in data generation
```
- **First value**: Time to run each individual test case
- **Second value**: Time to generate the random input data
- **Good sign**: Both values < 1ms means very efficient tests

#### 3. Test Results Summary
```
100 passing examples, 0 failing examples, 138 invalid examples
```

| Metric | Meaning | Interpretation |
|--------|---------|----------------|
| **Passing examples** | Test cases that met all constraints and passed assertions | ✅ This is your target (default: 100) |
| **Failing examples** | Test cases that failed assertions (found bugs) | ✅ 0 means no bugs found |
| **Invalid examples** | Test cases rejected by `assume()` statements | ⚠️ Normal, but high numbers may indicate inefficiency |

#### 4. Invalid Examples Breakdown
```
Events:
* 35.71%, invalid because: failed to satisfy assume() in test_validation_with_complex_graph (line 154)
* 8.40%, invalid because: failed to satisfy assume() in test_validation_with_complex_graph (line 157)
```

This shows **why** examples were rejected. Common reasons:
- `assume()` statements filtering out unwanted inputs
- Constraints that are hard to satisfy randomly
- Overlapping or conflicting requirements

### Understanding Invalid Examples

#### What Causes Invalid Examples?

In the example above, the test has these constraints:
```python
assume(len({task_a, task_b, task_c}) == 3)  # Line 154: All 3 tasks must be different
assume(task_a not in other_deps)             # Line 155: task_a not in other_deps list
assume(task_b not in other_deps)             # Line 156: task_b not in other_deps list
assume(task_c not in other_deps)             # Line 157: task_c not in other_deps list
```

Hypothesis generates random inputs, but many don't meet these constraints:
- **35.71% rejected at line 154**: Generated duplicate task IDs (e.g., task_a='x', task_b='x')
- **8.40% rejected at line 157**: task_c appeared in other_deps list
- And so on...

#### Is This a Problem?

**Usually no!** Here's when to worry:

| Rejection Rate | Status | Action |
|----------------|--------|--------|
| < 50% | ✅ Good | No action needed |
| 50-80% | ⚠️ Acceptable | Consider optimization if slow |
| 80-95% | ⚠️ Inefficient | Should optimize strategies |
| > 95% | ❌ Problem | Must optimize - Hypothesis will warn |

#### When to Optimize

Optimize if you see:
- **Very high rejection rate** (>90%) - Hypothesis struggles to find valid inputs
- **Slow generation** (>5 seconds) - Too much time wasted on invalid examples
- **Warning messages** - Hypothesis explicitly warns about health check failures

### Optimization Strategies

#### Before: Using `assume()` (Less Efficient)
```python
@given(task_a=task_ids, task_b=task_ids, task_c=task_ids)
def test_something(self, task_a, task_b, task_c):
    assume(len({task_a, task_b, task_c}) == 3)  # Rejects duplicates
    # Test logic...
```
**Problem**: Generates many duplicate combinations that get rejected

#### After: Using Specific Strategies (More Efficient)
```python
@given(tasks=st.lists(task_ids, min_size=3, max_size=3, unique=True))
def test_something(self, tasks):
    task_a, task_b, task_c = tasks  # Guaranteed to be different
    # Test logic...
```
**Benefit**: Only generates valid inputs, no rejections!

### Real-World Example Analysis

Let's analyze the example output:

```
100 passing examples, 0 failing examples, 138 invalid examples
```

**Calculations:**
- Total attempts: 100 + 138 = 238
- Rejection rate: 138/238 = 58%
- Success rate: 100/238 = 42%
- Time per attempt: 0.10s / 238 = 0.0004s (very fast!)

**Verdict:** ✅ Acceptable
- Got all 100 passing examples needed
- Only took 0.10 seconds despite 58% rejection rate
- No optimization needed unless you want to show best practices

### Quick Reference: What's Good vs Bad

#### ✅ Good Signs
- 100+ passing examples
- 0 failing examples (unless you're testing for bugs)
- Generation time < 1 second
- Runtime per test < 1ms
- Rejection rate < 50%

#### ⚠️ Warning Signs
- Rejection rate > 80%
- Generation time > 5 seconds
- Hypothesis warnings about health checks
- Very few passing examples despite long runtime

#### ❌ Problem Signs
- Rejection rate > 95%
- Generation time > 30 seconds
- Hypothesis errors or test timeouts
- "Unable to satisfy assumptions" errors

### Stopping Conditions

```
Stopped because settings.max_examples=100
```

Hypothesis stops when it reaches one of these conditions:
- **max_examples reached**: Successfully ran target number of valid tests (default: 100)
- **Deadline exceeded**: Took too long (default: 200ms per test)
- **Health check failed**: Too many invalid examples (>90% rejection)
- **Bug found**: Failing example discovered

### Advanced: Configuring Hypothesis

You can adjust settings in `pytest.ini` or per-test:

```python
from hypothesis import settings

@settings(max_examples=1000)  # Run 1000 examples instead of 100
@given(task_id=task_ids)
def test_something(self, task_id):
    ...
```

Common settings:
- `max_examples`: Number of valid test cases to run (default: 100)
- `deadline`: Max time per test case (default: 200ms)
- `suppress_health_check`: Disable specific health checks (use carefully!)

### Summary Checklist

When reviewing Hypothesis statistics, check:

- [ ] **Passing examples**: Did you get 100+ valid tests?
- [ ] **Failing examples**: Are there 0 (or expected failures)?
- [ ] **Generation time**: Is it < 1 second?
- [ ] **Rejection rate**: Is it < 80%?
- [ ] **Runtime**: Is each test < 1ms?
- [ ] **Warnings**: Are there any Hypothesis warnings?

If all checks pass, your property-based tests are working efficiently! 🎉


## When to Use Property-Based Testing

### Best Use Cases for PBT

Property-based testing shines in specific scenarios. Here's a practical guide:

#### ✅ Excellent Use Cases

**1. Pure Business Logic / Domain Logic**
```python
# Perfect for PBT - pure functions with clear invariants
def has_circular_dependency(task_id, dependency_id, graph):
    # No external dependencies, deterministic, testable properties
    ...
```

**Why it works:**
- Pure functions with no side effects
- Clear mathematical properties (reflexivity, transitivity, symmetry)
- Input/output relationships that should hold universally
- No dependency on specific data values

**Examples:**
- Validation logic (email, phone, data formats)
- State machines (valid transitions)
- Data transformations (parsing, serialization)
- Algorithm correctness (sorting, searching, graph algorithms)
- Business rules (pricing, discounts, eligibility)

**2. Parsers and Serializers**
```python
@given(data=st.dictionaries(st.text(), st.integers()))
def test_json_roundtrip(data):
    # Property: serialize then deserialize should equal original
    assert json.loads(json.dumps(data)) == data
```

**3. Data Structure Invariants**
```python
@given(items=st.lists(st.integers()))
def test_sorted_list_invariant(items):
    sorted_items = sorted(items)
    # Property: each element <= next element
    for i in range(len(sorted_items) - 1):
        assert sorted_items[i] <= sorted_items[i + 1]
```

**4. Encoding/Decoding**
```python
@given(text=st.text())
def test_base64_roundtrip(text):
    # Property: encode then decode should equal original
    encoded = base64.b64encode(text.encode())
    decoded = base64.b64decode(encoded).decode()
    assert decoded == text
```

#### ⚠️ Limited Use Cases

**1. Integration Tests with External Systems**

**Problem:** Random data doesn't work with real external systems
```python
# ❌ BAD: Can't use random event sources with real EventBridge
@given(source=st.text(), detail_type=st.text())
def test_eventbridge_integration(source, detail_type):
    # EventBridge test harness requires source='TEST-...'
    # Random data won't match test harness expectations
    publisher.publish_event(source, detail_type)
```

**Solution:** Use traditional example-based tests for integration
```python
# ✅ GOOD: Specific data for integration tests
def test_eventbridge_integration():
    # Test harness expects specific format
    publisher.publish_event(
        source='TEST-cns427-task-api',
        detail_type='TEST-TaskCreated'
    )
```

**When to use PBT for integration:**
- Testing error handling with various invalid inputs
- Testing retry logic with different failure scenarios
- Testing idempotency with repeated operations

**2. End-to-End Tests**

**Problem:** E2E tests require specific data flows and state
```python
# ❌ BAD: E2E requires specific user journey
@given(user_action=st.text())
def test_user_workflow(user_action):
    # Can't test "user logs in → creates task → completes task"
    # with random actions
```

**Solution:** Use traditional E2E tests with specific scenarios
```python
# ✅ GOOD: Specific user journey
def test_complete_task_workflow():
    user = login_user("test@example.com")
    task = create_task("Complete report")
    complete_task(task.id)
    assert task.status == "completed"
```

**3. Tests Requiring Specific Data**

**Problem:** Some tests need exact data values
```python
# ❌ BAD: Test requires specific test harness data
@given(task_id=st.text())
def test_task_appears_in_test_harness(task_id):
    # Test harness only captures tasks with title starting with "TEST-"
    # Random task_id won't work
```

**Solution:** Use example-based tests
```python
# ✅ GOOD: Specific test data
def test_task_appears_in_test_harness():
    task_id = f"TEST-{uuid.uuid4()}"
    create_task(task_id, title=f"TEST-{task_id}")
    # Now test harness will capture it
```

#### 🎯 Decision Matrix

| Test Type | Use PBT? | Reason |
|-----------|----------|--------|
| **Pure business logic** | ✅ Yes | Clear properties, no dependencies |
| **Validation functions** | ✅ Yes | Universal rules, deterministic |
| **Data transformations** | ✅ Yes | Roundtrip properties, invariants |
| **Algorithm correctness** | ✅ Yes | Mathematical properties |
| **Unit tests (no mocks)** | ✅ Yes | Fast, isolated, deterministic |
| **Integration tests** | ⚠️ Limited | Use for error cases, not happy path |
| **E2E tests** | ❌ No | Requires specific data flows |
| **Tests with external APIs** | ❌ No | Can't use random data with real systems |
| **Tests requiring specific state** | ❌ No | Need controlled test data |
| **UI tests** | ❌ No | Requires specific user interactions |

### Hybrid Approach: Best of Both Worlds

**Recommended Strategy:**

```python
# 1. Property-based tests for business logic
@given(task_id=st.text(min_size=1), dependency_id=st.text(min_size=1))
def test_circular_dependency_properties(task_id, dependency_id):
    # Test universal properties
    ...

# 2. Example-based tests for integration
def test_eventbridge_integration_with_test_harness():
    # Use specific TEST- prefixed data
    event = TaskCreatedEvent(
        task,
        source='TEST-cns427-task-api',
        detail_type_prefix='TEST-'
    )
    ...

# 3. Example-based tests for E2E
def test_complete_user_workflow():
    # Specific user journey with known data
    ...
```

## Performance and CI/CD Considerations

### Question: Should PBT Run on Every Commit?

**Short Answer:** It depends on your test suite organization and performance requirements.

### Performance Comparison

Let's compare actual performance from this project:

```bash
# Traditional unit tests (no mocks)
poetry run pytest tests/unit/test_domain_logic.py -v
# Result: 14 tests in 0.06s (0.004s per test)

# Property-based tests
poetry run pytest tests/property_based/ -v
# Result: 33 tests in 3.43s (0.104s per test)
```

**Analysis:**
- **Traditional tests:** 0.004s per test
- **Property-based tests:** 0.104s per test (26x slower)
- **But:** PBT runs 100 examples per test vs 1 example in traditional

**Per-example comparison:**
- Traditional: 0.004s for 1 example
- PBT: 0.104s for 100 examples = 0.001s per example (actually faster!)

### CI/CD Strategies

#### Strategy 1: Run Everything on Every Commit (Small Projects)

```yaml
# .github/workflows/test.yml
- name: Run all tests
  run: |
    poetry run pytest tests/ -v
```

**When to use:**
- Small test suites (< 5 minutes total)
- Fast CI runners
- High confidence requirements

**Pros:**
- Maximum confidence
- Catch bugs early
- Simple configuration

**Cons:**
- Slower CI pipeline
- May slow down development

#### Strategy 2: Separate Fast and Slow Tests (Recommended)

```yaml
# .github/workflows/test.yml
jobs:
  fast-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Run unit tests
        run: poetry run pytest tests/unit/ -v
      
  property-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Run property-based tests
        run: poetry run pytest tests/property_based/ -v
      
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Run integration tests
        run: poetry run pytest tests/integration/ -v
```

**When to use:**
- Medium to large projects
- Want fast feedback on unit tests
- Can parallelize test execution

**Pros:**
- Fast feedback from unit tests
- Parallel execution saves time
- Can fail fast on unit test failures

**Cons:**
- More complex CI configuration
- Need to manage multiple jobs

#### Strategy 3: Tiered Testing (Large Projects)

```yaml
# Run on every commit
on: [push]
jobs:
  unit-tests:
    run: poetry run pytest tests/unit/ -v

# Run on PR
on: [pull_request]
jobs:
  property-tests:
    run: poetry run pytest tests/property_based/ -v

# Run on merge to main
on:
  push:
    branches: [main]
jobs:
  all-tests:
    run: poetry run pytest tests/ -v
```

**When to use:**
- Large projects with slow test suites
- High commit frequency
- Want to optimize developer experience

**Pros:**
- Very fast feedback on commits
- Comprehensive testing before merge
- Optimized for developer productivity

**Cons:**
- Most complex configuration
- Bugs might not be caught until PR
- Requires discipline

#### Strategy 4: Reduced Examples for CI (Pragmatic)

```python
# conftest.py
import os
from hypothesis import settings

# Use fewer examples in CI for faster feedback
if os.getenv('CI'):
    settings.register_profile('ci', max_examples=20)
    settings.load_profile('ci')
else:
    settings.register_profile('dev', max_examples=100)
    settings.load_profile('dev')
```

```yaml
# .github/workflows/test.yml
- name: Run property-based tests (reduced)
  env:
    CI: true
  run: poetry run pytest tests/property_based/ -v
  # Runs 20 examples instead of 100 (5x faster)

# Nightly comprehensive run
on:
  schedule:
    - cron: '0 0 * * *'
jobs:
  comprehensive-tests:
    run: poetry run pytest tests/property_based/ -v
    # Runs full 100 examples
```

**When to use:**
- Want PBT on every commit but faster
- Can accept slightly less coverage in CI
- Run comprehensive tests nightly

**Pros:**
- Balance between speed and coverage
- Still get PBT benefits
- Comprehensive testing happens regularly

**Cons:**
- Might miss rare edge cases in CI
- Need to maintain two configurations

### Recommended Approach for This Project

Based on the performance numbers:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  # Fast feedback (< 1 second)
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: poetry run pytest tests/unit/ -v
      # 14 tests in 0.06s
  
  # Medium speed (< 5 seconds)
  property-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run property-based tests
        run: poetry run pytest tests/property_based/ -v
      # 33 tests in 3.43s
  
  # Slower (depends on AWS)
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run integration tests
        run: poetry run pytest tests/integration/ -v
      # Variable timing
```

**Why this works:**
- All tests run in parallel
- Fast feedback from unit tests (< 1s)
- Property tests complete quickly (< 5s)
- Total wall time ≈ slowest job (integration tests)

### Performance Optimization Tips

**1. Use Hypothesis Profiles**
```python
# conftest.py
from hypothesis import settings

settings.register_profile('ci', max_examples=20, deadline=None)
settings.register_profile('dev', max_examples=100, deadline=None)
settings.register_profile('thorough', max_examples=1000, deadline=None)
```

**2. Mark Slow Tests**
```python
import pytest

@pytest.mark.slow
@given(tasks=st.lists(task_ids, min_size=10, max_size=100))
def test_very_large_graphs(tasks):
    ...
```

```bash
# Run fast tests only
poetry run pytest -m "not slow"

# Run all tests
poetry run pytest
```

**3. Use Pytest-xdist for Parallelization**
```bash
poetry add --group dev pytest-xdist

# Run tests in parallel
poetry run pytest -n auto tests/property_based/
```

### Summary: When to Run PBT

| Scenario | Run PBT? | Configuration |
|----------|----------|---------------|
| **Local development** | ✅ Yes | Full 100 examples |
| **Pre-commit hook** | ⚠️ Optional | 20 examples (fast) |
| **Every commit (CI)** | ✅ Yes | 20-50 examples |
| **Pull request** | ✅ Yes | 100 examples |
| **Merge to main** | ✅ Yes | 100 examples |
| **Nightly builds** | ✅ Yes | 1000 examples (thorough) |
| **Release builds** | ✅ Yes | 1000+ examples |

### Bottom Line

**For this project:**
- ✅ Run PBT on every commit (only 3.43s)
- ✅ Run in parallel with other tests
- ✅ Use for pure business logic (circular dependency detection)
- ❌ Don't use for integration tests requiring specific data
- ⚠️ Consider reduced examples (20-50) for faster CI feedback

**The 3.43s runtime is acceptable for CI/CD**, especially when run in parallel with other test suites. The comprehensive coverage (3,300+ test cases) is worth the extra time.


## Debugging Invalid Examples

### What Causes Invalid Examples?

Invalid examples occur when Hypothesis generates data that doesn't meet your test's constraints. Common causes:

1. **Strategy constraints** - The strategy itself rejects some values
2. **assume() statements** - Your test explicitly rejects certain inputs
3. **UUID collisions** - Random UUIDs occasionally collide in complex data structures

### Example: Why test_self_dependency_returns_boolean_true Has 7 Invalid Examples

```bash
poetry run pytest tests/property_based/test_self_dependency_properties.py::TestSelfDependencyProperties::test_self_dependency_returns_boolean_true --hypothesis-show-statistics
```

Output shows:
```
100 passing examples, 0 failing examples, 7 invalid examples
```

**Why?** The test generates:
- A `task_id` (UUID)
- A `graph` (dictionary with UUID keys and UUID list values)

Occasionally, the randomly generated `task_id` matches a key in the randomly generated `graph`. This is rare (~1-2% probability) but happens due to the birthday paradox when generating many UUIDs.

### How to See What Data Was Rejected

#### Method 1: Run the Debug Test

We've created a special debug test that shows exactly what gets rejected:

```bash
poetry run pytest tests/property_based/test_show_rejections.py::test_demonstrate_uuid_collision_probability -v -s
```

This will show:
- Total number of collisions
- Collision rate percentage
- Example collisions with actual UUIDs
- Explanation of why it happens

Example output:
```
UUID COLLISION PROBABILITY DEMONSTRATION

Results:
   Total generations: 1000
   Collisions found: 17
   Collision rate: 1.70%

Example collisions:
   Example 1:
      task_id: c2a7af9e-ab79-b005-6dd1-77d2c700d84c
      graph_size: 7
      collision_type: task_id is a key in graph
```

#### Method 2: Use Hypothesis Verbosity

Add verbosity to any test to see all generated examples:

```python
from hypothesis import settings, Verbosity

@settings(verbosity=Verbosity.verbose, max_examples=10)
@given(task_id=task_ids, graph=dependency_graphs)
def test_something(self, task_id, graph):
    # Your test code
    ...
```

Run with `-s` flag to see output:
```bash
poetry run pytest tests/property_based/test_your_test.py -v -s
```

#### Method 3: Use event() to Track Patterns

Add `event()` calls to track what's happening:

```python
from hypothesis import event

@given(task_id=task_ids, graph=dependency_graphs)
def test_something(self, task_id, graph):
    if task_id in graph:
        event("task_id IS in graph")
    else:
        event("task_id NOT in graph")
    
    # Your test code
    ...
```

Run with `--hypothesis-show-statistics` to see event distribution:
```bash
poetry run pytest tests/property_based/test_your_test.py --hypothesis-show-statistics
```

Output shows:
```
Events:
  * 95%, task_id NOT in graph
  * 5%, task_id IS in graph
```

### Understanding the Numbers

For `test_self_dependency_returns_boolean_true`:
- **100 passing examples** - Successfully tested 100 valid cases ✅
- **0 failing examples** - No bugs found ✅
- **7 invalid examples** - 7 UUID collisions occurred (normal)

**Calculation:**
- Total attempts: 100 + 7 = 107
- Success rate: 100/107 = 93.5%
- Rejection rate: 7/107 = 6.5%

**Is this good?** Yes! A 6.5% rejection rate is excellent and has minimal performance impact.

### When to Worry About Invalid Examples

| Rejection Rate | Status | Action |
|----------------|--------|--------|
| 0-10% | ✅ Excellent | No action needed |
| 10-30% | ✅ Good | No action needed |
| 30-50% | ⚠️ Acceptable | Consider optimization if slow |
| 50-80% | ⚠️ Inefficient | Should optimize |
| 80%+ | ❌ Problem | Must optimize |

### Why UUID Collisions Happen (Birthday Paradox)

When generating many random UUIDs, collisions become more likely:

- **1 UUID**: 0% chance of collision
- **10 UUIDs**: ~0.00000001% chance
- **100 UUIDs**: ~0.000001% chance
- **1000 UUIDs**: ~0.0001% chance

In our tests:
- We generate 1 task_id
- We generate a graph with 0-20 keys (UUIDs)
- Each key has 0-10 values (UUIDs)
- Total: up to ~200 UUIDs per test
- Result: ~1-2% collision rate (matches our observations!)

This is the **birthday paradox** in action - with enough random values, collisions become probable even though each individual collision is unlikely.

### Reducing Invalid Examples (If Needed)

If you want to reduce invalid examples, you can:

#### Option 1: Use More Specific Strategies

Instead of generating independently and filtering:
```python
# Less efficient - generates then filters
@given(task_id=task_ids, graph=dependency_graphs)
def test_something(task_id, graph):
    assume(task_id not in graph)  # Causes rejections
```

Generate with constraints built-in:
```python
# More efficient - only generates valid data
@given(data=st.data())
def test_something(data):
    task_id = data.draw(task_ids)
    # Generate graph that doesn't include task_id
    graph = data.draw(st.dictionaries(
        keys=task_ids.filter(lambda x: x != task_id),
        values=st.lists(task_ids.filter(lambda x: x != task_id))
    ))
```

#### Option 2: Accept the Rejections

For low rejection rates (< 10%), it's often better to accept them:
- Simpler code
- Easier to understand
- Minimal performance impact
- More realistic data generation

**Our approach:** We accept the small number of UUID collisions because:
- Rejection rate is very low (1-7%)
- Code is simpler without complex filtering
- Performance impact is negligible
- Collisions are realistic (can happen in production too!)

### Summary

**Invalid examples are normal and expected** when using property-based testing. They occur due to:
1. Random data generation (UUID collisions)
2. Strategy constraints
3. Test assumptions

**For our tests:**
- 0-7 invalid examples per test is excellent
- Rejection rate of 0-7% is very good
- No optimization needed
- Tests run fast (< 0.3s per test)

**To debug invalid examples:**
1. Run `test_show_rejections.py` to see collision examples
2. Use `--hypothesis-show-statistics` to see rejection rates
3. Add `event()` calls to track patterns
4. Use `verbosity=Verbosity.verbose` to see all examples

The small number of invalid examples demonstrates that our UUID strategy is working well!
