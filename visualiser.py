"""
Interactive Visualiser for UK Energy Grid Model

A Streamlit app for exploring electricity market dynamics, renewable energy
penetration effects, and pricing patterns.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.grid import (
        Grid, DispatchResult, SimulationSummary,
        create_uk_grid, create_scenario_grid
    )
    from src.generators import (
        create_uk_current_fleet,
        SolarGenerator, OnshoreWindGenerator, OffshoreWindGenerator,
        NuclearGenerator, BiomassGenerator, HydroGenerator,
        GasGenerator, InterconnectorImport
    )
    from src.demand import create_uk_demand_profile, create_future_demand_profile
    from src.pricing import (
        PriceDurationCurve,
        calculate_generator_revenues
    )
    from src.cfd import (
        CfDContract, CfDPortfolio, LCCCSimulationResult,
        simulate_cfd_costs, create_cfd_portfolio_for_fleet, create_cfd_portfolio_from_state,
        CURRENT_STRIKE_PRICES, UK_CFD_STRIKE_PRICES,
        estimate_project_viability, PROJECT_COSTS
    )
    from src.ro import (
        ROPortfolio, ROPortfolioState, ROSimulationResult,
        simulate_ro_costs, create_ro_portfolio_from_state, get_ro_portfolio_state,
        DEFAULT_ROC_VALUE, simulate_combined_support, CombinedSupportResult
    )
    from src.ro_portfolio import (
        create_ro_portfolio_with_estimates, RO_FINAL_EXPIRY_YEAR, RO_CLOSURE_YEAR
    )
    from src.constants import (
        UK_BASE_PEAK_DEMAND_GW, GAS_EMISSIONS_FACTOR, GAS_VARIABLE_OM
    )
    from src.validation import (
        validate_capacities, validate_demand_parameters,
        validate_gas_parameters, validate_cfd_parameters
    )
    from src.capacity_planning import (
        calculate_required_gas_capacity, calculate_total_capacity
    )
    from src.cfd_portfolio import (
        CfDPortfolio as HistoricalCfDPortfolio,
        create_portfolio_with_projections
    )
except ImportError:
    # Fallback for direct execution
    from grid import (
        Grid, DispatchResult, SimulationSummary,
        create_uk_grid, create_scenario_grid
    )
    from generators import (
        create_uk_current_fleet,
        SolarGenerator, OnshoreWindGenerator, OffshoreWindGenerator,
        NuclearGenerator, BiomassGenerator, HydroGenerator,
        GasGenerator, InterconnectorImport
    )
    from demand import create_uk_demand_profile, create_future_demand_profile
    from pricing import (
        PriceDurationCurve,
        calculate_generator_revenues
    )
    from cfd import (
        CfDContract, CfDPortfolio, LCCCSimulationResult,
        simulate_cfd_costs, create_cfd_portfolio_for_fleet, create_cfd_portfolio_from_state,
        CURRENT_STRIKE_PRICES, UK_CFD_STRIKE_PRICES,
        estimate_project_viability, PROJECT_COSTS
    )
    from ro import (
        ROPortfolio, ROPortfolioState, ROSimulationResult,
        simulate_ro_costs, create_ro_portfolio_from_state, get_ro_portfolio_state,
        DEFAULT_ROC_VALUE, simulate_combined_support, CombinedSupportResult
    )
    from ro_portfolio import (
        create_ro_portfolio_with_estimates, RO_FINAL_EXPIRY_YEAR, RO_CLOSURE_YEAR
    )
    from constants import (
        UK_BASE_PEAK_DEMAND_GW, GAS_EMISSIONS_FACTOR, GAS_VARIABLE_OM
    )
    from validation import (
        validate_capacities, validate_demand_parameters,
        validate_gas_parameters, validate_cfd_parameters
    )
    from capacity_planning import (
        calculate_required_gas_capacity, calculate_total_capacity
    )
    from cfd_portfolio import (
        CfDPortfolio as HistoricalCfDPortfolio,
        create_portfolio_with_projections
    )

# Page configuration
st.set_page_config(
    page_title="UK Energy Grid Visualiser",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Wider sidebar */
    [data-testid="stSidebar"] {
        min-width: 340px;
        max-width: 340px;
    }
    [data-testid="stSidebar"] > div:first-child {
        width: 340px;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">⚡ UK Energy Grid Model Visualiser</p>', unsafe_allow_html=True)
st.markdown("Explore how renewable energy penetration affects wholesale electricity prices, generator revenues, and consumer costs")

# Beta notice
st.info("""
**⚠️ Beta Version**: This model is currently in beta. While it accurately captures core market dynamics, 
it is a simplified representation with known limitations. Results should be interpreted with caution 
and not used for investment or policy decisions. Feedback welcome: [joe@joebrindle.uk](mailto:joe@joebrindle.uk)
""")

# Sidebar controls
st.sidebar.header("⚙️ Simulation Controls")

# Preset dropdown
st.sidebar.subheader("📋 Presets")
preset_options = {
    "Current UK (2024) - BEIS/DESNZ": "current",
    "2030 NESO - New Dispatch": "neso_dispatch",
    "2050 NESO - Holistic Transition": "neso2050"
}

selected_preset = st.sidebar.selectbox(
    "Select Preset",
    options=list(preset_options.keys()),
    index=0,  # Default to "Current UK"
    help="Choose a preset. These are broadly based on some different models of future, renewable-heavy grids, but they need some refinement."
)

preset_value = preset_options[selected_preset]

# Convert dropdown selection to boolean flags for compatibility
preset_current = (preset_value == "current")
preset_neso_dispatch = (preset_value == "neso_dispatch")
preset_neso2050 = (preset_value == "neso2050")

# Initialize session state for slider values (default to Current UK values)
if "solar_cap" not in st.session_state:
    st.session_state.solar_cap = 15.5
if "solar_slider" not in st.session_state:
    st.session_state.solar_slider = 15.5
if "onshore_wind_cap" not in st.session_state:
    st.session_state.onshore_wind_cap = 14.8
if "onshore_slider" not in st.session_state:
    st.session_state.onshore_slider = 14.8
if "offshore_wind_cap" not in st.session_state:
    st.session_state.offshore_wind_cap = 14.7
if "offshore_slider" not in st.session_state:
    st.session_state.offshore_slider = 14.7
if "nuclear_cap" not in st.session_state:
    st.session_state.nuclear_cap = 6.5
if "nuclear_slider" not in st.session_state:
    st.session_state.nuclear_slider = 6.5
if "biomass_cap" not in st.session_state:
    st.session_state.biomass_cap = 3.5
if "biomass_slider" not in st.session_state:
    st.session_state.biomass_slider = 3.5
if "hydro_cap" not in st.session_state:
    st.session_state.hydro_cap = 1.9
if "hydro_slider" not in st.session_state:
    st.session_state.hydro_slider = 1.9
if "interconnector_cap" not in st.session_state:
    st.session_state.interconnector_cap = 8.4
if "interconnector_slider" not in st.session_state:
    st.session_state.interconnector_slider = 8.4
if "electrification" not in st.session_state:
    st.session_state.electrification = 1.0
if "electrification_slider" not in st.session_state:
    st.session_state.electrification_slider = 1.0
if "gas_price" not in st.session_state:
    st.session_state.gas_price = 73.0  # £/MWh - total gas wholesale price (calibrated for 2025)
if "gas_price_slider" not in st.session_state:
    st.session_state.gas_price_slider = 73.0  # £/MWh - total gas wholesale price (calibrated for 2025)

# Track last selected preset to only apply when it changes
if "last_selected_preset" not in st.session_state:
    st.session_state.last_selected_preset = None

# Apply presets - only update when preset selection changes
if st.session_state.last_selected_preset != selected_preset:
    st.session_state.last_selected_preset = selected_preset
    
    if preset_current:
        # Current UK (2024/2025) - BEIS/DESNZ Statistics
        # Based on official 2024 installed capacity data
        # Gas price calibrated to £50/MWh for 2025 validation (see VALIDATION_2025.md)
        # See PRESET_SOURCES.md for detailed documentation
        st.session_state.solar_cap = 15.5
        st.session_state.solar_slider = 15.5
        st.session_state.onshore_wind_cap = 14.8
        st.session_state.onshore_slider = 14.8
        st.session_state.offshore_wind_cap = 14.7
        st.session_state.offshore_slider = 14.7
        st.session_state.nuclear_cap = 6.5
        st.session_state.nuclear_slider = 6.5
        st.session_state.biomass_cap = 3.5
        st.session_state.biomass_slider = 3.5
        st.session_state.hydro_cap = 1.9
        st.session_state.hydro_slider = 1.9
        st.session_state.interconnector_cap = 8.4
        st.session_state.interconnector_slider = 8.4
        st.session_state.electrification = 1.0
        st.session_state.electrification_slider = 1.0
        # Gas price calibrated for 2025: £73/MWh (validated against expected £75/MWh wholesale price)
        st.session_state.gas_price = 73.0
        st.session_state.gas_price_slider = 73.0
        st.session_state.simulation_year = 2025  # CfD portfolio year
        st.rerun()

    elif preset_neso_dispatch:
        # 2030 NESO - New Dispatch Scenario
        # Based on NESO Clean Power 2030 report Table 1 (Published 5 November 2024)
        # "New Dispatch" scenario emphasizes new dispatchable low-carbon capacity
        # See PRESET_SOURCES.md for detailed documentation
        st.session_state.solar_cap = 47.4
        st.session_state.solar_slider = 47.4
        st.session_state.onshore_wind_cap = 27.3
        st.session_state.onshore_slider = 27.3
        st.session_state.offshore_wind_cap = 43.1
        st.session_state.offshore_slider = 43.1
        st.session_state.nuclear_cap = 4.1
        st.session_state.nuclear_slider = 4.1
        st.session_state.biomass_cap = 3.8
        st.session_state.biomass_slider = 3.8
        st.session_state.hydro_cap = 2.5  # Split from "Other renewables" (5.7 GW total: ~2.5 hydro, ~3.2 other)
        st.session_state.hydro_slider = 2.5
        st.session_state.interconnector_cap = 12.5
        st.session_state.interconnector_slider = 12.5
        st.session_state.electrification = 1.2
        st.session_state.electrification_slider = 1.2
        st.session_state.gas_price = 73.0  # Same as 2025 - gas prices are unpredictable
        st.session_state.gas_price_slider = 73.0
        st.session_state.simulation_year = 2030  # CfD portfolio year
        st.rerun()

    elif preset_neso2050:
        # 2050 NESO - Holistic Transition Scenario
        # Based on NESO Future Energy Scenarios 2025 Data Workbook
        # Extracted from F.55, F.56, F.57, F.62, F.70, F.12 sheets
        # See PRESET_SOURCES.md for detailed documentation
        st.session_state.solar_cap = 97.0
        st.session_state.solar_slider = 97.0
        st.session_state.onshore_wind_cap = 47.5
        st.session_state.onshore_slider = 47.5
        st.session_state.offshore_wind_cap = 103.9
        st.session_state.offshore_slider = 103.9
        st.session_state.nuclear_cap = 14.2
        st.session_state.nuclear_slider = 14.2
        st.session_state.biomass_cap = 4.5  # Main biomass (CCS Biomass 0.6 GW not separately modeled)
        st.session_state.biomass_slider = 4.5
        st.session_state.hydro_cap = 2.0  # Split from "Other Renewables" (5.08 GW total: ~2.0 hydro, ~3.08 other)
        st.session_state.hydro_slider = 2.0
        st.session_state.interconnector_cap = 16.5
        st.session_state.interconnector_slider = 16.5
        st.session_state.electrification = 1.8  # Higher electrification by 2050
        st.session_state.electrification_slider = 1.8
        st.session_state.gas_price = 73.0  # Same as 2025 - gas prices are unpredictable
        st.session_state.gas_price_slider = 73.0
        st.session_state.simulation_year = 2050  # CfD portfolio year
        st.rerun()

# Capacity section - collapsible
with st.sidebar.expander("⚡ Capacity (GW)", expanded=False):
    # Individual capacity sliders for each fuel source
    solar_capacity = st.slider(
        "Solar",
        min_value=0.0,
        max_value=150.0,
        step=1.0,
        key="solar_slider"
    )
    st.session_state.solar_cap = st.session_state.solar_slider

    onshore_wind_capacity = st.slider(
        "Onshore Wind",
        min_value=0.0,
        max_value=150.0,
        step=1.0,
        key="onshore_slider"
    )
    st.session_state.onshore_wind_cap = st.session_state.onshore_slider

    offshore_wind_capacity = st.slider(
        "Offshore Wind",
        min_value=0.0,
        max_value=150.0,
        step=1.0,
        key="offshore_slider"
    )
    st.session_state.offshore_wind_cap = st.session_state.offshore_slider

    nuclear_capacity = st.slider(
        "Nuclear",
        min_value=0.0,
        max_value=50.0,
        step=1.0,
        key="nuclear_slider"
    )
    st.session_state.nuclear_cap = st.session_state.nuclear_slider

    biomass_capacity = st.slider(
        "Biomass",
        min_value=0.0,
        max_value=50.0,
        step=0.5,
        key="biomass_slider"
    )
    st.session_state.biomass_cap = st.session_state.biomass_slider

    hydro_capacity = st.slider(
        "Hydro",
        min_value=0.0,
        max_value=50.0,
        step=0.5,
        key="hydro_slider"
    )
    st.session_state.hydro_cap = st.session_state.hydro_slider

    interconnector_capacity = st.slider(
        "Interconnectors",
        min_value=0.0,
        max_value=50.0,
        step=1.0,
        key="interconnector_slider"
    )
    st.session_state.interconnector_cap = st.session_state.interconnector_slider

    electrification = st.slider(
        "Electrification Factor",
        min_value=0.8,
        max_value=2.0,
        step=0.1,
        help="Demand multiplier (1.3 = 30% increase)",
        key="electrification_slider"
    )
    st.session_state.electrification = st.session_state.electrification_slider

    # Calculate gas capacity and total capacity using helper functions
    gas_capacity = calculate_required_gas_capacity(
        solar_capacity_gw=solar_capacity,
        onshore_wind_capacity_gw=onshore_wind_capacity,
        offshore_wind_capacity_gw=offshore_wind_capacity,
        nuclear_capacity_gw=nuclear_capacity,
        biomass_capacity_gw=biomass_capacity,
        hydro_capacity_gw=hydro_capacity,
        interconnector_capacity_gw=interconnector_capacity,
        electrification_factor=electrification,
        base_peak_demand_gw=UK_BASE_PEAK_DEMAND_GW
    )

    # Calculate total capacity
    re_capacity_total = solar_capacity + onshore_wind_capacity + offshore_wind_capacity
    total_capacity_gw = calculate_total_capacity(
        solar_capacity_gw=solar_capacity,
        onshore_wind_capacity_gw=onshore_wind_capacity,
        offshore_wind_capacity_gw=offshore_wind_capacity,
        nuclear_capacity_gw=nuclear_capacity,
        biomass_capacity_gw=biomass_capacity,
        hydro_capacity_gw=hydro_capacity,
        interconnector_capacity_gw=interconnector_capacity,
        gas_capacity_gw=gas_capacity
    )

    # Calculate peak demand for display
    peak_demand_gw = UK_BASE_PEAK_DEMAND_GW * electrification

    # Summary metrics inside expander
    st.markdown("---")
    cap_col1, cap_col2 = st.columns(2)
    with cap_col1:
        st.metric("Total Capacity", f"{total_capacity_gw:.0f} GW")
    with cap_col2:
        st.metric("Gas CCGT", f"{gas_capacity:.1f} GW")

# Gas price section - collapsible
with st.sidebar.expander("🔥 Gas Pricing", expanded=False):
    gas_price = st.slider(
        "Gas Wholesale Price (£/MWh)",
        min_value=30.0,
        max_value=200.0,
        step=5.0,
        help="Total gas wholesale price (includes fuel cost, carbon costs, and variable O&M)",
        key="gas_price_slider"
    )
    st.session_state.gas_price = st.session_state.gas_price_slider

# Calculate RE penetration
re_penetration = re_capacity_total / total_capacity_gw if total_capacity_gw > 0 else 0
    
# Store custom capacities for later use
custom_capacities = {
    'solar': solar_capacity,
    'onshore_wind': onshore_wind_capacity,
    'offshore_wind': offshore_wind_capacity,
    'nuclear': nuclear_capacity,
    'biomass': biomass_capacity,
    'hydro': hydro_capacity,
    'interconnectors': interconnector_capacity,
    'gas': gas_capacity
}

# Calculate RE penetration for display
re_penetration = (solar_capacity + onshore_wind_capacity + offshore_wind_capacity) / total_capacity_gw if total_capacity_gw > 0 else 0

# Initialize CfD session state (before expander)
if "simulation_year" not in st.session_state:
    st.session_state.simulation_year = 2025
if "cfd_price_mode" not in st.session_state:
    st.session_state.cfd_price_mode = "Portfolio (Historical)"
if "cfd_solar_strike" not in st.session_state:
    st.session_state.cfd_solar_strike = 69.0
if "cfd_onshore_strike" not in st.session_state:
    st.session_state.cfd_onshore_strike = 58.0
if "cfd_offshore_strike" not in st.session_state:
    st.session_state.cfd_offshore_strike = 71.0
if "cfd_coverage" not in st.session_state:
    st.session_state.cfd_coverage = 0.8

# CfD Settings section - collapsible
with st.sidebar.expander("📊 CfD Portfolio Settings", expanded=False):
    # Simulation Year
    simulation_year = st.slider(
        "Simulation Year",
        min_value=2025,
        max_value=2050,
        value=st.session_state.simulation_year,
        help="Year to simulate. Affects which CfD contracts are active."
    )
    st.session_state.simulation_year = simulation_year

    # Always include projected AR7/AR8
    historical_portfolio = create_portfolio_with_projections()

    portfolio_state = historical_portfolio.get_portfolio_state(simulation_year)

    # Strike Price Mode Toggle
    st.markdown("**Strike Price Source**")
    cfd_price_mode = st.radio(
        "Strike prices",
        options=["Portfolio (Historical)", "Manual"],
        index=0 if st.session_state.cfd_price_mode == "Portfolio (Historical)" else 1,
        horizontal=True,
        help="Portfolio: weighted average from active CfDs. Manual: custom values.",
        label_visibility="collapsed"
    )
    st.session_state.cfd_price_mode = cfd_price_mode

    use_portfolio_strikes = (cfd_price_mode == "Portfolio (Historical)")

    if use_portfolio_strikes:
        # Portfolio mode - show portfolio info compactly
        st.markdown(f"**{simulation_year} Portfolio**")

        # Get user's capacity settings
        solar_cap = st.session_state.get('solar_cap', 15.0)
        onshore_cap = st.session_state.get('onshore_wind_cap', 15.0)
        offshore_cap = st.session_state.get('offshore_wind_cap', 15.0)
        nuclear_cap = st.session_state.get('nuclear_cap', 6.5)
        
        # Calculate RE coverage using percentage-based approach
        re_coverage = portfolio_state.estimated_re_coverage(solar_cap, onshore_cap, offshore_cap)
        
        # Get actual CfD capacity based on user's capacity settings
        cfd_capacities = portfolio_state.get_cfd_capacity_gw(solar_cap, onshore_cap, offshore_cap, nuclear_cap)
        total_cfd_cap = cfd_capacities['total_gw']

        if total_cfd_cap > 0:
            st.caption(f"CfD Capacity: {total_cfd_cap:.1f} GW | RE Coverage: {re_coverage*100:.0f}%")
            st.caption(f"Coverage: Solar {portfolio_state.solar_coverage*100:.0f}% | "
                      f"Onshore {portfolio_state.onshore_wind_coverage*100:.0f}% | "
                      f"Offshore {portfolio_state.offshore_wind_coverage*100:.0f}% | "
                      f"Nuclear {portfolio_state.nuclear_coverage*100:.0f}%")
        else:
            st.caption("No active CfD contracts (all expired)")

        # Strike prices from portfolio (always show - interpolated if no capacity)
        st.markdown("**Avg Strikes (£/MWh)**")
        strike_col1, strike_col2, strike_col3 = st.columns(3)
        with strike_col1:
            st.metric("Solar", f"£{portfolio_state.avg_strike_solar:.0f}", label_visibility="collapsed")
            st.caption("Solar")
        with strike_col2:
            st.metric("Onshore", f"£{portfolio_state.avg_strike_onshore:.0f}", label_visibility="collapsed")
            st.caption("Onshore")
        with strike_col3:
            st.metric("Offshore", f"£{portfolio_state.avg_strike_offshore:.0f}", label_visibility="collapsed")
            st.caption("Offshore")

        # Set strike prices from portfolio (interpolated values available even with 0 capacity)
        cfd_strike_prices = {
            'solar': portfolio_state.avg_strike_solar,
            'onshore_wind': portfolio_state.avg_strike_onshore,
            'offshore_wind': portfolio_state.avg_strike_offshore,
        }
        
        # Also set individual variables for use later in the code
        cfd_solar_strike = portfolio_state.avg_strike_solar
        cfd_onshore_strike = portfolio_state.avg_strike_onshore
        cfd_offshore_strike = portfolio_state.avg_strike_offshore

        # Use RE coverage (what % of RE generation is covered by CfDs)
        cfd_coverage = re_coverage

    else:
        # Manual mode - show sliders
        st.markdown("**Manual Strike Prices (£/MWh)**")

        cfd_solar_strike = st.slider(
            "Solar",
            min_value=30.0,
            max_value=200.0,
            value=st.session_state.cfd_solar_strike,
            step=5.0,
            help="AR6 2024: ~£69/MWh"
        )
        st.session_state.cfd_solar_strike = cfd_solar_strike

        cfd_onshore_strike = st.slider(
            "Onshore Wind",
            min_value=30.0,
            max_value=200.0,
            value=st.session_state.cfd_onshore_strike,
            step=5.0,
            help="AR6 2024: ~£58/MWh"
        )
        st.session_state.cfd_onshore_strike = cfd_onshore_strike

        cfd_offshore_strike = st.slider(
            "Offshore Wind",
            min_value=30.0,
            max_value=200.0,
            value=st.session_state.cfd_offshore_strike,
            step=5.0,
            help="AR6 2024: ~£71/MWh"
        )
        st.session_state.cfd_offshore_strike = cfd_offshore_strike

        cfd_coverage = st.slider(
            "CfD Coverage (%)",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.cfd_coverage * 100,
            step=10.0,
            help="Percentage of RE capacity under CfD contracts"
        ) / 100
        st.session_state.cfd_coverage = cfd_coverage

        cfd_strike_prices = {
            'solar': cfd_solar_strike,
            'onshore_wind': cfd_onshore_strike,
            'offshore_wind': cfd_offshore_strike,
        }
    
    # RO Portfolio Information
    st.divider()
    st.markdown("**Renewables Obligation (RO)**")
    
    # Get RO portfolio state
    ro_portfolio_manager = create_ro_portfolio_with_estimates()
    ro_state = ro_portfolio_manager.get_portfolio_state(simulation_year)
    
    # Get user's capacity settings for RO coverage calculation
    solar_cap = st.session_state.get('solar_cap', 15.0)
    onshore_cap = st.session_state.get('onshore_wind_cap', 14.8)
    offshore_cap = st.session_state.get('offshore_wind_cap', 14.7)
    
    # Calculate RO coverage
    ro_coverage = ro_state.estimated_re_coverage(solar_cap, onshore_cap, offshore_cap)
    ro_capacities = ro_state.get_ro_capacity_gw(solar_cap, onshore_cap, offshore_cap)
    total_ro_cap = ro_capacities['total_gw']
    
    if total_ro_cap > 0:
        st.caption(f"RO Capacity: {total_ro_cap:.1f} GW | RE Coverage: {ro_coverage*100:.1f}%")
        st.caption(f"Coverage: Solar {ro_state.solar_coverage*100:.0f}% | "
                  f"Onshore {ro_state.onshore_wind_coverage*100:.0f}% | "
                  f"Offshore {ro_state.offshore_wind_coverage*100:.0f}%")
        st.caption(f"Avg ROC Value: £{ro_state.avg_roc_value:.0f}/MWh")
    else:
        st.caption("No active RO contracts (all expired)")
        st.info(f"RO projects expire 20 years after accreditation. All RO support ends by {RO_FINAL_EXPIRY_YEAR}.")
    
    # Show RO expiry timeline
    if simulation_year < RO_FINAL_EXPIRY_YEAR:
        years_remaining = RO_FINAL_EXPIRY_YEAR - simulation_year
        st.caption(f"⚠️ RO closed to new applicants in {RO_CLOSURE_YEAR}. Projects expire gradually until {RO_FINAL_EXPIRY_YEAR} ({years_remaining} years remaining).")

# Ensure portfolio_state is available outside expander
if 'portfolio_state' not in dir():
    historical_portfolio = create_portfolio_with_projections()
    portfolio_state = historical_portfolio.get_portfolio_state(st.session_state.simulation_year)

# Time period selection
# Options removed - all tabs are always visible

# Simulation runs automatically when parameters change
# No button needed - changes trigger automatic re-run

# Initialize session state (must be before using session_state values)
if "last_results" not in st.session_state:
    st.session_state.last_results = None
if "last_summary" not in st.session_state:
    st.session_state.last_summary = None
if "last_grid" not in st.session_state:
    st.session_state.last_grid = None
if "last_time_period" not in st.session_state:
    st.session_state.last_time_period = None
if "time_period" not in st.session_state:
    st.session_state.time_period = "1 Week"  # Default
if "last_custom_capacities" not in st.session_state:
    st.session_state.last_custom_capacities = None

# Get time period from session state or use default
time_period_options = ["1 Day", "1 Week", "1 Month", "1 Year"]
default_index = time_period_options.index(st.session_state.time_period) if st.session_state.time_period in time_period_options else 1

time_period = st.sidebar.selectbox(
    "Simulation Period",
    time_period_options,
    index=default_index,
    help="Longer periods provide more accurate statistics but take longer to compute"
)

# Store time period in session state to persist across preset changes
st.session_state.time_period = time_period

# Note about time period selection
st.sidebar.caption("""
**Time Period Selection:**
- **1 Day**: Day 180 (summer weekday)
- **1 Week**: Days 180-186 (summer week)
- **1 Month**: Days 180-209 (summer month)
- **1 Year**: Full year cycle (all 365 days)
""")

# Helper function to format time labels based on period
def format_time_labels(results, time_period):
    """Generate formatted time labels for x-axis based on simulation period."""
    labels = []
    
    if time_period == "1 Day":
        # Format as hours in AM/PM
        for i, result in enumerate(results):
            hour = result.hour
            if hour == 0:
                labels.append("12am")
            elif hour < 12:
                labels.append(f"{hour}am")
            elif hour == 12:
                labels.append("12pm")
            else:
                labels.append(f"{hour-12}pm")
    
    elif time_period == "1 Week":
        # Format as day name, show every 6 hours
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, result in enumerate(results):
            day_idx = i // 24
            hour = result.hour
            day_name = day_names[day_idx % 7]
            # Show day name at midnight, noon, and every 6 hours
            if hour in [0, 6, 12, 18]:
                if hour == 0:
                    labels.append(day_name)
                elif hour == 12:
                    labels.append(f"{day_name}\n12pm")
                else:
                    labels.append(f"{hour}am" if hour < 12 else f"{hour-12}pm")
            else:
                labels.append("")
    
    elif time_period == "1 Month":
        # Format as day number, show every day at midnight
        for i, result in enumerate(results):
            day_of_year = result.day_of_year
            # Approximate day of month (assuming starting from day 180 = July 1)
            day_of_month = (day_of_year - 180) % 30 + 1
            if result.hour == 0:  # Only label at start of each day
                labels.append(f"Day {day_of_month}")
            else:
                labels.append("")
    
    else:  # 1 Year
        # Format as month, show at start of each month
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        last_month = -1
        for i, result in enumerate(results):
            day_of_year = result.day_of_year
            month_idx = int(day_of_year / 30.4) % 12  # Approximate month
            # Show month name at start of month (day 0-2 of month) and hour 0
            if result.hour == 0 and month_idx != last_month:
                labels.append(month_names[month_idx])
                last_month = month_idx
            else:
                labels.append("")
    
    return labels

# Main content area - simulation runs automatically
# Check if we need to re-run (parameters changed or no results yet)
current_params_hash = f"{solar_capacity}_{onshore_wind_capacity}_{offshore_wind_capacity}_{nuclear_capacity}_{biomass_capacity}_{hydro_capacity}_{interconnector_capacity}_{electrification}_{gas_price}_{time_period}_{cfd_strike_prices['solar']}_{cfd_strike_prices['onshore_wind']}_{cfd_strike_prices['offshore_wind']}_{cfd_coverage}_{simulation_year}_{use_portfolio_strikes}"

if "last_params_hash" not in st.session_state:
    st.session_state.last_params_hash = ""

needs_rerun = (
    st.session_state.last_results is None or 
    st.session_state.last_params_hash != current_params_hash
)

if needs_rerun:
    # Validate inputs before running simulation
    capacities_dict = {
        'solar': solar_capacity,
        'onshore_wind': onshore_wind_capacity,
        'offshore_wind': offshore_wind_capacity,
        'nuclear': nuclear_capacity,
        'biomass': biomass_capacity,
        'hydro': hydro_capacity,
        'interconnectors': interconnector_capacity,
        'gas': gas_capacity
    }
    
    is_valid, error_msg = validate_capacities(capacities_dict)
    if not is_valid:
        st.error(f"❌ Invalid capacity settings: {error_msg}")
        st.info("Please adjust the capacity sliders and try again.")
        st.stop()
    
    is_valid, error_msg = validate_demand_parameters(
        peak_demand_gw=peak_demand_gw,
        total_capacity_gw=total_capacity_gw,
        re_capacity_gw=re_capacity_total
    )
    if not is_valid:
        st.warning(f"⚠️ {error_msg}")
        st.info("The simulation may not be able to meet demand. Results may be unreliable.")
    
    is_valid, error_msg = validate_gas_parameters(
        gas_price=gas_price
    )
    if not is_valid:
        st.error(f"❌ Invalid gas parameters: {error_msg}")
        st.stop()
    
    is_valid, error_msg = validate_cfd_parameters(
        strike_prices=cfd_strike_prices,
        coverage=cfd_coverage
    )
    if not is_valid:
        st.error(f"❌ Invalid CfD parameters: {error_msg}")
        st.stop()
    
    # Run simulation with error handling
    spinner_text = "Running simulation... This may take a moment for longer periods."
    if time_period == "1 Year":
        spinner_text = "Running 1-year simulation... This will take 30-60 seconds."
    
    with st.spinner(spinner_text):
        try:
            # Create custom fleet from individual capacities
            generators = []
            if custom_capacities['solar'] > 0:
                generators.append(SolarGenerator(name="Solar", capacity_mw=custom_capacities['solar'] * 1000))
            if custom_capacities['onshore_wind'] > 0:
                generators.append(OnshoreWindGenerator(name="Onshore Wind", capacity_mw=custom_capacities['onshore_wind'] * 1000))
            if custom_capacities['offshore_wind'] > 0:
                generators.append(OffshoreWindGenerator(name="Offshore Wind", capacity_mw=custom_capacities['offshore_wind'] * 1000))
            if custom_capacities['nuclear'] > 0:
                generators.append(NuclearGenerator(name="Nuclear", capacity_mw=custom_capacities['nuclear'] * 1000))
            if custom_capacities['biomass'] > 0:
                generators.append(BiomassGenerator(name="Biomass", capacity_mw=custom_capacities['biomass'] * 1000))
            if custom_capacities['hydro'] > 0:
                generators.append(HydroGenerator(name="Hydro", capacity_mw=custom_capacities['hydro'] * 1000))
            if custom_capacities['gas'] > 0:
                generators.append(GasGenerator(
                    name="Gas CCGT", 
                    capacity_mw=custom_capacities['gas'] * 1000,
                    marginal_cost_per_mwh=gas_price
                ))
            if custom_capacities['interconnectors'] > 0:
                generators.append(InterconnectorImport(name="Interconnectors", capacity_mw=custom_capacities['interconnectors'] * 1000))
            
            if not generators:
                st.error("❌ No generators configured. Please set at least one capacity > 0.")
                st.stop()
            
            grid = Grid(generators=generators)
            grid.demand_profile = create_future_demand_profile(electrification)
            
            # Determine simulation period with progress tracking
            if time_period == "1 Day":
                day_of_year = 180  # Summer day
                results = grid.simulate_day(day_of_year=day_of_year, is_weekday=True)
            elif time_period == "1 Week":
                results = []
                progress_bar = st.progress(0)
                for day in range(7):
                    day_of_year = 180 + day
                    is_weekday = day < 5
                    daily_results = grid.simulate_day(day_of_year=day_of_year, is_weekday=is_weekday)
                    results.extend(daily_results)
                    progress_bar.progress((day + 1) / 7)
                progress_bar.empty()
            elif time_period == "1 Month":
                results = []
                progress_bar = st.progress(0)
                for day in range(30):
                    day_of_year = 180 + day
                    is_weekday = (day % 7) < 5
                    daily_results = grid.simulate_day(day_of_year=day_of_year, is_weekday=is_weekday)
                    results.extend(daily_results)
                    progress_bar.progress((day + 1) / 30)
                progress_bar.empty()
            else:  # 1 Year
                # For year simulation, show progress but don't update too frequently
                # (updating 8760 times would be too slow)
                results = []
                progress_bar = st.progress(0)
                progress_placeholder = st.empty()
                
                # Simulate in chunks to show progress
                total_hours = 8760
                chunk_size = 24 * 7  # One week at a time
                num_chunks = (total_hours + chunk_size - 1) // chunk_size
                
                for chunk_idx in range(num_chunks):
                    start_hour = chunk_idx * chunk_size
                    end_hour = min(start_hour + chunk_size, total_hours)
                    
                    # Simulate this chunk
                    for h in range(start_hour, end_hour):
                        hour = h % 24
                        day = h // 24
                        day_of_year = day % 365
                        is_weekday = (day % 7) < 5
                        demand = grid.demand_profile.get_demand(hour, day_of_year, is_weekday)
                        result = grid.dispatch(demand, hour, day_of_year)
                        results.append(result)
                    
                    # Update progress
                    progress = (chunk_idx + 1) / num_chunks
                    progress_bar.progress(progress)
                    progress_placeholder.text(f"Simulating... {chunk_idx + 1}/{num_chunks} weeks complete")
                
                progress_bar.empty()
                progress_placeholder.empty()
            
            # Calculate summary
            summary = SimulationSummary.from_results(results)
            
            # Calculate CfD costs
            # Use portfolio-based approach if in portfolio mode, otherwise use uniform coverage
            if use_portfolio_strikes:
                cfd_portfolio = create_cfd_portfolio_from_state(
                    generators=generators,
                    portfolio_state=portfolio_state,
                    strike_prices=cfd_strike_prices
                )
            else:
                cfd_portfolio = create_cfd_portfolio_for_fleet(
                    generators=generators,
                    coverage=cfd_coverage,
                    strike_prices=cfd_strike_prices
                )
            cfd_result = simulate_cfd_costs(results, cfd_portfolio)
            
            # Calculate RO costs using portfolio system
            ro_portfolio_manager = create_ro_portfolio_with_estimates()
            ro_state = ro_portfolio_manager.get_portfolio_state(simulation_year)
            ro_portfolio = create_ro_portfolio_from_state(
                generators=generators,
                ro_state=ro_state
            )
            ro_result = simulate_ro_costs(results, ro_portfolio, simulation_year)

            # Store in session state
            st.session_state.last_results = results
            st.session_state.last_summary = summary
            st.session_state.last_grid = grid
            st.session_state.last_time_period = time_period
            st.session_state.last_custom_capacities = custom_capacities
            st.session_state.last_params_hash = current_params_hash
            st.session_state.last_cfd_result = cfd_result
            st.session_state.last_cfd_portfolio = cfd_portfolio
            st.session_state.last_ro_result = ro_result
            st.session_state.last_ro_portfolio = ro_portfolio
            st.session_state.last_ro_state = ro_state
            st.session_state.last_ro_portfolio_manager = ro_portfolio_manager
            
        except ValueError as e:
            st.error(f"❌ Simulation failed: {e}")
            st.info("Please check your capacity settings and try again.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error during simulation: {e}")
            st.info("If this problem persists, please check the console for details.")
            import traceback
            with st.expander("Error details"):
                st.code(traceback.format_exc())
            st.stop()

# Get results from session state
results = st.session_state.last_results
summary = st.session_state.last_summary
grid = st.session_state.last_grid
cfd_result = st.session_state.get('last_cfd_result')
cfd_portfolio = st.session_state.get('last_cfd_portfolio')
ro_result = st.session_state.get('last_ro_result')
ro_portfolio = st.session_state.get('last_ro_portfolio')
ro_state = st.session_state.get('last_ro_state')

if results is None:
    st.info("👈 Adjust parameters in the sidebar to run simulation")
    st.stop()

# Display key metrics
st.subheader("📊 Key Metrics")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "Wholesale Price",
        f"£{summary.average_price:.1f}/MWh",
        help="Average wholesale electricity price (before CfD levy)"
    )

with col2:
    # Calculate wholesale + CfD + RO levy
    # CfD levy = net CfD cost / total consumption
    # RO levy = RO payments / total consumption
    cfd_levy = cfd_result.subsidy_per_mwh_consumed if cfd_result else 0.0
    ro_levy = ro_result.subsidy_per_mwh_consumed if ro_result else 0.0
    total_levy = cfd_levy + ro_levy  # Combined CfD + RO support cost
    effective_price = summary.average_price + total_levy
    
    if cfd_result or ro_result:
        # Format delta string - put total first so Streamlit parses it for color determination
        # This ensures color is based on combined CfD + RO, not just CfD
        # Hide RO if it's 0 or effectively 0
        has_cfd = cfd_result and abs(cfd_levy) > 0.01
        has_ro = ro_result and abs(ro_levy) > 0.01
        
        if has_cfd and has_ro:
            # Both CfD and RO (both non-zero)
            delta_str = f"{total_levy:+.1f} (CfD {cfd_levy:+.1f} + RO {ro_levy:+.1f})"
        elif has_cfd:
            # Only CfD (RO is 0 or missing)
            delta_str = f"{cfd_levy:+.1f} CfD"
        elif has_ro:
            # Only RO (CfD is 0 or missing)
            delta_str = f"{ro_levy:+.1f} RO"
        else:
            # Both are 0 or missing
            delta_str = f"{total_levy:+.1f} Support"
    else:
        delta_str = None
    
    # Color is based on total_levy (CfD + RO combined), not just CfD
    # Red when positive (net cost to consumers), green when negative (net saving/clawback)
    st.metric(
        "Wholesale + Support",
        f"£{effective_price:.1f}/MWh",
        delta=delta_str,
        delta_color="inverse",  # Red when total_levy positive (cost), green when negative (saving)
        help="Wholesale price + CfD levy + RO levy. Note: This does not include capacity markets, balancing costs, network charges, or other components of the final consumer price."
    )

with col3:
    st.metric(
        "RE Share",
        f"{summary.average_re_share*100:.1f}%"
    )

with col4:
    st.metric(
        "Price Range",
        f"£{summary.min_price:.0f} - £{summary.max_price:.0f}",
        help="Min to max wholesale price range"
    )

with col5:
    st.metric(
        "Zero-Price Hours",
        f"{summary.zero_price_hours}",
        help="Hours where price was near-zero (RE oversupply)"
    )

with col6:
    st.metric(
        "Curtailment",
        f"{summary.total_curtailment_mwh/1000:.1f} GWh",
        help="Economic curtailment only (RE supply > demand). Real-world curtailment is higher due to network constraints (Scotland-England bottlenecks). The model does not capture constraint-based curtailment."
    )

st.divider()

# Create tabs for different visualizations
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Price Dynamics", "⚡ Merit Order", "💰 Revenues", "💷 CfD Economics", "📋 Details", "ℹ️ About"
])

with tab1:
    st.subheader("Generation Mix Over Time")
    st.markdown("Stacked area chart showing electricity generation by fuel source")
    
    # Initialize session state for view mode
    if "generation_view_mode" not in st.session_state:
        st.session_state.generation_view_mode = "Absolute (GW)"
    
    # Toggle for absolute vs relative view
    view_mode = st.radio(
        "View Mode",
        options=["Absolute (GW)", "Relative to Demand (%)"],
        horizontal=True,
        index=0 if st.session_state.generation_view_mode == "Absolute (GW)" else 1,
        help="Absolute shows generation in GW. Relative shows each source as percentage of demand at that time.",
        key="generation_view_mode_radio"
    )
    st.session_state.generation_view_mode = view_mode
    
    # Aggregate generation by source type for each hour
    hours = range(len(results))
    # Use stored time_period if available, otherwise use current selection
    display_time_period = st.session_state.last_time_period if st.session_state.last_time_period else time_period
    time_labels = format_time_labels(results, display_time_period)
    
    # Helper function to categorize generator type (used in multiple places)
    def categorize_generator(gen_name: str) -> str:
        """Categorize generator by name into fuel type."""
        if 'Solar' in gen_name:
            return 'Solar'
        elif 'Offshore Wind' in gen_name:
            return 'Offshore Wind'
        elif 'Onshore Wind' in gen_name or 'Wind' in gen_name:
            return 'Onshore Wind'
        elif 'Nuclear' in gen_name:
            return 'Nuclear'
        elif 'Gas' in gen_name:
            return 'Gas'
        elif 'Biomass' in gen_name:
            return 'Biomass'
        elif 'Hydro' in gen_name:
            return 'Hydro'
        elif 'Inter' in gen_name:
            return 'Interconnectors'
        else:
            return 'Other'
    
    # Get unique generator types
    generator_types = {}
    for result in results:
        for gen, mw in result.dispatched_generators:
            gen_type = categorize_generator(gen.name)
            if gen_type not in generator_types:
                generator_types[gen_type] = []
    
    # Initialize arrays for each type
    for gen_type in generator_types:
        generator_types[gen_type] = [0.0] * len(results)
    
    # Fill in generation data and demand
    demands_gw = []
    for i, result in enumerate(results):
        demand_gw = result.demand_mw / 1000  # Convert to GW
        demands_gw.append(demand_gw)
        for gen, mw in result.dispatched_generators:
            gen_type = categorize_generator(gen.name)
            generator_types[gen_type][i] += mw / 1000  # Convert to GW
    
    # Smooth data for 1 Year period (too many points otherwise)
    if display_time_period == "1 Year":
        # Aggregate hourly data to daily averages (24 hours per day)
        hours_per_day = 24
        num_days = len(results) // hours_per_day
        
        # Create smoothed data by averaging each day
        smoothed_generator_types = {}
        smoothed_demands = []
        smoothed_hours = []
        
        for gen_type in generator_types:
            smoothed_generator_types[gen_type] = []
            for day in range(num_days):
                start_idx = day * hours_per_day
                end_idx = start_idx + hours_per_day
                # Average generation for this day
                daily_avg = sum(generator_types[gen_type][start_idx:end_idx]) / hours_per_day
                smoothed_generator_types[gen_type].append(daily_avg)
        
        # Smooth demands too
        for day in range(num_days):
            start_idx = day * hours_per_day
            end_idx = start_idx + hours_per_day
            daily_avg_demand = sum(demands_gw[start_idx:end_idx]) / hours_per_day
            smoothed_demands.append(daily_avg_demand)
        
        # Create day indices for x-axis
        smoothed_hours = list(range(num_days))
        # Update time labels for daily view
        smoothed_time_labels = [f"Day {i+1}" for i in range(num_days)]
        # Use smoothed data
        generator_types = smoothed_generator_types
        demands_gw = smoothed_demands
        hours = smoothed_hours
        time_labels = smoothed_time_labels
    
    # Create stacked area chart
    fig_gen = go.Figure()
    
    # Color mapping for generation types
    gen_colors = {
        'Solar': '#FFD700',
        'Offshore Wind': '#4169E1',
        'Onshore Wind': '#87CEEB',
        'Nuclear': '#9370DB',
        'Gas': '#FF6347',
        'Biomass': '#228B22',
        'Hydro': '#1E90FF',
        'Interconnectors': '#808080',
        'Other': '#A9A9A9'
    }
    
    # Order for stacking (renewables first, then others)
    stack_order = ['Solar', 'Onshore Wind', 'Offshore Wind', 'Hydro', 'Nuclear', 'Biomass', 'Gas', 'Interconnectors', 'Other']
    
    # Convert to relative if needed
    if view_mode == "Relative to Demand (%)":
        # Convert each generator type to percentage of demand
        relative_generator_types = {}
        for gen_type in generator_types:
            relative_generator_types[gen_type] = []
            for i in range(len(generator_types[gen_type])):
                if demands_gw[i] > 0:
                    pct = (generator_types[gen_type][i] / demands_gw[i]) * 100
                else:
                    pct = 0.0
                relative_generator_types[gen_type].append(pct)
        plot_generator_types = relative_generator_types
        y_axis_title = "Generation (% of Demand)"
        hovertemplate_suffix = "%"
    else:
        plot_generator_types = generator_types
        y_axis_title = "Generation (GW)"
        hovertemplate_suffix = " GW"
    
    for gen_type in stack_order:
        if gen_type in plot_generator_types:
            fig_gen.add_trace(go.Scatter(
                x=list(hours),
                y=plot_generator_types[gen_type],
                mode='lines',
                name=gen_type,
                stackgroup='one',
                line=dict(width=0),
                fillcolor=gen_colors.get(gen_type, '#A9A9A9'),
                hovertemplate=f"{gen_type}<br>Time: %{{x}}<br>Generation: %{{y:.2f}}{hovertemplate_suffix}<extra></extra>"
            ))
    
    # Add demand line for relative view
    if view_mode == "Relative to Demand (%)":
        # Add 100% reference line
        fig_gen.add_trace(go.Scatter(
            x=list(hours),
            y=[100.0] * len(hours),
            mode='lines',
            name='Demand (100%)',
            line=dict(color='black', width=2, dash='dash'),
            hovertemplate="Demand: 100%<extra></extra>"
        ))
    
    fig_gen.update_layout(
        xaxis_title="Time",
        yaxis_title=y_axis_title,
        height=500,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(hours)))[::max(1, len(hours)//20)],  # Show ~20 labels
            ticktext=[time_labels[i] for i in range(len(hours))[::max(1, len(hours)//20)]],
            tickangle=-45 if display_time_period in ["1 Week", "1 Month"] else 0
        )
    )
    st.plotly_chart(fig_gen, use_container_width=True)
    
    st.subheader("Price Dynamics Over Time")
    
    # Prepare data
    prices = [r.wholesale_price for r in results]
    demands = [r.demand_mw / 1000 for r in results]  # Convert to GW
    re_shares = [r.re_share * 100 for r in results]
    price_hours = list(range(len(results)))
    
    # Smooth data for 1 Year period (too many points otherwise)
    if display_time_period == "1 Year":
        hours_per_day = 24
        num_days = len(results) // hours_per_day
        
        # Aggregate to daily averages
        smoothed_prices = []
        smoothed_demands = []
        smoothed_re_shares = []
        smoothed_hours_price = []
        
        for day in range(num_days):
            start_idx = day * hours_per_day
            end_idx = start_idx + hours_per_day
            # Average values for this day
            smoothed_prices.append(sum(prices[start_idx:end_idx]) / hours_per_day)
            smoothed_demands.append(sum(demands[start_idx:end_idx]) / hours_per_day)
            smoothed_re_shares.append(sum(re_shares[start_idx:end_idx]) / hours_per_day)
            smoothed_hours_price.append(day)
        
        # Use smoothed data
        prices = smoothed_prices
        demands = smoothed_demands
        re_shares = smoothed_re_shares
        price_hours = smoothed_hours_price
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("Wholesale Price (£/MWh)", "Demand (GW)", "RE Share (%)"),
        vertical_spacing=0.08,
        shared_xaxes=True
    )
    
    # Price plot
    fig.add_trace(
        go.Scatter(
            x=price_hours,
            y=prices,
            mode='lines',
            name='Wholesale Price',
            line=dict(color='#FF6347', width=2),
            hovertemplate='Time: %{x}<br>Price: £%{y:.1f}/MWh<extra></extra>'
        ),
        row=1, col=1
    )
    # Add reference line for typical gas marginal cost
    # NOTE: This is a fixed reference. Actual gas marginal cost varies based on
    # the gas price parameters set in the sidebar
    fig.add_hline(y=82, line_dash="dash", line_color="gray", 
                  annotation_text="Typical gas marginal cost (~£82/MWh)", row=1, col=1)
    
    # Demand plot
    fig.add_trace(
        go.Scatter(
            x=price_hours,
            y=demands,
            mode='lines',
            name='Demand',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.2)',
            hovertemplate='Time: %{x}<br>Demand: %{y:.1f} GW<extra></extra>'
        ),
        row=2, col=1
    )
    
    # RE share plot
    fig.add_trace(
        go.Scatter(
            x=price_hours,
            y=re_shares,
            mode='lines',
            name='RE Share',
            line=dict(color='#2ca02c', width=2),
            fill='tozeroy',
            fillcolor='rgba(44, 160, 44, 0.2)',
            hovertemplate='Time: %{x}<br>RE Share: %{y:.1f}%<extra></extra>'
        ),
        row=3, col=1
    )
    
    # Update x-axis with formatted labels
    data_length = len(price_hours)
    num_ticks = min(20, data_length)
    tick_interval = max(1, data_length // num_ticks)
    tick_positions = list(range(0, data_length, tick_interval))
    # Get time labels - use daily labels for 1 Year, otherwise use original time_labels
    if display_time_period == "1 Year":
        axis_time_labels = [f"Day {i+1}" for i in range(data_length)]
    else:
        axis_time_labels = time_labels
    tick_labels = [axis_time_labels[i] if i < len(axis_time_labels) and axis_time_labels[i] else "" for i in tick_positions]
    
    fig.update_xaxes(
        title_text="Time",
        tickmode='array',
        tickvals=tick_positions,
        ticktext=tick_labels,
        tickangle=-45 if display_time_period in ["1 Week", "1 Month"] else 0,
        row=3, col=1
    )
    fig.update_layout(height=700, showlegend=False, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    # Price duration curve
    st.subheader("Price Duration Curve")
    st.markdown("""
    Shows how often prices are at different levels. The curve is sorted from highest to lowest price.
    - **Left side (high prices)**: Rare peak demand periods
    - **Right side (low prices)**: Common periods when renewables dominate
    - **Steep drop**: Indicates many hours with similar prices
    - **Gradual slope**: Shows price volatility across hours
    """)
    
    price_curve = PriceDurationCurve.from_results(results)
    
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=price_curve.hours,
            y=price_curve.prices_sorted,
            mode='lines',
            name='Price',
            line=dict(color='#FF6347', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 99, 71, 0.3)',
            hovertemplate='Hours: %{x}<br>Price: £%{y:.1f}/MWh<extra></extra>'
        )
    )
    
    fig2.update_layout(
        xaxis_title="Cumulative Hours",
        yaxis_title="Wholesale Price (£/MWh)",
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Price statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "P50 Price",
            f"£{price_curve.price_at_percentile(50):.1f}/MWh",
            help="Median price: 50% of hours were at or below this price. This is the 'typical' price level."
        )
    with col2:
        st.metric(
            "P90 Price",
            f"£{price_curve.price_at_percentile(90):.1f}/MWh",
            help="90th percentile: 90% of hours were at or below this price. Only 10% of hours had higher prices (peak demand periods)."
        )
    with col3:
        st.metric(
            "P10 Price",
            f"£{price_curve.price_at_percentile(10):.1f}/MWh",
            help="10th percentile: Only 10% of hours were at or below this price. 90% of hours had higher prices (often renewable oversupply periods)."
        )
    
    # Add explanation box
    with st.expander("📊 Understanding Price Percentiles"):
        st.markdown("""
        **Price percentiles** show how prices are distributed across the simulation period:
        
        - **P50 (Median)**: The middle price - half of hours were above, half below. This is often closer to the "typical" 
          price than the average, especially when there are extreme high or low prices.
        
        - **P90**: 90% of hours had prices at or below this level. Only 10% of hours were higher. This shows the price 
          during **peak demand periods** when gas or other expensive generators set the price.
        
        - **P10**: Only 10% of hours had prices at or below this level. 90% of hours were higher. This often represents 
          periods of **renewable oversupply** when prices collapse.
        
        **Why this matters:**
        - A large gap between P90 and P10 indicates **high price volatility**
        - If P50 is much lower than the average price, it means prices are skewed by a few very expensive hours
        - P10 near zero suggests many hours with very low prices (renewable cannibalisation effect)
        """)

with tab2:
    st.subheader("Merit Order Stack")
    st.markdown("Generators ordered by marginal cost (cheapest first)")
    
    # Get generators sorted by marginal cost
    sorted_generators = sorted(grid.generators, key=lambda x: x.marginal_cost)
    
    # Build cumulative capacity
    cumulative = 0
    colors_map = {
        'Solar': '#FFD700',
        'Onshore': '#87CEEB',
        'Offshore': '#4169E1',
        'Wind': '#87CEEB',
        'Nuclear': '#9370DB',
        'Hydro': '#4169E1',
        'Biomass': '#228B22',
        'Gas': '#FF6347',
        'Inter': '#808080'
    }
    
    fig = go.Figure()
    
    # Separate zero-cost and non-zero-cost generators for better visibility
    zero_cost_generators = [g for g in sorted_generators if g.marginal_cost < 0.1]
    non_zero_generators = [g for g in sorted_generators if g.marginal_cost >= 0.1]
    
    cumulative = 0
    
    # First, add zero-cost generators at a visible height (2.0) with special styling
    for gen in zero_cost_generators:
        capacity_gw = gen.capacity_mw / 1000
        color = '#808080'  # default
        for key, c in colors_map.items():
            if key in gen.name:
                color = c
                break
        
        # Display at height 2.0 for good visibility
        fig.add_trace(go.Bar(
            x=[cumulative + capacity_gw / 2],
            y=[2.0],
            width=capacity_gw,
            name=gen.name,
            marker_color=color,
            hovertemplate=f"{gen.name}<br>Capacity: {capacity_gw:.1f} GW<br>Marginal Cost: £{gen.marginal_cost:.1f}/MWh (Zero-cost renewable)<extra></extra>",
            showlegend=True
        ))
        cumulative += capacity_gw
    
    # Then add non-zero-cost generators at their actual marginal cost
    for gen in non_zero_generators:
        capacity_gw = gen.capacity_mw / 1000
        color = '#808080'  # default
        for key, c in colors_map.items():
            if key in gen.name:
                color = c
                break
        
        fig.add_trace(go.Bar(
            x=[cumulative + capacity_gw / 2],
            y=[gen.marginal_cost],
            width=capacity_gw,
            name=gen.name,
            marker_color=color,
            hovertemplate=f"{gen.name}<br>Capacity: {capacity_gw:.1f} GW<br>Marginal Cost: £{gen.marginal_cost:.1f}/MWh<extra></extra>",
            showlegend=True
        ))
        cumulative += capacity_gw
    
    # Add average demand line
    avg_demand = np.mean([r.demand_mw / 1000 for r in results])
    fig.add_vline(
        x=avg_demand,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Avg Demand: {avg_demand:.1f} GW"
    )
    
    # Calculate y-axis range
    max_cost = max((g.marginal_cost for g in non_zero_generators), default=60)
    y_max = max(80, max_cost * 1.1)  # Add 10% padding
    
    fig.update_layout(
        xaxis_title="Cumulative Capacity (GW)",
        yaxis_title="Marginal Cost (£/MWh)",
        height=500,
        barmode='overlay',
        hovermode='closest',
        yaxis=dict(
            range=[0, y_max],
            tickmode='linear',
            tick0=0,
            dtick=10
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Generator details table
    st.subheader("Generator Fleet Details")
    gen_data = []
    for gen in sorted_generators:
        gen_data.append({
            "Generator": gen.name,
            "Capacity (GW)": f"{gen.capacity_mw/1000:.2f}",
            "Marginal Cost (£/MWh)": f"{gen.marginal_cost:.1f}",
            "Capacity Factor": f"{gen.capacity_factor*100:.1f}%"
        })
    st.dataframe(pd.DataFrame(gen_data), use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Generator Revenues")
    st.markdown("Total revenue = Σ(MWh dispatched × wholesale price)")
    
    revenues = calculate_generator_revenues(results)
    
    # Calculate CfD payments per generator if CfD portfolio exists
    cfd_payments_by_generator = {}
    if cfd_portfolio:
        for result in results:
            for gen, mw in result.dispatched_generators:
                mwh = mw  # 1 hour period
                contract = cfd_portfolio.get_contract_for_generator(gen.name)
                if contract:
                    payment = contract.calculate_payment(result.wholesale_price, mwh)
                    if gen.name not in cfd_payments_by_generator:
                        cfd_payments_by_generator[gen.name] = 0.0
                    cfd_payments_by_generator[gen.name] += payment
    
    # Initialize session state for toggles
    if "revenue_view" not in st.session_state:
        st.session_state.revenue_view = "Total Revenue"
    if "include_cfd_payments" not in st.session_state:
        st.session_state.include_cfd_payments = True
    
    # Toggle for revenue view
    revenue_view = st.radio(
        "Revenue View",
        options=["Total Revenue", "Revenue per Capacity (GW)"],
        horizontal=True,
        index=0 if st.session_state.revenue_view == "Total Revenue" else 1,
        help="Total Revenue shows absolute values. Revenue per Capacity shows revenue per GW of installed capacity.",
        key="revenue_view_radio"
    )
    st.session_state.revenue_view = revenue_view
    
    # Toggle for including CfD
    include_cfd = st.checkbox(
        "Include CfD Payments",
        value=st.session_state.include_cfd_payments,
        help="Include Contracts for Difference payments (top-up or clawback) in revenue calculations",
        key="include_cfd_checkbox"
    )
    st.session_state.include_cfd_payments = include_cfd
    
    # Calculate total revenue including CfD if requested
    generator_names = [r.name for r in revenues]
    wholesale_revenues = [r.total_revenue_gbp for r in revenues]
    cfd_revenues = [cfd_payments_by_generator.get(r.name, 0.0) for r in revenues]
    
    if include_cfd:
        total_revenues = [w + c for w, c in zip(wholesale_revenues, cfd_revenues)]
    else:
        total_revenues = wholesale_revenues
    
    # Convert to per-capacity if requested
    if revenue_view == "Revenue per Capacity (GW)":
        capacities_gw = [r.capacity_mw / 1000 for r in revenues]
        # Revenue per GW in millions: (total_revenue / 1e6) / capacity_gw
        display_values = [(t / 1e6) / c if c > 0 else 0 for t, c in zip(total_revenues, capacities_gw)]
        y_axis_title = "Revenue per Capacity (£M/GW)"
        text_values = [f"£{v:.1f}M/GW" for v in display_values]
        hovertemplate_suffix = "M/GW"
    else:
        display_values = [t / 1e6 for t in total_revenues]  # Convert to millions
        y_axis_title = "Total Revenue (£M)"
        text_values = [f"£{v:.1f}M" for v in display_values]
        hovertemplate_suffix = "M"
    
    # Create stacked bar chart if including CfD
    if include_cfd and any(c != 0 for c in cfd_revenues):
        fig = go.Figure()
        
        # Wholesale revenue (base)
        if revenue_view == "Revenue per Capacity (GW)":
            capacities_gw = [r.capacity_mw / 1000 for r in revenues]
            wholesale_display = [(w / 1e6) / c if c > 0 else 0 for w, c in zip(wholesale_revenues, capacities_gw)]
        else:
            wholesale_display = [w / 1e6 for w in wholesale_revenues]
        
        # CfD revenue - separate positive and negative
        if revenue_view == "Revenue per Capacity (GW)":
            capacities_gw = [r.capacity_mw / 1000 for r in revenues]
            cfd_display = [(c / 1e6) / cap if cap > 0 else 0 for c, cap in zip(cfd_revenues, capacities_gw)]
        else:
            cfd_display = [c / 1e6 for c in cfd_revenues]
        
        # Split into positive (top-up) and negative (clawback)
        cfd_positive = [max(0, c) for c in cfd_display]
        cfd_negative = [min(0, c) for c in cfd_display]
        
        # Calculate total labels (already calculated as display_values)
        total_labels = [f"£{v:.1f}{hovertemplate_suffix}" if v != 0 else "" for v in display_values]
        
        # Determine which segment should show the total label
        # If there's a positive CfD, show total on top-up segment (topmost)
        # If there's only negative CfD or no CfD, show total on wholesale segment
        has_positive_cfd = any(c > 0 for c in cfd_positive)
        has_negative_cfd = any(c < 0 for c in cfd_negative)
        
        # Add wholesale revenue bars
        # Show total label on wholesale if no positive CfD (or if only negative)
        wholesale_text = total_labels if not has_positive_cfd else [""] * len(generator_names)
        fig.add_trace(go.Bar(
            x=generator_names,
            y=wholesale_display,
            name='Wholesale Revenue',
            marker_color='#1f77b4',
            text=wholesale_text,
            textposition='outside',
            hovertemplate="%{x}<br>Wholesale: £%{y:.2f}{hovertemplate_suffix}<extra></extra>"
        ))
        
        # Add positive CfD payments (top-up) - stacked above wholesale
        if has_positive_cfd:
            fig.add_trace(go.Bar(
                x=generator_names,
                y=cfd_positive,
                name='CfD Top-up (Subsidy)',
                marker_color='#2ca02c',  # Green for positive (top-up)
                text=total_labels,  # Show total on top segment
                textposition='outside',
                hovertemplate="%{x}<br>CfD Top-up: £%{y:.2f}{hovertemplate_suffix}<extra></extra>",
                base=wholesale_display  # Stack on top of wholesale revenue
            ))
        
        # Add negative CfD payments (clawback) - stacked below wholesale
        # In stacked mode, negatives will automatically stack downward from zero
        if has_negative_cfd:
            fig.add_trace(go.Bar(
                x=generator_names,
                y=cfd_negative,
                name='CfD Clawback (Return)',
                marker_color='#FF6347',  # Red for negative (clawback)
                text=[""],  # No label on negative segment (total already on wholesale)
                textposition='outside',
                hovertemplate="%{x}<br>CfD Clawback: £%{y:.2f}{hovertemplate_suffix}<extra></extra>",
                base=wholesale_display  # Stack below wholesale (negative values extend downward)
            ))
        
        fig.update_layout(
            barmode='stack',  # Stacked mode: components stack on top of each other
            xaxis_title="Generator",
            yaxis_title=y_axis_title,
            height=400,
            xaxis_tickangle=-45,
            margin=dict(t=40, b=50, l=50, r=50),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
    else:
        # Simple bar chart if not including CfD or no CfD payments
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=generator_names,
            y=display_values,
            marker_color='#1f77b4',
            text=text_values,
            textposition='outside',
            hovertemplate="%{x}<br>Revenue: £%{y:.2f}{hovertemplate_suffix}<extra></extra>"
        ))
        
        fig.update_layout(
            xaxis_title="Generator",
            yaxis_title=y_axis_title,
            height=400,
            xaxis_tickangle=-45,
            margin=dict(t=40, b=50, l=50, r=50)
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Revenue details table
    revenue_data = []
    for r in revenues:
        cfd_payment = cfd_payments_by_generator.get(r.name, 0.0)
        total_revenue = r.total_revenue_gbp + (cfd_payment if include_cfd else 0.0)
        
        revenue_data.append({
            "Generator": r.name,
            "Wholesale Revenue (£M)": f"{r.total_revenue_gbp/1e6:.2f}",
            "CfD Payment (£M)": f"{cfd_payment/1e6:+.2f}" if cfd_portfolio else "N/A",
            "Total Revenue (£M)": f"{total_revenue/1e6:.2f}",
            "Generation (GWh)": f"{r.total_generation_mwh/1000:.1f}",
            "Avg Capture Price (£/MWh)": f"{r.average_capture_price:.1f}",
            "Load Factor": f"{r.load_factor*100:.1f}%"
        })
    st.dataframe(pd.DataFrame(revenue_data), use_container_width=True, hide_index=True)
    
    # Capture price comparison (including CfD if enabled)
    st.subheader("Average Capture Price vs Wholesale Price")
    avg_wholesale = summary.average_price
    
    # Calculate effective capture price including CfD
    effective_capture_prices = []
    for r in revenues:
        base_price = r.average_capture_price
        if include_cfd and r.total_generation_mwh > 0:
            cfd_payment = cfd_payments_by_generator.get(r.name, 0.0)
            cfd_per_mwh = cfd_payment / r.total_generation_mwh
            effective_price = base_price + cfd_per_mwh
        else:
            effective_price = base_price
        effective_capture_prices.append(effective_price)
    
    gen_names = [r.name for r in revenues]
    
    fig2 = go.Figure()
    
    if include_cfd and any(c != 0 for c in cfd_payments_by_generator.values()):
        # Bars showing wholesale + CfD (stacked)
        base_capture = [r.average_capture_price for r in revenues]
        cfd_per_mwh = [cfd_payments_by_generator.get(r.name, 0.0) / r.total_generation_mwh 
                       if r.total_generation_mwh > 0 else 0.0 for r in revenues]
        
        # Split into positive and negative
        cfd_positive = [max(0, c) for c in cfd_per_mwh]
        cfd_negative = [min(0, c) for c in cfd_per_mwh]
        
        # Calculate total (effective) capture price for labels
        total_labels = [f"£{p:.1f}" for p in effective_capture_prices]
        
        # Determine which segment should show the total label
        has_positive_cfd = any(c > 0 for c in cfd_positive)
        has_negative_cfd = any(c < 0 for c in cfd_negative)
        
        # Add wholesale capture price bars
        # Show total label on wholesale if no positive CfD (or if only negative)
        wholesale_text = total_labels if not has_positive_cfd else [""] * len(gen_names)
        fig2.add_trace(go.Bar(
            x=gen_names,
            y=base_capture,
            name='Wholesale Capture Price',
            marker_color='#1f77b4',  # Blue for wholesale (consistent with revenue chart)
            text=wholesale_text,
            textposition='outside',
            hovertemplate="%{x}<br>Wholesale: £%{y:.1f}/MWh<extra></extra>"
        ))
        
        # Positive CfD (top-up) - stacked above
        if has_positive_cfd:
            fig2.add_trace(go.Bar(
                x=gen_names,
                y=cfd_positive,
                name='CfD Top-up per MWh',
                marker_color='#2ca02c',  # Green for positive (top-up)
                text=total_labels,  # Show total on top segment
                textposition='outside',
                hovertemplate="%{x}<br>CfD Top-up: £%{y:.1f}/MWh<extra></extra>",
                base=base_capture  # Stack on top of wholesale
            ))
        
        # Negative CfD (clawback) - stacked below wholesale
        if has_negative_cfd:
            fig2.add_trace(go.Bar(
                x=gen_names,
                y=cfd_negative,
                name='CfD Clawback per MWh',
                marker_color='#FF6347',  # Red for negative (clawback)
                text=[""],  # No label on negative segment (total already on wholesale)
                textposition='outside',
                hovertemplate="%{x}<br>CfD Clawback: £%{y:.1f}/MWh<extra></extra>",
                base=base_capture  # Stack below wholesale (negative values extend downward)
            ))
        
        fig2.update_layout(
            barmode='stack',  # Stacked mode: components stack on top of each other
            xaxis_title="Generator",
            yaxis_title="Price (£/MWh)",
            height=400,
            xaxis_tickangle=-45,
            margin=dict(t=40, b=50, l=50, r=50),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
    else:
        # Simple bars
        fig2.add_trace(go.Bar(
            x=gen_names,
            y=effective_capture_prices,
            name='Capture Price',
            marker_color='#2ca02c',
            text=[f"£{p:.1f}" for p in effective_capture_prices],
            textposition='outside',
            hovertemplate="%{x}<br>Capture Price: £%{y:.1f}/MWh<extra></extra>"
        ))
    
    fig2.add_hline(
        y=avg_wholesale,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Avg Wholesale: £{avg_wholesale:.1f}/MWh"
    )
    
    fig2.update_layout(
        xaxis_title="Generator",
        yaxis_title="Price (£/MWh)",
        height=400,
        xaxis_tickangle=-45,
        margin=dict(t=40, b=50, l=50, r=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) if include_cfd else None
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.subheader("Renewable Energy Support Schemes")
    st.markdown("""
    **Contracts for Difference (CfDs)** guarantee renewable generators a fixed 'strike price'.
    When wholesale prices fall below the strike price, consumers pay the difference via LCCC.
    When wholesale prices are above the strike price, generators pay back the difference.
    
    **Renewables Obligation (RO)** provides fixed ROC payments per MWh generated (always a subsidy, no clawback).
    RO closed to new applicants in 2017, but existing generators continue to receive support until 2037.
    """)

    if cfd_result:
        # Key CfD metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Net CfD Cost",
                f"£{cfd_result.net_cfd_cost/1e6:.1f}M",
                help="Total LCCC cost passed to consumers (top-up minus clawback)"
            )

        with col2:
            st.metric(
                "Subsidy per MWh",
                f"£{cfd_result.subsidy_per_mwh_consumed:.2f}",
                help="CfD levy per MWh of electricity consumed"
            )

        with col3:
            annual_household = cfd_result.annual_household_cost
            st.metric(
                "Annual Household Cost",
                f"£{annual_household:.0f}",
                help="Estimated annual CfD cost per household (2,700 kWh/year)"
            )

        with col4:
            # Calculate whether it's a net subsidy or clawback
            if cfd_result.net_cfd_cost > 0:
                status = "Subsidy"
                status_color = "red"
            else:
                status = "Clawback"
                status_color = "green"
            st.metric(
                "CfD Status",
                status,
                help="Net subsidy means consumers pay; clawback means generators pay back"
            )

        st.divider()

        # CfD payment breakdown
        st.subheader("CfD Payment Breakdown")
        col1, col2 = st.columns(2)

        with col1:
            # Top-up vs Clawback bar chart
            fig_cfd = go.Figure()
            fig_cfd.add_trace(go.Bar(
                x=['Top-up Payments', 'Clawback Payments'],
                y=[cfd_result.total_topup_payments/1e6, cfd_result.total_clawback_payments/1e6],
                marker_color=['#FF6347', '#2ca02c'],
                text=[f"£{cfd_result.total_topup_payments/1e6:.1f}M", f"£{cfd_result.total_clawback_payments/1e6:.1f}M"],
                textposition='outside'
            ))
            fig_cfd.update_layout(
                yaxis_title="Amount (£M)",
                height=350,
                showlegend=False,
                margin=dict(t=40, b=30, l=50, r=30)  # Add top margin to prevent cropping
            )
            st.plotly_chart(fig_cfd, use_container_width=True)
            st.caption("**Top-up**: LCCC pays generators when wholesale < strike price")
            st.caption("**Clawback**: Generators pay LCCC when wholesale > strike price")

        with col2:
            # Payments by source
            if cfd_result.payments_by_source:
                sources = list(cfd_result.payments_by_source.keys())
                payments = [cfd_result.payments_by_source.get(s, 0)/1e6 for s in sources]

                # Color based on positive (subsidy) or negative (clawback)
                colors = ['#FF6347' if p > 0 else '#2ca02c' for p in payments]

                fig_sources = go.Figure()
                fig_sources.add_trace(go.Bar(
                    x=sources,
                    y=payments,
                    marker_color=colors,
                    text=[f"£{p:.1f}M" for p in payments],
                    textposition='outside'
                ))
                fig_sources.update_layout(
                    yaxis_title="Net CfD Payment (£M)",
                    height=350,
                    xaxis_tickangle=-45,
                    margin=dict(t=40, b=50, l=50, r=30)  # Add top margin to prevent cropping
                )
                st.plotly_chart(fig_sources, use_container_width=True)
                st.caption("Positive = consumers pay subsidy; Negative = clawback to consumers")

        st.divider()
        
        # RO metrics
        if ro_result:
            st.subheader("Renewables Obligation (RO) Costs")
            ro_col1, ro_col2, ro_col3, ro_col4 = st.columns(4)
            
            with ro_col1:
                st.metric(
                    "Total RO Payments",
                    f"£{ro_result.total_ro_payments/1e6:.1f}M",
                    help="Total RO subsidy payments (always positive - RO has no clawback)"
                )
            
            with ro_col2:
                st.metric(
                    "RO Subsidy per MWh",
                    f"£{ro_result.subsidy_per_mwh_consumed:.2f}",
                    help="RO levy per MWh of electricity consumed"
                )
            
            with ro_col3:
                ro_annual_household = ro_result.annual_household_cost
                st.metric(
                    "Annual Household Cost",
                    f"£{ro_annual_household:.0f}",
                    help="Estimated annual RO cost per household (2,700 kWh/year)"
                )
            
            with ro_col4:
                ro_coverage = ro_state.estimated_re_coverage(
                    custom_capacities['solar'],
                    custom_capacities['onshore_wind'],
                    custom_capacities['offshore_wind']
                ) if ro_state else 0.0
                st.metric(
                    "RO Coverage",
                    f"{ro_coverage*100:.1f}%",
                    help="Percentage of RE generation covered by RO"
                )
            
            st.divider()
            
            # Combined CfD + RO metrics
            st.subheader("Combined Support Costs (CfD + RO)")
            combined_col1, combined_col2, combined_col3 = st.columns(3)
            
            total_subsidy = cfd_result.net_cfd_cost + ro_result.total_ro_payments
            total_subsidy_per_mwh = cfd_result.subsidy_per_mwh_consumed + ro_result.subsidy_per_mwh_consumed
            total_annual_household = cfd_result.annual_household_cost + ro_result.annual_household_cost
            
            with combined_col1:
                st.metric(
                    "Total Support Cost",
                    f"£{total_subsidy/1e6:.1f}M",
                    help="Combined CfD + RO costs to consumers"
                )
            
            with combined_col2:
                st.metric(
                    "Total Subsidy per MWh",
                    f"£{total_subsidy_per_mwh:.2f}",
                    help="Combined CfD + RO levy per MWh consumed"
                )
            
            with combined_col3:
                st.metric(
                    "Total Annual Household Cost",
                    f"£{total_annual_household:.0f}",
                    help="Combined CfD + RO cost per household per year"
                )
            
            # Combined coverage
            if ro_state:
                # Get CfD coverage
                if use_portfolio_strikes and portfolio_state:
                    cfd_coverage_pct = portfolio_state.estimated_re_coverage(
                        custom_capacities['solar'],
                        custom_capacities['onshore_wind'],
                        custom_capacities['offshore_wind']
                    )
                else:
                    cfd_coverage_pct = cfd_coverage  # Use the slider value
                
                # Note: Coverage can overlap (some generators have both), so combined may be less than sum
                # For display, we show the sum but note it may overstate if there's overlap
                combined_coverage = min(1.0, cfd_coverage_pct + ro_coverage)
                st.info(f"**Combined Coverage**: {cfd_coverage_pct*100:.1f}% CfD + {ro_coverage*100:.1f}% RO = {combined_coverage*100:.1f}% of RE generation supported (note: some overlap possible)")
            
            st.divider()

        # CfD Cost Dynamics Explanation
        st.subheader("CfD Cost Dynamics")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            ### Current Scenario Metrics

            | Metric | Value |
            |--------|-------|
            | Average Wholesale Price | £{cfd_result.average_wholesale_price:.1f}/MWh |
            | RE Capture Price | £{cfd_result.average_re_capture_price:.1f}/MWh |
            | RE Share | {cfd_result.re_share*100:.1f}% |
            | Solar Strike | £{cfd_solar_strike:.0f}/MWh |
            | Onshore Strike | £{cfd_onshore_strike:.0f}/MWh |
            | Offshore Strike | £{cfd_offshore_strike:.0f}/MWh |
            """)

        with col2:
            # Calculate price gap
            avg_strike = (cfd_solar_strike + cfd_onshore_strike + cfd_offshore_strike) / 3
            price_gap = avg_strike - cfd_result.average_wholesale_price

            if price_gap > 0:
                st.warning(f"""
                **Wholesale price £{cfd_result.average_wholesale_price:.1f}/MWh is BELOW average strike price £{avg_strike:.0f}/MWh**

                Gap: £{price_gap:.1f}/MWh per MWh generated

                This means consumers are subsidising renewable generators through CfD top-up payments.
                """)
            else:
                st.success(f"""
                **Wholesale price £{cfd_result.average_wholesale_price:.1f}/MWh is ABOVE average strike price £{avg_strike:.0f}/MWh**

                Surplus: £{-price_gap:.1f}/MWh per MWh generated

                This means generators are paying back consumers through CfD clawback payments.
                """)

        st.divider()

        # Portfolio Evolution Over Time
        st.subheader("CfD Portfolio Evolution (2025-2050)")
        st.markdown(f"""
        Shows how the UK CfD portfolio evolves as old contracts expire and new ones come online.
        **Current selection: {simulation_year}** | Includes projected AR7/AR8
        """)

        # Calculate portfolio evolution
        evolution_years = list(range(2025, 2051))
        evolution_data = [historical_portfolio.get_portfolio_state(y) for y in evolution_years]

        # Create two charts side by side
        col_evo1, col_evo2 = st.columns(2)

        with col_evo1:
            # Stacked area chart of capacity by AR
            fig_capacity = go.Figure()

            # Get all unique ARs across all years
            all_ars = set()
            for state in evolution_data:
                all_ars.update(state.projects_by_ar.keys())

            # Sort ARs for consistent ordering
            ar_order = ['Investment Contract', 'Allocation Round 1', 'Allocation Round 2',
                       'Allocation Round 3', 'Allocation Round 4', 'Allocation Round 5',
                       'Allocation Round 6', 'Allocation Round 7', 'Allocation Round 8', 'Bespoke']
            sorted_ars = [ar for ar in ar_order if ar in all_ars]

            # Color mapping for ARs
            ar_colors = {
                'Investment Contract': '#8B4513',
                'Allocation Round 1': '#FF6347',
                'Allocation Round 2': '#FF8C00',
                'Allocation Round 3': '#FFD700',
                'Allocation Round 4': '#32CD32',
                'Allocation Round 5': '#4169E1',
                'Allocation Round 6': '#9370DB',
                'Allocation Round 7': '#FF69B4',
                'Allocation Round 8': '#00CED1',
                'Bespoke': '#808080',
            }

            for ar in sorted_ars:
                capacities = []
                for state in evolution_data:
                    cap = state.projects_by_ar.get(ar, {}).get('capacity_gw', 0)
                    capacities.append(cap)

                fig_capacity.add_trace(go.Scatter(
                    x=evolution_years,
                    y=capacities,
                    name=ar.replace('Allocation Round ', 'AR'),
                    mode='lines',
                    stackgroup='capacity',
                    line=dict(width=0),
                    fillcolor=ar_colors.get(ar, '#A9A9A9'),
                    hovertemplate=f"{ar}<br>Year: %{{x}}<br>Capacity: %{{y:.1f}} GW<extra></extra>"
                ))

            # Add vertical line for selected year
            fig_capacity.add_vline(
                x=simulation_year,
                line_dash="dash",
                line_color="black",
                annotation_text=f"{simulation_year}"
            )

            fig_capacity.update_layout(
                title="CfD Capacity by Allocation Round",
                xaxis_title="Year",
                yaxis_title="Capacity (GW)",
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='x unified'
            )
            st.plotly_chart(fig_capacity, use_container_width=True)

        with col_evo2:
            # Line chart of weighted average strike price
            avg_strikes = [state.avg_strike_all for state in evolution_data]
            # Get current capacity settings for demand coverage calculation
            solar_cap = st.session_state.get('solar_cap', 15.5)
            onshore_cap = st.session_state.get('onshore_wind_cap', 14.8)
            offshore_cap = st.session_state.get('offshore_wind_cap', 14.7)
            nuclear_cap = st.session_state.get('nuclear_cap', 6.5)
            demand_coverage = [state.estimated_demand_coverage(solar_cap, onshore_cap, offshore_cap, nuclear_cap) * 100 
                              for state in evolution_data]

            fig_strike = make_subplots(specs=[[{"secondary_y": True}]])

            fig_strike.add_trace(
                go.Scatter(
                    x=evolution_years,
                    y=avg_strikes,
                    name='Avg Strike Price',
                    mode='lines+markers',
                    line=dict(color='#FF6347', width=2),
                    hovertemplate="Year: %{x}<br>Avg Strike: £%{y:.0f}/MWh<extra></extra>"
                ),
                secondary_y=False
            )

            fig_strike.add_trace(
                go.Scatter(
                    x=evolution_years,
                    y=demand_coverage,
                    name='Demand Coverage',
                    mode='lines+markers',
                    line=dict(color='#4169E1', width=2, dash='dot'),
                    hovertemplate="Year: %{x}<br>Coverage: %{y:.0f}%<extra></extra>"
                ),
                secondary_y=True
            )

            # Add vertical line for selected year
            fig_strike.add_vline(
                x=simulation_year,
                line_dash="dash",
                line_color="black",
                annotation_text=f"{simulation_year}"
            )

            fig_strike.update_layout(
                title="Strike Price & Coverage Evolution",
                xaxis_title="Year",
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='x unified'
            )
            fig_strike.update_yaxes(title_text="Avg Strike Price (£/MWh)", secondary_y=False)
            fig_strike.update_yaxes(title_text="Demand Coverage (%)", secondary_y=True)

            st.plotly_chart(fig_strike, use_container_width=True)

        # Portfolio breakdown for selected year
        st.markdown(f"### {simulation_year} Portfolio Breakdown")

        col_tech, col_ar = st.columns(2)

        with col_tech:
            # Technology breakdown - use user's capacity to calculate actual CfD capacity
            solar_cap = st.session_state.get('solar_cap', 15.0)
            onshore_cap = st.session_state.get('onshore_wind_cap', 15.0)
            offshore_cap = st.session_state.get('offshore_wind_cap', 15.0)
            nuclear_cap = st.session_state.get('nuclear_cap', 6.5)
            cfd_capacities = portfolio_state.get_cfd_capacity_gw(solar_cap, onshore_cap, offshore_cap, nuclear_cap)
            
            tech_data = {
                'Technology': ['Offshore Wind', 'Onshore Wind', 'Solar PV', 'Nuclear', 'Other'],
                'Capacity (GW)': [
                    cfd_capacities['offshore_wind_gw'],
                    cfd_capacities['onshore_wind_gw'],
                    cfd_capacities['solar_gw'],
                    cfd_capacities['nuclear_gw'],
                    cfd_capacities['other_gw']
                ],
                'Coverage (%)': [
                    f"{portfolio_state.offshore_wind_coverage*100:.0f}%" if portfolio_state.offshore_wind_coverage > 0 else "-",
                    f"{portfolio_state.onshore_wind_coverage*100:.0f}%" if portfolio_state.onshore_wind_coverage > 0 else "-",
                    f"{portfolio_state.solar_coverage*100:.0f}%" if portfolio_state.solar_coverage > 0 else "-",
                    f"{portfolio_state.nuclear_coverage*100:.0f}%" if portfolio_state.nuclear_coverage > 0 else "-",
                    "-"   # Other doesn't use percentages
                ],
                'Avg Strike (£/MWh)': [
                    f"£{portfolio_state.avg_strike_offshore:.0f}" if cfd_capacities['offshore_wind_gw'] > 0 else "-",
                    f"£{portfolio_state.avg_strike_onshore:.0f}" if cfd_capacities['onshore_wind_gw'] > 0 else "-",
                    f"£{portfolio_state.avg_strike_solar:.0f}" if cfd_capacities['solar_gw'] > 0 else "-",
                    f"£{portfolio_state.avg_strike_nuclear:.0f}" if cfd_capacities['nuclear_gw'] > 0 else "-",
                    "-"
                ]
            }
            st.dataframe(pd.DataFrame(tech_data), use_container_width=True, hide_index=True)

        with col_ar:
            # AR breakdown
            ar_breakdown = []
            for ar, data in sorted(portfolio_state.projects_by_ar.items()):
                ar_breakdown.append({
                    'Allocation Round': ar.replace('Allocation Round ', 'AR'),
                    'Projects': data['count'],
                    'Capacity (GW)': f"{data['capacity_gw']:.2f}"
                })
            if ar_breakdown:
                st.dataframe(pd.DataFrame(ar_breakdown), use_container_width=True, hide_index=True)
            else:
                st.info("No active CfD contracts in this year")

        st.divider()

        # Historical context
        st.subheader("Historical UK CfD Strike Prices")
        st.markdown("*How strike prices have evolved through Allocation Rounds*")

        ar_data = []
        for ar, prices in UK_CFD_STRIKE_PRICES.items():
            for tech, price in prices.items():
                if price is not None:
                    ar_data.append({
                        'Allocation Round': ar.replace('_', ' '),
                        'Technology': tech.replace('_', ' ').title(),
                        'Strike Price (£/MWh)': price,
                        'AR_Order': int(ar.split('_')[0].replace('AR', ''))  # Extract number for sorting
                    })

        ar_df = pd.DataFrame(ar_data)
        
        # Sort by Allocation Round order to ensure chronological display
        ar_df = ar_df.sort_values('AR_Order')

        # Create line chart for strike price evolution
        fig_ar = go.Figure()
        for tech in ar_df['Technology'].unique():
            tech_data = ar_df[ar_df['Technology'] == tech].sort_values('AR_Order')
            fig_ar.add_trace(go.Scatter(
                x=tech_data['Allocation Round'],
                y=tech_data['Strike Price (£/MWh)'],
                name=tech,
                mode='lines+markers',
                connectgaps=False  # Don't connect across missing data points
            ))

        fig_ar.update_layout(
            xaxis_title="Allocation Round",
            yaxis_title="Strike Price (£/MWh)",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig_ar, use_container_width=True)
        st.caption("Note: AR5 had no offshore wind awards due to high strike prices vs budget.")

    else:
        st.info("Run simulation to see CfD economics analysis")

