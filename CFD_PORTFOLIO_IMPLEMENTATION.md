# CfD Portfolio Modeling - Implementation Plan

## Overview

Model the evolution of the UK's CfD portfolio over time, showing how the weighted average strike price changes as old (expensive) contracts expire and new (cheaper) contracts dominate.

**Key insight from the article**: Active CfDs average £151/MWh in 2025, but new AR6 contracts are £58-71/MWh. As AR1-AR3 contracts expire (~2030-2034), consumer costs from CfDs should fall significantly.

---

## Data Model

### 1. Historical AR Data (Hardcoded)

```python
# src/cfd_portfolio.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class AllocationRound:
    """Data for a single CfD allocation round."""
    name: str  # "AR1", "AR2", etc.
    award_year: int  # When contracts were awarded
    contract_length: int  # 15 or 20 years
    inflation_multiplier: float  # To convert 2012 prices to current

    # Capacity in GW
    offshore_wind_gw: float
    onshore_wind_gw: float
    solar_gw: float
    other_gw: float  # biomass, tidal, etc.

    # Strike prices in 2012 £/MWh (None if technology excluded)
    offshore_strike_2012: Optional[float]
    onshore_strike_2012: Optional[float]
    solar_strike_2012: Optional[float]

    @property
    def expiry_year(self) -> int:
        """When contracts from this round expire."""
        # Contracts typically start generating 2-4 years after award
        # Using 3 years as average lead time
        return self.award_year + 3 + self.contract_length

    @property
    def total_capacity_gw(self) -> float:
        return self.offshore_wind_gw + self.onshore_wind_gw + self.solar_gw + self.other_gw

    def strike_price_current(self, technology: str) -> Optional[float]:
        """Get strike price in current money."""
        strike_2012 = {
            'offshore_wind': self.offshore_strike_2012,
            'onshore_wind': self.onshore_strike_2012,
            'solar': self.solar_strike_2012,
        }.get(technology)

        if strike_2012 is None:
            return None
        return strike_2012 * self.inflation_multiplier


# Historical allocation round data
ALLOCATION_ROUNDS = {
    'AR1': AllocationRound(
        name='AR1',
        award_year=2015,
        contract_length=15,
        inflation_multiplier=1.47,  # 2012 to 2025
        offshore_wind_gw=1.2,
        onshore_wind_gw=0.7,
        solar_gw=0.07,
        other_gw=0.1,
        offshore_strike_2012=117.14,
        onshore_strike_2012=82.50,
        solar_strike_2012=79.23,
    ),
    'AR2': AllocationRound(
        name='AR2',
        award_year=2017,
        contract_length=15,
        inflation_multiplier=1.47,
        offshore_wind_gw=3.3,
        onshore_wind_gw=0.0,  # Excluded
        solar_gw=0.0,  # Excluded
        other_gw=0.0,
        offshore_strike_2012=57.50,
        onshore_strike_2012=None,
        solar_strike_2012=None,
    ),
    'AR3': AllocationRound(
        name='AR3',
        award_year=2019,
        contract_length=15,
        inflation_multiplier=1.47,
        offshore_wind_gw=5.5,
        onshore_wind_gw=0.0,
        solar_gw=0.0,
        other_gw=0.0,
        offshore_strike_2012=39.65,
        onshore_strike_2012=None,
        solar_strike_2012=None,
    ),
    'AR4': AllocationRound(
        name='AR4',
        award_year=2022,
        contract_length=15,
        inflation_multiplier=1.47,
        offshore_wind_gw=3.0,
        onshore_wind_gw=0.9,
        solar_gw=2.2,
        other_gw=0.1,
        offshore_strike_2012=37.35,
        onshore_strike_2012=42.47,
        solar_strike_2012=45.99,
    ),
    'AR5': AllocationRound(
        name='AR5',
        award_year=2023,
        contract_length=15,
        inflation_multiplier=1.47,
        offshore_wind_gw=0.0,  # None awarded!
        onshore_wind_gw=1.3,
        solar_gw=1.9,
        other_gw=0.4,
        offshore_strike_2012=None,
        onshore_strike_2012=52.29,
        solar_strike_2012=47.00,
    ),
    'AR6': AllocationRound(
        name='AR6',
        award_year=2024,
        contract_length=15,  # Some are 20 now
        inflation_multiplier=1.47,
        offshore_wind_gw=5.3,
        onshore_wind_gw=0.9,
        solar_gw=3.3,
        other_gw=0.4,  # Floating wind, tidal
        offshore_strike_2012=58.87,
        onshore_strike_2012=50.90,
        solar_strike_2012=47.00,
    ),
}
```

### 2. Portfolio State at a Given Year

