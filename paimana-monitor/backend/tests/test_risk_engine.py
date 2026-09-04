"""
Unit Tests — Risk Engine
Tests normalizer, feature engineering, rules, and scoring.
Run: cd backend && pytest tests/ -v
"""
import pytest
from datetime import date

from app.ingestion.normalizer import (
    normalize_cost, normalize_date, normalize_percentage, normalize_status,
)
from app.risk.config import RiskConfig
from app.risk.features import compute_features
from app.risk.rules import evaluate_rules
from app.risk.scoring import (
    compute_financial_health, compute_overall_health,
    compute_progress_health, compute_schedule_health,
    risk_level_from_health,
)
from app.models.orm import RiskLevel


# ─── Normalizer Tests ─────────────────────────────────────────────────────────

class TestNormalizeCost:
    def test_plain_number(self):
        assert normalize_cost("28500.00") == 28500.00

    def test_crore_suffix(self):
        assert normalize_cost("18.5 Cr") == pytest.approx(18.5 * 100, rel=1e-3)

    def test_lakh_suffix(self):
        assert normalize_cost("1250 Lakhs") == 1250.0

    def test_rupee_prefix(self):
        assert normalize_cost("₹1,234.56") == pytest.approx(1234.56, rel=1e-3)

    def test_with_commas(self):
        assert normalize_cost("1,84,000") == pytest.approx(184000.0, rel=1e-3)

    def test_crore_lowercase(self):
        assert normalize_cost("95.0crores") == pytest.approx(95.0 * 100, rel=1e-3)

    def test_none_input(self):
        assert normalize_cost(None) is None

    def test_na_string(self):
        assert normalize_cost("N/A") is None

    def test_negative_returns_negative(self):
        # Negative values — validator will catch these, normalizer just converts
        assert normalize_cost("-100") == -100.0


class TestNormalizePercentage:
    def test_plain_percent(self):
        assert normalize_percentage("68.52") == 68.52

    def test_percent_sign(self):
        assert normalize_percentage("68%") == 68.0

    def test_decimal_proportion(self):
        # 0.685 → 68.5
        assert normalize_percentage("0.685") == pytest.approx(68.5, rel=1e-3)

    def test_clamps_max(self):
        assert normalize_percentage("105") == 100.0

    def test_clamps_min(self):
        assert normalize_percentage("-5") == 0.0

    def test_none(self):
        assert normalize_percentage(None) is None


class TestNormalizeDate:
    def test_iso_date(self):
        assert normalize_date("2027-03-31") == date(2027, 3, 31)

    def test_slash_format(self):
        assert normalize_date("31/03/2027") == date(2027, 3, 31)

    def test_mon_year(self):
        assert normalize_date("Mar-2027") == date(2027, 3, 1)

    def test_na(self):
        assert normalize_date("N/A") is None

    def test_none(self):
        assert normalize_date(None) is None

    def test_empty(self):
        assert normalize_date("") is None


class TestNormalizeStatus:
    def test_ongoing(self):
        assert normalize_status("Ongoing") == "ongoing"

    def test_in_progress(self):
        assert normalize_status("In Progress") == "ongoing"

    def test_completed(self):
        assert normalize_status("Completed") == "completed"

    def test_stalled(self):
        assert normalize_status("Stalled") == "stalled"

    def test_unknown(self):
        assert normalize_status("XYZ Status") == "unknown"


# ─── Feature Engineering Tests ────────────────────────────────────────────────

class TestComputeFeatures:
    def _base_features(self, **kwargs):
        defaults = dict(
            physical_progress=60.0,
            planned_progress=70.0,
            cumulative_expenditure=50000.0,
            current_cost=100000.0,
            original_cost=90000.0,
            original_start_date=date(2020, 1, 1),
            original_completion_date=date(2025, 12, 31),
            revised_completion_date=date(2026, 6, 30),
            current_date=date(2026, 6, 1),
            prev_physical_progress=55.0,
            prev_expenditure=45000.0,
        )
        defaults.update(kwargs)
        return compute_features(**defaults)

    def test_progress_gap(self):
        f = self._base_features(physical_progress=60.0, planned_progress=70.0)
        assert f.progress_gap == pytest.approx(-10.0)

    def test_progress_velocity(self):
        f = self._base_features(physical_progress=60.0, prev_physical_progress=55.0)
        assert f.progress_velocity == pytest.approx(5.0)

    def test_expenditure_pct(self):
        f = self._base_features(cumulative_expenditure=50000.0, current_cost=100000.0)
        assert f.expenditure_pct == pytest.approx(50.0)

    def test_spending_progress_gap(self):
        f = self._base_features(cumulative_expenditure=80000.0, current_cost=100000.0, physical_progress=60.0)
        assert f.spending_progress_gap == pytest.approx(20.0)

    def test_cost_escalation(self):
        f = self._base_features(current_cost=110000.0, original_cost=100000.0)
        assert f.cost_escalation_pct == pytest.approx(10.0)

    def test_schedule_escalation_days(self):
        f = self._base_features(
            original_completion_date=date(2025, 12, 31),
            revised_completion_date=date(2026, 6, 30),
        )
        assert f.schedule_escalation_days == 181  # days between dates

    def test_missing_prev_data_no_velocity(self):
        f = self._base_features(prev_physical_progress=None)
        assert f.progress_velocity is None

    def test_missing_cost_no_escalation(self):
        f = self._base_features(original_cost=None)
        assert f.cost_escalation_pct is None


