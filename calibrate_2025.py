"""
Calibration script to find optimal parameters for 2025 validation.
Tests different combinations of gas prices, carbon prices, demand, and capacity factors.
"""

import sys
sys.path.insert(0, '.')

from src.generators import (
    SolarGenerator, OnshoreWindGenerator, OffshoreWindGenerator,
    NuclearGenerator, BiomassGenerator, HydroGenerator,
    GasGenerator, InterconnectorImport
)
from src.grid import Grid, SimulationSummary
from src.demand import DemandProfile

# Target: £75/MWh wholesale price for 2025
TARGET_PRICE = 75.0

# Parameter ranges to test
GAS_PRICES = [45.0, 50.0, 55.0, 60.0]  # £/MWh
CARBON_PRICES = [50.0, 55.0, 60.0, 65.0]  # £/tonne
DEMAND_LEVELS = [0.85, 0.90, 0.95, 1.0]  # Multiplier of base demand
CAPACITY_FACTORS = {
    'solar': [0.09, 0.10, 0.11, 0.12],
    'onshore': [0.24, 0.25, 0.26, 0.27],
    'offshore': [0.35, 0.37, 0.40, 0.42]
}

# 2025 capacity (slight growth from 2024)
CAPACITY_2025 = {
    'solar': 16.0,
    'onshore_wind': 15.0,
    'offshore_wind': 16.0,
    'nuclear': 6.5,
    'gas': 32.0,
    'biomass': 3.5,
    'hydro': 1.9,
    'interconnectors': 8.4,
}


def create_fleet(gas_price, carbon_price, solar_cf, onshore_cf, offshore_cf):
    """Create fleet with specified parameters."""
    return [
        SolarGenerator(
            name="Solar",
            capacity_mw=CAPACITY_2025['solar'] * 1000,
            capacity_factor=solar_cf
        ),
        OnshoreWindGenerator(
            name="Onshore Wind",
            capacity_mw=CAPACITY_2025['onshore_wind'] * 1000,
            capacity_factor=onshore_cf
        ),
        OffshoreWindGenerator(
            name="Offshore Wind",
            capacity_mw=CAPACITY_2025['offshore_wind'] * 1000,
            capacity_factor=offshore_cf
        ),
        NuclearGenerator(name="Nuclear", capacity_mw=CAPACITY_2025['nuclear'] * 1000),
        BiomassGenerator(name="Biomass", capacity_mw=CAPACITY_2025['biomass'] * 1000),
        HydroGenerator(name="Hydro", capacity_mw=CAPACITY_2025['hydro'] * 1000),
        GasGenerator(
            name="Gas CCGT",
            capacity_mw=CAPACITY_2025['gas'] * 1000,
            fuel_cost_per_mwh=gas_price,
            carbon_price_per_tonne=carbon_price
        ),
        InterconnectorImport(name="Interconnectors", capacity_mw=CAPACITY_2025['interconnectors'] * 1000),
    ]


def test_combination(gas_price, carbon_price, demand_mult, solar_cf, onshore_cf, offshore_cf):
    """Test a specific parameter combination."""
    fleet = create_fleet(gas_price, carbon_price, solar_cf, onshore_cf, offshore_cf)
    
    # Create demand profile with multiplier
    demand = DemandProfile(
        base_demand_gw=35.0 * demand_mult,
        peak_demand_gw=50.0 * demand_mult,
        min_demand_gw=25.0 * demand_mult
    )
    
    grid = Grid(generators=fleet, demand_profile=demand)
    results = grid.simulate_year()
    summary = SimulationSummary.from_results(results)
    
    error = abs(summary.average_price - TARGET_PRICE)
    
    return {
        'price': summary.average_price,
        'error': error,
        're_share': summary.average_re_share,
        'params': {
            'gas': gas_price,
            'carbon': carbon_price,
            'demand_mult': demand_mult,
            'solar_cf': solar_cf,
            'onshore_cf': onshore_cf,
            'offshore_cf': offshore_cf
        }
    }


