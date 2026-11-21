# Player-1 Dataset Metadata Audit

## 1. Purpose and Scope

This is a supporting research and reproducibility utility for understanding the published Player-1 training/evaluation data. It is not part of the runtime game agent and must not define a target game.

The audit must describe dataset composition from the complete released metadata. It must not assume that a dataset viewer summary is complete, and it must not make claims about unseen video content based only on metadata.

The audit is title-neutral: report all game labels and source categories as found. Do not search for, prioritize, or hard-code a particular game title or title alias.

## 2. Required Inputs

Use a complete local copy of the Player-1-Data release, including:
- All trajectory metadata files.
- The complete `recordings.jsonl` manifest.
- Source/session mapping files included in the release.
- Dataset revision or commit identifier.

The full image payload is not required for the initial metadata audit unless the published schema makes it necessary to interpret a field.

## 3. Download

```powershell
py -m pip install -U huggingface_hub
hf download yyyang/Player-1-Data --repo-type dataset --local-dir .\data\Player-1-Data
```

Verify that the local directory contains every required metadata file from the dataset repository. Do not audit a filtered sample or partial download.

## 4. Run

```powershell
py .\tools\audit_player1_dataset.py .\data\Player-1-Data --out .\reports\dataset-audit
```

The audit program must fail closed if:
- The dataset is incomplete.
- A required metadata file is missing.
- A file cannot be parsed.
- The discovered trajectory count conflicts with the expected release count without an explicit explanation.

The expected published trajectory count is 6,044. Treat this as a consistency check against the audited revision, not as permission to silently ignore additional or missing records.

## 5. Required Audit Outputs

Generate both machine-readable JSON and human-readable Markdown reports.

Report:
- Dataset repository and revision.
- Download date and file inventory.
- Total trajectory records.
- Trajectories by game label, mode, and source.
- Turn counts by available grouping fields.
- Sampled control-time estimates using the documented 200 ms/turn convention, clearly labeled as estimates.
- D2E-derived trajectory IDs and recording IDs.
- D2E source/session join results using the documented identifiers.
- Missing, duplicate, and unmatched IDs.
- Unknown or null labels and source values.
- Parsing errors and skipped records, if any.

Preserve original label and identifier values. Normalization may be used for grouping, but must not overwrite the source values.

## 6. D2E Source-Session Join

If the Player-1 release contains a D2E source/session allowlist or source manifest:

1. Extract the Player-1 D2E source/session identifiers.
2. Extract the D2E source manifest and its documented identifier fields.
3. Preserve original values and normalize only for matching.
4. Join using a schema-confirmed source/session key.
5. Report matched and unmatched IDs.
6. Sum durations only when the source provides explicit duration values.
7. Record the manifest version and dataset revision.

Do not guess the join key. Inspect the actual schema and document the exact fields used.

## 7. Video-Content Limitations

The Player-1-Data package may reference original recordings that are not included in the package. Metadata can establish what labels and source identifiers are present in the inspected release. It cannot prove what every frame of an unavailable source video depicts.

Any visual-content audit requires:
- A complete inventory of eligible source recordings.
- Verified provenance and permission to inspect them.
- A documented sampling or full-review policy.
- Reviewer/tool, timestamps, and evidence records.
- No transfer of restricted recordings to third-party services without permission.

## 8. Reproducibility and Acceptance

The audit is complete only when:
- The exact dataset revision is recorded.
- All required metadata files are inventoried.
- All records are parsed or explicitly accounted for.
- Counts reconcile or discrepancies are documented.
- Source/session joins are reproducible.
- JSON and Markdown reports are generated.
- The report distinguishes observed facts, estimates, unresolved mappings, and limitations.

This audit does not determine whether the agent can play an unfamiliar game. That capability must be evaluated separately through runtime cross-game tests.
