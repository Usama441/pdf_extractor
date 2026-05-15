#!/usr/bin/env python3
import argparse
import json
import sys

from extractor import ExtractionError, PasswordRequiredError, UnsupportedStatementError, extract_pdf_to_excel


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        result = extract_pdf_to_excel(args.input, args.output_xlsx, password=args.password)
        write_json(args.output_json, result.to_dict())
        return 0
    except PasswordRequiredError as exc:
        write_json(args.output_json, {"error_code": exc.error_code, "message": str(exc)})
        return 2
    except UnsupportedStatementError as exc:
        write_json(args.output_json, {"error_code": exc.error_code, "message": str(exc)})
        return 3
    except ExtractionError as exc:
        write_json(args.output_json, {"error_code": exc.error_code, "message": str(exc)})
        return 1
    except Exception as exc:  # noqa: BLE001
        write_json(args.output_json, {"error_code": "unexpected_error", "message": str(exc)})
        return 1


def build_parser():
    parser = argparse.ArgumentParser(description="Extract transactions from a bank statement PDF.")
    parser.add_argument("--input", required=True, help="Path to the input PDF.")
    parser.add_argument("--output-xlsx", required=True, help="Path to the generated XLSX file.")
    parser.add_argument("--output-json", required=True, help="Path to the JSON metadata file.")
    parser.add_argument("--password", help="Optional PDF password.")
    return parser


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    sys.exit(main())
