"""
RO Portfolio Modeling - Time-based analysis of UK Renewables Obligation contracts.

Models how the RO portfolio evolves over time, including contract expiry.
RO closed to new applicants in 2017, but existing generators continue until 2037.

Data sources:
- Ofgem RO accredited stations (if available)
- Estimated RO capacity by technology and accreditation year
"""

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from datetime import datetime


# RO contract length (years from accreditation)
# Most RO projects: 20 years, but can vary
DEFAULT_RO_CONTRACT_LENGTH = 20

# RO closed to new applicants
RO_CLOSURE_YEAR = 2017
RO_FINAL_EXPIRY_YEAR = 2037  # Last projects expire by 2037

# ROC values by year (£/MWh)
# ROC value = nominal ROC value per ROC × ROCs per MWh
# Generators typically receive 1 ROC per MWh (or more for some technologies)
# 
# 2024-2025: Nominal ROC value £73.71/ROC (buy-out £64.73 + recycling)
# For 1 ROC/MWh technologies: £73.71/MWh
# 
# Note: This is the value generators receive, which is higher than the obligation
# cost to suppliers (which is based on obligation level, not ROC value)
ROC_VALUES_BY_YEAR = {
    2024: 73.71,  # 2024-2025: Nominal ROC value £73.71/ROC = £73.71/MWh (1 ROC/MWh)
    2025: 73.71,  # 2024-2025 period continues
    2026: 75.0,   # Estimated with inflation
    2030: 80.0,   # Estimated future value
    2035: 85.0,
}


@dataclass
class ROProject:
    """A single RO-accredited project/station."""
    ro_id: str
    name: str
    technology: str
    capacity_mw: float
    accreditation_year: int  # Year project was accredited under RO
    status: str  # 'Active', 'Closed', etc.
    
    @property
    def is_active(self) -> bool:
        """Project is active (not closed/terminated)."""
        return self.status != 'Closed' and self.status != 'Terminated'
    
    @property
    def contract_length(self) -> int:
        """Contract duration in years (typically 20)."""
        return DEFAULT_RO_CONTRACT_LENGTH
    
    @property
    def expiry_year(self) -> int:
        """Year when RO support ends."""
        return self.accreditation_year + self.contract_length
    
    def is_active_in_year(self, year: int) -> bool:
        """Check if this project is active (receiving RO support) in a given year."""
        if not self.is_active:
            return False
        
        # RO closed in 2017, so no new projects after that
        if self.accreditation_year > RO_CLOSURE_YEAR:
            return False
        
        # Project is active if year is between accreditation and expiry
        return self.accreditation_year <= year < self.expiry_year
    
    def get_roc_value(self, year: int) -> float:
        """Get ROC value for a given year."""
        # Use year-specific value if available, otherwise interpolate or use default
        if year in ROC_VALUES_BY_YEAR:
            return ROC_VALUES_BY_YEAR[year]
        
        # Interpolate between known years
        known_years = sorted(ROC_VALUES_BY_YEAR.keys())
        if year < known_years[0]:
            return ROC_VALUES_BY_YEAR[known_years[0]]
        if year > known_years[-1]:
            return ROC_VALUES_BY_YEAR[known_years[-1]]
        
        # Find surrounding years
        for i in range(len(known_years) - 1):
            if known_years[i] <= year < known_years[i + 1]:
                y1, y2 = known_years[i], known_years[i + 1]
                v1, v2 = ROC_VALUES_BY_YEAR[y1], ROC_VALUES_BY_YEAR[y2]
                # Linear interpolation
                return v1 + (v2 - v1) * (year - y1) / (y2 - y1)
        
        return 45.0  # Default fallback


