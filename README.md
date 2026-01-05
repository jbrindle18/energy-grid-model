# UK Energy Grid Model

> **⚠️ Beta Version**: This model is currently in beta. While it accurately captures core market dynamics, it is a simplified representation with known limitations. Results should be interpreted with caution and not used for investment or policy decisions.

A Python simulation of UK wholesale electricity market dynamics, exploring how renewable energy penetration affects pricing, generator revenues, and consumer costs.

**Based on research from:** *"Profit vs the Planet: Is the UK's market-based electricity decarbonisation strategy feasible?"* - University of Sheffield

## The Core Paradox

> As renewable energy capacity grows, wholesale electricity prices fall. But consumer bills don't. Why?

This model explores the **subsidy spiral** - how Contracts for Difference (CfDs) create rising consumer costs even as renewable energy gets "cheaper".

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/energy-grid-model.git
cd energy-grid-model

# Install dependencies
pip install -r requirements.txt

# Run the interactive visualiser
streamlit run visualiser.py
```

Then open http://localhost:8501 in your browser.

## What This Model Does

### Merit Order Dispatch
Simulates how UK wholesale electricity markets work:
1. Generators are dispatched cheapest-first (solar/wind -> nuclear -> gas)
2. The most expensive generator needed sets the price for ALL generators
3. This explains why gas prices affect electricity bills even when renewables dominate

### CfD Economics
Models Contracts for Difference - the UK's main renewable subsidy mechanism:
- **Strike prices**: Guaranteed price to generators
- **Top-up payments**: Consumers pay when wholesale < strike (subsidy)
- **Clawback**: Generators pay back when wholesale > strike

### Key Metrics
- **Wholesale Price**: Market clearing price
- **Consumer Price**: Wholesale + CfD levy (what you actually pay)
- **Cannibalisation**: How RE generators earn less as RE grows
- **Curtailment**: RE that can't be used (no storage modelled)

## Interactive Visualiser

The Streamlit app provides:

- **6 tabs**: Price Dynamics, Merit Order, Revenues, CfD Economics, Details, About
- **Preset scenarios**: Current UK, 2030 targets, NESO projections, 2050 pathways
- **Custom controls**: Adjust capacity for each fuel type, gas prices, CfD strike prices
- **Real-time simulation**: See how changes affect prices and costs

## Project Structure

```
energy-grid-model/
├── src/
│   ├── generators.py   # Generator types (solar, wind, gas, nuclear, etc.)
│   ├── grid.py         # Merit order dispatch algorithm
│   ├── demand.py       # UK demand profiles
│   ├── pricing.py      # Price analysis & cannibalisation metrics
│   └── cfd.py          # Contracts for Difference economics
├── notebooks/
│   ├── 01_basic_dispatch.ipynb    # Learn how dispatch works
│   ├── 02_price_dynamics.ipynb    # Explore RE penetration effects
│   └── 03_cfd_economics.ipynb     # CfD and the subsidy spiral
├── tests/              # 47 unit tests
├── visualiser.py       # Interactive Streamlit app
└── blog_post_draft.md  # Explainer article
```

## Key Findings

| Scenario | RE Share | Wholesale Price | Consumer Price | CfD Status |
|----------|----------|-----------------|----------------|------------|
| Current UK | ~35% | £82/MWh | £75/MWh | Clawback |
| 2030 Targets | ~65% | £45/MWh | £55/MWh | Subsidy |
| High RE | ~85% | £18/MWh | £52/MWh | Large Subsidy |

As wholesale prices fall, CfD costs rise to compensate generators - the subsidy spiral.

## Caveats & Limitations

This model is **educational**, not a forecasting tool. It does NOT include:

- Curtailment payments (~£3bn/year projected)
- Battery storage (23-27 GW expected by 2030)
- Demand-side response
- Negative pricing
- Network constraints
- Balancing mechanism

See the "About" tab in the visualiser for detailed caveats.

## Data Sources

- **Capacity data**: BEIS/DESNZ Energy Statistics 2024
- **CfD strike prices**: Low Carbon Contracts Company (LCCC)
- **Capacity factors**: BEIS historical averages
- **Scenario presets**: NESO Clean Power 2030, UK Government targets

See [PRESET_SOURCES.md](PRESET_SOURCES.md) for detailed documentation.

## Running Tests

```bash
pytest tests/ -v
```

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions welcome! Please open an issue first to discuss proposed changes.

## Acknowledgments

- Brett Christophers, *The Price is Wrong: Why Capitalism Won't Save the Planet*
- NESO (formerly National Grid ESO) for scenario data
- BEIS/DESNZ for UK energy statistics
