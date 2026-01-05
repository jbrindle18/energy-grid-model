"""
Unit tests for generator classes.

Tests generator availability, marginal costs, and basic functionality.
"""
import pytest
from src.generators import (
    SolarGenerator, OnshoreWindGenerator, OffshoreWindGenerator,
    GasGenerator, NuclearGenerator, BiomassGenerator,
    HydroGenerator, InterconnectorImport
)


class TestSolarGenerator:
    """Tests for SolarGenerator."""
    
    def test_solar_zero_at_night(self):
        """Solar should produce zero power at night."""
        solar = SolarGenerator(name="Test Solar", capacity_mw=1000)
        output = solar.available_power(hour=0, day_of_year=172)  # Midnight
        assert output == 0.0
    
    def test_solar_peak_at_noon_summer(self):
        """Solar should have peak output at noon in summer."""
        solar = SolarGenerator(name="Test Solar", capacity_mw=1000)
        output = solar.available_power(hour=12, day_of_year=172)  # Noon, summer
        assert output > 0
        assert output < solar.capacity_mw  # Should be less than capacity
    
    def test_solar_marginal_cost_zero(self):
        """Solar should have zero marginal cost."""
        solar = SolarGenerator(name="Test Solar", capacity_mw=1000)
        assert solar.marginal_cost == 0.0


class TestWindGenerators:
    """Tests for wind generators."""
    
    def test_onshore_wind_has_output(self):
        """Onshore wind should have some output."""
        wind = OnshoreWindGenerator(name="Test Wind", capacity_mw=1000)
        output = wind.available_power(hour=12, day_of_year=172)
        assert output > 0
        assert output <= wind.capacity_mw
    
    def test_offshore_wind_higher_than_onshore(self):
        """Offshore wind typically has higher capacity factor."""
        onshore = OnshoreWindGenerator(name="Onshore", capacity_mw=1000)
        offshore = OffshoreWindGenerator(name="Offshore", capacity_mw=1000)
        
        # Average over a few hours
        onshore_avg = sum(onshore.available_power(hour=h, day_of_year=172) 
                         for h in range(24)) / 24
        offshore_avg = sum(offshore.available_power(hour=h, day_of_year=172) 
                          for h in range(24)) / 24
        
        assert offshore_avg > onshore_avg
    
    def test_wind_marginal_cost_zero(self):
        """Wind generators should have zero marginal cost."""
        onshore = OnshoreWindGenerator(name="Test", capacity_mw=1000)
        offshore = OffshoreWindGenerator(name="Test", capacity_mw=1000)
        assert onshore.marginal_cost == 0.0
        assert offshore.marginal_cost == 0.0


class TestGasGenerator:
    """Tests for GasGenerator."""
    
    def test_gas_marginal_cost_calculation(self):
        """Gas marginal cost should include fuel, carbon, and O&M."""
        gas = GasGenerator(
            name="Test Gas",
            capacity_mw=1000,
            fuel_cost_per_mwh=50.0,
            carbon_price_per_tonne=60.0,
            variable_om_per_mwh=3.0
        )
        # Expected: 50 + (60 * 0.4) + 3 = 50 + 24 + 3 = 77
        expected = 50.0 + (60.0 * 0.4) + 3.0
        assert gas.marginal_cost == pytest.approx(expected, abs=0.1)
    
    def test_gas_uses_full_capacity(self):
        """Gas should use full capacity when available."""
        gas = GasGenerator(name="Test Gas", capacity_mw=1000, fuel_cost_per_mwh=55.0)
        output = gas.available_power(hour=12, day_of_year=172)
        # Should be capacity * capacity_factor (0.95)
        assert output == pytest.approx(1000 * 0.95, abs=1.0)
    
    def test_gas_default_marginal_cost(self):
        """Default gas marginal cost should be reasonable."""
        gas = GasGenerator(name="Test Gas", capacity_mw=1000, fuel_cost_per_mwh=55.0)
        # Default should be around £82/MWh (55 + 24 + 3)
        assert 70 <= gas.marginal_cost <= 90


class TestOtherGenerators:
    """Tests for other generator types."""
    
    def test_nuclear_marginal_cost(self):
        """Nuclear should have low marginal cost."""
        nuclear = NuclearGenerator(name="Test Nuclear", capacity_mw=1000)
        assert nuclear.marginal_cost == 10.0
    
    def test_biomass_marginal_cost(self):
        """Biomass should have moderate marginal cost."""
        biomass = BiomassGenerator(name="Test Biomass", capacity_mw=1000)
        assert biomass.marginal_cost == 45.0
    
    def test_hydro_marginal_cost(self):
        """Hydro should have very low marginal cost."""
        hydro = HydroGenerator(name="Test Hydro", capacity_mw=1000)
        assert hydro.marginal_cost == 5.0
    
    def test_interconnector_marginal_cost(self):
        """Interconnector should have moderate marginal cost."""
        inter = InterconnectorImport(name="Test Inter", capacity_mw=1000)
        assert inter.marginal_cost == 55.0


class TestGeneratorBasics:
    """Basic tests for all generators."""
    
    def test_all_generators_have_name_and_capacity(self):
        """All generators should have name and capacity."""
        generators = [
            SolarGenerator(name="Solar", capacity_mw=100),
            OnshoreWindGenerator(name="Wind", capacity_mw=200),
            GasGenerator(name="Gas", capacity_mw=300),
            NuclearGenerator(name="Nuclear", capacity_mw=400),
        ]
        
        for gen in generators:
            assert gen.name
            assert gen.capacity_mw > 0
            assert gen.marginal_cost >= 0
    
    def test_generator_repr(self):
        """Generator __repr__ should be informative."""
        gas = GasGenerator(name="Test Gas", capacity_mw=1000, fuel_cost_per_mwh=55.0)
        repr_str = repr(gas)
        assert "Test Gas" in repr_str
        assert "1000" in repr_str or "1" in repr_str  # Might show as 1GW


