"""
Unit tests for Contracts for Difference (CfD) module.

Tests CfD contract calculations, portfolio management, and cost simulation.
"""
import pytest
from src.cfd import (
    CfDContract, CfDPortfolio, CfDPaymentResult, LCCCSimulationResult,
    simulate_cfd_costs, create_cfd_portfolio_for_fleet,
    CURRENT_STRIKE_PRICES, UK_CFD_STRIKE_PRICES
)
from src.grid import DispatchResult
from src.generators import (
    SolarGenerator, OnshoreWindGenerator, OffshoreWindGenerator,
    GasGenerator
)


class TestCfDContract:
    """Tests for CfDContract class."""
    
    def test_cfd_contract_creation(self):
        """Test creating a CfD contract."""
        contract = CfDContract(
            generator_name="Solar Farm",
            strike_price=50.0,
            capacity_mw=100.0
        )
        
        assert contract.generator_name == "Solar Farm"
        assert contract.strike_price == 50.0
        assert contract.capacity_mw == 100.0
        assert contract.contract_length_years == 15  # Default
    
    def test_cfd_payment_when_wholesale_below_strike(self):
        """Test top-up payment when wholesale < strike."""
        contract = CfDContract(
            generator_name="Solar",
            strike_price=50.0,
            capacity_mw=100.0
        )
        
        # Wholesale price below strike -> LCCC pays generator
        payment = contract.calculate_payment(wholesale_price=30.0, generation_mwh=100.0)
        
        assert payment > 0  # Positive = subsidy
        assert payment == (50.0 - 30.0) * 100.0  # £2000
    
    def test_cfd_payment_when_wholesale_above_strike(self):
        """Test clawback payment when wholesale > strike."""
        contract = CfDContract(
            generator_name="Solar",
            strike_price=50.0,
            capacity_mw=100.0
        )
        
        # Wholesale price above strike -> Generator pays LCCC
        payment = contract.calculate_payment(wholesale_price=70.0, generation_mwh=100.0)
        
        assert payment < 0  # Negative = clawback
        assert payment == (50.0 - 70.0) * 100.0  # -£2000
    
    def test_cfd_payment_when_wholesale_equals_strike(self):
        """Test no payment when wholesale = strike."""
        contract = CfDContract(
            generator_name="Solar",
            strike_price=50.0,
            capacity_mw=100.0
        )
        
        payment = contract.calculate_payment(wholesale_price=50.0, generation_mwh=100.0)
        
        assert payment == 0.0


class TestCfDPortfolio:
    """Tests for CfDPortfolio class."""
    
    def test_portfolio_creation(self):
        """Test creating an empty portfolio."""
        portfolio = CfDPortfolio()
        
        assert len(portfolio.contracts) == 0
        assert portfolio.total_contracted_capacity_gw == 0.0
    
    def test_add_contract(self):
        """Test adding contracts to portfolio."""
        portfolio = CfDPortfolio()
        
        contract1 = CfDContract("Solar", strike_price=50.0, capacity_mw=100.0)
        contract2 = CfDContract("Wind", strike_price=55.0, capacity_mw=200.0)
        
        portfolio.add_contract(contract1)
        portfolio.add_contract(contract2)
        
        assert len(portfolio.contracts) == 2
        assert portfolio.total_contracted_capacity_gw == 0.3  # 300 MW = 0.3 GW
    
    def test_get_contract_for_generator(self):
        """Test finding contract by generator name."""
        portfolio = CfDPortfolio()
        
        contract = CfDContract("UK Solar", strike_price=50.0, capacity_mw=100.0)
        portfolio.add_contract(contract)
        
        # Should find by partial match
        found = portfolio.get_contract_for_generator("UK Solar")
        assert found is not None
        assert found.strike_price == 50.0
        
        # Should not find non-matching generator
        not_found = portfolio.get_contract_for_generator("Gas CCGT")
        assert not_found is None


