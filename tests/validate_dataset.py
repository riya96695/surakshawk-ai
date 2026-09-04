from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_COLUMNS = [
    "id",
    "text",
    "label",
    "scam_type",
    "language",
    "communication_type",
    "urgency",
    "threat",
    "impersonation",
    "payment_request",
    "credential_request",
    "otp_request",
    "remote_access_request",
    "suspicious_link",
    "reward_or_promise",
    "fear",
    "authority_claim",
    "financial_pressure",
    "sender_type",
    "beneficiary_present",
    "transaction_present",
    "transaction_amount",
    "link_present",
    "action_requested",
    "sensitive_information_requested",
    "source_type",
    "split",
    "annotation_status",
    "notes",
]

REQUIRED_COLUMNS = [
    "id",
    "text",
    "label",
    "language",
    "split",
]

ALLOWED_LABELS = {"SCAM", "LEGITIMATE"}
ALLOWED_LANGUAGES = {"ENGLISH", "HINDI", "HINGLISH"}
ALLOWED_SPLITS = {"TRAIN", "VALIDATION", "TEST", "SCENARIO"}

BINARY_COLUMNS = [
    "urgency",
    "threat",
    "impersonation",
    "payment_request",
    "credential_request",
    "otp_request",
    "remote_access_request",
    "suspicious_link",
    "reward_or_promise",
    "fear",
    "authority_claim",
    "financial_pressure",
    "beneficiary_present",
    "transaction_present",
    "link_present",
]


def validate_file(path: Path, expected_split: str):
    print(f"\nChecking: {path}")

    assert path.exists(), f"Missing file: {path}"

    df = pd.read_csv(path)

    assert not df.empty, f"File is empty: {path}"

    # Column validation
    assert list(df.columns) == EXPECTED_COLUMNS, (
        f"Incorrect columns in {path}\n"
        f"Expected: {EXPECTED_COLUMNS}\n"
        f"Found:    {list(df.columns)}"
    )

    # Required fields
    for column in REQUIRED_COLUMNS:
        assert df[column].notna().all(), (
            f"Missing values found in required column '{column}'"
        )

    # Unique IDs
    assert df["id"].is_unique, f"Duplicate IDs found in {path}"

    # Labels
    labels = set(df["label"].unique())
    assert labels.issubset(ALLOWED_LABELS), (
        f"Invalid labels found: {labels - ALLOWED_LABELS}"
    )

    # Languages
    languages = set(df["language"].unique())
    assert languages.issubset(ALLOWED_LANGUAGES), (
        f"Invalid languages found: {languages - ALLOWED_LANGUAGES}"
    )

    # Split
    splits = set(df["split"].unique())
    assert splits.issubset(ALLOWED_SPLITS), (
        f"Invalid split values found: {splits - ALLOWED_SPLITS}"
    )

    assert splits == {expected_split}, (
        f"Expected split '{expected_split}', found {splits}"
    )

    # Binary fields
    for column in BINARY_COLUMNS:
        values = set(df[column].dropna().unique())
        assert values.issubset({0, 1}), (
            f"Column '{column}' contains non-binary values: {values}"
        )

    # Transaction amount
    assert (df["transaction_amount"] >= 0).all(), (
        "Negative transaction amount found"
    )

    # Scam type consistency
    scam_rows = df["label"] == "SCAM"
    legitimate_rows = df["label"] == "LEGITIMATE"

    assert (df.loc[scam_rows, "scam_type"] != "NONE").all(), (
        "SCAM record found with scam_type = NONE"
    )

    assert (df.loc[legitimate_rows, "scam_type"] == "NONE").all(), (
        "LEGITIMATE record found with scam_type != NONE"
    )

    # Source type
    assert (df["source_type"] == "SYNTHETIC").all(), (
        "Unexpected source_type found"
    )

    # Annotation status
    assert (df["annotation_status"] == "ANNOTATED").all(), (
        "Unexpected annotation_status found"
    )

    print(f"  Records: {len(df)}")
    print(f"  Labels:\n{df['label'].value_counts().to_string()}")
    print("  PASS")


def main():
    train_path = ROOT / "dataset" / "train" / "messages_train.csv"
    validation_path = ROOT / "dataset" / "validation" / "messages_validation.csv"
    test_path = ROOT / "dataset" / "test" / "messages_test.csv"
    golden_path = ROOT / "dataset" / "scenarios" / "golden_scenarios.csv"

    validate_file(train_path, "TRAIN")
    validate_file(validation_path, "VALIDATION")
    validate_file(test_path, "TEST")
    validate_file(golden_path, "SCENARIO")

    print("\n" + "=" * 50)
    print("ALL DATASET VALIDATION CHECKS PASS")
    print("=" * 50)


if __name__ == "__main__":
    main()