def run_calibration():
    """Run calibration to find best parameters."""
    print("=" * 80)
    print("2025 CALIBRATION: Finding Optimal Parameters")
    print("=" * 80)
    print(f"\nTarget: £{TARGET_PRICE}/MWh wholesale price")
    print("\nTesting parameter combinations...")
    print("(This may take a few minutes)\n")
    
    best_result = None
    best_error = float('inf')
    results = []
    
    # Test combinations (reduced grid for speed)
    test_count = 0
    total_tests = len(GAS_PRICES) * len(CARBON_PRICES) * len(DEMAND_LEVELS) * 4  # 4 CF combinations
    
    for gas_price in GAS_PRICES:
        for carbon_price in CARBON_PRICES:
            for demand_mult in DEMAND_LEVELS:
                # Test a few key CF combinations
                cf_combinations = [
                    (0.11, 0.27, 0.40),  # Default
                    (0.10, 0.26, 0.38),  # Slightly lower
                    (0.11, 0.26, 0.38),  # Mixed
                    (0.10, 0.25, 0.36),  # Lower
                ]
                
                for solar_cf, onshore_cf, offshore_cf in cf_combinations:
                    test_count += 1
                    if test_count % 10 == 0:
                        print(f"  Progress: {test_count}/{total_tests} tests...")
                    
                    result = test_combination(
                        gas_price, carbon_price, demand_mult,
                        solar_cf, onshore_cf, offshore_cf
                    )
                    results.append(result)
                    
                    if result['error'] < best_error:
                        best_error = result['error']
                        best_result = result
    
    # Sort by error
    results.sort(key=lambda x: x['error'])
    
    print(f"\nCompleted {test_count} tests")
    print("\n" + "=" * 80)
    print("TOP 10 PARAMETER COMBINATIONS")
    print("=" * 80)
    
    print(f"\n{'Rank':<6} {'Price':<10} {'Error':<10} {'Gas':<8} {'Carbon':<8} {'Demand':<8} {'Solar CF':<9} {'Onshore CF':<11} {'Offshore CF':<12} {'RE Share':<10}")
    print("-" * 100)
    
    for i, result in enumerate(results[:10], 1):
        p = result['params']
        print(f"{i:<6} "
              f"£{result['price']:>6.1f}  "
              f"£{result['error']:>6.2f}  "
              f"£{p['gas']:>5.0f}   "
              f"£{p['carbon']:>5.0f}   "
              f"{p['demand_mult']:>6.2f}   "
              f"{p['solar_cf']:>7.2f}   "
              f"{p['onshore_cf']:>9.2f}   "
              f"{p['offshore_cf']:>10.2f}   "
              f"{result['re_share']*100:>7.1f}%")
    
    print("\n" + "=" * 80)
    print("BEST PARAMETER SET")
    print("=" * 80)
    
    if best_result:
        p = best_result['params']
        print(f"\nWholesale Price: £{best_result['price']:.2f}/MWh")
        print(f"Error: £{best_result['error']:.2f}/MWh")
        print(f"RE Share: {best_result['re_share']*100:.1f}%")
        print(f"\nParameters:")
        print(f"  Gas Price: £{p['gas']:.0f}/MWh")
        print(f"  Carbon Price: £{p['carbon']:.0f}/tonne CO2")
        print(f"  Demand Multiplier: {p['demand_mult']:.2f}")
        print(f"  Solar Capacity Factor: {p['solar_cf']:.2f} ({p['solar_cf']*100:.1f}%)")
        print(f"  Onshore Wind CF: {p['onshore_cf']:.2f} ({p['onshore_cf']*100:.1f}%)")
        print(f"  Offshore Wind CF: {p['offshore_cf']:.2f} ({p['offshore_cf']*100:.1f}%)")
        
        # Calculate gas marginal cost
        gas_mc = p['gas'] + (p['carbon'] * 0.4) + 3.0
        print(f"\n  Gas Marginal Cost: £{gas_mc:.1f}/MWh")
        print(f"    (Fuel: £{p['gas']:.0f} + Carbon: £{p['carbon']*0.4:.1f} + O&M: £3.0)")
        
        # Check if these are realistic
        print(f"\nRealism Check:")
        print(f"  Gas price £{p['gas']:.0f}/MWh: {'[OK] Reasonable' if 45 <= p['gas'] <= 60 else '[?] Check actual 2025 data'}")
        print(f"  Carbon price £{p['carbon']:.0f}/tonne: {'[OK] Reasonable' if 50 <= p['carbon'] <= 65 else '[?] Check actual 2025 data'}")
        print(f"  Demand {p['demand_mult']:.2f}x: {'[OK] Reasonable' if 0.85 <= p['demand_mult'] <= 1.0 else '[?] Check actual 2025 data'}")
        print(f"  Capacity factors: {'[OK] Reasonable' if all(0.09 <= cf <= 0.42 for cf in [p['solar_cf'], p['onshore_cf'], p['offshore_cf']]) else '[?] Check actual 2025 data'}")
    
    return best_result


if __name__ == "__main__":
    best = run_calibration()
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("\n1. Update default gas price in generators.py if best result differs significantly")
    print("2. Update default carbon price if best result differs significantly")
    print("3. Consider updating capacity factors if they differ from defaults")
    print("4. Note: These are calibrated to match price, but may not reflect actual 2025 values")
    print("5. For validation purposes, document which parameters were used")

