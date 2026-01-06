"""
Unit tests for pricing and revenue calculations.
"""
import pytest
from src.grid import Grid, DispatchResult
from src.generators import (
    SolarGenerator, GasGenerator, NuclearGenerator
)
from src.pricing import (
    calculate_generator_revenues,
    PriceDurationCurve,
    CannibalalisationMetrics
)


class TestRevenueCalculation:
    """Tests for generator revenue calculations."""
    
    def test_revenue_calculation_basic(self):
        """Revenue should be generation * price for each hour."""
        # Create a simple scenario
        grid = Grid(generators=[
            SolarGenerator(name="Solar", capacity_mw=1000),
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0),
        ])
        
        # Simulate one hour
        result = grid.dispatch(demand_mw=1500, hour=12, day_of_year=172)
        results = [result]
        
        revenues = calculate_generator_revenues(results)
        
        # Should have revenues for dispatched generators
        assert len(revenues) > 0
        
        # Total revenue should equal sum of (generation * price)
        total_revenue = sum(r.total_revenue_gbp for r in revenues)
        expected = sum(mw * result.wholesale_price 
                      for _, mw in result.dispatched_generators)
        assert total_revenue == pytest.approx(expected, abs=0.01)
    
    def test_average_capture_price(self):
        """Average capture price should equal total revenue / total generation."""
        grid = Grid(generators=[
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0),
        ])
        
        results = []
        for hour in range(24):
            result = grid.dispatch(demand_mw=500, hour=hour, day_of_year=172)
            results.append(result)
        
        revenues = calculate_generator_revenues(results)
        gas_revenue = next(r for r in revenues if r.name == "Gas")
        
        # Average capture price should be revenue / generation
        if gas_revenue.total_generation_mwh > 0:
            expected_avg = (gas_revenue.total_revenue_gbp / 
                          gas_revenue.total_generation_mwh)
            assert gas_revenue.average_capture_price == pytest.approx(expected_avg, abs=0.01)
    
    def test_load_factor_calculation(self):
        """Load factor should be actual generation / potential generation."""
        grid = Grid(generators=[
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0),
        ])
        
        # Simulate 24 hours with constant demand
        results = []
        for hour in range(24):
            result = grid.dispatch(demand_mw=500, hour=hour, day_of_year=172)
            results.append(result)
        
        revenues = calculate_generator_revenues(results)
        gas_revenue = next(r for r in revenues if r.name == "Gas")
        
        # Load factor should be between 0 and 1
        assert 0 <= gas_revenue.load_factor <= 1
        
        # If running at half capacity, load factor should be around 0.5
        # (accounting for capacity_factor)
        expected_load = 500 / (1000 * 0.95)  # demand / (capacity * capacity_factor)
        assert gas_revenue.load_factor == pytest.approx(expected_load, abs=0.1)


class TestPriceDurationCurve:
    """Tests for price duration curve."""
    
    def test_price_duration_curve_creation(self):
        """Price duration curve should be created from results."""
        grid = Grid(generators=[
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0),
        ])
        
        results = []
        for hour in range(24):
            result = grid.dispatch(demand_mw=500, hour=hour, day_of_year=172)
            results.append(result)
        
        curve = PriceDurationCurve.from_results(results)
        
        assert len(curve.prices_sorted) == 24
        assert len(curve.hours) == 24
    
    def test_prices_sorted_descending(self):
        """Prices should be sorted in descending order."""
        grid = Grid(generators=[
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0),
        ])
        
        results = []
        for hour in range(10):
            result = grid.dispatch(demand_mw=500, hour=hour, day_of_year=172)
            results.append(result)
        
        curve = PriceDurationCurve.from_results(results)
        
        # Check prices are descending
        for i in range(len(curve.prices_sorted) - 1):
            assert curve.prices_sorted[i] >= curve.prices_sorted[i + 1]
    
    def test_price_at_percentile(self):
        """Price at percentile should return correct value."""
        grid = Grid(generators=[
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0),
        ])
        
        results = []
        for hour in range(100):
            result = grid.dispatch(demand_mw=500, hour=hour, day_of_year=172)
            results.append(result)
        
        curve = PriceDurationCurve.from_results(results)
        
        # P50 should be median
        p50 = curve.price_at_percentile(50)
        median_price = sorted([r.wholesale_price for r in results])[50]
        assert p50 == pytest.approx(median_price, abs=1.0)


class TestCannibalisationMetrics:
    """Tests for cannibalisation metrics."""
    
    def test_cannibalisation_metrics_creation(self):
        """Cannibalisation metrics should be calculated from results."""
        grid = Grid(generators=[
            SolarGenerator(name="Solar", capacity_mw=1000),
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0),
        ])
        
        results = []
        for hour in range(24):
            result = grid.dispatch(demand_mw=1000, hour=hour, day_of_year=172)
            results.append(result)
        
        metrics = CannibalalisationMetrics.from_results(results)
        
        assert metrics.average_wholesale_price > 0
        assert metrics.total_hours == 24
        assert 0 <= metrics.capture_rate <= 2  # Can be > 1 if RE gets higher prices
    
    def test_capture_rate_calculation(self):
        """Capture rate should be RE capture price / average wholesale price."""
        grid = Grid(generators=[
            SolarGenerator(name="Solar", capacity_mw=2000),
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0),
        ])
        
        results = []
        for hour in range(24):
            result = grid.dispatch(demand_mw=1500, hour=hour, day_of_year=172)
            results.append(result)
        
        metrics = CannibalalisationMetrics.from_results(results)
        
        # Capture rate should be calculated correctly
        if metrics.average_wholesale_price > 0:
            expected_rate = (metrics.average_re_capture_price / 
                           metrics.average_wholesale_price)
            assert metrics.capture_rate == pytest.approx(expected_rate, abs=0.01)
    
    def test_empty_results_raises_error(self):
        """Empty results should raise ValueError."""
        with pytest.raises(ValueError):
            CannibalalisationMetrics.from_results([])


