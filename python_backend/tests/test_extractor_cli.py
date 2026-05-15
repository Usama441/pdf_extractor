import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "python_backend" / "extractor_cli.py"
SUCCESS_FIXTURE = ROOT / "pdf" / "E-STATEMENT_02JUL2025_3601_unlocked.pdf"
ENCRYPTED_FIXTURE = ROOT / "pdf" / "ADCBStmt01Jan25to31Jan25.pdf"


class ExtractorCliTest(unittest.TestCase):
    def test_successful_cli_run_outputs_json_and_xlsx(self):
        if not SUCCESS_FIXTURE.exists():
            self.skipTest("Success PDF fixture is not available in this workspace.")

        with tempfile.TemporaryDirectory() as directory:
            output_xlsx = Path(directory) / "result.xlsx"
            output_json = Path(directory) / "result.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "--input",
                    str(SUCCESS_FIXTURE),
                    "--output-xlsx",
                    str(output_xlsx),
                    "--output-json",
                    str(output_json),
                ],
                check=False,
            )

            self.assertEqual(0, completed.returncode)
            self.assertTrue(output_xlsx.exists())
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertIn("columns", payload)
            self.assertIn("rows", payload)
            self.assertGreater(payload["transaction_count"], 0)

    def test_encrypted_pdf_without_password_returns_exit_code_2(self):
        if not ENCRYPTED_FIXTURE.exists():
            self.skipTest("Encrypted PDF fixture is not available in this workspace.")

        with tempfile.TemporaryDirectory() as directory:
            output_xlsx = Path(directory) / "result.xlsx"
            output_json = Path(directory) / "result.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "--input",
                    str(ENCRYPTED_FIXTURE),
                    "--output-xlsx",
                    str(output_xlsx),
                    "--output-json",
                    str(output_json),
                ],
                check=False,
            )

            self.assertEqual(2, completed.returncode)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("password_required", payload["error_code"])

    def test_encrypted_pdf_with_wrong_password_returns_exit_code_2(self):
        if not ENCRYPTED_FIXTURE.exists():
            self.skipTest("Encrypted PDF fixture is not available in this workspace.")

        with tempfile.TemporaryDirectory() as directory:
            output_xlsx = Path(directory) / "result.xlsx"
            output_json = Path(directory) / "result.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "--input",
                    str(ENCRYPTED_FIXTURE),
                    "--output-xlsx",
                    str(output_xlsx),
                    "--output-json",
                    str(output_json),
                    "--password",
                    "wrong",
                ],
                check=False,
            )

            self.assertEqual(2, completed.returncode)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertIn("invalid", payload["message"].lower())


if __name__ == "__main__":
    unittest.main()
