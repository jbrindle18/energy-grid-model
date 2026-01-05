"""
Pricing analysis and CfD (Contracts for Difference) support.

This module provides:
- Price duration curves
- Cannibalisation analysis
- Revenue calculations
- Future: CfD strike price mechanisms
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np

try:
    from .grid import DispatchResult, SimulationSummary
    from .constants import RE_MARGINAL_COST_THRESHOLD
except ImportError:
    from grid import DispatchResult, SimulationSummary
    from constants import RE_MARGINAL_COST_THRESHOLD


@dataclass
class PriceDurationCurve:
    """
    Price duration curve - shows price distribution over time.

    Useful for understanding:
    - How often prices are at different levels
    - Baseload vs peak pricing
    - Zero-price hour frequency
    """
    prices_sorted: np.ndarray  # Prices sorted descending
    hours: np.ndarray  # Cumulative hours at or above each price

    @classmethod
    def from_results(cls, results: list[DispatchResult]) -> 'PriceDurationCurve':
        """Create price duration curve from simulation results."""
        prices = np.array([r.wholesale_price for r in results])
        prices_sorted = np.sort(prices)[::-1]  # Descending
        hours = np.arange(1, len(prices) + 1)
        return cls(prices_sorted=prices_sorted, hours=hours)

    def price_at_percentile(self, percentile: float) -> float:
        """Get price at a given percentile (0-100)."""
        idx = int(len(self.prices_sorted) * percentile / 100)
        return self.prices_sorted[min(idx, len(self.prices_sorted) - 1)]

    def hours_above_price(self, price: float) -> int:
        """Count hours where wholesale price was above given level."""
        return np.sum(self.prices_sorted > price)

    def hours_below_price(self, price: float) -> int:
        """Count hours where wholesale price was below given level."""
        return np.sum(self.prices_sorted < price)


@dataclass
class CannibalalisationMetrics:
    """
    Metrics for understanding RE cannibalisation effect.

    Cannibalisation: as RE penetration increases, RE generators earn less
    because they're more often setting the (low) marginal price.
    """
    average_re_capture_price: float  # Average price when RE was generating
    average_wholesale_price: float  # Overall average price
    capture_rate: float  # Ratio of RE capture price to average (< 1 = cannibalisation)
    zero_price_hours: int
    total_hours: int

    @classmethod
    def from_results(cls, results: list[DispatchResult]) -> 'CannibalalisationMetrics':
        """
        Calculate cannibalisation metrics from simulation.
        
        Cannibalisation occurs when renewable generators earn less than the
        average wholesale price because they're more often setting the (low)
        marginal price themselves.
        
        Returns:
            CannibalalisationMetrics with capture rate and price statistics
        """
        if not results:
            raise ValueError("Cannot calculate metrics from empty results")
        
        all_prices = [r.wholesale_price for r in results]
        avg_price = np.mean(all_prices)

        # Calculate RE capture price (weighted by RE generation)
        re_weighted_prices = []
        re_generation = []

        # Use the constant from constants module
        RE_THRESHOLD = RE_MARGINAL_COST_THRESHOLD
        
        for r in results:
            re_gen = sum(
                mw for gen, mw in r.dispatched_generators
                if gen.marginal_cost < RE_THRESHOLD  # RE sources
            )
            if re_gen > 0:
                re_weighted_prices.append(r.wholesale_price * re_gen)
                re_generation.append(re_gen)

        total_re_gen = sum(re_generation)
        if total_re_gen > 0:
            re_capture_price = sum(re_weighted_prices) / total_re_gen
        else:
            re_capture_price = avg_price

        capture_rate = re_capture_price / avg_price if avg_price > 0 else 1.0

        return cls(
            average_re_capture_price=re_capture_price,
            average_wholesale_price=avg_price,
            capture_rate=capture_rate,
            zero_price_hours=sum(1 for p in all_prices if p < 5),
            total_hours=len(results)
        )


@dataclass
class GeneratorRevenue:
    """Revenue breakdown for a generator over simulation period."""
    name: str
    total_revenue_gbp: float
    total_generation_mwh: float
    average_capture_price: float  # £/MWh actually received
    capacity_mw: float
    load_factor: float  # Actual generation / potential generation


def calculate_generator_revenues(results: list[DispatchResult]) -> list[GeneratorRevenue]:
    """
    Calculate revenue for each generator in the fleet.

    Revenue = sum(MWh dispatched * wholesale price at that hour)
    """
    # Aggregate by generator name
    revenue_totals: dict[str, float] = {}
    generation_totals: dict[str, float] = {}
    capacity_map: dict[str, float] = {}

    for result in results:
        for gen, mw in result.dispatched_generators:
            name = gen.name
            revenue = mw * result.wholesale_price  # MWh * £/MWh
            revenue_totals[name] = revenue_totals.get(name, 0) + revenue
            generation_totals[name] = generation_totals.get(name, 0) + mw
            capacity_map[name] = gen.capacity_mw

    revenues = []
    hours = len(results)

    for name in revenue_totals:
        total_gen = generation_totals[name]
        total_rev = revenue_totals[name]
        capacity = capacity_map[name]

        avg_price = total_rev / total_gen if total_gen > 0 else 0
        max_possible_gen = capacity * hours
        load_factor = total_gen / max_possible_gen if max_possible_gen > 0 else 0

        revenues.append(GeneratorRevenue(
            name=name,
            total_revenue_gbp=total_rev,
            total_generation_mwh=total_gen,
            average_capture_price=avg_price,
            capacity_mw=capacity,
            load_factor=load_factor
        ))

    return sorted(revenues, key=lambda x: x.total_revenue_gbp, reverse=True)


# Note: CfD (Contracts for Difference) functionality has been moved to cfd.py
# Import from there instead: from cfd import CfDContract, CfDPortfolio, etc.