class TestSimulateCfDCosts:
    """Tests for simulate_cfd_costs function."""
    
    def test_simulate_with_subsidy(self):
        """Test simulation when wholesale prices are below strike prices."""
        # Create generators
        solar = SolarGenerator(name="Solar", capacity_mw=1000)
        
        # Create CfD contract
        portfolio = CfDPortfolio()
        contract = CfDContract("Solar", strike_price=50.0, capacity_mw=1000.0)
        portfolio.add_contract(contract)
        
        # Create dispatch results with low wholesale prices
        results = []
        for hour in range(24):
            # Low wholesale price (below strike)
            result = DispatchResult(
                hour=hour,
                day_of_year=180,
                demand_mw=50000,
                wholesale_price=30.0,  # Below strike of 50.0
                dispatched_generators=[(solar, 500.0)],  # 500 MW solar
                total_generation_mw=50000,
                price_setter=solar,
                curtailment_mw=0.0
            )
            results.append(result)
        
        cfd_result = simulate_cfd_costs(results, portfolio)
        
        # Should have net subsidy (top-up > clawback)
        assert cfd_result.net_cfd_cost > 0
        assert cfd_result.total_topup_payments > 0
        assert cfd_result.total_clawback_payments == 0
    
    def test_simulate_with_clawback(self):
        """Test simulation when wholesale prices are above strike prices."""
        solar = SolarGenerator(name="Solar", capacity_mw=1000)
        
        portfolio = CfDPortfolio()
        contract = CfDContract("Solar", strike_price=50.0, capacity_mw=1000.0)
        portfolio.add_contract(contract)
        
        # Create dispatch results with high wholesale prices
        results = []
        for hour in range(24):
            result = DispatchResult(
                hour=hour,
                day_of_year=180,
                demand_mw=50000,
                wholesale_price=70.0,  # Above strike of 50.0
                dispatched_generators=[(solar, 500.0)],
                total_generation_mw=50000,
                price_setter=solar,
                curtailment_mw=0.0
            )
            results.append(result)
        
        cfd_result = simulate_cfd_costs(results, portfolio)
        
        # Should have net clawback (generators pay back)
        assert cfd_result.net_cfd_cost < 0
        assert cfd_result.total_clawback_payments > 0
        assert cfd_result.total_topup_payments == 0
    
    def test_simulate_mixed_prices(self):
        """Test simulation with mixed wholesale prices."""
        solar = SolarGenerator(name="Solar", capacity_mw=1000)
        
        portfolio = CfDPortfolio()
        contract = CfDContract("Solar", strike_price=50.0, capacity_mw=1000.0)
        portfolio.add_contract(contract)
        
        # Mix of prices above and below strike
        # More hours below strike (30, 40) than above (60, 70) to ensure net positive
        prices = [30.0, 30.0, 40.0, 40.0, 50.0, 60.0, 70.0] * 4  # 28 hours, weighted toward lower prices
        results = []
        for i, price in enumerate(prices):
            result = DispatchResult(
                hour=i % 24,
                day_of_year=180,
                demand_mw=50000,
                wholesale_price=price,
                dispatched_generators=[(solar, 500.0)],
                total_generation_mw=50000,
                price_setter=solar,
                curtailment_mw=0.0
            )
            results.append(result)
        
        cfd_result = simulate_cfd_costs(results, portfolio)
        
        # Should have both top-up and clawback
        assert cfd_result.total_topup_payments > 0
        assert cfd_result.total_clawback_payments > 0
        
        # Net cost depends on balance
        # With more hours below strike (30, 40) than above (60, 70), net should be positive
        assert cfd_result.net_cfd_cost > 0
    
    def test_subsidy_per_mwh_consumed(self):
        """Test calculation of subsidy per MWh consumed."""
        solar = SolarGenerator(name="Solar", capacity_mw=1000)
        
        portfolio = CfDPortfolio()
        contract = CfDContract("Solar", strike_price=50.0, capacity_mw=1000.0)
        portfolio.add_contract(contract)
        
        results = []
        total_demand = 0
        for hour in range(24):
            demand = 50000
            total_demand += demand
            result = DispatchResult(
                hour=hour,
                day_of_year=180,
                demand_mw=demand,
                wholesale_price=30.0,
                dispatched_generators=[(solar, 500.0)],
                total_generation_mw=demand,
                price_setter=solar,
                curtailment_mw=0.0
            )
            results.append(result)
        
        cfd_result = simulate_cfd_costs(results, portfolio)
        
        # Subsidy per MWh should be positive
        assert cfd_result.subsidy_per_mwh_consumed > 0
        
        # Should equal net cost / total demand
        expected = cfd_result.net_cfd_cost / total_demand
        assert cfd_result.subsidy_per_mwh_consumed == pytest.approx(expected)


