"""
UK electricity demand model.

Models realistic UK demand patterns:
- Hourly variation (morning and evening peaks)
- Daily variation (weekday vs weekend)
- Seasonal variation (higher in winter)

Based on National Grid ESO historical demand patterns.
UK typical demand range: 25-50 GW
"""

import numpy as np
from dataclasses import dataclass

try:
    from .constants import (
        UK_BASE_PEAK_DEMAND_GW, UK_BASE_AVERAGE_DEMAND_GW, UK_BASE_MIN_DEMAND_GW
    )
except ImportError:
    from constants import (
        UK_BASE_PEAK_DEMAND_GW, UK_BASE_AVERAGE_DEMAND_GW, UK_BASE_MIN_DEMAND_GW
    )


@dataclass
class DemandProfile:
    """
    UK electricity demand profile generator.

    Attributes:
        base_demand_gw: Average annual demand in GW (~35 GW for UK)
        peak_demand_gw: Maximum demand in GW (~50 GW for UK winter peak)
        min_demand_gw: Minimum demand in GW (~25 GW for UK summer night)
    """
    base_demand_gw: float = UK_BASE_AVERAGE_DEMAND_GW
    peak_demand_gw: float = UK_BASE_PEAK_DEMAND_GW
    min_demand_gw: float = UK_BASE_MIN_DEMAND_GW

    def get_demand(self, hour: int, day_of_year: int, is_weekday: bool = True) -> float:
        """
        Calculate demand in MW for a specific time.

        Args:
            hour: Hour of day (0-23)
            day_of_year: Day of year (0-364)
            is_weekday: Whether it's a weekday (higher commercial demand)

        Returns:
            Demand in MW
        """
        # Seasonal factor: higher in winter, lower in summer
        # Winter solstice = day 355, summer solstice = day 172
        winter_solstice = 355
        days_from_winter = min(abs(day_of_year - winter_solstice),
                               365 - abs(day_of_year - winter_solstice))
        seasonal_factor = 1.0 - 0.3 * (days_from_winter / 182)  # ±15% seasonal swing

        # Daily profile: two peaks (morning ~8am, evening ~6pm)
        # Minimum overnight (3-5am)
        hourly_factors = np.array([
            0.70, 0.65, 0.62, 0.60, 0.60, 0.62,  # 0-5am (overnight low)
            0.70, 0.82, 0.92, 0.95, 0.95, 0.93,  # 6-11am (morning ramp)
            0.90, 0.88, 0.87, 0.88, 0.92, 1.00,  # 12-5pm (afternoon)
            1.00, 0.97, 0.92, 0.87, 0.80, 0.75,  # 6-11pm (evening peak then decline)
        ])
        hourly_factor = hourly_factors[hour]

        # Weekend factor: lower commercial/industrial demand
        weekend_factor = 0.90 if not is_weekday else 1.0

        # Calculate final demand
        demand_range = self.peak_demand_gw - self.min_demand_gw
        demand_gw = (self.min_demand_gw +
                     demand_range * hourly_factor * seasonal_factor * weekend_factor)

        return demand_gw * 1000  # Return in MW

    def generate_year_profile(self, year_hours: int = 8760) -> np.ndarray:
        """
        Generate hourly demand for a full year.

        Args:
            year_hours: Number of hours (default 8760 = 365 days)

        Returns:
            Array of demand values in MW for each hour
        """
        demands = np.zeros(year_hours)

        for h in range(year_hours):
            hour = h % 24
            day = h // 24
            day_of_year = day % 365
            # Simple weekday logic: 5 weekdays, 2 weekend days
            is_weekday = (day % 7) < 5

            demands[h] = self.get_demand(hour, day_of_year, is_weekday)

        return demands

    def generate_day_profile(self, day_of_year: int = 172,
                             is_weekday: bool = True) -> np.ndarray:
        """
        Generate hourly demand for a single day.

        Args:
            day_of_year: Day of year (0-364)
            is_weekday: Whether it's a weekday

        Returns:
            Array of 24 hourly demand values in MW
        """
        return np.array([
            self.get_demand(hour, day_of_year, is_weekday)
            for hour in range(24)
        ])


def create_uk_demand_profile() -> DemandProfile:
    """Create a demand profile with typical UK parameters."""
    return DemandProfile(
        base_demand_gw=UK_BASE_AVERAGE_DEMAND_GW,
        peak_demand_gw=UK_BASE_PEAK_DEMAND_GW,
        min_demand_gw=UK_BASE_MIN_DEMAND_GW
    )


def create_future_demand_profile(electrification_factor: float = 1.3) -> DemandProfile:
    """
    Create a future demand profile accounting for electrification.

    Args:
        electrification_factor: Multiplier for demand growth (1.3 = 30% increase)
            Accounts for EVs, heat pumps, etc.
    """
    return DemandProfile(
        base_demand_gw=UK_BASE_AVERAGE_DEMAND_GW * electrification_factor,
        peak_demand_gw=UK_BASE_PEAK_DEMAND_GW * electrification_factor,
        min_demand_gw=UK_BASE_MIN_DEMAND_GW * electrification_factor
    )
