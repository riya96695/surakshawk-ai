from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def normalize_text(text):
    return " ".join(str(text).lower().strip().split())


def load_texts(path):
    df = pd.read_csv(path)
    return set(df["text"].map(normalize_text))


def main():
    train_path = ROOT / "dataset" / "train" / "messages_train.csv"
    validation_path = ROOT / "dataset" / "validation" / "messages_validation.csv"
    test_path = ROOT / "dataset" / "test" / "messages_test.csv"

    train = load_texts(train_path)
    validation = load_texts(validation_path)
    test = load_texts(test_path)

    train_validation = train & validation
    train_test = train & test
    validation_test = validation & test

    print(f"Train ∩ Validation: {len(train_validation)}")
    print(f"Train ∩ Test:       {len(train_test)}")
    print(f"Validation ∩ Test:  {len(validation_test)}")

    assert len(train_validation) == 0, (
        f"Data leakage detected between Train and Validation: "
        f"{train_validation}"
    )

    assert len(train_test) == 0, (
        f"Data leakage detected between Train and Test: "
        f"{train_test}"
    )

    assert len(validation_test) == 0, (
        f"Data leakage detected between Validation and Test: "
        f"{validation_test}"
    )

    print("\nNO DATA LEAKAGE DETECTED")


if __name__ == "__main__":
    main()