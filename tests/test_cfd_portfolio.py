"""Tests for CfD portfolio modeling."""

import pytest
from datetime import datetime
from src.cfd_portfolio import (
    CfDProject,
    CfDPortfolio,
    CfDPortfolioState,
    AR_STRIKE_PRICES_2012,
    INFLATION_MULTIPLIER_2012_TO_2025,
)


class TestCfDProject:
    """Tests for individual CfD project behavior."""

    def test_strike_price_inflation(self):
        """Strike prices should be inflated from 2012 to current money."""
        project = CfDProject(
            cfd_id='TEST-001',
            name='Test Project',
            allocation_round='Allocation Round 1',
            technology='Offshore Wind',
            capacity_mw=500,
            status='Live (Post-FIC)',
        )

        # AR1 offshore strike is £117.14 in 2012 money
        assert project.strike_price_2012 == 117.14
        # In 2025 money with 1.47x inflation
        expected_current = 117.14 * INFLATION_MULTIPLIER_2012_TO_2025
        assert abs(project.strike_price_current - expected_current) < 0.01

    def test_project_active_status(self):
        """Terminated projects should not be active."""
        live_project = CfDProject(
            cfd_id='LIVE-001',
            name='Live Project',
            allocation_round='Allocation Round 1',
            technology='Solar PV',
            capacity_mw=50,
            status='Live (Post-FIC)',
        )
        assert live_project.is_active is True

        terminated_project = CfDProject(
            cfd_id='TERM-001',
            name='Terminated Project',
            allocation_round='Allocation Round 1',
            technology='Solar PV',
            capacity_mw=50,
            status='Terminated',
        )
        assert terminated_project.is_active is False

    def test_project_active_in_year_with_start_date(self):
        """Projects should be active from start date to start + contract length."""
        project = CfDProject(
            cfd_id='TEST-001',
            name='Test Project',
            allocation_round='Allocation Round 4',
            technology='Solar PV',
            capacity_mw=50,
            status='Pre-Start Date',
            expected_start_date=datetime(2026, 1, 1),
        )

        # Contract is 15 years, so active 2026-2040
        assert project.is_active_in_year(2025) is False  # Before start
        assert project.is_active_in_year(2026) is True   # Start year
        assert project.is_active_in_year(2030) is True   # Mid contract
        assert project.is_active_in_year(2040) is True   # Last year
        assert project.is_active_in_year(2041) is False  # After expiry

    def test_nuclear_contract_length(self):
        """Nuclear projects have 35-year contracts."""
        nuclear = CfDProject(
            cfd_id='NUC-001',
            name='Hinkley Point C',
            allocation_round='Bespoke',
            technology='Nuclear',
            capacity_mw=3287,
            status='Pre-MDD',
            expected_start_date=datetime(2030, 1, 1),
        )
        assert nuclear.contract_length == 35

        # Should be active 2030-2064
        assert nuclear.is_active_in_year(2029) is False
        assert nuclear.is_active_in_year(2030) is True
        assert nuclear.is_active_in_year(2060) is True
        assert nuclear.is_active_in_year(2065) is False


