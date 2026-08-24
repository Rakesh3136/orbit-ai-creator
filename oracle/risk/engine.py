"""Deterministic safety boundary between AI proposals and execution."""

from oracle.core.models import RiskDecision, TradeProposal, TraderState


class RiskEngine:
    """Rejects unsafe proposals before an execution adapter can see them."""

    def __init__(self, *, max_drawdown: float = 0.10, max_leverage: float = 3.0) -> None:
        self.max_drawdown = max_drawdown
        self.max_leverage = max_leverage

    def evaluate(self, proposal: TradeProposal, state: TraderState) -> RiskDecision:
        if not state.trading_enabled:
            return RiskDecision(False, "trading_disabled")
        if state.drawdown >= self.max_drawdown:
            return RiskDecision(False, "drawdown_limit")
        if proposal.action.value == "NO_TRADE":
            return RiskDecision(False, "no_trade_proposal")
        if proposal.confidence <= 0.0:
            return RiskDecision(False, "invalid_confidence")
        return RiskDecision(True, "approved_for_sizing", max_leverage=self.max_leverage)
