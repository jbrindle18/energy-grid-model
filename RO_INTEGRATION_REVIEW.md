# RO Integration Review

## Issues Found

### 1. Generator Revenues - RO Payments Missing ❌

**Location**: `visualiser.py` lines 1528-1713

**Issue**: The "Generator Revenues" section calculates:
- Wholesale revenue (from `calculate_generator_revenues`)
- CfD payments (added if checkbox enabled)
- **RO payments are NOT included**

**Impact**: Generator revenues are understated for RO-supported generators. RO payments should be added similar to how CfD payments are handled.

**Current Code**:
```python
cfd_payments_by_generator = {}  # Only CfD tracked
# ... CfD calculation ...
# RO payments never calculated or added
```

**Fix Needed**: 
- Calculate RO payments per generator (similar to CfD)
- Add RO payments to total revenue when RO checkbox is enabled
- Update stacked bar chart to include RO payments
- Update revenue table to show RO payments

### 2. Average Capture Price - RO Missing ❌

**Location**: `visualiser.py` lines 1715-1750

**Issue**: The "Average Capture Price vs Wholesale Price" chart includes:
- Wholesale price
- CfD-adjusted capture price (if CfD enabled)
- **RO-adjusted capture price is NOT included**

**Impact**: Capture prices for RO generators don't reflect their actual revenue (wholesale + RO payment).

**Fix Needed**:
- Calculate RO-adjusted capture price per generator
- Include RO in the capture price comparison chart
- Update to show: Wholesale, CfD-adjusted, RO-adjusted, and Combined (CfD+RO) capture prices

### 3. Revenue Calculation Logic ✅

**Location**: `src/pricing.py` lines 134-174

**Status**: Correct - `calculate_generator_revenues` only calculates wholesale revenue, which is correct. Support scheme payments (CfD/RO) should be added separately in the UI.

### 4. RO Simulation ✅

**Location**: `visualiser.py` lines 910-917

**Status**: Correct - RO simulation is run and results are stored in session state.

### 5. Consumer Cost Metrics ✅

**Location**: `visualiser.py` lines 965-993

**Status**: Correct - "Wholesale + Support" metric correctly includes both CfD and RO levies.

### 6. RO Display Section ✅

**Location**: `visualiser.py` lines 1917-1980

**Status**: Correct - RO metrics are displayed in the "Renewable Energy Support Schemes" tab.

## Summary

**Missing RO Integration:**
1. ❌ Generator Revenues - RO payments not included
2. ❌ Average Capture Price - RO not included in capture price calculations

**Correctly Integrated:**
1. ✅ RO simulation runs correctly
2. ✅ Consumer cost metrics include RO
3. ✅ RO metrics displayed in support schemes tab
4. ✅ Revenue calculation base logic is correct (wholesale only)

## Recommended Fixes

1. **Add RO payments to generator revenues**:
   - Calculate `ro_payments_by_generator` similar to `cfd_payments_by_generator`
   - Add checkbox for "Include RO Payments"
   - Update stacked bar chart to include RO segment
   - Update revenue table to show RO payments column

2. **Add RO to capture price calculations**:
   - Calculate RO-adjusted capture price per generator
   - Update chart to show RO impact on capture prices
   - Show combined CfD+RO capture price option

