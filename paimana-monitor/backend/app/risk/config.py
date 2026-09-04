"""
Risk Engine — Configuration
All weights and thresholds are loaded from the database (risk_configurations table).
This module provides the dataclass representation and defaults.
"""
from dataclasses import dataclass, field


@dataclass
class RiskConfig:
    """
    Immutable snapshot of the risk configuration used for a given calculation.
    Serialized into risk_assessments.config_snapshot for auditability.
    """
    # Health dimension weights (must sum to 1.0)
    financial_weight: float = 0.250
    schedule_weight: float = 0.300
    progress_weight: float = 0.250
    milestone_weight: float = 0.200

    # Progress gap thresholds (percentage points)
    progress_gap_warning: float = -10.0    # below this → medium risk flag
    progress_gap_high: float = -20.0       # below this → high risk flag

    # Spending-progress gap thresholds (percentage points)
    spending_progress_gap_warning: float = 10.0
    spending_progress_gap_high: float = 25.0

    # Cost escalation thresholds (%)
    cost_escalation_warning_pct: float = 10.0
    cost_escalation_high_pct: float = 25.0

    # Schedule delay thresholds (days)
    schedule_delay_warning_days: int = 30
    schedule_delay_high_days: int = 90

    # Overall health → risk level mapping
    # health >= health_low_threshold       → LOW risk
    # health >= health_medium_threshold    → MEDIUM risk
    # health >= health_critical_threshold  → HIGH risk
    # health <  health_critical_threshold  → CRITICAL risk
    health_low_threshold: float = 75.0
    health_medium_threshold: float = 55.0
    health_critical_threshold: float = 35.0

    def to_dict(self) -> dict:
        import dataclasses
        return dataclasses.asdict(self)

    @classmethod
    def from_orm(cls, orm_config) -> "RiskConfig":
        """Create from SQLAlchemy RiskConfiguration ORM object."""
        return cls(
            financial_weight=float(orm_config.financial_weight),
            schedule_weight=float(orm_config.schedule_weight),
            progress_weight=float(orm_config.progress_weight),
            milestone_weight=float(orm_config.milestone_weight),
            progress_gap_warning=float(orm_config.progress_gap_warning),
            progress_gap_high=float(orm_config.progress_gap_high),
            spending_progress_gap_warning=float(orm_config.spending_progress_gap_warning),
            spending_progress_gap_high=float(orm_config.spending_progress_gap_high),
            cost_escalation_warning_pct=float(orm_config.cost_escalation_warning_pct),
            cost_escalation_high_pct=float(orm_config.cost_escalation_high_pct),
            schedule_delay_warning_days=int(orm_config.schedule_delay_warning_days),
            schedule_delay_high_days=int(orm_config.schedule_delay_high_days),
            health_low_threshold=float(orm_config.health_low_threshold),
            health_medium_threshold=float(orm_config.health_medium_threshold),
            health_critical_threshold=float(orm_config.health_critical_threshold),
        )


DEFAULT_CONFIG = RiskConfig()
