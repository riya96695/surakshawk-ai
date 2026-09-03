from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

MASTER = ROOT / "dataset" / "processed" / "messages_master.csv"

TRAIN_OUT = ROOT / "dataset" / "train" / "messages_train.csv"
VALIDATION_OUT = ROOT / "dataset" / "validation" / "messages_validation.csv"
TEST_OUT = ROOT / "dataset" / "test" / "messages_test.csv"


def normalize_text(text):
    return " ".join(str(text).lower().strip().split())


def main():
    df = pd.read_csv(MASTER)

    # Normalize text for duplicate detection.
    df["_normalized_text"] = df["text"].map(normalize_text)

    # Golden scenarios are handled separately.
    assert "SCENARIO" not in set(df["split"]), (
        "Master dataset unexpectedly contains SCENARIO records."
    )

    # Every unique normalized message must belong to exactly one split.
    # Grouping prevents identical messages from being distributed across
    # train/validation/test.
    groups = (
        df.groupby(["_normalized_text", "label"], sort=False)
        .agg(
            indices=("id", list),
            count=("id", "size"),
        )
        .reset_index()
    )

    # We need exact target sizes and balanced classes.
    targets = {
        "TRAIN": {"SCAM": 200, "LEGITIMATE": 200},
        "VALIDATION": {"SCAM": 50, "LEGITIMATE": 50},
        "TEST": {"SCAM": 75, "LEGITIMATE": 75},
    }

    # Work independently by label.
    assignments = {}

    for label in ["SCAM", "LEGITIMATE"]:
        label_groups = groups[groups["label"] == label].copy()

        # Deterministic ordering.
        label_groups = label_groups.sort_values(
            by=["_normalized_text"]
        ).reset_index(drop=True)

        required = sum(targets[split][label] for split in targets)

        assert label_groups["count"].sum() == required, (
            f"{label}: expected {required} records, "
            f"found {label_groups['count'].sum()}"
        )

        # We need to allocate whole duplicate groups to a split.
        # Since the current synthetic dataset contains repeated templates,
        # exact target counts may not be possible while keeping every
        # duplicate group intact.
        #
        # Therefore, first determine whether an exact allocation exists.
        group_sizes = label_groups["count"].tolist()

        # Dynamic programming: find groups for validation and test,
        # leaving the remainder for train.
        target_validation = targets["VALIDATION"][label]
        target_test = targets["TEST"][label]

        possible = {(0, 0): []}

        for group_index, size in enumerate(group_sizes):
            new_possible = dict(possible)

            for (v_count, t_count), selected in possible.items():
                # Assign group to validation.
                if v_count + size <= target_validation:
                    key = (v_count + size, t_count)
                    if key not in new_possible:
                        new_possible[key] = selected + [(group_index, "VALIDATION")]

                # Assign group to test.
                if t_count + size <= target_test:
                    key = (v_count, t_count + size)
                    if key not in new_possible:
                        new_possible[key] = selected + [(group_index, "TEST")]

                # Assign to train by doing nothing.
                # The group remains unassigned for now.
            
            possible = new_possible

        target_key = (target_validation, target_test)

        if target_key not in possible:
            raise RuntimeError(
                f"Could not create exact leakage-free {label} split. "
                f"Duplicate groups prevent exact 200/50/75 allocation."
            )

        selected = possible[target_key]

        selected_map = dict(selected)

        for group_index, group in label_groups.iterrows():
            normalized = group["_normalized_text"]

            split = selected_map.get(group_index, "TRAIN")

            for record_id in group["indices"]:
                assignments[record_id] = split

    df["split"] = df["id"].map(assignments)

    assert df["split"].notna().all(), "Some records were not assigned."

    # Verify exact counts.
    counts = pd.crosstab(df["split"], df["label"])

    for split in ["TRAIN", "VALIDATION", "TEST"]:
        for label in ["SCAM", "LEGITIMATE"]:
            actual = int(counts.loc[split, label])
            expected = targets[split][label]

            assert actual == expected, (
                f"{split}/{label}: expected {expected}, found {actual}"
            )

    # Verify no normalized text occurs across different splits.
    leakage_check = df.groupby("_normalized_text")["split"].nunique()

    assert leakage_check.max() == 1, (
        "Duplicate normalized text still exists across multiple splits."
    )

    # Remove helper column.
    df = df.drop(columns=["_normalized_text"])

    # Write output files.
    df[df["split"] == "TRAIN"].to_csv(TRAIN_OUT, index=False)
    df[df["split"] == "VALIDATION"].to_csv(VALIDATION_OUT, index=False)
    df[df["split"] == "TEST"].to_csv(TEST_OUT, index=False)

    print("Leakage-free dataset splits created successfully.\n")

    print(
        pd.crosstab(
            df["split"],
            df["label"]
        )
    )

    print("\nFiles updated:")
    print(TRAIN_OUT)
    print(VALIDATION_OUT)
    print(TEST_OUT)


if __name__ == "__main__":
    main()