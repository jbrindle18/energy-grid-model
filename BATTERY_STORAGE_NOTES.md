# Battery Storage Modeling - Design Notes

## Overview
Batteries could fundamentally change the dynamics shown in this model by:
- Reducing curtailment (storing excess RE instead of wasting it)
- Smoothing price volatility (arbitraging price differences)
- Potentially reducing CfD costs (RE earns more from market)
- Reducing gas backup requirements

## Key Design Considerations

### 1. Bidirectional Nature
- Batteries can CHARGE (consume electricity) and DISCHARGE (generate)
- Need two "modes" in dispatch algorithm

### 2. State of Charge (SOC) Tracking
- Track stored energy (MWh) across hours
- Constraints: max energy capacity (MWh) and max charge/discharge rate (MW)
- SOC must persist across simulation hours

### 3. Economic Decision-Making
- Charge when prices are LOW (negative marginal cost - willing to pay)
- Discharge when prices are HIGH (positive marginal cost - covers efficiency loss)
- Round-trip efficiency: ~85-90% (if charge 100 MWh, can only discharge ~85-90 MWh)

## Implementation Options

### Option 1: Integrated Merit Order (RECOMMENDED)
- Treat batteries as bidirectional participants in merit order
- Battery discharge: positive marginal cost (participates when demand > supply)
- Battery charge: negative marginal cost (participates when supply > demand)
- Sort all options (generators + battery discharge + battery charge) by marginal cost
- Update SOC after dispatch

**Pros:**
- Fits existing architecture
- Batteries naturally participate in price formation
- More realistic market behavior

**Cons:**
- More complex dispatch algorithm
- Need to handle negative marginal costs

### Option 2: Two-Pass Dispatch
- Pass 1: Normal dispatch to meet demand
- Pass 2: 
  - If curtailment → batteries charge (absorb excess)
  - If demand unmet → batteries discharge (if SOC > 0)

**Pros:**
- Simpler implementation
- Clear separation of concerns

**Cons:**
- Less integrated with market
- Batteries don't affect price formation

### Option 3: Price-Based Optimization
- Batteries optimize based on price expectations
- Requires forecasting or heuristics
- More sophisticated but complex

## Implementation Details Needed

### BatteryStorage Class
```python
@dataclass
class BatteryStorage(Generator):
    capacity_mw: float  # Max charge/discharge rate (MW)
    energy_capacity_mwh: float  # Max energy storage (MWh)
    round_trip_efficiency: float = 0.85
    state_of_charge_mwh: float = 0.0
    
    def get_charge_marginal_cost(self, wholesale_price: float) -> float:
        """Negative cost = willing to pay to charge"""
        return -wholesale_price * 0.9
    
    def get_discharge_marginal_cost(self) -> float:
        """Positive cost = covers efficiency loss"""
        return 0.0  # or small value
```

### Modified Dispatch Algorithm
1. Calculate net demand (demand - renewable generation)
2. If net demand > 0: batteries can discharge (if SOC > 0)
3. If net demand < 0: batteries can charge (if SOC < max)
4. Add both battery modes to merit order
5. Dispatch in order, updating SOC

### State Persistence
- Store SOC in Grid class or pass through simulate_day()/simulate_year()
- Initialize SOC at start of simulation
- Update after each hour's dispatch

### Revenue Calculation
- Revenue = (discharge_price × discharge_MWh) - (charge_price × charge_MWh)
- Track both charging and discharging separately
- Net revenue from arbitrage

### Visualization Needs
- SOC over time graph
- Charge/discharge patterns
- Impact on prices and curtailment
- Comparison: with vs without batteries

## Challenges
1. State persistence across hours
2. Handling negative marginal costs in merit order
3. Revenue calculation (arbitrage, not generation)
4. Visualizing bidirectional behavior
5. Testing edge cases (full battery, empty battery, etc.)

## Future Enhancements
- Multiple battery systems with different characteristics
- Degradation over time
- Different efficiency for charge vs discharge
- Market participation rules (can't charge and discharge same hour?)
- Longer-duration storage (4+ hours)