class TestCreateCfDPortfolioForFleet:
    """Tests for create_cfd_portfolio_for_fleet function."""
    
    def test_create_portfolio_for_renewables_only(self):
        """Test that only RE generators get CfD contracts."""
        generators = [
            SolarGenerator(name="Solar", capacity_mw=1000),
            OnshoreWindGenerator(name="Onshore Wind", capacity_mw=2000),
            OffshoreWindGenerator(name="Offshore Wind", capacity_mw=3000),
            GasGenerator(name="Gas", capacity_mw=5000, marginal_cost_per_mwh=73.0)
        ]
        
        portfolio = create_cfd_portfolio_for_fleet(generators, coverage=1.0)
        
        # Should have contracts for RE only (solar, onshore, offshore)
        assert len(portfolio.contracts) == 3
        
        # Gas should not have a contract
        contract_names = [c.generator_name for c in portfolio.contracts]
        assert "Gas" not in contract_names
    
    def test_coverage_parameter(self):
        """Test that coverage parameter affects contracted capacity."""
        generators = [
            SolarGenerator(name="Solar", capacity_mw=1000)
        ]
        
        # 50% coverage
        portfolio_50 = create_cfd_portfolio_for_fleet(generators, coverage=0.5)
        assert len(portfolio_50.contracts) == 1
        assert portfolio_50.contracts[0].capacity_mw == 500.0
        
        # 100% coverage
        portfolio_100 = create_cfd_portfolio_for_fleet(generators, coverage=1.0)
        assert portfolio_100.contracts[0].capacity_mw == 1000.0
    
    def test_custom_strike_prices(self):
        """Test using custom strike prices."""
        generators = [
            SolarGenerator(name="Solar", capacity_mw=1000),
            OffshoreWindGenerator(name="Offshore Wind", capacity_mw=2000)
        ]
        
        custom_strikes = {
            'solar': 45.0,
            'offshore_wind': 55.0
        }
        
        portfolio = create_cfd_portfolio_for_fleet(
            generators,
            coverage=1.0,
            strike_prices=custom_strikes
        )
        
        # Check strike prices are set correctly
        for contract in portfolio.contracts:
            if 'Solar' in contract.generator_name:
                assert contract.strike_price == 45.0
            elif 'Offshore' in contract.generator_name:
                assert contract.strike_price == 55.0
    
    def test_default_strike_prices(self):
        """Test that default strike prices are used when not specified."""
        generators = [
            SolarGenerator(name="Solar", capacity_mw=1000)
        ]
        
        portfolio = create_cfd_portfolio_for_fleet(generators, coverage=1.0)
        
        # Should use CURRENT_STRIKE_PRICES defaults
        assert portfolio.contracts[0].strike_price == CURRENT_STRIKE_PRICES['solar']


class TestLCCCSimulationResult:
    """Tests for LCCCSimulationResult dataclass."""
    
    def test_annual_household_cost(self):
        """Test calculation of annual household cost."""
        result = LCCCSimulationResult(
            period_hours=8760,  # 1 year
            total_demand_mwh=300000,  # 300 TWh
            total_re_generation_mwh=150000,
            total_topup_payments=1000000000,  # £1bn
            total_clawback_payments=0,
            net_cfd_cost=1000000000,
            average_wholesale_price=50.0,
            average_re_capture_price=45.0,
            payments_by_source={},
            generation_by_source={}
        )
        
        # Subsidy per MWh = £1bn / 300 TWh = £3.33/MWh
        # Annual household (2.7 MWh) = £3.33 * 2.7 = £9.00
        annual_cost = result.annual_household_cost
        
        assert annual_cost > 0
        # Should be approximately correct (allowing for rounding)
        expected = (1000000000 / 300000) * 2.7
        assert annual_cost == pytest.approx(expected, rel=0.1)
    
    def test_re_share_calculation(self):
        """Test RE share calculation."""
        result = LCCCSimulationResult(
            period_hours=100,
            total_demand_mwh=1000,
            total_re_generation_mwh=600,  # 60% RE
            total_topup_payments=0,
            total_clawback_payments=0,
            net_cfd_cost=0,
            average_wholesale_price=50.0,
            average_re_capture_price=45.0,
            payments_by_source={},
            generation_by_source={}
        )
        
        assert result.re_share == 0.6
    
    def test_re_share_zero_demand(self):
        """Test RE share when demand is zero."""
        result = LCCCSimulationResult(
            period_hours=100,
            total_demand_mwh=0,
            total_re_generation_mwh=0,
            total_topup_payments=0,
            total_clawback_payments=0,
            net_cfd_cost=0,
            average_wholesale_price=0.0,
            average_re_capture_price=0.0,
            payments_by_source={},
            generation_by_source={}
        )
        
        assert result.re_share == 0.0

