"""
Grid dispatch and merit order simulation.

Implements the UK wholesale electricity market dispatch mechanism:
1. Generators are ordered by marginal cost (cheapest first)
2. Generators are dispatched in order until demand is met
3. The marginal cost of the last dispatched generator sets the wholesale price

This is the core mechanism that explains why:
- RE with near-zero marginal costs drives down wholesale prices
- Gas often sets the marginal price (and thus all generators benefit from high gas prices)
- Cannibalisation occurs as RE penetration increases

NOTE: This is a simplified model. Real markets have:
- Bilateral contracts and forward markets
- Balancing mechanism for real-time adjustments
- Network constraints and transmission limits
- Market maker margins and other costs not modeled here
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np

try:
    from .generators import Generator
    from .demand import DemandProfile
    from .constants import RE_MARGINAL_COST_THRESHOLD, EMERGENCY_PRICE_CAP
except ImportError:
    from generators import Generator
    from demand import DemandProfile
    from constants import RE_MARGINAL_COST_THRESHOLD, EMERGENCY_PRICE_CAP


@dataclass
class DispatchResult:
    """Result of a single dispatch period."""
    hour: int
    day_of_year: int
    demand_mw: float
    wholesale_price: float  # £/MWh - set by marginal generator
    dispatched_generators: list[tuple[Generator, float]]  # (generator, MW dispatched)
    total_generation_mw: float
    price_setter: Optional[Generator] = None  # Which generator set the price
    curtailment_mw: float = 0.0  # RE that couldn't be dispatched

    @property
    def is_oversupply(self) -> bool:
        """True if there's more RE available than demand."""
        return self.curtailment_mw > 0

    @property
    def re_share(self) -> float:
        """
        Share of generation from renewable sources.
        
        Returns:
            Fraction (0-1) of total generation from renewables
        """
        re_gen = sum(
            mw for gen, mw in self.dispatched_generators
            if gen.marginal_cost < RE_MARGINAL_COST_THRESHOLD  # RE has near-zero marginal cost
        )
        return re_gen / self.total_generation_mw if self.total_generation_mw > 0 else 0


@dataclass
class Grid:
    """
    UK electricity grid simulation.

    Manages generator fleet and performs merit order dispatch.
    """
    generators: list[Generator] = field(default_factory=list)
    demand_profile: Optional[DemandProfile] = None

    def add_generator(self, generator: Generator):
        """Add a generator to the fleet."""
        self.generators.append(generator)

    def dispatch(self, demand_mw: float, hour: int = 12,
                 day_of_year: int = 172) -> DispatchResult:
        """
        Perform merit order dispatch to meet demand.

        This is the core dispatch algorithm that simulates how the UK wholesale
        electricity market operates. All generators receive the same price (the
        marginal cost of the last dispatched generator).

        Args:
            demand_mw: Electricity demand to meet (MW). Should be positive.
            hour: Hour of day (0-23), affects solar output
            day_of_year: Day of year (0-364), affects solar/seasonal patterns

        Returns:
            DispatchResult with wholesale price and dispatch details
            
        Raises:
            ValueError: If demand is negative or generators list is empty
        """
        # Input validation
        if demand_mw < 0:
            raise ValueError(f"Demand must be non-negative, got {demand_mw}")
        if not self.generators:
            raise ValueError("Cannot dispatch with no generators in fleet")
        # Calculate available power for each generator
        # For dispatchable generators (gas, nuclear, biomass), use full capacity
        # Capacity factor represents average utilization, not max availability
        available = []
        for gen in self.generators:
            # Dispatchable generators can run at full capacity when needed
            # (capacity_factor represents average utilization over time, not max availability)
            if gen.marginal_cost >= RE_MARGINAL_COST_THRESHOLD:  # Non-RE sources (gas, nuclear, biomass, etc.)
                # Interconnectors are not truly dispatchable - they depend on European market conditions
                # Use capacity_factor to limit their availability (typically ~50%)
                # Check by class name to avoid import issues
                if 'Interconnector' in gen.__class__.__name__:
                    # Interconnectors are limited by capacity_factor (average availability ~50%)
                    available_mw = gen.capacity_mw * gen.capacity_factor
                else:
                    # True dispatchable sources (gas, nuclear, biomass) use full capacity
                    available_mw = gen.capacity_mw
            else:
                # RE sources have time-varying availability (solar, wind)
                available_mw = gen.available_power(hour, day_of_year)
            available.append((gen, available_mw))

        # Sort by marginal cost (merit order)
        # NOTE: If multiple generators have the same marginal cost, order is non-deterministic
        # In practice, this is rare and doesn't significantly affect results
        available.sort(key=lambda x: (x[0].marginal_cost, x[0].name))

        # Dispatch generators until demand is met
        remaining_demand = demand_mw
        dispatched = []
        total_generation = 0
        price_setter = None
        wholesale_price = 0

        for gen, available_mw in available:
            if remaining_demand <= 0:
                break

            dispatch_mw = min(available_mw, remaining_demand)
            if dispatch_mw > 0:
                dispatched.append((gen, dispatch_mw))
                remaining_demand -= dispatch_mw
                total_generation += dispatch_mw
                price_setter = gen
                wholesale_price = gen.marginal_cost

        # Calculate curtailment (RE that couldn't be dispatched)
        # This happens when RE supply exceeds demand
        # NOTE: In reality, curtailment can also occur due to network constraints,
        # but this model only considers economic curtailment (oversupply)
        re_available = sum(
            avail for gen, avail in available
            if gen.marginal_cost < RE_MARGINAL_COST_THRESHOLD  # RE sources
        )
        re_dispatched = sum(
            mw for gen, mw in dispatched
            if gen.marginal_cost < RE_MARGINAL_COST_THRESHOLD
        )
        curtailment = max(0, re_available - re_dispatched)

        # If demand couldn't be fully met, price would spike
        # (in reality, this triggers emergency measures like demand response, imports, etc.)
        # This should rarely happen now that dispatchable generators use full capacity
        if remaining_demand > 0:
            # WARNING: This indicates insufficient capacity in the fleet
            # In production, you might want to log this or raise an exception
            wholesale_price = EMERGENCY_PRICE_CAP  # Price cap / emergency pricing

        return DispatchResult(
            hour=hour,
            day_of_year=day_of_year,
            demand_mw=demand_mw,
            wholesale_price=wholesale_price,
            dispatched_generators=dispatched,
            total_generation_mw=total_generation,
            price_setter=price_setter,
            curtailment_mw=curtailment
        )

    def simulate_day(self, day_of_year: int = 172,
                     is_weekday: bool = True) -> list[DispatchResult]:
        """
        Simulate dispatch for every hour of a day.

        Args:
            day_of_year: Day of year (0-364)
            is_weekday: Whether it's a weekday

        Returns:
            List of 24 DispatchResults
        """
        if self.demand_profile is None:
            raise ValueError("No demand profile set. Use grid.demand_profile = DemandProfile()")

        results = []
        for hour in range(24):
            demand = self.demand_profile.get_demand(hour, day_of_year, is_weekday)
            result = self.dispatch(demand, hour, day_of_year)
            results.append(result)

        return results

    def simulate_year(self) -> list[DispatchResult]:
        """
        Simulate dispatch for every hour of a year (8760 hours).

        Returns:
            List of 8760 DispatchResults
        """
        if self.demand_profile is None:
            raise ValueError("No demand profile set.")

        results = []
        for h in range(8760):
            hour = h % 24
            day = h // 24
            day_of_year = day % 365
            is_weekday = (day % 7) < 5

            demand = self.demand_profile.get_demand(hour, day_of_year, is_weekday)
            result = self.dispatch(demand, hour, day_of_year)
            results.append(result)

        return results


