"""
Constants used throughout the energy grid model.

Centralized constants to avoid magic numbers and improve maintainability.
"""

# Renewable energy threshold for classification
# Generators with marginal cost below this are considered renewable
RE_MARGINAL_COST_THRESHOLD = 5.0  # £/MWh

# Emergency pricing when demand cannot be met
EMERGENCY_PRICE_CAP = 1000.0  # £/MWh

# Gas generator constants
GAS_EMISSIONS_FACTOR = 0.4  # tonnes CO₂ per MWh for gas CCGT
GAS_VARIABLE_OM = 3.0  # £/MWh - variable operations & maintenance

# UK demand constants
UK_BASE_PEAK_DEMAND_GW = 50.0  # UK typical peak demand in GW
UK_BASE_AVERAGE_DEMAND_GW = 35.0  # UK average demand in GW
UK_BASE_MIN_DEMAND_GW = 25.0  # UK minimum demand in GW

# Capacity factor defaults
UK_SOLAR_CAPACITY_FACTOR = 0.11  # UK average solar capacity factor
UK_ONSHORE_WIND_CAPACITY_FACTOR = 0.27  # UK average onshore wind capacity factor
UK_OFFSHORE_WIND_CAPACITY_FACTOR = 0.40  # UK average offshore wind capacity factor

# Worst-case renewable output factor for capacity planning
MIN_RE_OUTPUT_FACTOR = 0.08  # Worst-case wind output (8% capacity factor)
CAPACITY_SAFETY_MARGIN = 1.1  # 10% safety margin for dispatchable capacity