@dataclass
class ROPortfolioState:
    """The state of the RO portfolio at a specific year."""
    year: int
    
    # Coverage percentages (0-1) - what fraction of each technology is covered by RO
    solar_coverage: float = 0.0
    onshore_wind_coverage: float = 0.0
    offshore_wind_coverage: float = 0.0
    
    # Weighted average ROC value (£/MWh)
    avg_roc_value: float = 73.71  # 2024-2025: Nominal ROC value
    
    # Active projects by accreditation period
    projects_by_period: dict = field(default_factory=dict)
    
    def estimated_re_coverage(self, solar_capacity_gw: float, onshore_wind_capacity_gw: float,
                             offshore_wind_capacity_gw: float) -> float:
        """
        Estimate what fraction of RE generation is covered by RO.
        
        Args:
            solar_capacity_gw: User's solar capacity setting
            onshore_wind_capacity_gw: User's onshore wind capacity setting
            offshore_wind_capacity_gw: User's offshore wind capacity setting
            
        Returns:
            Fraction of RE generation covered by RO (0-1)
        """
        total_re_capacity_gw = solar_capacity_gw + onshore_wind_capacity_gw + offshore_wind_capacity_gw
        if total_re_capacity_gw <= 0:
            return 0.0
        
        # Estimate total RE generation using capacity factors
        total_re_gen_twh = (
            solar_capacity_gw * 0.11 * 8.76 +
            onshore_wind_capacity_gw * 0.27 * 8.76 +
            offshore_wind_capacity_gw * 0.40 * 8.76
        )
        
        # RO RE generation (using coverage percentages)
        ro_re_gen_twh = (
            solar_capacity_gw * self.solar_coverage * 0.11 * 8.76 +
            onshore_wind_capacity_gw * self.onshore_wind_coverage * 0.27 * 8.76 +
            offshore_wind_capacity_gw * self.offshore_wind_coverage * 0.40 * 8.76
        )
        
        if total_re_gen_twh <= 0:
            return 0.0
        
        return min(ro_re_gen_twh / total_re_gen_twh, 1.0)
    
    def get_ro_capacity_gw(self, solar_capacity_gw: float, onshore_wind_capacity_gw: float,
                          offshore_wind_capacity_gw: float) -> dict:
        """
        Calculate actual RO capacity in GW based on user's capacity settings.
        
        Args:
            solar_capacity_gw: User's solar capacity setting
            onshore_wind_capacity_gw: User's onshore wind capacity setting
            offshore_wind_capacity_gw: User's offshore wind capacity setting
            
        Returns:
            Dict with 'solar_gw', 'onshore_wind_gw', 'offshore_wind_gw', 'total_gw'
        """
        return {
            'solar_gw': solar_capacity_gw * self.solar_coverage,
            'onshore_wind_gw': onshore_wind_capacity_gw * self.onshore_wind_coverage,
            'offshore_wind_gw': offshore_wind_capacity_gw * self.offshore_wind_coverage,
            'total_gw': (
                solar_capacity_gw * self.solar_coverage +
                onshore_wind_capacity_gw * self.onshore_wind_coverage +
                offshore_wind_capacity_gw * self.offshore_wind_coverage
            )
        }


