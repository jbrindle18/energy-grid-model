# UK Energy Grid Model
# Simulates wholesale electricity price dynamics under varying renewable penetration

from .generators import (
    Generator, SolarGenerator, OnshoreWindGenerator, OffshoreWindGenerator,
    NuclearGenerator, BiomassGenerator, HydroGenerator, GasGenerator,
    InterconnectorImport, create_uk_current_fleet, create_scaled_fleet,
    UK_CURRENT_CAPACITY
)
from .demand import DemandProfile, create_uk_demand_profile, create_future_demand_profile
from .grid import Grid, DispatchResult, SimulationSummary, create_uk_grid, create_scenario_grid
from .pricing import (
    PriceDurationCurve, CannibalalisationMetrics, GeneratorRevenue,
    calculate_generator_revenues
)
from .cfd import (
    CfDContract, CfDPortfolio, CfDPaymentResult, LCCCSimulationResult,
    simulate_cfd_costs, create_cfd_portfolio_for_fleet,
    CURRENT_STRIKE_PRICES, UK_CFD_STRIKE_PRICES, PROJECT_COSTS,
    estimate_project_viability
)

__version__ = "0.1.0"
__all__ = [
    # Generators
    'Generator', 'SolarGenerator', 'OnshoreWindGenerator', 'OffshoreWindGenerator',
    'NuclearGenerator', 'BiomassGenerator', 'HydroGenerator', 'GasGenerator',
    'InterconnectorImport', 'create_uk_current_fleet', 'create_scaled_fleet',
    'UK_CURRENT_CAPACITY',
    # Demand
    'DemandProfile', 'create_uk_demand_profile', 'create_future_demand_profile',
    # Grid
    'Grid', 'DispatchResult', 'SimulationSummary', 'create_uk_grid', 'create_scenario_grid',
    # Pricing
    'PriceDurationCurve', 'CannibalalisationMetrics', 'GeneratorRevenue',
    'calculate_generator_revenues',
    # CfD
    'CfDContract', 'CfDPortfolio', 'CfDPaymentResult', 'LCCCSimulationResult',
    'simulate_cfd_costs', 'create_cfd_portfolio_for_fleet',
    'CURRENT_STRIKE_PRICES', 'UK_CFD_STRIKE_PRICES', 'PROJECT_COSTS',
    'estimate_project_viability',
]
