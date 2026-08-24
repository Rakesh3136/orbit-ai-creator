"""Core domain models for the ORACLE trader.

These models deliberately contain no exchange-specific execution logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Mapping


class Action(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    HOLD = "HOLD"
    CLOSE = "CLOSE"
    REDUCE = "REDUCE"
    NO_TRADE = "NO_TRADE"


class Regime(str, Enum):
    UNKNOWN = "UNKNOWN"
    TREND_BULL = "TREND_BULL"
    TREND_BEAR = "TREND_BEAR"
    RANGE = "RANGE"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    ABNORMAL = "ABNORMAL"


@dataclass(frozen=True)
class Thesis:
    """A falsifiable market hypothesis, not a generic prediction."""

    statement: str
    evidence_for: tuple[str, ...] = ()
    evidence_against: tuple[str, ...] = ()
    invalidation: tuple[str, ...] = ()
    confidence: float = 0.0


@dataclass(frozen=True)
class TradeProposal:
    symbol: str
    action: Action
    thesis: Thesis
    expected_reward_risk: float
    confidence: float
    timestamp: datetime
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    reason: str
    max_notional: float = 0.0
    max_leverage: float = 0.0


@dataclass(frozen=True)
class MarketContext:
    symbol: str
    timestamp: datetime
    regime: Regime = Regime.UNKNOWN
    features: Mapping[str, float] = field(default_factory=dict)


@dataclass
class TraderState:
    """Persistent cognitive/risk state of the autonomous trader."""

    regime: Regime = Regime.UNKNOWN
    current_thesis: Thesis | None = None
    alternative_thesis: Thesis | None = None
    conviction: float = 0.0
    uncertainty: float = 1.0
    daily_pnl: float = 0.0
    drawdown: float = 0.0
    consecutive_losses: int = 0
    trading_enabled: bool = False
