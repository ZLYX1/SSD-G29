# Converts Bandit JSON output to GitHub-compatible SARIF format

import json
import sys

bandit_input_path = sys.argv[1]
sarif_output_path = sys.argv[2]

with open(bandit_input_path, "r") as f:
    bandit_data = json.load(f)

sarif_results = []

for result in bandit_data.get("results", []):
    sarif_results.append(
        {
            "ruleId": result.get("test_id"),
            "level": "warning",
            "message": {"text": result.get("issue_text", "")},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": result.get("filename")},
                        "region": {"startLine": result.get("line_number")},
                    }
                }
            ],
        }
    )

sarif_output = {
    "version": "2.1.0",
    "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
    "runs": [
        {
            "tool": {
                "driver": {
                    "name": "Bandit",
                    "informationUri": "https://bandit.readthedocs.io/",
                    "rules": [],
                }
            },
            "results": sarif_results,
        }
    ],
}

with open(sarif_output_path, "w") as f:
    json.dump(sarif_output, f, indent=2)