# ─── Rule Engine Tests ────────────────────────────────────────────────────────

class TestRules:
    def _features_with(self, **kwargs):
        from app.risk.features import ProjectFeatures
        f = ProjectFeatures()
        for k, v in kwargs.items():
            setattr(f, k, v)
        return f

    def test_progress_gap_warning(self):
        config = RiskConfig(progress_gap_warning=-10.0, progress_gap_high=-20.0)
        f = self._features_with(progress_gap=-12.0, physical_progress=58.0, planned_progress=70.0)
        results = evaluate_rules(f, config)
        rule_ids = [r.rule_id for r in results]
        assert "R01_PROGRESS_WARNING" in rule_ids

    def test_progress_gap_high(self):
        config = RiskConfig(progress_gap_warning=-10.0, progress_gap_high=-20.0)
        f = self._features_with(progress_gap=-25.0, physical_progress=45.0, planned_progress=70.0)
        results = evaluate_rules(f, config)
        rule_ids = [r.rule_id for r in results]
        assert "R01_PROGRESS_HIGH" in rule_ids

    def test_spending_gap_warning(self):
        config = RiskConfig(spending_progress_gap_warning=10.0, spending_progress_gap_high=25.0)
        f = self._features_with(spending_progress_gap=12.0, expenditure_pct=72.0, physical_progress=60.0)
        results = evaluate_rules(f, config)
        assert any(r.rule_id == "R02_SPENDING_WARNING" for r in results)

    def test_cost_escalation_high(self):
        config = RiskConfig(cost_escalation_warning_pct=10.0, cost_escalation_high_pct=25.0)
        f = self._features_with(cost_escalation_pct=30.0)
        results = evaluate_rules(f, config)
        assert any(r.rule_id == "R03_COST_ESC_HIGH" for r in results)

    def test_no_rules_on_healthy_project(self):
        config = RiskConfig()
        f = self._features_with(
            progress_gap=2.0,
            spending_progress_gap=3.0,
            cost_escalation_pct=5.0,
            schedule_escalation_days=20,
        )
        results = evaluate_rules(f, config)
        high_or_critical = [r for r in results if r.risk_level in (RiskLevel.high, RiskLevel.critical)]
        assert len(high_or_critical) == 0


# ─── Scoring Tests ────────────────────────────────────────────────────────────

class TestScoring:
    def test_progress_health_on_track(self):
        from app.risk.features import ProjectFeatures
        f = ProjectFeatures(progress_gap=0.0)
        score = compute_progress_health(f, RiskConfig())
        assert score == pytest.approx(100.0)

    def test_progress_health_behind(self):
        from app.risk.features import ProjectFeatures
        f = ProjectFeatures(progress_gap=-15.0)
        score = compute_progress_health(f, RiskConfig())
        assert score is not None and score < 60

    def test_overall_health_weighted(self):
        config = RiskConfig(
            financial_weight=0.25, schedule_weight=0.30,
            progress_weight=0.25, milestone_weight=0.20
        )
        score = compute_overall_health(80.0, 60.0, 70.0, 90.0, config)
        # 0.25*80 + 0.30*60 + 0.25*70 + 0.20*90 = 20+18+17.5+18 = 73.5
        assert score == pytest.approx(73.5, rel=1e-2)

    def test_risk_level_low(self):
        config = RiskConfig(health_low_threshold=75.0)
        assert risk_level_from_health(80.0, config) == RiskLevel.low

    def test_risk_level_medium(self):
        config = RiskConfig(health_low_threshold=75.0, health_medium_threshold=55.0)
        assert risk_level_from_health(65.0, config) == RiskLevel.medium

    def test_risk_level_high(self):
        config = RiskConfig(health_medium_threshold=55.0, health_critical_threshold=35.0)
        assert risk_level_from_health(45.0, config) == RiskLevel.high

    def test_risk_level_critical(self):
        config = RiskConfig(health_critical_threshold=35.0)
        assert risk_level_from_health(20.0, config) == RiskLevel.critical


# ─── Forecasting Tests ────────────────────────────────────────────────────────

class TestForecasting:
    def test_insufficient_data(self):
        from app.analytics.forecasting import forecast_project
        result = forecast_project(
            snapshots=[{"report_month": date(2026, 4, 1), "physical_progress": 40.0, "cumulative_expenditure": 20000.0}],
            original_completion_date=date(2027, 3, 31),
            original_cost=100000.0,
        )
        assert result.method_used == "insufficient_data"
        assert result.forecast_completion_date is None

    def test_linear_forecast_completion(self):
        from app.analytics.forecasting import forecast_project
        # 5% per month progress → 100% in 20 months from 0%
        snapshots = [
            {"report_month": date(2026, i, 1), "physical_progress": float(i * 5), "cumulative_expenditure": float(i * 5000)}
            for i in range(1, 5)
        ]
        result = forecast_project(
            snapshots=snapshots,
            original_completion_date=date(2028, 1, 1),
            original_cost=100000.0,
            current_date=date(2026, 5, 1),
        )
        assert result.forecast_completion_date is not None
        assert result.method_used in ("linear_regression", "moving_average")
