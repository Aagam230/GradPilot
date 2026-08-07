import csv
from pathlib import Path
from sqlalchemy.orm import Session
from .repository import create_historical_application


def _parse_int(value):
    if value is None or str(value).strip() == "": return None
    try: return int(float(value))
    except (ValueError, TypeError): return None


def _parse_float(value):
    if value is None or str(value).strip() == "": return None
    try: return float(value)
    except (ValueError, TypeError): return None


def import_historical_csv(db: Session, csv_path: str) -> dict:
    path = Path(csv_path)
    if not path.exists(): raise FileNotFoundError(f"CSV file not found: {csv_path}")
    imported, skipped, errors = 0, 0, []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        for row_number, row in enumerate(csv.DictReader(file), start=2):
            try:
                record = {
                    "canonical_university": (row.get("canonical_university") or "").strip(),
                    "canonical_program": (row.get("canonical_program") or "").strip(),
                    "application_year": _parse_int(row.get("application_year")), "decision": row.get("decision"),
                    "gpa_value": _parse_float(row.get("gpa_value")), "gpa_scale": _parse_float(row.get("gpa_scale")),
                    "gre_total": _parse_int(row.get("gre_total")), "gre_quant": _parse_int(row.get("gre_quant")),
                    "gre_verbal": _parse_int(row.get("gre_verbal")), "toefl": _parse_int(row.get("toefl")),
                    "ielts": _parse_float(row.get("ielts")), "undergraduate_major": row.get("undergraduate_major") or None,
                    "undergraduate_country": row.get("undergraduate_country") or None,
                    "research_experience": row.get("research_experience"),
                    "publication_count": _parse_int(row.get("publication_count")),
                    "work_experience_months": _parse_int(row.get("work_experience_months")),
                    "source_type": row.get("source_type") or "csv", "source_url": row.get("source_url") or None,
                    "data_quality_score": _parse_float(row.get("data_quality_score")),
                }
                create_historical_application(db, record); imported += 1
            except Exception as exc:
                skipped += 1; errors.append({"row": row_number, "error": str(exc)})
    return {"imported": imported, "skipped": skipped, "errors": errors}
