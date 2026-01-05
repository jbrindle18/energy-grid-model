# Preset Scenario Sources and Documentation

This document details the sources and assumptions for each preset scenario in the energy grid model visualiser.

## Current UK (2024/2025) - BEIS/DESNZ Statistics

**Source:** UK Department for Energy Security and Net Zero (DESNZ) Energy Trends, 2024 data

**Capacity Values (GW):**
- Solar: 15.5 GW
- Onshore Wind: 14.8 GW
- Offshore Wind: 14.7 GW
- Nuclear: 6.5 GW
- Biomass: 3.5 GW
- Hydro: 1.9 GW
- Interconnectors: 8.4 GW
- Gas: ~32 GW (auto-calculated based on demand)

**Total Renewable Capacity:** ~45 GW  
**Total Capacity:** ~97 GW  
**Renewable Share:** ~46%

**Electrification Factor:** 1.0 (baseline, no growth)

**References:**
- DESNZ Energy Trends: https://www.gov.uk/government/collections/energy-trends
- BEIS Energy Statistics: https://www.gov.uk/government/statistics/energy-trends

---

## 2030 Target - UK Government Energy Security Strategy

**Source:** UK Government Energy Security Strategy (2022) and related policy documents

**Official Targets:**
- Offshore Wind: **50 GW by 2030** (including up to 5 GW floating)
- Solar PV: **45-47 GW by 2030** (Solar Roadmap target)
- Nuclear: ~9-10 GW (Sizewell C and other projects)

**Preset Values (GW):**
- Solar: 21.0 GW (conservative estimate, well below 45-47 GW target to account for deployment timeline and grid constraints)
- Onshore Wind: 25.2 GW (estimated growth from current 14.8 GW, ~70% increase)
- Offshore Wind: 37.8 GW (below 50 GW target to reflect realistic deployment pace; target may be ambitious)
- Nuclear: 10.0 GW (includes Sizewell C and other projects)
- Biomass: 2.4 GW (slight reduction, focus shifts to wind/solar)
- Hydro: 1.9 GW (unchanged, limited expansion potential)
- Interconnectors: 1.6 GW (reduced, focus on domestic capacity expansion)

**Note on Conservative Estimates:** These values are intentionally conservative to reflect:
- Grid connection delays
- Planning and consenting timelines
- Supply chain constraints
- Realistic deployment rates vs. aspirational targets

**Total Renewable Capacity:** ~84 GW  
**Total Capacity:** ~120 GW  
**Renewable Share:** ~70%

**Electrification Factor:** 1.2 (20% demand growth from EVs, heat pumps)

**References:**
- UK Energy Security Strategy: https://www.gov.uk/government/publications/british-energy-security-strategy
- Solar Roadmap: https://www.gov.uk/government/publications/solar-roadmap
- House of Commons Library: https://commonslibrary.parliament.uk/where-will-britains-future-energy-supply-come-from/

**Note:** These values are conservative estimates. The 50 GW offshore wind target may not be fully achieved by 2030, so this preset uses a more realistic deployment scenario.

---

## 2030 NESO - Further Flex and Renewables Scenario

**Source:** NESO (National Energy System Operator) Clean Power 2030 Report, Table 1 (Published 5 November 2024)

**Scenario Description:** This scenario emphasizes further flexibility and renewable capacity expansion, with higher offshore wind deployment and lower nuclear capacity.

**Preset Values (GW) - from NESO Table 1:**
- Solar: 47.4 GW
- Onshore Wind: 27.3 GW
- Offshore Wind: 50.6 GW
- Nuclear: 3.5 GW
- Biomass/BECCS: 4.0 GW
- Hydro: 2.5 GW (split from "Other renewables" 5.7 GW total)
- Interconnectors: 12.5 GW

**Total Renewable Capacity:** ~132 GW  
**Total Capacity:** ~160 GW  
**Renewable Share:** ~82%

**Electrification Factor:** 1.2 (20% demand growth)

**References:**
- NESO Clean Power 2030 Report: https://www.neso.energy/clean-power-2030
- Table 1: Changes in generation from 2023 to 2030 (Installed Capacities)