@dataclass
class SimulationSummary:
    """Summary statistics from a simulation run."""
    average_price: float
    min_price: float
    max_price: float
    price_std: float
    zero_price_hours: int  # Hours where price was near-zero
    average_re_share: float
    total_curtailment_mwh: float
    hours_simulated: int

    # Revenue by generator type
    revenue_by_source: dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_results(cls, results: list[DispatchResult]) -> 'SimulationSummary':
        """Calculate summary statistics from simulation results."""
        prices = [r.wholesale_price for r in results]
        re_shares = [r.re_share for r in results]

        # Calculate revenue for each generator
        revenue_by_source: dict[str, float] = {}
        for result in results:
            for gen, mw in result.dispatched_generators:
                name = gen.name
                # Revenue = MW dispatched * wholesale price for that hour
                revenue = mw * result.wholesale_price
                revenue_by_source[name] = revenue_by_source.get(name, 0) + revenue

        return cls(
            average_price=np.mean(prices),
            min_price=np.min(prices),
            max_price=np.max(prices),
            price_std=np.std(prices),
            zero_price_hours=sum(1 for p in prices if p < 5),
            average_re_share=np.mean(re_shares),
            total_curtailment_mwh=sum(r.curtailment_mw for r in results),
            hours_simulated=len(results),
            revenue_by_source=revenue_by_source
        )


def create_uk_grid() -> Grid:
    """Create a grid with current UK capacity and demand."""
    try:
        from .generators import create_uk_current_fleet
        from .demand import create_uk_demand_profile
    except ImportError:
        from generators import create_uk_current_fleet
        from demand import create_uk_demand_profile

    grid = Grid(generators=create_uk_current_fleet())
    grid.demand_profile = create_uk_demand_profile()
    return grid


def create_scenario_grid(re_penetration: float = 0.5,
                         total_capacity_gw: float = 100,
                         electrification_factor: float = 1.0) -> Grid:
    """
    Create a grid for a specific scenario.

    Args:
        re_penetration: Target RE share of capacity (0-1)
        total_capacity_gw: Total installed capacity
        electrification_factor: Demand growth multiplier

    Returns:
        Configured Grid instance
    """
    try:
        from .generators import create_scaled_fleet
        from .demand import create_future_demand_profile
    except ImportError:
        from generators import create_scaled_fleet
        from demand import create_future_demand_profile

    # Calculate peak demand to ensure sufficient dispatchable capacity
    demand_profile = create_future_demand_profile(electrification_factor)
    peak_demand_gw = demand_profile.peak_demand_gw
    
    grid = Grid(generators=create_scaled_fleet(re_penetration, total_capacity_gw, peak_demand_gw))
    grid.demand_profile = demand_profile
    return grid