with tab5:
    st.subheader("Simulation Details")
    
    # Summary statistics
    st.markdown("### Summary Statistics")
    summary_data = {
        "Metric": [
            "Average Price",
            "Min Price",
            "Max Price",
            "Price Std Dev",
            "Average RE Share",
            "Zero-Price Hours",
            "Total Curtailment",
            "Hours Simulated"
        ],
        "Value": [
            f"£{summary.average_price:.2f}/MWh",
            f"£{summary.min_price:.2f}/MWh",
            f"£{summary.max_price:.2f}/MWh",
            f"£{summary.price_std:.2f}/MWh",
            f"{summary.average_re_share*100:.2f}%",
            f"{summary.zero_price_hours}",
            f"{summary.total_curtailment_mwh/1000:.2f} GWh",
            f"{summary.hours_simulated}"
        ]
    }
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
    
    # Note about curtailment limitation
    if summary.total_curtailment_mwh == 0:
        st.info("ℹ️ **Curtailment Note**: The model only captures economic curtailment (when RE supply > demand). Real-world curtailment is significantly higher due to network constraints (especially Scotland-England transmission bottlenecks) that the model does not simulate. Actual UK curtailment in 2024/2025 was several TWh annually.")
    
    # Scenario parameters
    st.markdown("### Scenario Parameters")
    param_data = {
        "Parameter": [
            "Renewable Penetration",
            "Total Capacity",
            "Electrification Factor"
        ],
        "Value": [
            f"{re_penetration*100:.1f}%",
            f"{total_capacity_gw:.1f} GW",
            f"{electrification:.2f}x"
        ]
    }
    st.dataframe(pd.DataFrame(param_data), use_container_width=True, hide_index=True)
    
    # Download results
    st.markdown("### Export Results")
    if st.button("📥 Download Results as CSV"):
        # Create DataFrame with all results
        export_data = []
        for i, r in enumerate(results):
            export_data.append({
                "Hour": i,
                "Day_of_Year": r.day_of_year,
                "Hour_of_Day": r.hour,
                "Demand_MW": r.demand_mw,
                "Wholesale_Price_GBP_MWh": r.wholesale_price,
                "RE_Share": r.re_share,
                "Curtailment_MW": r.curtailment_mw,
                "Total_Generation_MW": r.total_generation_mw,
                "Price_Setter": r.price_setter.name if r.price_setter else "None"
            })
        
        df_export = pd.DataFrame(export_data)
        csv = df_export.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"grid_simulation_custom_{time_period.replace(' ', '_')}.csv",
            mime="text/csv"
        )

with tab6:
    st.subheader("About This Model")
    
    # Read and display the ABOUT.md file
    try:
        with open("ABOUT.md", "r", encoding="utf-8") as f:
            about_content = f.read()
        st.markdown(about_content)
    except FileNotFoundError:
        st.error("""
        **About page content file not found.**
        
        Please ensure `ABOUT.md` exists in the project root directory.
        """)
        st.info("""
        The About page content has been moved to a separate markdown file (`ABOUT.md`) 
        for easier editing. You can edit that file directly without modifying Python code.
        """)

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
    <p>UK Energy Grid Model | Based on research: "Profit vs the Planet"</p>
    <p>Simulates merit order dispatch and renewable energy cannibalisation effects</p>
    </div>
    """,
    unsafe_allow_html=True
)

