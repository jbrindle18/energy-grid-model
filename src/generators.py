"""
Generator classes for UK electricity grid simulation.

Each generator type models:
- Capacity (MW)
- Marginal cost (£/MWh)
- Capacity factor (average availability)
- Time-varying availability for weather-dependent sources

UK-realistic parameters based on BEIS/DESNZ statistics and industry estimates.
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np

try:
    from .constants import (
        GAS_EMISSIONS_FACTOR, GAS_VARIABLE_OM,
        UK_SOLAR_CAPACITY_FACTOR, UK_ONSHORE_WIND_CAPACITY_FACTOR,
        UK_OFFSHORE_WIND_CAPACITY_FACTOR
    )
except ImportError:
    from constants import (
        GAS_EMISSIONS_FACTOR, GAS_VARIABLE_OM,
        UK_SOLAR_CAPACITY_FACTOR, UK_ONSHORE_WIND_CAPACITY_FACTOR,
        UK_OFFSHORE_WIND_CAPACITY_FACTOR
    )


@dataclass
class Generator:
    """Base generator class."""
    name: str
    capacity_mw: float  # Nameplate capacity in MW
    marginal_cost: float = field(init=False)  # £/MWh - can be set in __post_init__ or as property
    capacity_factor: float = 1.0  # Average availability (0-1)

    def available_power(self, hour: int = 0, day_of_year: int = 0) -> float:
        """
        Calculate available power at a given time.
        Base implementation returns capacity * capacity_factor.
        Override in subclasses for time-varying availability.
        """
        return self.capacity_mw * self.capacity_factor

    def __repr__(self):
        return f"{self.name}: {self.capacity_mw:.0f}MW @ £{self.marginal_cost:.1f}/MWh"


@dataclass
class SolarGenerator(Generator):
    """
    Solar PV generator with time-varying output.

    UK solar capacity factor: ~11% annual average (BEIS 2023)
    Output varies by:
    - Hour of day (peak around noon)
    - Season (higher in summer)
    """
    marginal_cost: float = 0.0  # Near-zero marginal cost
    capacity_factor: float = UK_SOLAR_CAPACITY_FACTOR  # UK average

    def available_power(self, hour: int = 12, day_of_year: int = 172) -> float:
        """
        Calculate solar output based on time of day and season.

        Args:
            hour: Hour of day (0-23)
            day_of_year: Day of year (0-364), 172 = summer solstice
        """
        # Simplified but realistic UK solar profile
        # Peak capacity factor ~50-60% at noon in summer, 0 at night

        summer_solstice = 172
        days_from_solstice = min(abs(day_of_year - summer_solstice),
                                  365 - abs(day_of_year - summer_solstice))

        # Daylight hours: ~16.5h at summer solstice, ~7.5h at winter solstice in UK
        daylight_hours = 16.5 - (days_from_solstice / 182) * 9
        sunrise = 12 - daylight_hours / 2
        sunset = 12 + daylight_hours / 2

        if hour < sunrise or hour > sunset:
            return 0.0

        # Smooth bell curve using sine - peaks at noon
        # Map hour to 0-pi range during daylight
        daylight_position = (hour - sunrise) / daylight_hours  # 0 to 1
        daily_factor = np.sin(np.pi * daylight_position)  # Smooth curve 0->1->0

        # Seasonal factor: higher irradiance in summer (1.0 summer, 0.4 winter)
        seasonal_factor = 1.0 - 0.6 * (days_from_solstice / 182)

        # Peak output ~55% of capacity at noon in summer
        peak_factor = 0.55

        return self.capacity_mw * daily_factor * seasonal_factor * peak_factor


@dataclass
class OnshoreWindGenerator(Generator):
    """
    Onshore wind generator.

    UK onshore wind capacity factor: ~27% average (BEIS 2023)
    But highly variable: 5-80% depending on weather.
    """
    marginal_cost: float = 0.0
    capacity_factor: float = UK_ONSHORE_WIND_CAPACITY_FACTOR

    def available_power(self, hour: int = 0, day_of_year: int = 0) -> float:
        """
        Wind output with realistic day-to-day weather variation.
        Creates pattern of windy days vs calm days.
        """
        # Create "weather systems" - multi-day patterns
        # Use multiple overlapping waves to create realistic-looking variation
        weather1 = np.sin(2 * np.pi * day_of_year / 3.7)   # ~4 day cycle
        weather2 = np.sin(2 * np.pi * day_of_year / 7.3)   # ~weekly
        weather3 = np.sin(2 * np.pi * day_of_year / 2.1)   # ~2 day

        # Combine for weather pattern (-1 to 1)
        weather = (weather1 + weather2 * 0.7 + weather3 * 0.5) / 2.2

        # Daily variation: wind often higher at night, lower afternoon
        daily = 0.08 * np.sin(2 * np.pi * (hour - 14) / 24)

        # Map to capacity factor: base 27%, range from 8% to 75%
        # weather=-1 -> 8%, weather=0 -> 27%, weather=1 -> 75%
        if weather >= 0:
            factor = self.capacity_factor + weather * 0.48  # Up to 75%
        else:
            factor = self.capacity_factor + weather * 0.19  # Down to 8%

        factor = factor + daily
        factor = max(0.05, min(0.80, factor))

        return self.capacity_mw * factor


@dataclass
class OffshoreWindGenerator(Generator):
    """
    Offshore wind generator.

    UK offshore wind capacity factor: ~40% average (BEIS 2023)
    More consistent than onshore but still variable: 15-85%.
    """
    marginal_cost: float = 0.0
    capacity_factor: float = UK_OFFSHORE_WIND_CAPACITY_FACTOR

    def available_power(self, hour: int = 0, day_of_year: int = 0) -> float:
        """
        Offshore wind - higher and more consistent than onshore.
        Still has significant weather-driven variation.
        """
        # Similar weather pattern but less extreme
        weather1 = np.sin(2 * np.pi * day_of_year / 3.7)
        weather2 = np.sin(2 * np.pi * day_of_year / 7.3)
        weather3 = np.sin(2 * np.pi * day_of_year / 2.1)

        weather = (weather1 + weather2 * 0.7 + weather3 * 0.5) / 2.2

        # Smaller daily variation offshore
        daily = 0.05 * np.sin(2 * np.pi * (hour - 14) / 24)

        # Map to capacity factor: base 40%, range from 15% to 80%
        if weather >= 0:
            factor = self.capacity_factor + weather * 0.40  # Up to 80%
        else:
            factor = self.capacity_factor + weather * 0.25  # Down to 15%

        factor = factor + daily
        factor = max(0.12, min(0.85, factor))

        return self.capacity_mw * factor


@dataclass
class GasGenerator(Generator):
    """
    Combined Cycle Gas Turbine (CCGT).

    Gas is the marginal price-setter in most UK hours.
    Marginal cost includes:
    - Fuel cost (gas price)
    - Carbon cost (UK ETS allowance price × emissions factor)
    - Variable O&M (~£2-5/MWh)

    UK ETS: ~£50-70/tonne CO₂ (2025)
    Gas emissions: ~0.4 tonnes CO₂/MWh
    Carbon cost: ~£20-30/MWh

    Total marginal cost typically £70-100/MWh in 2025
    (can vary from £50-150+ depending on gas and carbon markets).
    """
    fuel_cost_per_mwh: float = 55.0  # £/MWh - gas fuel cost (highly variable)
    carbon_price_per_tonne: float = 60.0  # £/tonne CO₂ - UK ETS price (2025 typical)
    emissions_factor: float = GAS_EMISSIONS_FACTOR  # tonnes CO₂ per MWh for gas CCGT
    variable_om_per_mwh: float = GAS_VARIABLE_OM  # £/MWh - variable operations & maintenance
    capacity_factor: float = 0.95  # Technical availability (dispatchable)
    # Override base class marginal_cost - calculated dynamically, not stored
    marginal_cost: float = field(init=False, repr=False)

    def __post_init__(self):
        """Initialize - marginal_cost is calculated dynamically."""
        pass

    def __getattribute__(self, name: str):
        """Override to calculate marginal_cost dynamically."""
        if name == 'marginal_cost':
            # Calculate on-the-fly from current fuel and carbon prices
            fuel = object.__getattribute__(self, 'fuel_cost_per_mwh')
            carbon_price = object.__getattribute__(self, 'carbon_price_per_tonne')
            emissions = object.__getattribute__(self, 'emissions_factor')
            om = object.__getattribute__(self, 'variable_om_per_mwh')
            return fuel + (carbon_price * emissions) + om
        return object.__getattribute__(self, name)

    def available_power(self, hour: int = 0, day_of_year: int = 0) -> float:
        return self.capacity_mw * self.capacity_factor


@dataclass
class NuclearGenerator(Generator):
    """
    Nuclear power plant.

    UK nuclear capacity factor: ~70% (includes planned outages)
    Very low marginal cost but inflexible - typically runs as baseload.
    """
    marginal_cost: float = 10.0  # £/MWh - low marginal, high fixed costs
    capacity_factor: float = 0.70

    def available_power(self, hour: int = 0, day_of_year: int = 0) -> float:
        return self.capacity_mw * self.capacity_factor


@dataclass
class BiomassGenerator(Generator):
    """
    Biomass power plant (e.g., Drax).

    Dispatchable renewable but with fuel costs.
    """
    marginal_cost: float = 45.0  # £/MWh - includes biomass fuel
    capacity_factor: float = 0.65


@dataclass
class HydroGenerator(Generator):
    """
    Hydroelectric (conventional, not pumped storage).

    UK has limited hydro capacity, mostly in Scotland.
    """
    marginal_cost: float = 5.0  # £/MWh - very low
    capacity_factor: float = 0.35


@dataclass
class InterconnectorImport(Generator):
    """
    Interconnector imports from Europe.

    Price depends on continental markets - often sets price when UK demand is high.
    
    NOTE: This is a simplified model. Real interconnectors:
    - Can flow both ways (import/export) based on price differences
    - Have dynamic prices that reflect European market conditions
    - May have transmission losses and constraints
    - Currently modeled as imports only with fixed price
    """
    marginal_cost: float = 55.0  # £/MWh - varies with EU prices (simplified to fixed value)
    capacity_factor: float = 0.50  # Availability varies (represents average utilization)


# UK 2024 approximate installed capacity (GW)
UK_CURRENT_CAPACITY = {
    'solar': 15.5,
    'onshore_wind': 14.8,
    'offshore_wind': 14.7,
    'gas': 32.0,
    'nuclear': 6.5,
    'biomass': 3.5,
    'hydro': 1.9,
    'interconnectors': 8.4,
}


def create_uk_current_fleet() -> list[Generator]:
    """
    Create generator fleet representing current UK capacity mix.

    Returns list of generators that can be used in dispatch simulation.
    """
    return [
        SolarGenerator(name="UK Solar", capacity_mw=UK_CURRENT_CAPACITY['solar'] * 1000),
        OnshoreWindGenerator(name="UK Onshore Wind", capacity_mw=UK_CURRENT_CAPACITY['onshore_wind'] * 1000),
        OffshoreWindGenerator(name="UK Offshore Wind", capacity_mw=UK_CURRENT_CAPACITY['offshore_wind'] * 1000),
        NuclearGenerator(name="UK Nuclear", capacity_mw=UK_CURRENT_CAPACITY['nuclear'] * 1000),
        BiomassGenerator(name="UK Biomass", capacity_mw=UK_CURRENT_CAPACITY['biomass'] * 1000),
        HydroGenerator(name="UK Hydro", capacity_mw=UK_CURRENT_CAPACITY['hydro'] * 1000),
        GasGenerator(
            name="UK Gas CCGT", 
            capacity_mw=UK_CURRENT_CAPACITY['gas'] * 1000,
            fuel_cost_per_mwh=55.0,  # 2025 typical gas fuel cost
            carbon_price_per_tonne=60.0  # 2025 UK ETS price
        ),
        InterconnectorImport(name="Interconnectors", capacity_mw=UK_CURRENT_CAPACITY['interconnectors'] * 1000),
    ]


def create_scaled_fleet(re_penetration_target: float = 0.5,
                        total_capacity_gw: float = 100,
                        peak_demand_gw: float = 50.0) -> list[Generator]:
    """
    Create a fleet with specified renewable penetration.

    Args:
        re_penetration_target: Target RE share of capacity (0-1)
        total_capacity_gw: Total installed capacity in GW
        peak_demand_gw: Peak demand in GW (used to ensure sufficient dispatchable capacity)

    Returns:
        List of generators scaled to meet targets
    """
    re_capacity = total_capacity_gw * re_penetration_target * 1000  # MW

    # Calculate minimum dispatchable capacity needed
    # Must be able to meet peak demand even when renewables are at minimum output
    try:
        from .constants import MIN_RE_OUTPUT_FACTOR, CAPACITY_SAFETY_MARGIN
    except ImportError:
        from constants import MIN_RE_OUTPUT_FACTOR, CAPACITY_SAFETY_MARGIN
    
    min_re_output_factor = MIN_RE_OUTPUT_FACTOR  # Worst-case wind output
    min_re_available = re_capacity * min_re_output_factor / 1000  # GW
    
    # Dispatchable capacity must cover: peak_demand - min_re_available
    # Plus a safety margin
    required_dispatchable_gw = (peak_demand_gw - min_re_available) * CAPACITY_SAFETY_MARGIN
    
    # Also ensure minimum backup capacity for grid stability
    min_backup_gw = 40
    
    # Use the larger of: calculated requirement, minimum backup, or nominal non-RE capacity
    nominal_other_capacity = total_capacity_gw * (1 - re_penetration_target)
    other_capacity_gw = max(required_dispatchable_gw, min_backup_gw, nominal_other_capacity)
    
    # Cap it at reasonable maximum (don't exceed total capacity)
    other_capacity_gw = min(other_capacity_gw, total_capacity_gw * 0.5)  # Max 50% dispatchable
    
    other_capacity = other_capacity_gw * 1000  # Convert to MW

    # Split RE between solar (25%), onshore wind (30%), offshore wind (45%)
    # Offshore wind is more consistent and critical for high-RE grids
    solar_share = 0.25
    onshore_share = 0.30
    offshore_share = 0.45

    # Split non-RE between gas (60%), nuclear (25%), other (15%)
    gas_share = 0.60
    nuclear_share = 0.25
    other_share = 0.15

    return [
        SolarGenerator(name="Solar", capacity_mw=re_capacity * solar_share),
        OnshoreWindGenerator(name="Onshore Wind", capacity_mw=re_capacity * onshore_share),
        OffshoreWindGenerator(name="Offshore Wind", capacity_mw=re_capacity * offshore_share),
        NuclearGenerator(name="Nuclear", capacity_mw=other_capacity * nuclear_share),
        GasGenerator(
            name="Gas CCGT", 
            capacity_mw=other_capacity * gas_share,
            fuel_cost_per_mwh=55.0,  # 2025 typical
            carbon_price_per_tonne=60.0  # 2025 UK ETS
        ),
        BiomassGenerator(name="Biomass", capacity_mw=other_capacity * other_share * 0.6),
        InterconnectorImport(name="Interconnectors", capacity_mw=other_capacity * other_share * 0.4),
    ]
