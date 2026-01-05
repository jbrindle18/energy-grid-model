# Energy Grid Model - Development Roadmap

## Goal
Build a tool that demonstrates how CfD economics change as renewable penetration increases, suitable for blog posts and policy discussions.

## Phase 1: Core Engine ✅ COMPLETE
- [x] Generator classes with UK-realistic parameters
- [x] Merit order dispatch algorithm
- [x] Demand model with hourly/seasonal variation
- [x] Basic price formation
- [x] Cannibalisation metrics

## Phase 2: CfD Economics Layer ✅ COMPLETE

### 2.1 Core CfD Mechanics
- [x] CfD contract class with strike prices
- [x] Top-up payments (when wholesale < strike)
- [x] Clawback payments (when wholesale > strike)
- [x] Generator revenue = wholesale + CfD payment

### 2.2 LCCC (Low Carbon Contracts Company) Simulation
- [x] Aggregate CfD costs across all contracted generators
- [x] Model how costs change with RE penetration
- [x] Consumer levy calculation (£/MWh on bills)

### 2.3 Key Scenarios to Model
- [x] Current CfD strike prices (~£40-50/MWh for offshore wind)
- [x] What strike price is needed at 70% RE? 95% RE?
- [x] Total subsidy cost to consumers at different penetration levels
- [ ] The "2023 allocation failure" - when ASP was set too low (documented in code)

### 2.4 Key Outputs
- [x] CfD subsidy cost vs RE penetration curve (in visualiser)
- [x] Consumer bill impact (£/year per household)
- [x] Required strike price to achieve target IRR for investors
- [x] "Subsidy trap" visualization - showing costs spiral as RE increases

## Phase 3: Credibility & Polish

### 3.1 Real Data Integration
- [ ] Historical wind capacity factors from National Grid ESO
- [ ] Historical demand data
- [ ] Actual CfD strike prices from allocation rounds
- [ ] Validation against real wholesale prices

### 3.2 Better Visualizations
- [x] Price duration curves
- [x] Merit order stack charts
- [x] CfD cost waterfall charts (in CfD Economics tab)
- [x] Interactive scenario comparison (preset dropdown)

### 3.3 Battery Storage (Optional)
- [ ] Simple storage model (charge when cheap, discharge when expensive)
- [ ] Test if storage "solves" cannibalisation
- [ ] Show storage needed to avoid negative prices

## Phase 4: Blog/Policy Output

### 4.1 Key Charts for Blog Post
1. "The Cannibalisation Curve" - RE capture price vs penetration
2. "The Subsidy Spiral" - CfD costs vs penetration
3. "The Market Paradox" - wholesale prices collapse but bills don't
4. "The 2035 Question" - what does a decarbonised grid cost?

### 4.2 Interactive Tool ✅ COMPLETE
- [x] Simple web interface (Streamlit)
- [x] Sliders for RE capacity, strike prices, gas prices
- [x] Real-time charts showing price/cost impacts
- [ ] Shareable URL for policy discussions (requires deployment)

## Data Sources

| Data | Source | Status |
|------|--------|--------|
| Capacity factors | DESNZ Energy Trends | Need to fetch |
| Demand profiles | National Grid ESO | Need to fetch |
| CfD strike prices | LCCC annual reports | Need to compile |
| Wholesale prices | Nordpool/EPEX | For validation |
| Gas prices | ICE/NBP | For sensitivity |

## Success Criteria

A successful v1.0 should answer:
1. At current CfD strike prices, what happens to subsidy costs as RE grows?
2. What strike price would make a 2035 project bankable?
3. What's the consumer bill impact of a 95% RE grid?
4. Why can't markets alone deliver decarbonisation?

## Technical Debt to Address
- [ ] Fix notebooks to work with updated code
- [x] Add proper error handling (validation module + error handling in visualiser)
- [x] Add unit tests for core functions (47+ tests, including CfD tests)
- [x] Document all assumptions clearly (constants module, docstrings)

## Recent Improvements (2025-01-05)
- [x] Consolidated duplicate CfD classes (removed from pricing.py)
- [x] Extracted constants to src/constants.py
- [x] Added validation module for input validation
- [x] Added capacity planning utilities
- [x] Made GasGenerator.marginal_cost reactive (property)
- [x] Added comprehensive error handling in visualiser
- [x] Added progress tracking for long simulations
- [x] Added tests for cfd.py module
- [x] Standardized import handling
