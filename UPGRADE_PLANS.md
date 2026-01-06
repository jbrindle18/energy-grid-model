# Upgrade Implementation Plans

Based on validation results and the article analysis, here are prioritized upgrades for the energy grid model.

---

## 1. TIME-BASED CfD PORTFOLIO MODELING (High Priority)

### The Problem
Current model uses single strike prices. Reality: active CfDs average £151/MWh (old AR1-3 contracts), but new AR6 contracts are £58-71/MWh. The mix evolves over time as old contracts expire.

### Key Data Points (from article)
- 2025: CfDs cover ~12% of demand, weighted average £151/MWh
- 2031: CfDs will cover ~40% of demand
- AR1 (2015): Offshore £117/MWh, Onshore £82/MWh
- AR6 (2024): Offshore £71/MWh, Onshore £58/MWh, Solar £69/MWh
- CfD contracts last 15-20 years

### Implementation

#### New Data Structure: `CfDVintage`
```python
@dataclass
class CfDVintage:
    """A vintage of CfD contracts from a specific allocation round."""
    allocation_round: str  # e.g., "AR1", "AR6"
    award_year: int
    contract_length: int  # 15 or 20 years
    expiry_year: int
    capacity_gw: float
    strike_prices: dict  # {technology: price}

# Historical AR data
CFD_VINTAGES = {
    'AR1': CfDVintage('AR1', 2015, 15, 2030, capacity_gw=2.1,
                      strike_prices={'offshore_wind': 117, 'onshore_wind': 82, 'solar': 79}),
    'AR2': CfDVintage('AR2', 2017, 15, 2032, capacity_gw=3.3,
                      strike_prices={'offshore_wind': 57}),
    # ... etc
}
```

#### New Function: `calculate_portfolio_strike_price(year)`
Returns weighted average strike price for all active CfDs in a given year.

#### Visualizer Changes
- Add "Simulation Year" slider (2025-2040)
- Show CfD portfolio composition by vintage
- Display how weighted average strike price evolves as old contracts expire

### Files to Modify
- `src/cfd.py` - Add CfDVintage class and historical data
- `visualiser.py` - Add year selector and portfolio breakdown

---

## 2. BATTERY STORAGE MODEL (High Priority)

### The Problem
Model shows extreme price volatility and curtailment. Storage could smooth this. Need to show whether storage "fixes" the subsidy spiral or just delays it.

### Key Data Points
- UK targets 23-27 GW battery by 2030
- Most batteries are 2-4 hour duration
- Arbitrage: charge when price < threshold, discharge when price > threshold

### Implementation

#### New Class: `BatteryStorage`
```python
@dataclass
class BatteryStorage:
    """Grid-scale battery storage."""
    capacity_mw: float  # Power capacity
    duration_hours: float = 2.0  # Storage duration (2-4h typical)
    efficiency: float = 0.85  # Round-trip efficiency

    # State
    state_of_charge_mwh: float = 0.0

    @property
    def energy_capacity_mwh(self) -> float:
        return self.capacity_mw * self.duration_hours

    def decide_action(self, price: float,
                      charge_threshold: float = 30.0,
                      discharge_threshold: float = 80.0) -> tuple[str, float]:
        """Decide whether to charge, discharge, or idle."""
        if price < charge_threshold and self.state_of_charge_mwh < self.energy_capacity_mwh:
            return 'charge', min(self.capacity_mw,
                                 self.energy_capacity_mwh - self.state_of_charge_mwh)
        elif price > discharge_threshold and self.state_of_charge_mwh > 0:
            return 'discharge', min(self.capacity_mw, self.state_of_charge_mwh)
        return 'idle', 0.0
```

#### Integration with Grid Dispatch
1. Run initial dispatch without storage
2. Battery decides action based on price
3. If charging: add to demand (reduces curtailment)
4. If discharging: add to supply (displaces gas)
5. Recalculate price with storage effect

#### Visualizer Changes
- Add "Battery Storage" capacity slider (0-30 GW)
- Show storage state-of-charge over time
- Compare curtailment with/without storage
- Show price smoothing effect

### Files to Create/Modify
- `src/storage.py` - New module for battery storage
- `src/grid.py` - Add storage integration to dispatch
- `visualiser.py` - Add storage controls and charts

---

## 3. CAPACITY MARKET & BALANCING COSTS (Medium Priority)

### The Problem
Model underestimates wholesale price by ~£16/MWh. Missing costs explain this.

