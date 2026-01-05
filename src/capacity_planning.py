"""
Capacity planning utilities for energy grid model.

Provides functions to calculate required gas capacity and validate capacity mixes.
"""

from typing import Optional

try:
    from .constants import (
        UK_BASE_PEAK_DEMAND_GW, MIN_RE_OUTPUT_FACTOR, CAPACITY_SAFETY_MARGIN
    )
except ImportError:
    from constants import (
        UK_BASE_PEAK_DEMAND_GW, MIN_RE_OUTPUT_FACTOR, CAPACITY_SAFETY_MARGIN
    )


def calculate_required_gas_capacity(
    solar_capacity_gw: float,
    onshore_wind_capacity_gw: float,
    offshore_wind_capacity_gw: float,
    nuclear_capacity_gw: float,
    biomass_capacity_gw: float,
    hydro_capacity_gw: float,
    interconnector_capacity_gw: float,
    electrification_factor: float = 1.0,
    base_peak_demand_gw: float = UK_BASE_PEAK_DEMAND_GW
) -> float:
    """
    Calculate required gas capacity to meet peak demand.
    
    Gas capacity is automatically adjusted to fill the gap between:
    - Required dispatchable capacity (to meet peak demand)
    - Other dispatchable sources (nuclear, biomass, hydro, interconnectors)
    
    Args:
        solar_capacity_gw: Solar capacity in GW
        onshore_wind_capacity_gw: Onshore wind capacity in GW
        offshore_wind_capacity_gw: Offshore wind capacity in GW
        nuclear_capacity_gw: Nuclear capacity in GW
        biomass_capacity_gw: Biomass capacity in GW
        hydro_capacity_gw: Hydro capacity in GW
        interconnector_capacity_gw: Interconnector capacity in GW
        electrification_factor: Demand growth multiplier
        base_peak_demand_gw: Base peak demand in GW
        
    Returns:
        Required gas capacity in GW (non-negative)
    """
    # Calculate peak demand from electrification factor
    peak_demand_gw = base_peak_demand_gw * electrification_factor
    
    # Calculate total renewable capacity
    re_capacity_total = solar_capacity_gw + onshore_wind_capacity_gw + offshore_wind_capacity_gw
    
    # Assume worst case: solar = 0, wind at minimum output
    min_re_available = re_capacity_total * MIN_RE_OUTPUT_FACTOR
    
    # Required dispatchable capacity = peak_demand - min_re_available + safety margin
    required_dispatchable = (peak_demand_gw - min_re_available) * CAPACITY_SAFETY_MARGIN
    
    # Other dispatchable sources
    other_dispatchable = (
        nuclear_capacity_gw + biomass_capacity_gw + 
        hydro_capacity_gw + interconnector_capacity_gw
    )
    
    # Gas capacity fills the gap
    gas_capacity = max(0.0, required_dispatchable - other_dispatchable)
    
    return gas_capacity


def calculate_total_capacity(
    solar_capacity_gw: float,
    onshore_wind_capacity_gw: float,
    offshore_wind_capacity_gw: float,
    nuclear_capacity_gw: float,
    biomass_capacity_gw: float,
    hydro_capacity_gw: float,
    interconnector_capacity_gw: float,
    gas_capacity_gw: float
) -> float:
    """
    Calculate total installed capacity.
    
    Args:
        All capacity values in GW
        
    Returns:
        Total capacity in GW
    """
    return (
        solar_capacity_gw + onshore_wind_capacity_gw + offshore_wind_capacity_gw +
        nuclear_capacity_gw + biomass_capacity_gw + hydro_capacity_gw +
        interconnector_capacity_gw + gas_capacity_gw
    )