**Note:** This scenario prioritizes renewable expansion and flexibility solutions (batteries, LDES) over new dispatchable capacity. Nuclear capacity decreases from 6.1 GW (2023) to 3.5 GW (2030) as older plants retire.

---

## 2030 NESO - New Dispatch Scenario

**Source:** NESO (National Energy System Operator) Clean Power 2030 Report, Table 1 (Published 5 November 2024)

**Scenario Description:** This scenario emphasizes new dispatchable low-carbon capacity, with slightly lower offshore wind but higher nuclear and low-carbon dispatchable power.

**Preset Values (GW) - from NESO Table 1:**
- Solar: 47.4 GW
- Onshore Wind: 27.3 GW
- Offshore Wind: 43.1 GW (lower than Further Flex scenario)
- Nuclear: 4.1 GW
- Biomass/BECCS: 3.8 GW
- Hydro: 2.5 GW (split from "Other renewables" 5.7 GW total)
- Interconnectors: 12.5 GW

**Total Renewable Capacity:** ~125 GW  
**Total Capacity:** ~160 GW  
**Renewable Share:** ~78%

**Electrification Factor:** 1.2 (20% demand growth)

**References:**
- NESO Clean Power 2030 Report: https://www.neso.energy/clean-power-2030
- Table 1: Changes in generation from 2023 to 2030 (Installed Capacities)

**Note:** This scenario includes 2.7 GW of "Low carbon dispatchable power" (not separately modeled in this preset). The scenario balances renewable expansion with maintaining more dispatchable capacity for grid stability.

---

## 2030 UK Government - Clean Power Targets

**Source:** UK Government Clean Power 2030 Action Plan (Published 13 December 2024)

**Official Government Targets:**
- Solar PV: **50 GW by 2030**
- Offshore Wind: **55 GW by 2030**
- Onshore Wind: **35 GW by 2030**
- Renewable Hydrogen Production: **10 GW** (not modeled in this preset)
- At least **95% low-carbon generation** by 2030

**Preset Values (GW):**
- Solar: 50.0 GW (official government target)
- Onshore Wind: 35.0 GW (official government target)
- Offshore Wind: 55.0 GW (official government target)
- Nuclear: 10.0 GW
- Biomass: 2.4 GW
- Hydro: 1.9 GW
- Interconnectors: 8.4 GW (maintain current capacity)

**Total Renewable Capacity:** ~140 GW  
**Total Capacity:** ~170 GW  
**Renewable Share:** ~82%

**Electrification Factor:** 1.2 (20% demand growth)

**References:**
- Clean Power 2030 Action Plan: https://www.gov.uk/government/publications/clean-power-2030-action-plan
- Technical Annex: https://www.gov.uk/government/publications/clean-power-2030-action-plan/clean-power-2030-action-plan-a-new-era-of-clean-electricity-technical-annex
- S&P Global Analysis: https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/110524-uk-system-operator-details-formidable-challenge-of-reaching-clean-power-by-2030

**Note:** These are the official government targets. Achieving these will require significant investment (~£40 billion annually 2025-2030 according to NESO) and may face deployment challenges. This preset represents the most ambitious 2030 scenario.

---

## 2035 Target - GlobalData Projections & Net Zero Pathway

**Source:** GlobalData renewable energy capacity forecasts and UK Net Zero Strategy projections

**Projections:**
- Total Renewable Capacity: **172.7 GW by 2035** (GlobalData forecast)
- Offshore Wind: **~58.3 GW by 2035** (GlobalData)
- Nuclear: **9 GW by 2035** (government projections)

**Preset Values (GW):**
- Solar: 35.6 GW (estimated growth trajectory)
- Onshore Wind: 42.8 GW (significant expansion)
- Offshore Wind: 64.1 GW (exceeds GlobalData projection, includes floating wind)
- Nuclear: 10.0 GW
- Biomass: 2.4 GW
- Hydro: 1.9 GW
- Interconnectors: 1.6 GW

**Total Renewable Capacity:** ~142.5 GW  
**Total Capacity:** ~178 GW  
**Renewable Share:** ~80%

**Electrification Factor:** 1.5 (50% demand growth from full electrification)

