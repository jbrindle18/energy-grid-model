# Interactive Visualiser Guide

## Quick Start

1. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the visualiser**:
   ```bash
   streamlit run visualiser.py
   ```

3. **Open your browser** - Streamlit will automatically open at `http://localhost:8501`

## Features

### 📊 Interactive Controls

- **Scenario Selection**: Choose from predefined scenarios with specific source documentation:
  - **Current UK (2024) - BEIS/DESNZ**: Official 2024 statistics
  - **2030 Target - Energy Security Strategy**: UK government targets (50GW offshore wind, 45-47GW solar)
  - **2035 Projection - GlobalData/Net Zero**: Industry forecasts for high-renewable pathway
  - See [PRESET_SOURCES.md](../PRESET_SOURCES.md) for detailed documentation
- **Time Period**: Simulate 1 day, 1 week, 1 month, or 1 year
- **Parameter Adjustment**: Adjust renewable penetration, total capacity, and electrification factors

### 📈 Visualizations

1. **Price Dynamics Tab**
   - Time series of wholesale prices, demand, and RE share
   - Price duration curve showing price distribution
   - Price statistics (P10, P50, P90)

2. **Merit Order Tab**
   - Interactive merit order stack showing generators by marginal cost
   - Generator fleet details table
   - Average demand overlay

3. **Revenues Tab**
   - Total revenue by generator
   - Average capture price vs wholesale price
   - Load factors and generation statistics

4. **Details Tab**
   - Complete simulation summary
   - Scenario parameters
   - Export results as CSV

## Understanding the Results

### Key Metrics

- **Average Price**: Mean wholesale price over the simulation period
- **RE Share**: Percentage of generation from renewable sources
- **Zero-Price Hours**: Hours where price was near-zero (RE oversupply)
- **Curtailment**: Renewable energy that couldn't be dispatched

### Cannibalisation Effect

As renewable penetration increases:
- Wholesale prices fall (RE has near-zero marginal cost)
- RE generators earn less because they're setting the (low) price
- This is the "cannibalisation problem" - RE competes with itself

### Merit Order

The merit order shows generators stacked by marginal cost:
- Cheapest generators (RE) are dispatched first
- Most expensive generator needed to meet demand sets the price
- Gas typically sets the price when demand exceeds RE + nuclear capacity

## Tips

- Start with shorter time periods (1 day or 1 week) for faster results
- Use 1 year simulations for comprehensive statistics
- Compare different scenarios side-by-side by running multiple simulations
- Export results to CSV for further analysis

## Troubleshooting

- **Slow performance**: Use shorter time periods or reduce total capacity
- **Import errors**: Make sure you're running from the project root directory
- **Missing visualizations**: Click "Run Simulation" in the sidebar first