```python
@dataclass
class CfDPortfolioState:
    """The state of the CfD portfolio at a specific simulation year."""
    year: int

    # Active capacity by AR
    active_rounds: dict[str, AllocationRound]

    # Aggregate metrics
    total_capacity_gw: float
    weighted_avg_strike_offshore: float
    weighted_avg_strike_onshore: float
    weighted_avg_strike_solar: float
    weighted_avg_strike_all: float

    # What percent of generation this covers (estimate)
    estimated_demand_coverage: float


def calculate_portfolio_state(year: int) -> CfDPortfolioState:
    """
    Calculate the CfD portfolio state for a given year.

    Contracts are active from (award_year + 3) to (award_year + 3 + contract_length).
    """
    active_rounds = {}

    for ar_name, ar in ALLOCATION_ROUNDS.items():
        start_year = ar.award_year + 3  # Average construction time
        end_year = start_year + ar.contract_length

        if start_year <= year < end_year:
            active_rounds[ar_name] = ar

    # Calculate weighted averages
    total_offshore_gw = sum(ar.offshore_wind_gw for ar in active_rounds.values())
    total_onshore_gw = sum(ar.onshore_wind_gw for ar in active_rounds.values())
    total_solar_gw = sum(ar.solar_gw for ar in active_rounds.values())
    total_gw = sum(ar.total_capacity_gw for ar in active_rounds.values())

    # Weighted average strike prices (current money)
    def weighted_avg(tech: str, total_tech_gw: float) -> float:
        if total_tech_gw == 0:
            return 0.0
        weighted_sum = sum(
            ar.strike_price_current(tech) * getattr(ar, f'{tech}_gw')
            for ar in active_rounds.values()
            if ar.strike_price_current(tech) is not None
        )
        return weighted_sum / total_tech_gw

    avg_offshore = weighted_avg('offshore_wind', total_offshore_gw)
    avg_onshore = weighted_avg('onshore_wind', total_onshore_gw)
    avg_solar = weighted_avg('solar', total_solar_gw)

    # Overall weighted average (by generation, not capacity)
    # Use capacity factors: offshore 40%, onshore 27%, solar 11%
    offshore_gen = total_offshore_gw * 0.40
    onshore_gen = total_onshore_gw * 0.27
    solar_gen = total_solar_gw * 0.11
    total_gen = offshore_gen + onshore_gen + solar_gen

    if total_gen > 0:
        avg_all = (
            avg_offshore * offshore_gen +
            avg_onshore * onshore_gen +
            avg_solar * solar_gen
        ) / total_gen
    else:
        avg_all = 0.0

    # Estimate demand coverage (UK demand ~300 TWh/year)
    annual_gen_twh = (
        total_offshore_gw * 0.40 * 8760 / 1000 +
        total_onshore_gw * 0.27 * 8760 / 1000 +
        total_solar_gw * 0.11 * 8760 / 1000
    )
    uk_demand_twh = 300
    coverage = annual_gen_twh / uk_demand_twh

    return CfDPortfolioState(
        year=year,
        active_rounds=active_rounds,
        total_capacity_gw=total_gw,
        weighted_avg_strike_offshore=avg_offshore,
        weighted_avg_strike_onshore=avg_onshore,
        weighted_avg_strike_solar=avg_solar,
        weighted_avg_strike_all=avg_all,
        estimated_demand_coverage=coverage,
    )
```

### 3. Integration with Existing CfD Simulation

```python
def create_cfd_portfolio_for_year(
    generators: list,
    simulation_year: int,
    coverage_fraction: float = 1.0,
) -> CfDPortfolio:
    """
    Create CfD contracts using the weighted average strike prices
    for the given simulation year.
    """
    portfolio_state = calculate_portfolio_state(simulation_year)

    # Use the year-appropriate strike prices
    strike_prices = {
        'solar': portfolio_state.weighted_avg_strike_solar,
        'onshore_wind': portfolio_state.weighted_avg_strike_onshore,
        'offshore_wind': portfolio_state.weighted_avg_strike_offshore,
    }

    return create_cfd_portfolio_for_fleet(
        generators=generators,
        coverage=coverage_fraction * portfolio_state.estimated_demand_coverage,
        strike_prices=strike_prices,
    )
```

---

## Visualizer Changes

### New Controls in Sidebar

```python
st.sidebar.markdown("---")
st.sidebar.subheader("CfD Portfolio Settings")

# Simulation year slider
simulation_year = st.sidebar.slider(
    "Simulation Year",
    min_value=2025,
    max_value=2040,
    value=2025,
    help="Year to simulate. Affects which CfD contracts are active and their strike prices."
)

# Show portfolio state
portfolio_state = calculate_portfolio_state(simulation_year)
st.sidebar.metric("Active CfD Capacity", f"{portfolio_state.total_capacity_gw:.1f} GW")
st.sidebar.metric("Avg Strike Price", f"£{portfolio_state.weighted_avg_strike_all:.0f}/MWh")
st.sidebar.metric("Demand Coverage", f"{portfolio_state.estimated_demand_coverage*100:.0f}%")
```