class TestCfDPortfolio:
    """Tests for portfolio-level calculations."""

    def test_portfolio_loads_from_csv(self):
        """Portfolio should load real data from CSV."""
        portfolio = CfDPortfolio()
        assert len(portfolio.projects) > 0
        # Should have projects from multiple ARs
        allocation_rounds = set(p.allocation_round for p in portfolio.projects)
        assert 'Allocation Round 1' in allocation_rounds
        assert 'Allocation Round 6' in allocation_rounds

    def test_2025_matches_article_data(self):
        """2025 portfolio should roughly match article's figures."""
        portfolio = CfDPortfolio()
        state = portfolio.get_portfolio_state(2025)

        # Article says ~£151/MWh weighted average, ~12% demand coverage
        # Allow 20% tolerance for data differences
        assert 120 < state.avg_strike_all < 180  # Around £151
        assert 0.08 < state.estimated_demand_coverage < 0.20  # Around 12%

    def test_2030_coverage_increases(self):
        """By 2030, CfD coverage should be higher than 2025."""
        portfolio = CfDPortfolio()
        state_2025 = portfolio.get_portfolio_state(2025)
        state_2030 = portfolio.get_portfolio_state(2030)

        # Coverage should roughly triple (article says 40% by 2031)
        assert state_2030.estimated_demand_coverage > state_2025.estimated_demand_coverage * 2

    def test_strike_price_falls_over_time(self):
        """Weighted average strike should fall as old contracts expire."""
        portfolio = CfDPortfolio()
        state_2025 = portfolio.get_portfolio_state(2025)
        state_2035 = portfolio.get_portfolio_state(2035)

        # Old AR1/AR2/Investment contracts (~£150+) expire by 2035
        # Replaced by AR4-AR6 (~£70-90)
        assert state_2035.avg_strike_all < state_2025.avg_strike_all

    def test_ar1_expires_around_2033(self):
        """AR1 contracts (started ~2018) should mostly expire by 2033-2035."""
        portfolio = CfDPortfolio()
        state_2030 = portfolio.get_portfolio_state(2030)
        state_2035 = portfolio.get_portfolio_state(2035)

        ar1_2030 = state_2030.projects_by_ar.get('Allocation Round 1', {}).get('capacity_gw', 0)
        ar1_2035 = state_2035.projects_by_ar.get('Allocation Round 1', {}).get('capacity_gw', 0)

        # AR1 capacity should be significantly lower in 2035
        assert ar1_2035 < ar1_2030 * 0.5

    def test_hinkley_point_c_included(self):
        """Hinkley Point C should be included in nuclear capacity."""
        portfolio = CfDPortfolio()
        # HPC expected online around 2030
        state_2030 = portfolio.get_portfolio_state(2030)

        # Should have ~3.3 GW nuclear
        assert state_2030.nuclear_gw > 3.0

    def test_portfolio_evolution(self):
        """Portfolio evolution should return states for range of years."""
        portfolio = CfDPortfolio()
        evolution = portfolio.get_portfolio_evolution(2025, 2035)

        assert len(evolution) == 11  # 2025-2035 inclusive
        assert evolution[0].year == 2025
        assert evolution[-1].year == 2035


class TestCfDPortfolioState:
    """Tests for portfolio state calculations."""

    def test_total_capacity(self):
        """Total capacity should sum all technologies."""
        state = CfDPortfolioState(
            year=2030,
            offshore_wind_gw=10.0,
            onshore_wind_gw=5.0,
            solar_gw=3.0,
            nuclear_gw=3.3,
            other_gw=1.0,
        )
        assert state.total_capacity_gw == 22.3

    def test_estimated_generation(self):
        """Generation estimate should use capacity factors."""
        state = CfDPortfolioState(
            year=2030,
            offshore_wind_gw=10.0,  # 40% CF = 35 TWh
            onshore_wind_gw=0.0,
            solar_gw=0.0,
            nuclear_gw=0.0,
            other_gw=0.0,
        )
        # 10 GW * 0.40 CF * 8760 hours / 1000 = 35.04 TWh
        expected = 10 * 0.40 * 8.76
        assert abs(state.estimated_generation_twh - expected) < 0.1


class TestStrikePriceData:
    """Tests for strike price data integrity."""

    def test_all_ars_have_strike_prices(self):
        """All allocation rounds should have strike price data."""
        expected_ars = [
            'Allocation Round 1',
            'Allocation Round 2',
            'Allocation Round 3',
            'Allocation Round 4',
            'Allocation Round 5',
            'Allocation Round 6',
        ]
        for ar in expected_ars:
            assert ar in AR_STRIKE_PRICES_2012

    def test_offshore_prices_decline_ar1_to_ar3(self):
        """Offshore wind prices fell dramatically from AR1 to AR3."""
        ar1_offshore = AR_STRIKE_PRICES_2012['Allocation Round 1']['Offshore Wind']
        ar3_offshore = AR_STRIKE_PRICES_2012['Allocation Round 3']['Offshore Wind']

        # AR1 ~£117, AR3 ~£40 (in 2012 prices)
        assert ar1_offshore > ar3_offshore * 2

    def test_ar6_prices_higher_than_ar3_ar4(self):
        """AR6 offshore prices rose from AR3/AR4 lows."""
        ar3_offshore = AR_STRIKE_PRICES_2012['Allocation Round 3']['Offshore Wind']
        ar6_offshore = AR_STRIKE_PRICES_2012['Allocation Round 6']['Offshore Wind']

        # AR6 ~£59 vs AR3 ~£40 (in 2012 prices)
        assert ar6_offshore > ar3_offshore
