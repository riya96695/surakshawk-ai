"""
SuraksHawk Risk Engine — Reference Implementation (v0)
=======================================================

This is a WORKING but PLACEHOLDER implementation of the risk-scoring
contract described in `suraksHawk_risk_engine_interface_v0.md`.

What's real here:
  - The input/output shapes match the v0 JSON schema exactly.
  - The scoring logic runs end-to-end and degrades gracefully when
    signals are missing (per the "graceful degradation" principle in
    the source docs).
  - Risk tiers and intervention mapping are concrete and documented,
    so you have real numbers to build an evaluation harness against.

What's NOT real / needs replacing before production:
  - `_semantic_flags()` uses naive keyword matching as a stand-in for
    the multilingual semantic/intent classifier described in the
    source docs (Strategy doc, sections 4/7). It will NOT generalize
    to Hindi/Hinglish/regional-language scam phrasing as-is.
  - Signal weights below are arbitrary starting points, not calibrated
    against any labeled fraud data. Treat every WEIGHT_* constant as
    a tunable hyperparameter, not a validated coefficient.
  - There is no model versioning/rollback, no drift monitoring, no
    persistence layer, and no partner-specific policy config — all of
    which the source docs call out as required before production.

Run this file directly for a demo:
    python risk_engine.py
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


MODEL_VERSION = "suraks-risk-heuristic-v0.1"
POLICY_VERSION = "suraks-policy-v0.1"

# ---------------------------------------------------------------------------
# Tunable weights — placeholders, not calibrated against real fraud outcomes.
# Each is the max contribution that signal can add to the raw score (0-1 space
# before squashing). Confidence-bearing signals get scaled by their confidence.
# ---------------------------------------------------------------------------
WEIGHT_NEW_BENEFICIARY = 0.15
WEIGHT_VELOCITY_FLAG = 0.10
WEIGHT_REMOTE_ACCESS = 0.25
WEIGHT_SCREEN_SHARING = 0.15
WEIGHT_UNKNOWN_ACTIVE_CALL = 0.20
WEIGHT_SEMANTIC_COERCION = 0.30
WEIGHT_SEMANTIC_URGENCY = 0.20
WEIGHT_SEMANTIC_AUTHORITY_IMPERSONATION = 0.25

# Naive keyword lexicon standing in for the real semantic/intent classifier.
# Real implementation should use the multilingual model described in the docs.
_COERCION_KEYWORDS = ["don't tell", "keep this secret", "urgent action required", "account will be blocked"]
_URGENCY_KEYWORDS = ["immediately", "right now", "within 10 minutes", "urgent", "asap"]
_AUTHORITY_KEYWORDS = ["rbi", "income tax department", "police", "cyber cell", "bank officer", "customs"]

# ---------------------------------------------------------------------------
# Risk tier thresholds — placeholder bands on the calibrated 0-1 score.
# Must be re-derived from shadow-mode evaluation against confirmed fraud
# outcomes before being treated as production thresholds (per Limitations
# doc, "shadow-mode evaluation + calibrated risk tiers" is P0, not optional).
# ---------------------------------------------------------------------------
TIER_THRESHOLDS = [
    (0.75, "critical"),
    (0.50, "high"),
    (0.25, "medium"),
    (0.00, "low"),
]

# Tier -> allowed intervention, per Strategy doc §4.2
TIER_TO_INTERVENTION = {
    "low": "allow",
    "medium": "step_up_confirmation",
    "high": "warning_with_delay",
    "critical": "escalate_to_analyst",
}

TIER_TO_COOLDOWN_SECONDS = {
    "low": None,
    "medium": None,
    "high": 300,       # the "five-minute cooldown" mentioned in the source docs
    "critical": None,  # critical routes to analyst rather than a timed delay
}

TIER_REQUIRES_HUMAN_REVIEW = {
    "low": False,
    "medium": False,
    "high": False,
    "critical": True,
}


@dataclass
class ContributingSignal:
    signal: str
    weight: float
    note: Optional[str] = None

    def to_dict(self) -> dict:
        return {"signal": self.signal, "weight": round(self.weight, 4), "note": self.note}


def _get(d: Optional[dict], *path, default=None):
    """Safe nested-dict getter — every signal block is optional."""
    cur = d
    for key in path:
        if cur is None:
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def _semantic_flags(text: Optional[str]) -> dict[str, bool]:
    """
    STAND-IN for the multilingual semantic/intent classifier described in
    the source docs. Naive keyword match only — does not handle Hindi,
    Hinglish, transliteration, or code-switching. Replace before production.
    """
    if not text:
        return {"coercion": False, "urgency": False, "authority": False}
    lowered = text.lower()
    return {
        "coercion": any(k in lowered for k in _COERCION_KEYWORDS),
        "urgency": any(k in lowered for k in _URGENCY_KEYWORDS),
        "authority": any(k in lowered for k in _AUTHORITY_KEYWORDS),
    }


def _squash(raw_sum: float) -> float:
    """Map an unbounded weighted sum into a calibrated-looking 0-1 score."""
    # Simple logistic squashing centered so ~0.5 raw weight lands near mid-risk.
    return 1 / (1 + math.exp(-6 * (raw_sum - 0.35)))


def _tier_for_score(score: float) -> str:
    for threshold, tier in TIER_THRESHOLDS:
        if score >= threshold:
            return tier
    return "low"


def score_transaction(
    request_id: Optional[str] = None,
    partner_id: str = "unknown",
    transaction_context: Optional[dict] = None,
    device_context: Optional[dict] = None,
    call_context: Optional[dict] = None,
    messaging_context: Optional[dict] = None,
    language_context: Optional[dict] = None,
    available_signals: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Score a single transaction/event against the signals provided.
    Never raises on missing context blocks — degrades to whatever is present.

    Returns a dict matching the v0 response schema:
    {"model_evidence": {...}, "policy_decision": {...}, "audit": {...}}
    """
    request_id = request_id or str(uuid.uuid4())
    contributions: list[ContributingSignal] = []
    reason_codes: list[str] = []
    raw = 0.0

    # --- Transaction signals ---
    if _get(transaction_context, "beneficiary_known") is False:
        raw += WEIGHT_NEW_BENEFICIARY
        contributions.append(ContributingSignal("new_beneficiary", WEIGHT_NEW_BENEFICIARY))
        reason_codes.append("new_beneficiary")

    if _get(transaction_context, "transaction_velocity_flag") is True:
        raw += WEIGHT_VELOCITY_FLAG
        contributions.append(ContributingSignal("transaction_velocity_flag", WEIGHT_VELOCITY_FLAG))
        reason_codes.append("unusual_transaction_velocity")

    # --- Device signals ---
    remote_present = _get(device_context, "remote_access_indicator", "present")
    remote_conf = _get(device_context, "remote_access_indicator", "confidence", default=1.0)
    if remote_present is True:
        contribution = WEIGHT_REMOTE_ACCESS * float(remote_conf)
        raw += contribution
        contributions.append(ContributingSignal("remote_access_detected", contribution))
        reason_codes.append("remote_access_detected")

    if _get(device_context, "screen_sharing_active") is True:
        raw += WEIGHT_SCREEN_SHARING
        contributions.append(ContributingSignal("screen_sharing_active", WEIGHT_SCREEN_SHARING))
        reason_codes.append("screen_sharing_active")

    # --- Call signals ---
    if _get(call_context, "active_call") is True and _get(call_context, "unknown_caller") is True:
        raw += WEIGHT_UNKNOWN_ACTIVE_CALL
        contributions.append(ContributingSignal("active_unknown_call", WEIGHT_UNKNOWN_ACTIVE_CALL))
        reason_codes.append("active_unknown_call")

    # --- Semantic signals (transcript + messaging content) ---
    transcript_text = _get(call_context, "transcript_segment")
    message_text = _get(messaging_context, "content_excerpt")
    combined_text = " ".join(t for t in [transcript_text, message_text] if t)
    flags = _semantic_flags(combined_text)

    if flags["coercion"]:
        raw += WEIGHT_SEMANTIC_COERCION
        contributions.append(ContributingSignal("coercive_language", WEIGHT_SEMANTIC_COERCION))
        reason_codes.append("coercive_urgency_language")
    if flags["urgency"]:
        raw += WEIGHT_SEMANTIC_URGENCY
        contributions.append(ContributingSignal("urgency_language", WEIGHT_SEMANTIC_URGENCY))
        reason_codes.append("urgency_language")
    if flags["authority"]:
        raw += WEIGHT_SEMANTIC_AUTHORITY_IMPERSONATION
        contributions.append(ContributingSignal("authority_impersonation_language", WEIGHT_SEMANTIC_AUTHORITY_IMPERSONATION))
        reason_codes.append("authority_impersonation")

    score = round(_squash(raw), 4)
    tier = _tier_for_score(score)

    # Confidence is naive here: fewer available signals -> lower confidence,
    # since the model is working with a partial picture (graceful degradation
    # principle from the source docs — the score itself never depends on one
    # signal, but confidence should reflect how much evidence backs it).
    n_signals_seen = len(available_signals) if available_signals else max(len(contributions), 1)
    confidence = round(min(1.0, 0.3 + 0.15 * n_signals_seen), 4)

    model_evidence = {
        "risk_score": score,
        "confidence": confidence,
        "reason_codes": reason_codes,
        "contributing_signals": [c.to_dict() for c in contributions],
        "language_evaluated": _get(language_context, "detected_language"),
        "model_version": MODEL_VERSION,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }

    policy_decision = {
        "risk_tier": tier,
        "intervention": TIER_TO_INTERVENTION[tier],
        "policy_version": POLICY_VERSION,
        "cooldown_seconds": TIER_TO_COOLDOWN_SECONDS[tier],
        "requires_human_review": TIER_REQUIRES_HUMAN_REVIEW[tier],
        "partner_override_allowed": tier != "critical",
    }

    audit = {
        "decision_id": str(uuid.uuid4()),
        "explainability_ref": f"evidence-bundle:{request_id}",
    }

    return {
        "request_id": request_id,
        "model_evidence": model_evidence,
        "policy_decision": policy_decision,
        "audit": audit,
    }


if __name__ == "__main__":
    import json

    example_low_risk = score_transaction(
        partner_id="demo-fintech",
        transaction_context={"beneficiary_known": True, "transaction_velocity_flag": False},
    )

    example_high_risk = score_transaction(
        partner_id="demo-fintech",
        transaction_context={"beneficiary_known": False, "transaction_velocity_flag": True},
        device_context={
            "remote_access_indicator": {"present": True, "confidence": 0.9, "app_hint": "anydesk"},
            "screen_sharing_active": True,
        },
        call_context={
            "active_call": True,
            "unknown_caller": True,
            "transcript_segment": "This is urgent, RBI has flagged your account, you must act immediately or your account will be blocked.",
        },
        available_signals=["transaction_context", "device_context", "call_context"],
    )

    print("=== Low-risk example ===")
    print(json.dumps(example_low_risk, indent=2))
    print("\n=== High-risk example ===")
    print(json.dumps(example_high_risk, indent=2))
