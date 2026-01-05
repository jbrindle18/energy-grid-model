"""
Unit tests for demand profile calculations.
"""
import pytest
from src.demand import DemandProfile, create_uk_demand_profile, create_future_demand_profile


class TestDemandProfile:
    """Tests for DemandProfile class."""
    
    def test_demand_positive(self):
        """Demand should always be positive."""
        profile = DemandProfile()
        
        for hour in range(24):
            for day in [0, 90, 180, 270]:  # Different seasons
                demand = profile.get_demand(hour, day, is_weekday=True)
                assert demand > 0
    
    def test_demand_weekday_higher_than_weekend(self):
        """Weekday demand should generally be higher than weekend."""
        profile = DemandProfile()
        
        weekday_demands = [profile.get_demand(h, 180, is_weekday=True) 
                          for h in range(24)]
        weekend_demands = [profile.get_demand(h, 180, is_weekday=False) 
                          for h in range(24)]
        
        # Average weekday should be higher
        avg_weekday = sum(weekday_demands) / len(weekday_demands)
        avg_weekend = sum(weekend_demands) / len(weekend_demands)
        
        assert avg_weekday > avg_weekend
    
    def test_demand_peak_hours(self):
        """Demand should peak in morning and evening."""
        profile = DemandProfile()
        
        demands = [profile.get_demand(h, 180, is_weekday=True) 
                  for h in range(24)]
        
        # Morning peak around 8am (hour 8)
        # Evening peak around 6pm (hour 18)
        morning_peak = demands[8]
        evening_peak = demands[18]
        overnight = demands[3]  # 3am
        
        assert morning_peak > overnight
        assert evening_peak > overnight
    
    def test_demand_seasonal_variation(self):
        """Winter demand should be higher than summer demand."""
        profile = DemandProfile()
        
        # Winter (day 355) vs Summer (day 172)
        winter_demands = [profile.get_demand(h, 355, is_weekday=True) 
                         for h in range(24)]
        summer_demands = [profile.get_demand(h, 172, is_weekday=True) 
                         for h in range(24)]
        
        avg_winter = sum(winter_demands) / len(winter_demands)
        avg_summer = sum(summer_demands) / len(summer_demands)
        
        assert avg_winter > avg_summer
    
    def test_demand_within_bounds(self):
        """Demand should be within min and max bounds."""
        profile = DemandProfile(
            min_demand_gw=25.0,
            peak_demand_gw=50.0
        )
        
        for hour in range(24):
            for day in range(365):
                demand_mw = profile.get_demand(hour, day, is_weekday=True)
                demand_gw = demand_mw / 1000
                
                assert 25.0 <= demand_gw <= 50.0
    
    def test_generate_year_profile(self):
        """generate_year_profile should return correct number of hours."""
        profile = DemandProfile()
        
        year_demands = profile.generate_year_profile()
        
        assert len(year_demands) == 8760  # 365 * 24
        assert all(d > 0 for d in year_demands)
    
    def test_generate_day_profile(self):
        """generate_day_profile should return 24 hours."""
        profile = DemandProfile()
        
        day_demands = profile.generate_day_profile(day_of_year=180, is_weekday=True)
        
        assert len(day_demands) == 24
        assert all(d > 0 for d in day_demands)


class TestDemandProfileFactories:
    """Tests for demand profile factory functions."""
    
    def test_create_uk_demand_profile(self):
        """create_uk_demand_profile should return valid profile."""
        profile = create_uk_demand_profile()
        
        assert isinstance(profile, DemandProfile)
        assert profile.base_demand_gw == 35.0
        assert profile.peak_demand_gw == 50.0
        assert profile.min_demand_gw == 25.0
    
    def test_create_future_demand_profile(self):
        """create_future_demand_profile should scale demand."""
        profile = create_future_demand_profile(electrification_factor=1.5)
        
        assert isinstance(profile, DemandProfile)
        # Should scale all demand values
        assert profile.peak_demand_gw == 50.0 * 1.5
        assert profile.min_demand_gw == 25.0 * 1.5
        assert profile.base_demand_gw == 35.0 * 1.5
    
    def test_electrification_factor_scaling(self):
        """Electrification factor should scale demand proportionally."""
        base_profile = create_uk_demand_profile()
        future_profile = create_future_demand_profile(electrification_factor=2.0)
        
        # Check that future demand is exactly double
        assert future_profile.peak_demand_gw == base_profile.peak_demand_gw * 2.0
        assert future_profile.min_demand_gw == base_profile.min_demand_gw * 2.0


