# ORACLE — Autonomous Human-Style Trading Intelligence

## Mission
Build a research-first autonomous trading system for Bybit USDT perpetuals that behaves like a disciplined professional trader: observe, form a thesis, challenge it, quantify risk, wait when there is no edge, execute, manage, review, and learn.

## Non-negotiable principles
- Capital preservation before return maximization.
- NO_TRADE is a first-class decision.
- LLMs may reason and propose; deterministic controls authorize orders.
- No self-modification of risk limits, credentials, or kill switches.
- New strategies/models require backtest, walk-forward, out-of-sample, paper, and staged validation before production.
- Every decision must be auditable and reproducible.
- Never hard-code exchange credentials.

## Trader Core
Maintain explicit state:
- market context and regime
- current thesis and alternative thesis
- evidence for/against each thesis
- invalidation conditions
- conviction and uncertainty
- opportunity quality
- risk budget and portfolio exposure
- open-position thesis
- recent performance and drawdown
- strategy/model reliability by regime

Before a trade, the decision loop asks:
1. What is happening?
2. Why might it be happening?
3. What are the strongest competing explanations?
4. Where is the edge?
5. What invalidates the thesis?
6. What is the expected reward relative to risk and costs?
7. Is waiting better than trading now?
8. What evidence would change the decision?

## Architecture
Market Data -> Feature/Context Engine -> Regime Engine -> Strategy Ensemble -> Thesis/Debate Layer -> Opportunity Ranker -> Deterministic Risk Engine -> Position Sizing -> Execution -> Position Monitor -> Trade Journal -> Research/Learning -> Challenger Models -> Validation -> Production.

## Initial implementation phases
1. Foundation and domain models.
2. Historical data/replay and event-driven backtester.
3. Market context/features and regime detection.
4. Strategy interface and initial independent strategies.
5. Trader Core/thesis engine.
6. Deterministic risk engine.
7. Paper execution and reconciliation.
8. AI research/evaluation loop.
9. Bybit adapter behind a production safety gate.
10. Monitoring, dashboard, alerts, and staged deployment.

## Initial safety mode
The first implementation must not place live orders. Production execution remains disabled until explicit configuration and validation gates are implemented.
