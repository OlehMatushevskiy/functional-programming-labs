import json
import subprocess
import sys
from pathlib import Path

from ..lab2 import Record, build_pipeline, reduce_stats

LAB_DIR = Path(__file__).resolve().parents[2]


def test_package_exposes_the_pipeline() -> None:
    records: list[Record] = [
        {"id": 1, "name": "Mouse", "category": "electronics", "price": 80, "stock": 2}
    ]

    result = build_pipeline(category="electronics", factor=1.5)(records)

    assert result[0]["total"] == 240
    assert reduce_stats(result) == {
        "count": 1,
        "inventory_value": 240,
        "avg_value": 240,
    }


def test_package_cli_runs_with_sample_json() -> None:
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "lab2.main",
            "--data",
            "lab2/sample_data.json",
            "--top",
            "3",
        ],
        cwd=LAB_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    result = json.loads(run.stdout)

    assert [record["id"] for record in result["records"]] == [1, 2, 3]
    assert result["stats"]["count"] == 3
    assert result["stats"]["inventory_value"] == 682.0


def test_script_cli_rejects_negative_top_n() -> None:
    run = subprocess.run(
        [sys.executable, "app.py", "--top", "-1"],
        cwd=LAB_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    assert run.returncode == 2
    assert "non-negative integer" in run.stderr