### Key Data Points (from article)
- Capacity market: ~£5/MWh (£1.4bn/year in 2025)
- Balancing costs: £9-18/MWh (£2.5bn in 2024, rising to £4.3-5.2bn in 2025)
- Total hidden costs: £14-23/MWh

### Implementation

#### New Constants
```python
# Additional system costs (£/MWh)
CAPACITY_MARKET_LEVY = 5.0  # £/MWh
BALANCING_COST_BASE = 9.0  # £/MWh at current RE penetration
BALANCING_COST_GROWTH = 0.15  # Additional £/MWh per 10pp RE increase
```

#### New Function: `calculate_system_costs(re_share)`
```python
def calculate_system_costs(re_share: float) -> dict:
    """Calculate additional system costs based on RE penetration."""
    # Balancing costs increase with RE share (more constraints)
    balancing = BALANCING_COST_BASE + BALANCING_COST_GROWTH * (re_share * 100 - 50)
    balancing = max(BALANCING_COST_BASE, balancing)

    return {
        'capacity_market': CAPACITY_MARKET_LEVY,
        'balancing': balancing,
        'total': CAPACITY_MARKET_LEVY + balancing,
    }
```

#### Visualizer Changes
- Add toggle "Include system costs"
- Show breakdown: Wholesale + Capacity Market + Balancing + CfD Levy = Consumer Price
- Document these in About page

### Files to Modify
- `src/constants.py` - Add new cost constants
- `src/pricing.py` or new `src/system_costs.py` - Add calculation
- `visualiser.py` - Add toggle and breakdown display

---

## 4. SCENARIO COMPARISON VIEW (Medium Priority)

### The Problem
Users must mentally compare between tab switches. Side-by-side would be more compelling.

### Implementation

#### New Tab: "Scenario Comparison"
- Select 2-3 scenarios from presets or save custom
- Side-by-side metrics table
- Overlaid price duration curves
- Stacked bar chart showing cost breakdown

#### Data Structure
```python
@dataclass
class ScenarioResult:
    """Cached results from a scenario run."""
    name: str
    params: dict
    wholesale_price: float
    consumer_price: float
    re_share: float
    cfd_cost: float
    curtailment_twh: float
```

#### Visualizer Changes
- New tab with comparison layout
- "Save scenario" button on main view
- Comparison table and charts

### Files to Modify
- `visualiser.py` - Add comparison tab and scenario caching

---

## 5. FUTURE CfD PRICE PROJECTIONS (Lower Priority)

### The Problem
New AR prices trend differently from old. Model should project what future ARs might cost.

### Implementation

#### Approach
- Extrapolate from AR1-AR6 price trends
- Account for learning curves (technology gets cheaper)
- But also supply chain constraints (can push prices up)

#### Simple Model
```python
def project_ar_strike_price(technology: str, year: int) -> float:
    """Project future AR strike prices based on trends."""
    # Base: AR6 2024 prices
    ar6_prices = {'solar': 69, 'onshore_wind': 58, 'offshore_wind': 71}

    # Learning rate: prices fall ~3% per year on average
    years_from_2024 = year - 2024
    learning_factor = 0.97 ** years_from_2024

    # But floor at ~£40/MWh (can't go below LCOE)
    projected = ar6_prices[technology] * learning_factor
    return max(40.0, projected)
```

---

## Implementation Order

### Phase 1: Quick Wins
1. **Capacity market & balancing costs** - Simple addition, explains price gap
2. **Update ABOUT.md** with validation results

### Phase 2: Core Upgrades
3. **Time-based CfD portfolio** - Critical for realistic modeling
4. **Battery storage** - Addresses main counterargument

### Phase 3: Polish
5. **Scenario comparison view** - UX improvement
6. **Future CfD projections** - Nice to have

---

## Estimated Scope

| Upgrade | New Code | Complexity | Impact |
|---------|----------|------------|--------|
| System costs | ~50 lines | Low | High (fixes price gap) |
| CfD vintages | ~150 lines | Medium | High (realistic CfD) |
| Battery storage | ~200 lines | Medium | High (key counterargument) |
| Scenario comparison | ~100 lines | Medium | Medium (UX) |
| Future AR projection | ~50 lines | Low | Medium |

---

## Questions for Implementation

1. **CfD vintages**: Should we model each AR separately, or group into "legacy" (AR1-3) vs "modern" (AR4+)?

2. **Battery storage**: Simple price-threshold model, or more sophisticated optimization?

3. **System costs**: Fixed values or scale with RE penetration?

4. **Comparison view**: How many scenarios to compare (2 vs 3)?
