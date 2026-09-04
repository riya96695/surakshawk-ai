# SuraksHawk AI — Member 5 Dataset (Step 2)

This package contains a **synthetic prototype dataset** built against the finalized 29-column schema.

Counts:
- Train: 400 (200 SCAM / 200 LEGITIMATE)
- Validation: 100 (50 / 50)
- Test: 150 (75 / 75)
- Golden scenarios: 30 (15 / 15)

Languages represented:
- English
- Hinglish
- Hindi

Important:
- These records are synthetic and are not evidence of real-world prevalence.
- Do not present these metrics as production performance.
- Do not tune the model on the test set.
- The `source_type` field is `SYNTHETIC`.
- Before public release, review every record and add public/licensed data with documented provenance where permitted.
- No real personal data is included.

Recommended next action:
1. Copy/replace `dataset/processed/messages_master.csv` in your branch.
2. Keep train/validation/test/scenario files under the corresponding directories.
3. Run the team's schema validation/tests.
4. Commit the completed dataset milestone.
