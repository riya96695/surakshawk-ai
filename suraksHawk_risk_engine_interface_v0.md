# SuraksHawk Risk Engine — Draft Interface Spec (v0)

**Status:** Proposed, not implemented. Derived from the concepts described in
`SuraksHawkAI_Startup_Strategy` and `SuraksHawkAI_Limitations_and_Mitigation_Strategy`.
No schema, API, or code existed in the source material — this is a starting
point for you to build an evaluation harness against, to be revised once
real partner signal contracts (Section 7, Limitations doc) are defined.

Design principles encoded here (from the docs):
- Signals are **partial by default** — every field is optional except identifiers/timestamps. The engine must degrade gracefully, never depend on one signal.
- Output is a **probability/score**, not a binary verdict.
- Every decision carries **reason codes** and **model/policy version** for auditability.
- Model prediction and policy/intervention decision are **separate objects** — the model does not decide the action.

---

## 1. Request — `POST /v0/risk-scan`

```json
{
  "request_id": "uuid",
  "partner_id": "string",
  "timestamp": "ISO-8601",
  "user_ref": {
    "partner_user_id": "string (pseudonymous/tokenized, never raw PII)",
    "known_since": "ISO-8601 | null"
  },
  "transaction_context": {
    "amount": "number | null",
    "currency": "string | null",
    "beneficiary_ref": "string | null (tokenized VPA/account id)",
    "beneficiary_known": "boolean | null",
    "beneficiary_first_seen": "ISO-8601 | null",
    "transaction_velocity_flag": "boolean | null",
    "channel": "string | null  // e.g. 'upi', 'imps', 'neft'"
  },
  "device_context": {
    "platform": "android | ios | web | null",
    "remote_access_indicator": {
      "present": "boolean | null",
      "confidence": "number 0-1 | null",
      "app_hint": "string | null  // e.g. 'anydesk' — informational only"
    },
    "screen_sharing_active": "boolean | null"
  },
  "call_context": {
    "active_call": "boolean | null",
    "call_direction": "inbound | outbound | null",
    "unknown_caller": "boolean | null",
    "transcript_available": "boolean | null",
    "transcript_confidence": "number 0-1 | null",
    "transcript_segment": "string | null  // fraud-intent-relevant excerpt only, not full call"
  },
  "messaging_context": {
    "source": "sms | whatsapp | email | user_reported | null",
    "content_available": "boolean | null",
    "content_excerpt": "string | null  // only if partner/user authorized sharing"
  },
  "language_context": {
    "detected_language": "string | null  // e.g. 'hi', 'ta', 'hinglish'",
    "script": "native | romanized | mixed | null"
  },
  "available_signals": [
    "list of strings naming which of the above blocks are actually populated —
     lets the engine know what's genuinely absent vs. null-because-negative"
  ]
}
```

Notes:
- `available_signals` exists because in this domain `null` is ambiguous ("not present" vs "not authorized/not collected"). The docs' Section 7 "Signal Contract" concept implies the engine needs to know *why* a field is empty.
- No raw call audio, no full message bodies, no raw account numbers — only tokenized refs and minimal excerpts, per the privacy/data-minimization principle (Limitations doc §18).

---

## 2. Response — Risk Object

```json
{
  "request_id": "uuid",
  "model_evidence": {
    "risk_score": "number 0-1  // calibrated probability, not binary",
    "confidence": "number 0-1",
    "reason_codes": [
      "string, e.g. 'new_beneficiary', 'coercive_urgency_language',
       'active_unknown_call', 'remote_access_detected'"
    ],
    "contributing_signals": [
      {"signal": "string", "weight": "number", "note": "string | null"}
    ],
    "language_evaluated": "string | null",
    "model_version": "string",
    "evaluated_at": "ISO-8601"
  },
  "policy_decision": {
    "risk_tier": "low | medium | high | critical",
    "intervention": "allow | step_up_confirmation | warning_with_delay | escalate_to_analyst | recommend_block",
    "policy_version": "string",
    "cooldown_seconds": "number | null",
    "requires_human_review": "boolean",
    "partner_override_allowed": "boolean"
  },
  "audit": {
    "decision_id": "uuid",
    "explainability_ref": "string  // pointer to full evidence bundle for analyst UI"
  }
}
```

Notes:
- `model_evidence` and `policy_decision` are deliberately separate objects — per the docs' explicit rule that the model doesn't have intervention authority; a policy engine maps score+context to an allowed action, and the partner institution owns final execution (Strategy doc §17, Limitations doc §17).
- `intervention` is an enum of the tiers described in Strategy doc §4.2 (Low/Medium/High/Critical → allow/confirm/warn+delay/block+escalate).
- Nothing here authorizes an automatic account freeze or fund reversal — that stays with the partner's system per the "SuraksHawk detects and recommends" boundary.

---

## 3. Function signature (if you're prototyping in Python before an API exists)

```python
def score_transaction(
    request_id: str,
    partner_id: str,
    transaction_context: dict | None = None,
    device_context: dict | None = None,
    call_context: dict | None = None,
    messaging_context: dict | None = None,
    language_context: dict | None = None,
    available_signals: list[str] | None = None,
) -> dict:
    """
    Returns a dict matching the Response schema above:
    {"model_evidence": {...}, "policy_decision": {...}, "audit": {...}}

    Must not raise/fail hard when any *_context is None — degrade to
    whatever signals are present (see 'available_signals').
    """
```

---

## What this does NOT cover yet (open items, not in source docs)

- Exact reason-code taxonomy (needs the scam taxonomy from Strategy doc §7.1)
- Batch/async scoring for post-event campaign intelligence (Limitations §14 mentions this exists but not its shape)
- Feedback/outcome-labeling endpoint (confirmed fraud / legitimate / uncertain) referenced in Strategy doc §5.1 and §13
- Per-partner signal contract format (Limitations doc §7's "Signal Contract" concept — this needs its own spec)

Treat this whole document as a v0 draft for internal alignment, not a finalized interface.
