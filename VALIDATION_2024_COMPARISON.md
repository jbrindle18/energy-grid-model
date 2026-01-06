# 2024 Real-World Data vs Model Comparison

## Real-World 2024 Data
- **Solar**: 5.2% of supply (14.8 TWh)
- **Nuclear**: 14.25% of supply (40.6 TWh)
- **Low carbon total**: 65% of supply (185.2 TWh)
- **Fossil fuels**: 31.5% of supply (89.7 TWh)
- **Total supply**: 274.9 TWh

## Model Preset (Current UK 2025)
- **Solar capacity**: 15.5 GW
- **Nuclear capacity**: 6.5 GW
- **Solar capacity factor**: 11.0%
- **Nuclear capacity factor**: 70.0%

## Generation Comparison

### Solar
- **Model expected**: 15.5 GW × 0.11 × 8.76 = **14.9 TWh** ✅
- **Real-world 2024**: **14.8 TWh**
- **Difference**: +0.1 TWh (0.7% higher) - **Excellent match!**

### Nuclear
- **Model expected**: 6.5 GW × 0.70 × 8.76 = **39.9 TWh**
- **Real-world 2024**: **40.6 TWh**
- **Difference**: -0.7 TWh (1.8% lower)
- **Implied real-world capacity factor**: 40.6 / (6.5 × 8.76) = **71.3%**
- **Model uses**: 70.0%
- **Gap**: 1.3 percentage points

### Total Low-Carbon Generation
- **Model expected**: ~167.1 TWh (solar + wind + nuclear + biomass + hydro)
- **Real-world 2024**: **185.2 TWh**
- **Difference**: -18.1 TWh (9.8% lower)

## Percentage Comparison

### Solar
- **Real-world**: 14.8 TWh / 274.9 TWh = **5.4%** (reported as 5.2%)
- **Model**: 14.9 TWh / 274.9 TWh = **5.4%** ✅
- **Match**: Excellent

### Nuclear
- **Real-world**: 40.6 TWh / 274.9 TWh = **14.8%** (reported as 14.25%)
- **Model**: 39.9 TWh / 274.9 TWh = **14.5%**
- **Match**: Very close (0.3 percentage points difference)

## Potential Causes of Differences

### 1. Nuclear Capacity Factor
- Model uses **70%**, but 2024 data suggests **~71.3%**
- This accounts for ~0.7 TWh of the difference
- **Recommendation**: Consider updating to 71-72% to better match recent performance

### 2. Total Low-Carbon Generation Gap (-18.1 TWh)
Possible causes:
- **Capacity growth between 2024 and 2025**: The preset is labeled "2025" but may reflect 2024 capacity. Some capacity may have been added.
- **Missing sources**: The model may not fully account for all renewable sources (e.g., some biomass categories, small hydro, etc.)
- **Capacity factors**: Some renewable capacity factors may be slightly conservative
- **Interconnectors**: These are imports, not generation, so they don't contribute to UK generation totals

### 3. Preset Year Labeling
- The preset is labeled "Current UK (2024/2025)" but uses 2025 as the simulation year
- If actual 2024 capacity was slightly lower, this could explain some differences
- **Recommendation**: Verify if preset should reflect 2024 or 2025 capacity

## Recommendations

1. **Update nuclear capacity factor** from 70% to **71-72%** to better match 2024 performance
2. **Verify preset capacity values** match actual 2024 installed capacity (or clearly label as 2025)
3. **Review total low-carbon generation** - the 18.1 TWh gap suggests either:
   - Missing capacity in the preset
   - Conservative capacity factors
   - Year mismatch (2024 vs 2025)

## Conclusion

**Solar generation matches almost perfectly** (14.9 vs 14.8 TWh), confirming the model's solar capacity and capacity factor are accurate.

**Nuclear generation is very close** (39.9 vs 40.6 TWh), with a small gap that could be addressed by increasing the capacity factor from 70% to 71-72%.

**The percentages are accurate** when calculated against total supply, matching the real-world data closely.

The main discrepancy is in **total low-carbon generation**, which is 9.8% lower than real-world. This suggests the model may be missing some capacity or using slightly conservative capacity factors for other sources.

