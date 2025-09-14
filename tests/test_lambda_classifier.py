# Ariadne Clew – Final Hackathon Bundle Builder
# This script packages the project components into a downloadable bundle.

import zipfile
import os
import json

# Define the files you want to include in the bundle
files_to_include = [
    "frontend/script.js",  # Frontend JS
    "frontend/style.css",  # CSS styling
    "frontend/index.html",  # Frontend HTML
    "tests/test_lambda_classifier.py",  # ✅ Corrected test path
    "tests/test_schema_validation.py",  # Schema test (if present)
    "schema.py",  # TypedDict schema
    "lambda_classifier.py",  # Core logic
    "classifier_prompt.md",  # Prompt template
    "README.md",  # Glorious README
    "diffcheck.py",  # Optional diff tool
    "mypy.ini",  # Type checking config
    "ruff.toml",  # Linting config
]

# Sample JSON output to include in README/demo
sample_output = {
    "session_id": "ac-demo-001",
    "timestamp": "2025-09-14T12:34:56Z",
    "aha_moments": ["Realized MVP scope was bloated by CI/CD pipeline discussion."],
    "mvp_changes": ["Dropped CI/CD setup from MVP."],
    "scope_creep": ["Debated metrics dashboard before core classifier was stable."],
    "readme_notes": ["Define session log format expectations."],
    "post_mvp_ideas": ["Add visual prompt editor for tweaking classifiers."],
    "summary": "This session clarified MVP boundaries, removed CI/CD from scope, and emphasized logging clarity.",
    "quality_flags": [
        "✅ Scoped appropriately",
        "⚠️ Model confused early scope discussion",
    ],
}

# Create the zip
bundle_name = "ariadne-clew-final.zip"
with zipfile.ZipFile(bundle_name, "w") as zipf:
    for file in files_to_include:
        if os.path.exists(file):
            zipf.write(file)
        else:
            print(f"⚠️ File not found: {file} – skipping")

    # Write sample output JSON
    with open("sample_recap.json", "w") as f:
        json.dump(sample_output, f, indent=2)
        zipf.write("sample_recap.json")

print(f"✅ Bundle created: {bundle_name}")
