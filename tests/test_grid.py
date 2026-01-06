"""
Unit tests for grid dispatch logic.

Tests the core merit order dispatch algorithm and edge cases.
"""
import pytest
from src.grid import Grid, DispatchResult, RE_MARGINAL_COST_THRESHOLD
from src.generators import (
    SolarGenerator, OnshoreWindGenerator, GasGenerator,
    NuclearGenerator, BiomassGenerator
)


class TestBasicDispatch:
    """Tests for basic dispatch functionality."""
    
    def test_dispatch_single_generator(self):
        """Dispatch with a single generator should meet demand."""
        grid = Grid(generators=[
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0)
        ])
        
        result = grid.dispatch(demand_mw=500, hour=12, day_of_year=172)
        
        assert result.total_generation_mw == 500
        assert result.wholesale_price == pytest.approx(82.0, abs=1.0)  # Default gas cost
        assert len(result.dispatched_generators) == 1
    
    def test_dispatch_merit_order(self):
        """Generators should be dispatched in merit order (cheapest first)."""
        grid = Grid(generators=[
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0),
            SolarGenerator(name="Solar", capacity_mw=1000),
            NuclearGenerator(name="Nuclear", capacity_mw=1000),
        ])
        
        result = grid.dispatch(demand_mw=1500, hour=12, day_of_year=172)
        
        # Solar (zero cost) should be dispatched first
        dispatched_names = [gen.name for gen, _ in result.dispatched_generators]
        assert "Solar" in dispatched_names
        
        # Price should be set by the marginal generator (Nuclear at £10/MWh)
        assert result.wholesale_price == 10.0
    
    def test_dispatch_meets_demand(self):
        """Dispatch should always meet demand if capacity is sufficient."""
        grid = Grid(generators=[
            GasGenerator(name="Gas", capacity_mw=2000, marginal_cost_per_mwh=73.0)
        ])
        
        result = grid.dispatch(demand_mw=1500, hour=12, day_of_year=172)
        
        assert result.total_generation_mw == 1500
        assert result.demand_mw == 1500
    
    def test_price_set_by_marginal_generator(self):
        """Wholesale price should equal marginal cost of last dispatched generator."""
        grid = Grid(generators=[
            SolarGenerator(name="Solar", capacity_mw=500),
            NuclearGenerator(name="Nuclear", capacity_mw=500),
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0),
        ])
        
        # Demand that requires all three
        result = grid.dispatch(demand_mw=1500, hour=12, day_of_year=172)
        
        # Price should be set by Gas (the marginal generator)
        assert result.wholesale_price == pytest.approx(82.0, abs=1.0)
        assert result.price_setter.name == "Gas"


class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_negative_demand_raises_error(self):
        """Negative demand should raise ValueError."""
        grid = Grid(generators=[
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0)
        ])
        
        with pytest.raises(ValueError, match="Demand must be non-negative"):
            grid.dispatch(demand_mw=-100, hour=12, day_of_year=172)
    
    def test_zero_demand(self):
        """Zero demand should result in zero generation."""
        grid = Grid(generators=[
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0)
        ])
        
        result = grid.dispatch(demand_mw=0, hour=12, day_of_year=172)
        
        assert result.total_generation_mw == 0
        assert len(result.dispatched_generators) == 0
    
    def test_empty_generators_raises_error(self):
        """Empty generator list should raise ValueError."""
        grid = Grid(generators=[])
        
        with pytest.raises(ValueError, match="Cannot dispatch with no generators"):
            grid.dispatch(demand_mw=100, hour=12, day_of_year=172)
    
    def test_insufficient_capacity_emergency_pricing(self):
        """When demand exceeds capacity, price should spike to emergency level."""
        grid = Grid(generators=[
            GasGenerator(name="Gas", capacity_mw=500, marginal_cost_per_mwh=73.0)
        ])
        
        result = grid.dispatch(demand_mw=1000, hour=12, day_of_year=172)
        
        # Should hit emergency price cap
        assert result.wholesale_price == 1000.0
        assert result.total_generation_mw < result.demand_mw


