# Test Suite for Energy Grid Model

This directory contains unit tests for the energy grid model.

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
# From project root
pytest tests/

# With verbose output
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=html
```

### Run Specific Test Files

```bash
# Test generators only
pytest tests/test_generators.py

# Test grid dispatch only
pytest tests/test_grid.py

# Test pricing calculations only
pytest tests/test_pricing.py
```

### Run Specific Tests

```bash
# Run a specific test function
pytest tests/test_grid.py::TestBasicDispatch::test_dispatch_merit_order

# Run tests matching a pattern
pytest tests/ -k "solar"
```

## Test Structure

- `test_generators.py` - Tests for generator classes (solar, wind, gas, etc.)
- `test_grid.py` - Tests for dispatch algorithm and edge cases
- `test_pricing.py` - Tests for revenue calculations and price analysis
- `test_demand.py` - Tests for demand profile calculations

## What's Tested

### Generators
- ✅ Solar output at different times (zero at night, peak at noon)
- ✅ Wind generator availability
- ✅ Gas marginal cost calculation (fuel + carbon + O&M)
- ✅ All generators have required attributes

### Grid Dispatch
- ✅ Merit order sorting (cheapest first)
- ✅ Demand is met when capacity is sufficient
- ✅ Price set by marginal generator
- ✅ Edge cases: negative demand, zero demand, insufficient capacity
- ✅ Renewable energy curtailment calculation

### Pricing
- ✅ Revenue calculations (generation × price)
- ✅ Average capture price
- ✅ Load factor calculations
- ✅ Price duration curves
- ✅ Cannibalisation metrics

### Demand
- ✅ Demand is always positive
- ✅ Weekday vs weekend patterns
- ✅ Seasonal variation (winter > summer)
- ✅ Peak hours (morning/evening)
- ✅ Electrification factor scaling

## Adding New Tests

When adding new functionality, add corresponding tests:

1. Create a test file or add to existing one
2. Follow the naming convention: `test_*.py`
3. Use descriptive test names: `test_what_it_does`
4. Use pytest fixtures for setup if needed
5. Use `assert` statements to verify behavior

Example:

```python
def test_new_feature():
    """Test description."""
    # Setup
    grid = Grid(generators=[...])
    
    # Execute
    result = grid.some_method()
    
    # Verify
    assert result.expected_value == actual_value
```

## Test Coverage

To see test coverage:

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

This shows which lines of code are covered by tests and which aren't.


