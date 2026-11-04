# AIMN local feedback and lesson memory

Owners can rate completed internal task outputs (1–5), record corrections, and propose reusable lessons. Evaluations retain network/channel scope, reviewer identity, task ID, agent ID, skill ID/version, and registry version.

A proposed lesson is stored as `pending`; it is not available to agents until the owner explicitly approves it. Rejected lessons are never retrieved. Network-level lessons are visible to all channels in that network. Channel-specific lessons are visible only to that channel. Up to eight recent approved lessons are attached to future matching local task results with their evaluation and skill provenance.

API:
- `GET /api/v1/networks/{network_id}/evaluations`
- `POST /api/v1/networks/{network_id}/tasks/{task_id}/evaluation` with rating, optional correction and optional lesson
- `POST /api/v1/evaluations/{evaluation_id}/lesson-decision` with approved/rejected and optional note

This is deterministic retrieval of owner-reviewed text. It does not train or fine-tune model weights, call paid AI providers, or perform external actions. Only completed internal tasks can be evaluated.
