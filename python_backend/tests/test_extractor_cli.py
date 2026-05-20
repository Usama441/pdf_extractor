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
MASHREQ_FIXTURE = ROOT / "python_backend" / "tests" / "fixtures" / "mashreq_statement.pdf"


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

    def test_mashreq_description_spillover_and_duplicate_pages_are_cleaned(self):
        if not MASHREQ_FIXTURE.exists():
            self.skipTest("Mashreq PDF fixture is not available in this workspace.")

        with tempfile.TemporaryDirectory() as directory:
            output_xlsx = Path(directory) / "result.xlsx"
            output_json = Path(directory) / "result.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "--input",
                    str(MASHREQ_FIXTURE),
                    "--output-xlsx",
                    str(output_xlsx),
                    "--output-json",
                    str(output_json),
                ],
                check=False,
            )

            self.assertEqual(0, completed.returncode)
            payload = json.loads(output_json.read_text(encoding="utf-8"))

            self.assertEqual(5, payload["transaction_count"])
            self.assertTrue(all(row[0].startswith("2025-") for row in payload["rows"]))
            self.assertFalse(any(row[1].startswith("20\n") for row in payload["rows"]))

            descriptions = "\n".join(row[1] for row in payload["rows"])
            references = "\n".join(row[2] for row in payload["rows"])

            self.assertIn("TRADECONNECT MEDIA", descriptions)
            self.assertIn("Monthly Maintenance Fee -", descriptions)
            self.assertIn("Value Added Tax - Output -", descriptions)
            self.assertNotIn("\nMEDIA", references)
            self.assertNotIn("Fee -", references)
            self.assertIn("033AACT25092C6W", references)
            self.assertIn("099REFEAED 00001", references)

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