### New Chart: Portfolio Evolution Over Time

```python
# In CfD Economics tab, add a chart showing:
# - X axis: Year (2025-2040)
# - Y axis: Weighted average strike price
# - Stacked area: Capacity by AR vintage

years = range(2025, 2041)
data = [calculate_portfolio_state(y) for y in years]

fig = go.Figure()

# Add line for weighted average strike price
fig.add_trace(go.Scatter(
    x=years,
    y=[d.weighted_avg_strike_all for d in data],
    name="Weighted Avg Strike (£/MWh)",
    yaxis="y2"
))

# Add stacked area for capacity by AR
for ar_name in ['AR1', 'AR2', 'AR3', 'AR4', 'AR5', 'AR6']:
    capacities = []
    for state in data:
        if ar_name in state.active_rounds:
            capacities.append(state.active_rounds[ar_name].total_capacity_gw)
        else:
            capacities.append(0)
    fig.add_trace(go.Scatter(
        x=years,
        y=capacities,
        name=ar_name,
        stackgroup='capacity',
        mode='none'
    ))
```

---

## Files to Create/Modify

| File | Action | Changes |
|------|--------|---------|
| `src/cfd_portfolio.py` | **CREATE** | AllocationRound class, ALLOCATION_ROUNDS data, calculate_portfolio_state() |
| `src/cfd.py` | MODIFY | Add create_cfd_portfolio_for_year() function |
| `visualiser.py` | MODIFY | Add year slider, portfolio state display, evolution chart |
| `tests/test_cfd_portfolio.py` | **CREATE** | Tests for portfolio calculations |

---

## Test Cases

```python
# tests/test_cfd_portfolio.py

def test_ar1_expires_around_2033():
    """AR1 contracts (2015 + 3 + 15 = 2033) should expire around 2033."""
    state_2032 = calculate_portfolio_state(2032)
    state_2034 = calculate_portfolio_state(2034)

    assert 'AR1' in state_2032.active_rounds
    assert 'AR1' not in state_2034.active_rounds

def test_weighted_avg_falls_after_ar1_expires():
    """After expensive AR1 contracts expire, weighted avg should drop."""
    state_2030 = calculate_portfolio_state(2030)
    state_2035 = calculate_portfolio_state(2035)

    # AR1 had highest strike prices, so avg should fall
    assert state_2035.weighted_avg_strike_all < state_2030.weighted_avg_strike_all

def test_2025_matches_article_data():
    """2025 portfolio should roughly match article's £151/MWh figure."""
    state = calculate_portfolio_state(2025)

    # Article says weighted average is ~£151/MWh for active contracts
    # Our calculation might differ slightly due to data granularity
    assert 130 < state.weighted_avg_strike_all < 170

def test_demand_coverage_increases_over_time():
    """As more ARs come online, demand coverage should increase."""
    state_2025 = calculate_portfolio_state(2025)
    state_2030 = calculate_portfolio_state(2030)

    # Article says 12% in 2025, 40% by 2031
    assert state_2025.estimated_demand_coverage < state_2030.estimated_demand_coverage
```

---

## Open Questions

1. **AR delivery timing**: I'm assuming contracts start generating 3 years after award. The actual timing varies by project. Should we model this more precisely if you can get project-level data?

2. **Future ARs**: Should we add placeholder AR7/AR8 data for simulating 2030+? Or just show existing contracted capacity?

3. **Nuclear CfDs**: The article mentions nuclear CfD at £127/MWh. Should we include Hinkley Point C and Sizewell C in the portfolio?

4. **Investment Contracts**: Pre-AR1 "Investment Contracts" (like early offshore wind) also exist. Include these?

---

## Data You Could Provide

If you can access the LCCC register and export a CSV with:
- Project name
- Technology
- Allocation round
- Capacity (MW)
- Strike price (2012 prices)
- Expected commissioning date

...that would let us model individual projects rather than AR-level aggregates, giving more accurate expiry timing and weighted averages.

---

## Sources

- [LCCC CfD Register](https://register.lowcarboncontracts.uk/)
- [LCCC Data Portal](https://www.lowcarboncontracts.uk/data-portal/dataset/?tags=CfD)
- [Parliament Research Briefing CBP-9871](https://researchbriefings.files.parliament.uk/documents/CBP-9871/CBP-9871.pdf)
- [ORE Catapult AR6 Analysis](https://ore.catapult.org.uk/resource-hub/blog/allocation-round-6-results-and-analysis/)
