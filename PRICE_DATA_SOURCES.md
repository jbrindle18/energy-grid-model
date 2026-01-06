# Gas and Carbon Price Data Sources

## Current Values and Their Origins

### Gas Price: £50/MWh

**Current Status**: This value was **calibrated** to match expected 2025 wholesale electricity prices (£75/MWh), not directly from actual gas price data.

**2024 Reference**:
- Actual 2024: **£27.0/MWh** (Q3 2024, from DESNZ/BEIS Energy Trends)
- Source: `validation_2024.py` line 41
- Note: 2024 had unusually low gas prices

**Where to Find Actual 2025 Data**:

1. **DESNZ Energy Trends** (Quarterly):
   - URL: https://www.gov.uk/government/collections/energy-trends
   - Look for: "Fuel prices for electricity generation" or "Gas prices"
   - Published quarterly with ~3 month delay

2. **ICE NBP (National Balancing Point) Prices**:
   - URL: https://www.theice.com/products/27996665/UK-Natural-Gas-Futures
   - Daily spot and futures prices in pence per therm
   - **Conversion needed**: p/therm → £/MWh for electricity generation

3. **Conversion Formula**:
   - 1 therm = 29.3 kWh = 0.0293 MWh
   - CCGT efficiency ~50% (heat rate ~7,000 BTU/kWh)
   - To generate 1 MWh electricity, need ~2 MWh thermal = ~68 therms
   - **Rough conversion**: p/therm × 0.68 ≈ £/MWh
   - Example: 50 p/therm ≈ £34/MWh (simplified)

### Carbon Price: £60/tonne CO₂

**Current Status**: This is an **assumption** (20% increase from 2024's £50/tonne), not from actual 2025 data.

**2024 Reference**:
- Actual 2024: **£50.0/tonne CO₂** (UK ETS average, from DESNZ)
- Source: `validation_2024.py` line 42

**Where to Find Actual 2025 Data**:

1. **UK ETS Statistics (DESNZ)**:
   - URL: https://www.gov.uk/government/collections/uk-emissions-trading-scheme-uk-ets
   - Quarterly publications with average UK ETS prices
   - Look for: "UK ETS allowance prices" or "Carbon price"

2. **ICE UK ETS Futures**:
   - URL: https://www.theice.com/products/6681985/UK-Emissions-Allowance-Futures
   - Daily spot and futures prices
   - Directly in £/tonne CO₂

3. **EEX UK ETS Prices**:
   - European Energy Exchange also lists UK ETS prices
   - Daily and historical data available

## Recommended Actions

### Immediate Steps

1. **Download 2025 Gas Price Data**:
   - Check DESNZ Energy Trends Q1-Q4 2025 (when available)
   - Or use ICE NBP daily prices and calculate average
   - Convert to £/MWh for electricity generation

2. **Download 2025 Carbon Price Data**:
   - Check DESNZ UK ETS statistics for 2025
   - Or use ICE UK ETS daily prices and calculate average
   - Should be directly in £/tonne CO₂

3. **Update Model Defaults**:
   - Replace calibrated/assumed values with actual data
   - Document sources in code comments
   - Update `VALIDATION_2025.md` with actual sources

### Data Collection Script (Future)

Consider creating a script that:
- Downloads NBP prices from ICE API (if available)
- Downloads UK ETS prices from ICE API
- Converts NBP to £/MWh using proper heat rate
- Updates model defaults automatically
- Or at least provides a function to fetch and convert

## Current Assumptions vs Reality

| Parameter | Current Value | Source | Status |
|-----------|--------------|--------|--------|
| Gas Price | £50/MWh | Calibrated (to match £75/MWh wholesale) | ⚠️ Needs actual data |
| Carbon Price | £60/tonne | Assumed (20% increase from 2024) | ⚠️ Needs actual data |
| 2024 Gas | £27/MWh | DESNZ Energy Trends Q3 2024 | ✅ Actual data |
| 2024 Carbon | £50/tonne | DESNZ UK ETS average 2024 | ✅ Actual data |

## Notes

- The £50/MWh gas price was found through **calibration** (testing different values to match expected wholesale price)
- This is a reasonable approach but should be validated against actual gas price data
- The £60/tonne carbon price is a **reasonable assumption** (20% increase from 2024) but should be verified
- Both values produce accurate wholesale prices, suggesting they're in the right ballpark
- However, for documentation and transparency, actual data sources should be used

## Conversion Reference

**NBP Gas Price Conversion**:
- NBP typically quoted in: **pence per therm** (p/therm)
- CCGT heat rate: ~7,000 BTU/kWh (~50% efficiency)
- To generate 1 MWh electricity: need ~2 MWh thermal = ~68 therms
- **Formula**: £/MWh ≈ (p/therm × 0.68) / 100
- **Example**: 50 p/therm = (50 × 0.68) / 100 = £0.34/MWh thermal = ~£68/MWh electricity (at 50% efficiency)

**Note**: This is simplified. Actual conversion depends on:
- Plant efficiency (varies by plant, typically 45-55%)
- Heat rate (varies, typically 6,500-7,500 BTU/kWh)
- Gas quality and composition