**References:**
- GlobalData UK Renewable Power Capacity Forecast: https://www.globaldata.com/media/power/uk-renewable-power-capacity-reach-172-7gw-2035-forecasts-globaldata/
- UK Net Zero Strategy: https://www.gov.uk/government/publications/net-zero-strategy
- National Grid ESO Future Energy Scenarios: https://www.nationalgrideso.com/future-energy/future-energy-scenarios

**Note:** This scenario represents a high-renewable pathway but does not reach 95% RE share as mentioned in some documentation. The actual RE share is ~80%, which is more realistic for a decarbonised grid that still requires dispatchable backup capacity.

---

## 2050 NESO - Holistic Transition Scenario

**Source:** NESO Future Energy Scenarios 2025 Data Workbook (Published 2025)

**Scenario Description:** The Holistic Transition pathway achieves net zero through a combination of electrification and hydrogen, with significant consumer engagement in energy efficiency and demand flexibility. This is NESO's main net-zero pathway.

**Preset Values (GW) - from NESO FES 2025 Data Workbook:**
- Solar PV: 97.0 GW
- Onshore Wind: 47.5 GW
- Offshore Wind: 103.9 GW
- Nuclear: 14.2 GW
- Biomass: 4.5 GW (main biomass; CCS Biomass 0.6 GW not separately modeled)
- Hydro: 2.0 GW (split from "Other Renewables" 5.08 GW total: ~2.0 hydro, ~3.08 other)
- Interconnectors: 16.5 GW

**Total Renewable Capacity:** ~255 GW  
**Total Capacity:** ~290 GW  
**Renewable Share:** ~88%

**Electrification Factor:** 1.8 (80% demand growth from full electrification by 2050)

**References:**
- NESO Future Energy Scenarios 2025 Data Workbook: `research/Future Energy Scenarios 2025 Data Workbook V005_0.xlsx`
- Sheets: F.55 (Offshore Wind), F.56 (Onshore Wind), F.57 (Solar PV), F.62 (Nuclear), F.70 (Biomass), F.12 (Summary)
- NESO FES 2025: https://www.neso.energy/future-energy/future-energy-scenarios

**Note:** This represents a fully decarbonised grid by 2050. The Holistic Transition scenario balances renewable expansion with maintaining dispatchable capacity (nuclear, biomass) for grid stability. Offshore wind becomes the dominant generation source at over 100 GW.

---

## Gas Capacity Calculation

Gas capacity is automatically calculated to ensure grid stability:

```
Required Dispatchable = (Peak Demand - Min RE Available) × 1.1

Where:
- Peak Demand = Base Peak (50 GW) × Electrification Factor
- Min RE Available = RE Capacity × 0.08 (worst-case wind output)
- 1.1 = 10% safety margin
```

This ensures the grid can meet demand even when renewables are at minimum output.

---

## Assumptions and Limitations

1. **Capacity Factors:** Based on UK averages (Solar 11%, Onshore Wind 27%, Offshore Wind 40%)

2. **Gas Marginal Cost:** Includes fuel cost (£55/MWh), carbon price (£60/tonne), and O&M (£3/MWh)

3. **Demand Growth:** Electrification factors account for:
   - Electric vehicle adoption
   - Heat pump deployment
   - Industrial electrification
   - Data center growth

4. **Interconnectors:** Modeled as imports only (simplified). Real interconnectors can flow both ways.

5. **Storage:** Not explicitly modeled in these presets (future enhancement).

---

## Data Quality Notes

- **Current UK:** Based on official 2024 statistics - high confidence
- **2030 Target:** Based on government targets but uses conservative deployment estimates - medium confidence
- **2035 Target:** Based on industry projections and forecasts - lower confidence (longer time horizon)

All values should be updated as new official data becomes available.

---

## Other Organizations' Projections

Several other organizations have published detailed scenarios for a decarbonized UK grid. These could serve as additional preset options or reference points:

### National Energy System Operator (NESO) - Future Energy Scenarios

**Source:** NESO (formerly National Grid ESO) Future Energy Scenarios (FES) 2025

**Key Scenarios:**
- **Holistic Transition:** Achieves net zero through electrification and hydrogen
- **Electric Engagement:** Focuses on electrified demand (heat pumps, EVs)
- **Hydrogen Evolution:** Emphasizes rapid hydrogen adoption

