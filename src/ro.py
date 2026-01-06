"""
Renewables Obligation (RO) Economics Module

Models the UK's Renewables Obligation scheme for supporting renewable energy:
- ROC certificates: Generators receive ROCs for each MWh generated
- ROC value: Varies based on buy-out price and recycling payments
- Fixed payment: Unlike CfDs, RO is always a top-up (no clawback)
- Consumer levy: RO costs passed to bills via supplier obligations

Key differences from CfD:
- RO closed to new applicants in 2017, but existing generators continue until 2037
- RO is always a subsidy (no clawback when wholesale > strike)
- ROC value typically £40-50/MWh (varies with buy-out price)
- RO supports older renewable capacity (pre-2017)
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np

try:
    from .grid import DispatchResult
except ImportError:
    from grid import DispatchResult


# Typical ROC values (£/MWh) - varies by year and technology
# Based on Ofgem data: ROC value = buy-out price + recycling payments
# Historical average: ~£40-50/MWh, can vary significantly
DEFAULT_ROC_VALUE = 73.71  # £/MWh - 2024-2025: Nominal ROC value £73.71/ROC = £73.71/MWh (for 1 ROC/MWh technologies)

# Technology-specific ROC multipliers (some technologies get multiple ROCs per MWh)
# Most technologies: 1 ROC per MWh
# Some older/less mature technologies: 2 ROCs per MWh
ROC_MULTIPLIERS = {
    'solar': 1.0,  # 1 ROC per MWh
    'onshore_wind': 1.0,
    'offshore_wind': 1.0,
    'biomass': 1.0,
    'hydro': 1.0,
}


@dataclass
class ROContract:
    """
    A Renewables Obligation contract for a specific generator.

    Attributes:
        generator_name: Name matching the generator in the fleet
        roc_value_per_mwh: Value of ROC support in £/MWh
        capacity_mw: Contracted capacity
        roc_multiplier: Number of ROCs per MWh (typically 1.0)
        end_year: When RO support ends (typically 2037 for pre-2017 projects)
    """
    generator_name: str
    roc_value_per_mwh: float = DEFAULT_ROC_VALUE  # £/MWh
    capacity_mw: float = 0.0
    roc_multiplier: float = 1.0  # ROCs per MWh
    end_year: int = 2037  # RO closed in 2017, support continues until 2037

    def calculate_payment(self, wholesale_price: float, generation_mwh: float, year: int = 2025) -> float:
        """
        Calculate RO payment for a single period.

        Unlike CfDs, RO is always a top-up payment (no clawback).
        Payment = ROC value × ROC multiplier × generation

        Args:
            wholesale_price: Market price in £/MWh (not used for RO, but kept for consistency)
            generation_mwh: Actual generation in MWh
            year: Current year (to check if RO support has ended)

        Returns:
            Payment amount in £ (always positive - RO is always a subsidy)
        """
        if year >= self.end_year:
            return 0.0  # RO support has ended
        
        # RO payment = ROC value × multiplier × generation
        # This is always a top-up (no clawback)
        return self.roc_value_per_mwh * self.roc_multiplier * generation_mwh


@dataclass
class ROPortfolio:
    """
    Collection of all RO contracts - represents RO-supported generation.
    
    RO closed to new applicants in 2017, but existing generators
    continue to receive support until 2037.
    """
    contracts: list[ROContract] = field(default_factory=list)

    def add_contract(self, contract: ROContract):
        """Add an RO contract to the portfolio."""
        self.contracts.append(contract)

    def get_contract_for_generator(self, generator_name: str) -> Optional[ROContract]:
        """Find RO contract matching a generator name."""
        for contract in self.contracts:
            if contract.generator_name in generator_name or generator_name in contract.generator_name:
                return contract
        return None

    @property
    def total_contracted_capacity_gw(self) -> float:
        """Total RO-supported capacity in GW."""
        return sum(c.capacity_mw for c in self.contracts) / 1000


@dataclass
class ROSimulationResult:
    """
    Aggregate RO costs over a simulation period.
    
    RO is always a subsidy (no clawback), so all payments are top-ups.
    """
    period_hours: int
    total_demand_mwh: float
    total_ro_generation_mwh: float
    
    # RO Payments (always positive - always subsidy)
    total_ro_payments: float  # Total RO subsidy payments
    
    # Price metrics
    average_wholesale_price: float
    average_ro_capture_price: float  # Wholesale + RO payment
    
    # Per-generator breakdown
    payments_by_source: dict  # generator_type -> payment
    generation_by_source: dict  # generator_type -> MWh
    
    @property
    def subsidy_per_mwh_consumed(self) -> float:
        """Consumer levy per MWh of electricity consumed."""
        if self.total_demand_mwh > 0:
            return self.total_ro_payments / self.total_demand_mwh
        return 0
    
    @property
    def annual_household_cost(self) -> float:
        """
        Estimated annual cost per household from RO levy.
        Average UK household uses ~2,700 kWh/year = 2.7 MWh/year
        """
        household_consumption_mwh = 2.7
        hours_per_year = 8760
        annual_levy_per_mwh = self.subsidy_per_mwh_consumed * (hours_per_year / self.period_hours)
        return annual_levy_per_mwh * household_consumption_mwh
    
    @property
    def ro_share(self) -> float:
        """Share of demand met by RO-supported generation."""
        if self.total_demand_mwh > 0:
            return self.total_ro_generation_mwh / self.total_demand_mwh
        return 0


def simulate_ro_costs(
    dispatch_results: list[DispatchResult],
    ro_portfolio: ROPortfolio,
    year: int = 2025
) -> ROSimulationResult:
    """
    Calculate RO costs for a simulation run.

    Args:
        dispatch_results: Results from grid.simulate_day() or simulate_year()
        ro_portfolio: Portfolio of RO contracts
        year: Current year (to check if RO support has ended)

    Returns:
        ROSimulationResult with aggregate costs
    """
    total_demand = 0
    total_ro_generation = 0
    total_ro_payments = 0
    
    payments_by_source = {}
    generation_by_source = {}
    
    wholesale_prices = []
    ro_weighted_prices = []
    ro_generation_weights = []
    
    for result in dispatch_results:
        total_demand += result.demand_mw  # MW for 1 hour = MWh
        wholesale_prices.append(result.wholesale_price)
        
        for gen, mw in result.dispatched_generators:
            mwh = mw  # 1 hour period
            
            # Track generation by source
            gen_type = gen.name.split()[0]  # First word of name
            generation_by_source[gen_type] = generation_by_source.get(gen_type, 0) + mwh
            
            # Calculate RO payment if contract exists
            contract = ro_portfolio.get_contract_for_generator(gen.name)
            if contract:
                # RO is always a subsidy (no clawback)
                payment = contract.calculate_payment(result.wholesale_price, mwh, year)
                total_ro_payments += payment
                total_ro_generation += mwh
                
                ro_weighted_prices.append((result.wholesale_price + payment / mwh) * mwh if mwh > 0 else 0)
                ro_generation_weights.append(mwh)
                
                # Track by source
                payments_by_source[gen_type] = payments_by_source.get(gen_type, 0) + payment
    
    # Calculate averages
    avg_wholesale = np.mean(wholesale_prices) if wholesale_prices else 0
    
    if sum(ro_generation_weights) > 0:
        avg_ro_capture = sum(ro_weighted_prices) / sum(ro_generation_weights)
    else:
        avg_ro_capture = avg_wholesale
    
    return ROSimulationResult(
        period_hours=len(dispatch_results),
        total_demand_mwh=total_demand,
        total_ro_generation_mwh=total_ro_generation,
        total_ro_payments=total_ro_payments,
        average_wholesale_price=avg_wholesale,
        average_ro_capture_price=avg_ro_capture,
        payments_by_source=payments_by_source,
        generation_by_source=generation_by_source,
    )


def create_ro_portfolio_for_fleet(
    generators: list,
    coverage: float = 1.0,
    roc_value: float = DEFAULT_ROC_VALUE,
) -> ROPortfolio:
    """
    Create an RO portfolio covering RE generators in a fleet.

    Args:
        generators: List of Generator objects
        coverage: Fraction of RE capacity under RO (0-1) - applies uniformly to all RE
        roc_value: ROC value in £/MWh

    Returns:
        ROPortfolio with contracts for RE generators
    """
    portfolio = ROPortfolio()
    
    for gen in generators:
        # Only create RO contracts for RE sources (marginal cost < £5)
        if gen.marginal_cost >= 5:
            continue
        
        # Determine ROC multiplier based on generator type
        gen_lower = gen.name.lower()
        if 'solar' in gen_lower:
            multiplier = ROC_MULTIPLIERS.get('solar', 1.0)
        elif 'offshore' in gen_lower:
            multiplier = ROC_MULTIPLIERS.get('offshore_wind', 1.0)
        elif 'wind' in gen_lower:
            multiplier = ROC_MULTIPLIERS.get('onshore_wind', 1.0)
        else:
            multiplier = 1.0  # Default
        
        contract = ROContract(
            generator_name=gen.name,
            roc_value_per_mwh=roc_value,
            capacity_mw=gen.capacity_mw * coverage,
            roc_multiplier=multiplier,
        )
        portfolio.add_contract(contract)
    
    return portfolio


@dataclass
class ROPortfolioState:
    """
    The state of the RO portfolio at a specific year.
    
    RO closed to new applicants in 2017, but existing generators
    continue to receive support until 2037.
    """
    year: int
    
    # Coverage percentages (0-1) - what fraction of each technology is covered by RO
    solar_coverage: float = 0.0
    onshore_wind_coverage: float = 0.0
    offshore_wind_coverage: float = 0.0
    
    # ROC value (£/MWh)
    roc_value: float = DEFAULT_ROC_VALUE
    
    def estimated_re_coverage(self, solar_capacity_gw: float, onshore_wind_capacity_gw: float,
                             offshore_wind_capacity_gw: float) -> float:
        """
        Estimate what fraction of RE generation is covered by RO.
        
        Args:
            solar_capacity_gw: User's solar capacity setting
            onshore_wind_capacity_gw: User's onshore wind capacity setting
            offshore_wind_capacity_gw: User's offshore wind capacity setting
            
        Returns:
            Fraction of RE generation covered by RO (0-1)
        """
        total_re_capacity_gw = solar_capacity_gw + onshore_wind_capacity_gw + offshore_wind_capacity_gw
        if total_re_capacity_gw <= 0:
            return 0.0
        
        # Estimate total RE generation using capacity factors
        total_re_gen_twh = (
            solar_capacity_gw * 0.11 * 8.76 +
            onshore_wind_capacity_gw * 0.27 * 8.76 +
            offshore_wind_capacity_gw * 0.40 * 8.76
        )
        
        # RO RE generation (using coverage percentages)
        ro_re_gen_twh = (
            solar_capacity_gw * self.solar_coverage * 0.11 * 8.76 +
            onshore_wind_capacity_gw * self.onshore_wind_coverage * 0.27 * 8.76 +
            offshore_wind_capacity_gw * self.offshore_wind_coverage * 0.40 * 8.76
        )
        
        if total_re_gen_twh <= 0:
            return 0.0
        
        return min(ro_re_gen_twh / total_re_gen_twh, 1.0)
    
    def get_ro_capacity_gw(self, solar_capacity_gw: float, onshore_wind_capacity_gw: float,
                          offshore_wind_capacity_gw: float) -> dict:
        """
        Calculate actual RO capacity in GW based on user's capacity settings.
        
        Args:
            solar_capacity_gw: User's solar capacity setting
            onshore_wind_capacity_gw: User's onshore wind capacity setting
            offshore_wind_capacity_gw: User's offshore wind capacity setting
            
        Returns:
            Dict with 'solar_gw', 'onshore_wind_gw', 'offshore_wind_gw', 'total_gw'
        """
        return {
            'solar_gw': solar_capacity_gw * self.solar_coverage,
            'onshore_wind_gw': onshore_wind_capacity_gw * self.onshore_wind_coverage,
            'offshore_wind_gw': offshore_wind_capacity_gw * self.offshore_wind_coverage,
            'total_gw': (
                solar_capacity_gw * self.solar_coverage +
                onshore_wind_capacity_gw * self.onshore_wind_coverage +
                offshore_wind_capacity_gw * self.offshore_wind_coverage
            )
        }


def create_ro_portfolio_from_state(
    generators: list,
    ro_state: ROPortfolioState,
    roc_value: Optional[float] = None,
) -> ROPortfolio:
    """
    Create an RO portfolio using coverage percentages from an ROPortfolioState.
    
    This allows per-technology coverage (e.g., 30% solar, 40% onshore wind)
    that adapts to the user's RE capacity settings.

    Args:
        generators: List of Generator objects
        ro_state: ROPortfolioState with coverage percentages
        roc_value: ROC value in £/MWh (uses ro_state.avg_roc_value if None)

    Returns:
        ROPortfolio with contracts for RE generators
    """
    if roc_value is None:
        roc_value = ro_state.avg_roc_value
    
    portfolio = ROPortfolio()
    
    for gen in generators:
        gen_lower = gen.name.lower()
        
        # Determine coverage and multiplier based on generator type
        if 'solar' in gen_lower:
            coverage = ro_state.solar_coverage
            multiplier = ROC_MULTIPLIERS.get('solar', 1.0)
        elif 'offshore' in gen_lower:
            coverage = ro_state.offshore_wind_coverage
            multiplier = ROC_MULTIPLIERS.get('offshore_wind', 1.0)
        elif 'wind' in gen_lower:
            coverage = ro_state.onshore_wind_coverage
            multiplier = ROC_MULTIPLIERS.get('onshore_wind', 1.0)
        else:
            coverage = 0.0  # Other technologies not typically under RO
            multiplier = 1.0
        
        if coverage > 0:
            contract = ROContract(
                generator_name=gen.name,
                roc_value_per_mwh=roc_value,
                capacity_mw=gen.capacity_mw * coverage,
                roc_multiplier=multiplier,
            )
            portfolio.add_contract(contract)
    
    return portfolio


@dataclass
class CombinedSupportResult:
    """
    Combined result from both CfD and RO support schemes.
    
    This provides a unified view of all renewable energy subsidies.
    """
    period_hours: int
    total_demand_mwh: float
    total_re_generation_mwh: float
    
    # CfD payments
    total_cfd_topup: float
    total_cfd_clawback: float
    net_cfd_cost: float
    
    # RO payments (always subsidy)
    total_ro_payments: float
    
    # Combined
    total_subsidy_cost: float  # CfD top-up + RO payments
    total_clawback_return: float  # CfD clawback only (RO has no clawback)
    net_support_cost: float  # Total cost to consumers (subsidy - clawback)
    
    # Price metrics
    average_wholesale_price: float
    average_re_capture_price: float  # Including both CfD and RO
    
    @property
    def subsidy_per_mwh_consumed(self) -> float:
        """Total subsidy levy per MWh of electricity consumed."""
        if self.total_demand_mwh > 0:
            return self.net_support_cost / self.total_demand_mwh
        return 0
    
    @property
    def annual_household_cost(self) -> float:
        """Estimated annual cost per household from CfD + RO levies."""
        household_consumption_mwh = 2.7
        hours_per_year = 8760
        annual_levy_per_mwh = self.subsidy_per_mwh_consumed * (hours_per_year / self.period_hours)
        return annual_levy_per_mwh * household_consumption_mwh
    
    @property
    def re_share(self) -> float:
        """Share of demand met by renewable generation."""
        if self.total_demand_mwh > 0:
            return self.total_re_generation_mwh / self.total_demand_mwh
        return 0


def simulate_combined_support(
    dispatch_results: list[DispatchResult],
    cfd_portfolio = None,  # CfDPortfolio (imported dynamically to avoid circular dependency)
    ro_portfolio: Optional[ROPortfolio] = None,
    year: int = 2025
) -> CombinedSupportResult:
    """
    Calculate combined CfD and RO costs for a simulation run.
    
    This provides a unified view of all renewable energy support costs.
    
    Args:
        dispatch_results: Results from grid.simulate_day() or simulate_year()
        cfd_portfolio: Portfolio of CfD contracts (optional)
        ro_portfolio: Portfolio of RO contracts (optional)
        year: Current year
        
    Returns:
        CombinedSupportResult with aggregate costs from both schemes
    """
    # Import here to avoid circular dependency
    try:
        from .cfd import simulate_cfd_costs
    except ImportError:
        from cfd import simulate_cfd_costs
    
    total_demand = sum(r.demand_mw for r in dispatch_results)
    total_re_generation = sum(
        mw for r in dispatch_results
        for gen, mw in r.dispatched_generators
        if gen.marginal_cost < 5  # RE sources
    )
    
    # Calculate CfD costs
    cfd_topup = 0.0
    cfd_clawback = 0.0
    if cfd_portfolio:
        cfd_result = simulate_cfd_costs(dispatch_results, cfd_portfolio)
        cfd_topup = cfd_result.total_topup_payments
        cfd_clawback = cfd_result.total_clawback_payments
    
    # Calculate RO costs
    ro_payments = 0.0
    if ro_portfolio:
        ro_result = simulate_ro_costs(dispatch_results, ro_portfolio, year)
        ro_payments = ro_result.total_ro_payments
    
    # Combined metrics
    total_subsidy = cfd_topup + ro_payments
    net_cost = total_subsidy - cfd_clawback
    
    # Average prices
    wholesale_prices = [r.wholesale_price for r in dispatch_results]
    avg_wholesale = np.mean(wholesale_prices) if wholesale_prices else 0
    
    # Estimate average RE capture price (wholesale + support)
    # Simplified: assume support adds to wholesale price
    if total_re_generation > 0:
        support_per_mwh = net_cost / total_re_generation if total_re_generation > 0 else 0
        avg_re_capture = avg_wholesale + support_per_mwh
    else:
        avg_re_capture = avg_wholesale
    
    return CombinedSupportResult(
        period_hours=len(dispatch_results),
        total_demand_mwh=total_demand,
        total_re_generation_mwh=total_re_generation,
        total_cfd_topup=cfd_topup,
        total_cfd_clawback=cfd_clawback,
        net_cfd_cost=cfd_topup - cfd_clawback,
        total_ro_payments=ro_payments,
        total_subsidy_cost=total_subsidy,
        total_clawback_return=cfd_clawback,
        net_support_cost=net_cost,
        average_wholesale_price=avg_wholesale,
        average_re_capture_price=avg_re_capture,
    )


# Import RO portfolio system
try:
    from .ro_portfolio import ROPortfolioManager, ROPortfolioState, create_ro_portfolio_with_estimates
except ImportError:
    from ro_portfolio import ROPortfolioManager, ROPortfolioState, create_ro_portfolio_with_estimates


def get_ro_portfolio_state(year: int = 2025) -> ROPortfolioState:
    """
    Get RO portfolio state for a given year using the portfolio system.
    
    This uses the ROPortfolio class which models individual RO projects
    with varying accreditation dates and expiry dates.
    
    Args:
        year: Year to get portfolio state for
        
    Returns:
        ROPortfolioState with coverage percentages and ROC value
    """
    portfolio = create_ro_portfolio_with_estimates()
    return portfolio.get_portfolio_state(year)

