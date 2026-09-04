from pathlib import Path
import json
import sys

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from risk_engine import score_transaction

SCENARIO_DATASET = Path("dataset/scenarios/golden_scenarios.csv")
RESULTS_DIR = Path("evaluation/results")
RESULTS_FILE = RESULTS_DIR / "risk_engine_results.json"


EXPECTED_INTERVENTIONS = {
    "low": "allow",
    "medium": "step_up_confirmation",
    "high": "warning_with_delay",
    "critical": "escalate_to_analyst",
}

EXPECTED_HUMAN_REVIEW = {
    "low": False,
    "medium": False,
    "high": False,
    "critical": True,
}


def build_context(row):
    transaction_context = {
        "transaction_velocity_flag": False,
    }

    device_context = None
    if int(row["remote_access_request"]) == 1:
        device_context = {
            "remote_access_indicator": {
                "present": True,
                "confidence": 1.0,
            },
            "screen_sharing_active": False,
        }

    # Do not infer a phone call from communication_type == "SCENARIO".
    # The golden dataset does not explicitly identify these scenarios as calls.
    call_context = None

    messaging_context = {
        "content_excerpt": row["text"]
    }

    language_context = {
        "detected_language": row["language"]
    }

    available_signals = [
        "transaction_context",
        "messaging_context",
        "language_context",
    ]

    if device_context is not None:
        available_signals.append("device_context")

    return (
        transaction_context,
        device_context,
        call_context,
        messaging_context,
        language_context,
        available_signals,
    )


def evaluate_policy_consistency(result):
    """Check whether policy output matches the engine's documented rules."""

    tier = result["policy_decision"]["risk_tier"]
    intervention = result["policy_decision"]["intervention"]
    human_review = result["policy_decision"]["requires_human_review"]

    intervention_ok = (
        intervention == EXPECTED_INTERVENTIONS[tier]
    )

    human_review_ok = (
        human_review == EXPECTED_HUMAN_REVIEW[tier]
    )

    return intervention_ok and human_review_ok


def main():
    if not SCENARIO_DATASET.exists():
        raise FileNotFoundError(
            f"Scenario dataset not found: {SCENARIO_DATASET}"
        )

    df = pd.read_csv(SCENARIO_DATASET)

    results = []
    policy_pass_count = 0

    for _, row in df.iterrows():

        (
            transaction_context,
            device_context,
            call_context,
            messaging_context,
            language_context,
            available_signals,
        ) = build_context(row)

        result = score_transaction(
            request_id=row["id"],
            partner_id="evaluation",
            transaction_context=transaction_context,
            device_context=device_context,
            call_context=call_context,
            messaging_context=messaging_context,
            language_context=language_context,
            available_signals=available_signals,
        )

        policy_consistent = evaluate_policy_consistency(result)

        if policy_consistent:
            policy_pass_count += 1

        results.append(
            {
                "scenario_id": row["id"],
                "actual_label": row["label"],
                "scam_type": row["scam_type"],
                "language": row["language"],
                "risk_score": result["model_evidence"]["risk_score"],
                "confidence": result["model_evidence"]["confidence"],
                "risk_tier": result["policy_decision"]["risk_tier"],
                "intervention": result["policy_decision"]["intervention"],
                "requires_human_review": result["policy_decision"][
                    "requires_human_review"
                ],
                "reason_codes": result["model_evidence"]["reason_codes"],
                "policy_consistent": policy_consistent,
            }
        )

    total = len(results)

    summary = {
        "dataset": str(SCENARIO_DATASET),
        "total_scenarios": total,
        "policy_consistency": {
            "passed": policy_pass_count,
            "failed": total - policy_pass_count,
            "pass_rate": round(policy_pass_count / total, 4)
            if total
            else 0,
        },
        "risk_tier_distribution": {},
        "scam_type_distribution": {},
    }

    for item in results:
        tier = item["risk_tier"]
        scam_type = item["scam_type"]

        summary["risk_tier_distribution"][tier] = (
            summary["risk_tier_distribution"].get(tier, 0) + 1
        )

        summary["scam_type_distribution"][scam_type] = (
            summary["scam_type_distribution"].get(scam_type, 0) + 1
        )

    output = {
        "summary": summary,
        "scenarios": results,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4, ensure_ascii=False)

    print("\nRisk Engine Evaluation Complete")
    print("-" * 35)
    print(f"Scenarios tested : {total}")
    print(
        f"Policy passed    : {policy_pass_count}/{total}"
    )
    print(
        f"Policy pass rate : "
        f"{summary['policy_consistency']['pass_rate']:.2%}"
    )

    print("\nRisk Tier Distribution")
    for tier, count in summary["risk_tier_distribution"].items():
        print(f"{tier:10} : {count}")

    print(f"\nResults saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()