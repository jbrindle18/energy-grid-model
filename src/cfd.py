"""
Contracts for Difference (CfD) Economics Module

Models the UK's CfD mechanism for supporting renewable energy:
- Strike prices: Guaranteed price to generators
- Top-up payments: LCCC pays when wholesale < strike
- Clawback: Generator pays when wholesale > strike
- Consumer levy: CfD costs passed to bills

Key insight from dissertation:
As RE penetration increases, wholesale prices fall, but CfD costs rise
because generators increasingly need top-up payments to reach strike price.
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np

try:
    from .grid import DispatchResult
except ImportError:
    from grid import DispatchResult


# Historical UK CfD strike prices (£/MWh, 2012 prices, approximate)
# These are indexed to CPI, so real values are higher
UK_CFD_STRIKE_PRICES = {
    'AR1_2015': {'offshore_wind': 117.14, 'onshore_wind': 82.50, 'solar': 79.23},
    'AR2_2017': {'offshore_wind': 57.50, 'onshore_wind': None, 'solar': None},  # Onshore/solar excluded
    'AR3_2019': {'offshore_wind': 39.65, 'onshore_wind': None, 'solar': None},
    'AR4_2022': {'offshore_wind': 37.35, 'onshore_wind': 42.47, 'solar': 45.99},
    'AR5_2023': {'offshore_wind': None, 'onshore_wind': 52.29, 'solar': 47.00},  # No offshore awarded!
    'AR6_2024': {'offshore_wind': 58.87, 'onshore_wind': 50.90, 'solar': 47.00},
}

# Current typical strike prices for new projects (AR6 2024, 2025 money)
# Based on Allocation Round 6 prices and 2025 market data
CURRENT_STRIKE_PRICES = {
    'solar': 69.0,  # AR6: £47/MWh (2012 prices) + inflation ≈ £69/MWh (2025)
    'onshore_wind': 58.0,  # AR6: £50.90/MWh (2012 prices) + inflation ≈ £58/MWh (2025)
    'offshore_wind': 71.0,  # AR6: £58.87/MWh (2012 prices) + inflation ≈ £71/MWh (2025)
}


@dataclass
class CfDContract:
    """
    A Contract for Difference for a specific generator.

    Attributes:
        generator_name: Name matching the generator in the fleet
        strike_price: Guaranteed price in £/MWh
        capacity_mw: Contracted capacity
        contract_length_years: Typically 15 years
        start_year: When contract begins (for modeling purposes)
    """
    generator_name: str
    strike_price: float  # £/MWh
    capacity_mw: float
    contract_length_years: int = 15
    start_year: int = 2025

    def calculate_payment(self, wholesale_price: float, generation_mwh: float) -> float:
        """
        Calculate CfD payment for a single period.

        Args:
            wholesale_price: Market price in £/MWh
            generation_mwh: Actual generation in MWh

        Returns:
            Payment amount in £
            Positive = LCCC pays generator (subsidy/top-up)
            Negative = Generator pays LCCC (clawback)
        """
        difference = self.strike_price - wholesale_price
        return difference * generation_mwh


@dataclass
class CfDPortfolio:
    """
    Collection of all CfD contracts - represents LCCC's portfolio.
    """
    contracts: list[CfDContract] = field(default_factory=list)

    def add_contract(self, contract: CfDContract):
        self.contracts.append(contract)

    def get_contract_for_generator(self, generator_name: str) -> Optional[CfDContract]:
        """Find contract matching a generator name."""
        for contract in self.contracts:
            if contract.generator_name in generator_name or generator_name in contract.generator_name:
                return contract
        return None

    @property
    def total_contracted_capacity_gw(self) -> float:
        return sum(c.capacity_mw for c in self.contracts) / 1000


@dataclass
class CfDPaymentResult:
    """Result of CfD payments for a single hour."""
    hour: int
    day_of_year: int
    wholesale_price: float
    total_generation_mwh: float
    total_cfd_payment: float  # Positive = subsidy, negative = clawback
    payments_by_generator: dict  # generator_name -> payment

    @property
    def is_subsidy(self) -> bool:
        return self.total_cfd_payment > 0

    @property
    def payment_per_mwh(self) -> float:
        """Average CfD payment per MWh generated."""
        if self.total_generation_mwh > 0:
            return self.total_cfd_payment / self.total_generation_mwh
        return 0


@dataclass
class LCCCSimulationResult:
    """
    Aggregate LCCC costs over a simulation period.

    This is the key output showing the "subsidy spiral":
    - At low RE penetration: Clawback exceeds top-up (net return to consumers)
    - At high RE penetration: Top-up dominates (net cost to consumers)
    """
    period_hours: int
    total_demand_mwh: float
    total_re_generation_mwh: float

    # CfD Payments
    total_topup_payments: float  # LCCC -> Generators (subsidy)
    total_clawback_payments: float  # Generators -> LCCC (return)
    net_cfd_cost: float  # Total cost to consumers

    # Price metrics
    average_wholesale_price: float
    average_re_capture_price: float

    # Per-generator breakdown
    payments_by_source: dict  # generator_type -> net payment
    generation_by_source: dict  # generator_type -> MWh

    @property
    def subsidy_per_mwh_consumed(self) -> float:
        """Consumer levy per MWh of electricity consumed."""
        if self.total_demand_mwh > 0:
            return self.net_cfd_cost / self.total_demand_mwh
        return 0

    @property
    def annual_household_cost(self) -> float:
        """
        Estimated annual cost per household from CfD levy.
        Average UK household uses ~2,700 kWh/year = 2.7 MWh/year
        """
        household_consumption_mwh = 2.7
        # Scale from simulation period to annual
        hours_per_year = 8760
        annual_levy_per_mwh = self.subsidy_per_mwh_consumed * (hours_per_year / self.period_hours)
        return annual_levy_per_mwh * household_consumption_mwh

    @property
    def re_share(self) -> float:
        """RE share of total generation."""
        if self.total_demand_mwh > 0:
            return self.total_re_generation_mwh / self.total_demand_mwh
        return 0


def simulate_cfd_costs(
    dispatch_results: list[DispatchResult],
    cfd_portfolio: CfDPortfolio,
) -> LCCCSimulationResult:
    """
    Calculate CfD costs for a simulation run.

    Args:
        dispatch_results: Results from grid.simulate_day() or simulate_year()
        cfd_portfolio: Portfolio of CfD contracts

    Returns:
        LCCCSimulationResult with aggregate costs
    """
    total_demand = 0
    total_re_generation = 0
    total_topup = 0
    total_clawback = 0

    payments_by_source = {}
    generation_by_source = {}

    wholesale_prices = []
    re_weighted_prices = []
    re_generation_weights = []

    for result in dispatch_results:
        total_demand += result.demand_mw  # MW for 1 hour = MWh
        wholesale_prices.append(result.wholesale_price)

        for gen, mw in result.dispatched_generators:
            mwh = mw  # 1 hour period

            # Track RE generation
            if gen.marginal_cost < 5:  # RE sources
                total_re_generation += mwh
                re_weighted_prices.append(result.wholesale_price * mwh)
                re_generation_weights.append(mwh)

            # Track generation by source
            gen_type = gen.name.split()[0]  # First word of name
            generation_by_source[gen_type] = generation_by_source.get(gen_type, 0) + mwh

            # Calculate CfD payment if contract exists
            contract = cfd_portfolio.get_contract_for_generator(gen.name)
            if contract:
                payment = contract.calculate_payment(result.wholesale_price, mwh)

                if payment > 0:
                    total_topup += payment
                else:
                    total_clawback += abs(payment)

                # Track by source
                payments_by_source[gen_type] = payments_by_source.get(gen_type, 0) + payment

    # Calculate averages
    avg_wholesale = np.mean(wholesale_prices) if wholesale_prices else 0

    if sum(re_generation_weights) > 0:
        avg_re_capture = sum(re_weighted_prices) / sum(re_generation_weights)
    else:
        avg_re_capture = avg_wholesale

    return LCCCSimulationResult(
        period_hours=len(dispatch_results),
        total_demand_mwh=total_demand,
        total_re_generation_mwh=total_re_generation,
        total_topup_payments=total_topup,
        total_clawback_payments=total_clawback,
        net_cfd_cost=total_topup - total_clawback,
        average_wholesale_price=avg_wholesale,
        average_re_capture_price=avg_re_capture,
        payments_by_source=payments_by_source,
        generation_by_source=generation_by_source,
    )


def create_cfd_portfolio_for_fleet(
    generators: list,
    coverage: float = 1.0,
    strike_prices: Optional[dict] = None,
) -> CfDPortfolio:
    """
    Create a CfD portfolio covering RE generators in a fleet.

    Args:
        generators: List of Generator objects
        coverage: Fraction of RE capacity under CfD (0-1)
        strike_prices: Dict of {generator_type: strike_price}, uses defaults if None

    Returns:
        CfDPortfolio with contracts for RE generators
    """
    if strike_prices is None:
        strike_prices = CURRENT_STRIKE_PRICES

    portfolio = CfDPortfolio()

    for gen in generators:
        # Only create CfDs for RE sources (marginal cost < £5)
        if gen.marginal_cost >= 5:
            continue

        # Determine strike price based on generator type
        gen_lower = gen.name.lower()
        if 'solar' in gen_lower:
            strike = strike_prices.get('solar', 50.0)
        elif 'offshore' in gen_lower:
            strike = strike_prices.get('offshore_wind', 60.0)
        elif 'wind' in gen_lower:
            strike = strike_prices.get('onshore_wind', 55.0)
        else:
            strike = 50.0  # Default

        contract = CfDContract(
            generator_name=gen.name,
            strike_price=strike,
            capacity_mw=gen.capacity_mw * coverage,
        )
        portfolio.add_contract(contract)

    return portfolio


def calculate_required_strike_price(
    target_revenue_per_mwh: float,
    average_wholesale_price: float,
    capture_rate: float,
) -> float:
    """
    Calculate the strike price needed to achieve a target revenue.

    This shows how strike prices need to RISE as wholesale prices FALL,
    because generators capture an even smaller share of falling prices.

    Args:
        target_revenue_per_mwh: What the generator needs to earn (£/MWh)
        average_wholesale_price: Expected average wholesale price
        capture_rate: Expected RE capture rate (< 1.0 due to cannibalisation)

    Returns:
        Required strike price in £/MWh
    """
    # Without CfD, generator earns: wholesale * capture_rate
    # With CfD at strike S, generator earns: S (guaranteed)
    # To earn target_revenue, need S = target_revenue

    # But the actual calculation depends on how CfDs work:
    # CfD payment = (strike - wholesale) * generation
    # Total revenue = wholesale * generation + CfD payment
    #               = wholesale * generation + (strike - wholesale) * generation
    #               = strike * generation

    # So the strike price IS the required revenue per MWh
    return target_revenue_per_mwh


def estimate_project_viability(
    capex_per_mw: float,  # £ million per MW
    capacity_factor: float,
    lifetime_years: int,
    target_irr: float,  # e.g., 0.08 for 8%
    opex_per_mwh: float = 5.0,  # Operating costs
) -> float:
    """
    Estimate the strike price needed to make a project financially viable.

    This is a simplified LCOE-style calculation.

    Args:
        capex_per_mw: Capital cost in £ million per MW
        capacity_factor: Expected capacity factor (0-1)
        lifetime_years: Project lifetime
        target_irr: Required internal rate of return
        opex_per_mwh: Operating cost per MWh

    Returns:
        Required strike price in £/MWh
    """
    # Annual generation per MW
    hours_per_year = 8760
    annual_mwh_per_mw = hours_per_year * capacity_factor

    # Simple annuity calculation for required annual revenue
    # Annuity factor = IRR / (1 - (1 + IRR)^-n)
    annuity_factor = target_irr / (1 - (1 + target_irr) ** -lifetime_years)

    # Required annual revenue per MW to cover capex
    annual_capex_recovery = capex_per_mw * 1_000_000 * annuity_factor  # £/year per MW

    # Required revenue per MWh
    required_per_mwh = (annual_capex_recovery / annual_mwh_per_mw) + opex_per_mwh

    return required_per_mwh


# Typical project costs (2024 estimates)
PROJECT_COSTS = {
    'solar': {
        'capex_per_mw': 0.5,  # £0.5m per MW
        'capacity_factor': 0.11,
        'lifetime': 30,
    },
    'onshore_wind': {
        'capex_per_mw': 1.2,  # £1.2m per MW
        'capacity_factor': 0.27,
        'lifetime': 25,
    },
    'offshore_wind': {
        'capex_per_mw': 2.5,  # £2.5m per MW
        'capacity_factor': 0.40,
        'lifetime': 25,
    },
}


def print_project_economics():
    """Print required strike prices for different project types."""
    print("Required Strike Prices for Project Viability (8% IRR)")
    print("=" * 60)

    for project_type, params in PROJECT_COSTS.items():
        required = estimate_project_viability(
            capex_per_mw=params['capex_per_mw'],
            capacity_factor=params['capacity_factor'],
            lifetime_years=params['lifetime'],
            target_irr=0.08,
        )
        print(f"{project_type:<20} £{required:.1f}/MWh")


if __name__ == "__main__":
    print_project_economics()