class TestRenewableEnergy:
    """Tests for renewable energy behavior."""
    
    def test_renewables_dispatched_first(self):
        """Renewables (zero cost) should be dispatched before fossil fuels."""
        grid = Grid(generators=[
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0),
            SolarGenerator(name="Solar", capacity_mw=500),
            OnshoreWindGenerator(name="Wind", capacity_mw=500),
        ])
        
        result = grid.dispatch(demand_mw=1000, hour=12, day_of_year=172)
        
        # All renewables should be dispatched before gas (check order)
        dispatched_names = [gen.name for gen, _ in result.dispatched_generators]
        
        # Renewables should appear before gas in the dispatch order
        if "Gas" in dispatched_names:
            gas_index = dispatched_names.index("Gas")
            # Check that at least one renewable comes before gas
            renewables_before_gas = any(
                name in ["Solar", "Wind"] and dispatched_names.index(name) < gas_index
                for name in dispatched_names
            )
            assert renewables_before_gas, "Renewables should be dispatched before gas"
        
        # If renewables fully meet demand, gas shouldn't be dispatched
        re_generation = sum(
            mw for gen, mw in result.dispatched_generators
            if gen.marginal_cost < RE_MARGINAL_COST_THRESHOLD
        )
        if re_generation >= result.demand_mw:
            assert "Gas" not in dispatched_names
            assert result.wholesale_price == 0.0
    
    def test_curtailment_calculation(self):
        """Curtailment should be calculated when RE exceeds demand."""
        grid = Grid(generators=[
            SolarGenerator(name="Solar", capacity_mw=2000),
            OnshoreWindGenerator(name="Wind", capacity_mw=2000),
        ])
        
        # Low demand, high RE availability
        result = grid.dispatch(demand_mw=500, hour=12, day_of_year=172)
        
        # Should have curtailment if RE available > demand
        re_available = sum(
            gen.available_power(12, 172) 
            for gen in grid.generators 
            if gen.marginal_cost < RE_MARGINAL_COST_THRESHOLD
        )
        
        if re_available > 500:
            assert result.curtailment_mw > 0
    
    def test_re_share_property(self):
        """RE share should be calculated correctly."""
        grid = Grid(generators=[
            SolarGenerator(name="Solar", capacity_mw=1000),
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0),
        ])
        
        result = grid.dispatch(demand_mw=1500, hour=12, day_of_year=172)
        
        # RE share should be between 0 and 1
        assert 0 <= result.re_share <= 1
        
        # If solar is dispatched, RE share should be > 0
        if any(gen.name == "Solar" for gen, _ in result.dispatched_generators):
            assert result.re_share > 0


class TestDispatchResult:
    """Tests for DispatchResult properties."""
    
    def test_is_oversupply_property(self):
        """is_oversupply should be True when there's curtailment."""
        grid = Grid(generators=[
            SolarGenerator(name="Solar", capacity_mw=2000),
        ])
        
        result = grid.dispatch(demand_mw=500, hour=12, day_of_year=172)
        
        # If there's curtailment, is_oversupply should be True
        assert result.is_oversupply == (result.curtailment_mw > 0)
    
    def test_dispatch_result_fields(self):
        """DispatchResult should have all required fields."""
        grid = Grid(generators=[
            GasGenerator(name="Gas", capacity_mw=1000, marginal_cost_per_mwh=73.0)
        ])
        
        result = grid.dispatch(demand_mw=500, hour=12, day_of_year=172)
        
        assert hasattr(result, 'hour')
        assert hasattr(result, 'day_of_year')
        assert hasattr(result, 'demand_mw')
        assert hasattr(result, 'wholesale_price')
        assert hasattr(result, 'dispatched_generators')
        assert hasattr(result, 'total_generation_mw')
        assert hasattr(result, 'price_setter')
        assert hasattr(result, 'curtailment_mw')