**Clean Power 2030 Recommendations:**
- Solar: **47 GW by 2030** (4.6 GW annual deployment from 2025)
- Battery Storage: **23-27 GW by 2030** (from 5 GW in 2023)
- Offshore Wind: Cornerstone of clean power system
- Solar + Onshore Wind: Expected to contribute 29% of generation

**References:**
- NESO Future Energy Scenarios: https://www.neso.energy/future-energy/future-energy-scenarios
- Clean Power 2030 Report: https://www.neso.energy/clean-power-2030
- Cost Analysis: https://www.neso.energy/britains-energy-system-operator-publishes-cost-analysis-decarbonisation-pathways

### Climate Change Committee (CCC) - Sixth Carbon Budget

**Source:** CCC Sixth Carbon Budget (December 2020)

**Balanced Pathway Scenario:**
- Offshore Wind: 40 GW by 2030, 100 GW by 2050
- Significant expansion of onshore wind and solar
- Comprehensive analysis of net-zero pathway by 2050

**References:**
- Sixth Carbon Budget: https://www.theccc.org.uk/publication/sixth-carbon-budget/

### UK Government - Clean Power 2030 Action Plan

**Source:** UK Government Clean Power 2030 Action Plan (Published 13 December 2024)

**Official Targets:**
- Offshore Wind: **55 GW by 2030**
- Solar PV: **50 GW by 2030**
- Onshore Wind: **35 GW by 2030**
- Renewable Hydrogen Production: **10 GW**
- At least **95% low-carbon generation** by 2030

**Flexible Low-Carbon Technologies:**
- Pumped hydro storage
- Gas with CCUS (Carbon Capture, Usage and Storage)
- Hydrogen-to-power
- Liquid air energy storage

**References:**
- Clean Power 2030 Action Plan: https://www.gov.uk/government/publications/clean-power-2030-action-plan
- Technical Annex: https://www.gov.uk/government/publications/clean-power-2030-action-plan/clean-power-2030-action-plan-a-new-era-of-clean-electricity-technical-annex

### Electricity Networks Strategic Framework

**Source:** UK Government (2024)

**Projections:**
- Electricity demand: **40-50% increase by 2035** (vs 2020)
- Renewable capacity: **175-240 GW by 2050**
- Generation: **475-585 TWh by 2050**
- Solar: Up to **70 GW by 2035**

**References:**
- Electricity Networks Strategic Framework: https://www.gov.uk/government/publications/electricity-networks-strategic-framework

### Energy Transitions Commission (ETC)

**Source:** ETC Power Systems Transformation Report

**Key Findings:**
- Cost per kWh of zero-carbon system in 2030: **20-40% higher** than 2050 cost
- Emphasizes optimal pace assessment for decarbonization

**References:**
- ETC Report: https://www.energy-transitions.org/wp-content/uploads/2025/07/Power-Systems-Transformation_Main-report_vf.pdf

### Comparison Summary

| Organization | 2030 Solar | 2030 Offshore Wind | 2030 Onshore Wind | Notes |
|-------------|------------|-------------------|-------------------|-------|
| **UK Government (Clean Power 2030)** | 50 GW | 55 GW | 35 GW | Official targets |
| **NESO Further Flex & Renewables** | 47.4 GW | 50.6 GW | 27.3 GW | From NESO Table 1 |
| **NESO New Dispatch** | 47.4 GW | 43.1 GW | 27.3 GW | From NESO Table 1 |
| **Energy Security Strategy Preset** | 21 GW | 37.8 GW | 25.2 GW | Conservative estimates |
| **CCC Balanced Pathway** | - | 40 GW | - | By 2030 |

**Preset Comparison:**
- **Energy Security Strategy**: Conservative, realistic deployment estimates
- **NESO Further Flex & Renewables**: Emphasizes renewable expansion and flexibility (from NESO Table 1)
- **NESO New Dispatch**: Balances renewables with dispatchable capacity (from NESO Table 1)
- **UK Government Clean Power 2030**: Official aspirational targets, most ambitious

**Note:** The current presets use conservative estimates that are below official targets to account for realistic deployment constraints. NESO's recommendations align closely with government targets but may be more achievable given their system planning expertise.