class ROPortfolioManager:
    """
    Manager for the UK RO portfolio.
    
    Models RO-accredited projects with varying accreditation dates and expiry.
    RO closed to new applicants in 2017, projects expire 20 years after accreditation.
    """
    
    def __init__(self, csv_path: Optional[Path] = None):
        """
        Initialize portfolio from Ofgem RO data (if available) or estimated data.
        
        Args:
            csv_path: Path to RO accredited stations CSV
                     If None, uses estimated data based on historical RO capacity.
        """
        self.projects: list[ROProject] = []
        self._cached_evolution: Optional[dict[int, ROPortfolioState]] = None
        
        if csv_path and csv_path.exists():
            self._load_from_csv(csv_path)
        else:
            # Use estimated RO capacity data
            self._load_estimated_data()
    
    def _load_from_csv(self, csv_path: Path):
        """Load project data from Ofgem RO CSV (if available)."""
        # This would load actual RO data if CSV is available
        # For now, fall back to estimated data
        self._load_estimated_data()
    
    def _load_estimated_data(self):
        """
        Load estimated RO project data based on historical RO capacity.
        
        RO supported significant capacity, with most projects accredited between
        2002-2017. Projects expire 20 years after accreditation.
        
        Estimated RO capacity in 2025:
        - RO supported ~31.5% of UK electricity supply in 2023-2024 (Ofgem data)
        - RO + FIT + CfD together = 43.8% of UK electricity supply
        - Renewables = 46.4% of UK supply in 2023, so RO coverage of renewables ≈ 67.9%
        - For wind/solar specifically: ~10 GW solar, ~10 GW onshore wind, ~1 GW offshore
        - Model estimates ~30% of renewable generation (wind/solar) covered by RO in 2025
        - Note: Model's 30% is lower than real-world 67.9% because RO also supports biomass, 
          hydro, and other technologies not modeled here. The 30% represents RO's wind/solar portion.
        """
        # Create estimated projects with varying accreditation years
        # This models the gradual expiry of RO projects
        
        # Solar RO projects (accredited 2010-2017, expiring 2030-2037)
        # Estimated total: ~10 GW in 2025
        # RO supported 31.5% of UK supply in 2023-2024
        # Most solar capacity built 2010-2017 was under RO (RO closed to new applicants in 2017)
        # Target: ~65% of solar capacity under RO
        solar_projects = [
            # Early solar (2010-2013) - expiring 2030-2033
            ROProject(ro_id='SOL_EST_2010', name='Estimated Solar 2010', technology='Solar PV',
                     capacity_mw=2000, accreditation_year=2010, status='Active'),
            ROProject(ro_id='SOL_EST_2011', name='Estimated Solar 2011', technology='Solar PV',
                     capacity_mw=2500, accreditation_year=2011, status='Active'),
            ROProject(ro_id='SOL_EST_2012', name='Estimated Solar 2012', technology='Solar PV',
                     capacity_mw=3000, accreditation_year=2012, status='Active'),
            # Later solar (2014-2017) - expiring 2034-2037
            ROProject(ro_id='SOL_EST_2014', name='Estimated Solar 2014', technology='Solar PV',
                     capacity_mw=1500, accreditation_year=2014, status='Active'),
            ROProject(ro_id='SOL_EST_2015', name='Estimated Solar 2015', technology='Solar PV',
                     capacity_mw=1000, accreditation_year=2015, status='Active'),
        ]
        
        # Onshore Wind RO projects (accredited 2002-2017, expiring 2022-2037)
        # Estimated total: ~10 GW in 2025
        # Onshore wind was the dominant RO technology; most onshore capacity pre-2017 was under RO
        # Target: ~70% of onshore capacity under RO (critical for overall coverage due to high capacity factor)
        onshore_projects = [
            # Early onshore (2002-2005) - expiring 2022-2025
            ROProject(ro_id='ON_EST_2002', name='Estimated Onshore 2002', technology='Onshore Wind',
                     capacity_mw=3000, accreditation_year=2002, status='Active'),
            ROProject(ro_id='ON_EST_2003', name='Estimated Onshore 2003', technology='Onshore Wind',
                     capacity_mw=3500, accreditation_year=2003, status='Active'),
            ROProject(ro_id='ON_EST_2004', name='Estimated Onshore 2004', technology='Onshore Wind',
                     capacity_mw=4000, accreditation_year=2004, status='Active'),
            # Mid-period onshore (2006-2010) - expiring 2026-2030
            ROProject(ro_id='ON_EST_2006', name='Estimated Onshore 2006', technology='Onshore Wind',
                     capacity_mw=3000, accreditation_year=2006, status='Active'),
            ROProject(ro_id='ON_EST_2007', name='Estimated Onshore 2007', technology='Onshore Wind',
                     capacity_mw=2500, accreditation_year=2007, status='Active'),
            ROProject(ro_id='ON_EST_2008', name='Estimated Onshore 2008', technology='Onshore Wind',
                     capacity_mw=2000, accreditation_year=2008, status='Active'),
        ]
        
        # Offshore Wind RO projects (early projects, most moved to CfD)
        # Estimated total: ~2.5 GW in 2025 (early offshore projects)
        # Most offshore capacity moved to CfD, but early projects remain under RO
        offshore_projects = [
            ROProject(ro_id='OFF_EST_2005', name='Estimated Offshore 2005', technology='Offshore Wind',
                     capacity_mw=1500, accreditation_year=2005, status='Active'),
            ROProject(ro_id='OFF_EST_2006', name='Estimated Offshore 2006', technology='Offshore Wind',
                     capacity_mw=1000, accreditation_year=2006, status='Active'),
        ]
        
        self.projects = solar_projects + onshore_projects + offshore_projects
    
    def get_portfolio_state(self, year: int) -> ROPortfolioState:
        """
        Calculate portfolio state for a given year.
        
        Args:
            year: Simulation year (e.g., 2025, 2030, 2050)
            
        Returns:
            ROPortfolioState with coverage percentages and ROC value
        """
        # Check cache
        if self._cached_evolution and year in self._cached_evolution:
            return self._cached_evolution[year]
        
        state = self._calculate_portfolio_state(year)
        
        # Cache result
        if self._cached_evolution is None:
            self._cached_evolution = {}
        self._cached_evolution[year] = state
        
        return state
    
    def _calculate_portfolio_state(self, year: int) -> ROPortfolioState:
        """
        Calculate raw portfolio state for a given year.
        """
        state = ROPortfolioState(year=year)
        
        # Track absolute capacity from active projects
        solar_cap_gw = 0.0
        onshore_cap_gw = 0.0
        offshore_cap_gw = 0.0
        
        # Track ROC values weighted by capacity
        solar_roc_sum = 0.0
        onshore_roc_sum = 0.0
        offshore_roc_sum = 0.0
        
        projects_by_period = {}
        
        for project in self.projects:
            if not project.is_active_in_year(year):
                continue
            
            cap_gw = project.capacity_mw / 1000
            roc_value = project.get_roc_value(year)
            
            # Track by accreditation period (grouped by 5-year periods)
            period = (project.accreditation_year // 5) * 5
            if period not in projects_by_period:
                projects_by_period[period] = {'count': 0, 'capacity_gw': 0.0}
            projects_by_period[period]['count'] += 1
            projects_by_period[period]['capacity_gw'] += cap_gw
            
            # Categorize by technology
            tech = project.technology
            if 'Solar' in tech or 'PV' in tech:
                solar_cap_gw += cap_gw
                solar_roc_sum += cap_gw * roc_value
            elif 'Onshore' in tech:
                onshore_cap_gw += cap_gw
                onshore_roc_sum += cap_gw * roc_value
            elif 'Offshore' in tech:
                offshore_cap_gw += cap_gw
                offshore_roc_sum += cap_gw * roc_value
        
        # Convert absolute GW to percentages based on estimated UK capacity
        uk_cap = self._estimate_uk_capacity_by_year(year)
        
        # Calculate coverage percentages
        state.solar_coverage = min(1.0, solar_cap_gw / uk_cap['solar_gw']) if uk_cap['solar_gw'] > 0 else 0.0
        state.onshore_wind_coverage = min(1.0, onshore_cap_gw / uk_cap['onshore_wind_gw']) if uk_cap['onshore_wind_gw'] > 0 else 0.0
        state.offshore_wind_coverage = min(1.0, offshore_cap_gw / uk_cap['offshore_wind_gw']) if uk_cap['offshore_wind_gw'] > 0 else 0.0
        
        # Calculate weighted average ROC value
        total_cap = solar_cap_gw + onshore_cap_gw + offshore_cap_gw
        total_roc_sum = solar_roc_sum + onshore_roc_sum + offshore_roc_sum
        state.avg_roc_value = total_roc_sum / total_cap if total_cap > 0 else ROC_VALUES_BY_YEAR.get(year, 73.71)
        
        state.projects_by_period = projects_by_period
        
        return state
    
    def _estimate_uk_capacity_by_year(self, year: int) -> dict:
        """
        Estimate UK RE capacity for a given year (for converting absolute GW to percentages).
        Returns dict with 'solar_gw', 'onshore_wind_gw', 'offshore_wind_gw'
        """
        base_2025 = {'solar_gw': 15.5, 'onshore_wind_gw': 14.8, 'offshore_wind_gw': 14.7}
        years_from_2025 = year - 2025
        
        return {
            'solar_gw': max(0, base_2025['solar_gw'] + years_from_2025 * 2.0),
            'onshore_wind_gw': max(0, base_2025['onshore_wind_gw'] + years_from_2025 * 1.0),
            'offshore_wind_gw': max(0, base_2025['offshore_wind_gw'] + years_from_2025 * 3.0),
        }
    
    def get_portfolio_evolution(self, start_year: int = 2025, end_year: int = 2050) -> list[ROPortfolioState]:
        """
        Calculate portfolio state for a range of years.
        
        Returns:
            List of ROPortfolioState for each year
        """
        return [self.get_portfolio_state(year) for year in range(start_year, end_year + 1)]


def create_ro_portfolio_with_estimates() -> ROPortfolioManager:
    """
    Create an RO portfolio manager with estimated project data.
    
    This provides a realistic model of RO projects expiring over time.
    
    Returns:
        ROPortfolioManager with estimated projects
    """
    return ROPortfolioManager()

