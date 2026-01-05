"""
Validation functions for energy grid model inputs.

Provides validation to ensure simulation parameters are reasonable and safe.
"""

from typing import Dict, Optional, Tuple


def validate_capacities(capacities: Dict[str, float]) -> Tuple[bool, Optional[str]]:
    """
    Validate that capacity values are reasonable.
    
    Args:
        capacities: Dictionary mapping generator type to capacity in GW
        
    Returns:
        Tuple of (is_valid, error_message)
        If is_valid is True, error_message is None
    """
    # Check all capacities are non-negative
    for gen_type, capacity in capacities.items():
        if capacity < 0:
            return False, f"Capacity for {gen_type} cannot be negative: {capacity}"
    
    # Check total capacity is positive
    total = sum(capacities.values())
    if total <= 0:
        return False, "Total capacity must be greater than zero"
    
    # Check for unreasonably large values (sanity check)
    MAX_REASONABLE_CAPACITY = 500.0  # GW
    for gen_type, capacity in capacities.items():
        if capacity > MAX_REASONABLE_CAPACITY:
            return False, f"Capacity for {gen_type} seems unreasonably large: {capacity} GW"
    
    return True, None


def validate_demand_parameters(
    peak_demand_gw: float,
    total_capacity_gw: float,
    re_capacity_gw: float
) -> Tuple[bool, Optional[str]]:
    """
    Validate that demand can be met with available capacity.
    
    Args:
        peak_demand_gw: Peak demand in GW
        total_capacity_gw: Total installed capacity in GW
        re_capacity_gw: Total renewable capacity in GW
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if peak_demand_gw <= 0:
        return False, "Peak demand must be positive"
    
    if total_capacity_gw <= 0:
        return False, "Total capacity must be positive"
    
    # Check that total capacity exceeds peak demand (with some margin)
    if total_capacity_gw < peak_demand_gw * 0.8:
        return False, (
            f"Total capacity ({total_capacity_gw:.1f} GW) is insufficient "
            f"for peak demand ({peak_demand_gw:.1f} GW)"
        )
    
    # Check RE penetration is reasonable (0-100%)
    re_penetration = re_capacity_gw / total_capacity_gw if total_capacity_gw > 0 else 0
    if re_penetration > 1.0:
        return False, f"Renewable penetration ({re_penetration*100:.1f}%) exceeds 100%"
    
    return True, None


def validate_gas_parameters(
    fuel_cost: float,
    carbon_price: float
) -> Tuple[bool, Optional[str]]:
    """
    Validate gas price parameters.
    
    Args:
        fuel_cost: Gas fuel cost in £/MWh
        carbon_price: Carbon price in £/tonne CO₂
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if fuel_cost < 0:
        return False, "Gas fuel cost cannot be negative"
    
    if carbon_price < 0:
        return False, "Carbon price cannot be negative"
    
    # Reasonable ranges (can be adjusted)
    if fuel_cost > 200:
        return False, f"Gas fuel cost seems unreasonably high: £{fuel_cost}/MWh"
    
    if carbon_price > 200:
        return False, f"Carbon price seems unreasonably high: £{carbon_price}/tonne"
    
    return True, None


def validate_cfd_parameters(
    strike_prices: Dict[str, float],
    coverage: float
) -> Tuple[bool, Optional[str]]:
    """
    Validate CfD parameters.
    
    Args:
        strike_prices: Dictionary mapping generator type to strike price
        coverage: Coverage fraction (0-1)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if coverage < 0 or coverage > 1:
        return False, f"CfD coverage must be between 0 and 1, got {coverage}"
    
    for gen_type, strike in strike_prices.items():
        if strike < 0:
            return False, f"Strike price for {gen_type} cannot be negative: £{strike}/MWh"
        
        if strike > 200:
            return False, f"Strike price for {gen_type} seems unreasonably high: £{strike}/MWh"
    
    return True, None

