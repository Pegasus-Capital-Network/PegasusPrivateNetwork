"""Offline, human-reviewed investor acquisition queue for Pegasus Private Network.

No network calls, database writes or email sending. Public source assertions are
human attestations, not facts independently verified by this program.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

TYPES = {"direct_investor", "gatekeeper", "platform", "community", "lender", "strategic", "sovereign_fund"}
EVIDENCE = {"us_closed_deal", "us_public_mandate"}
HIGH_REVIEW = {"china", "hong kong", "prc", "people's republic of china"}


def tidy(value):
    """Single-line untrusted input for report and draft output."""
    return re.sub(r"\s+", " ", str(value or "")).strip()[:1000]


def domain(value):
    value = tidy(value)
    if not value:
        return ""
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    host = (urlsplit(value).hostname or "").lower().rstrip(".")
    return host[4:] if host.startswith("www.") else host


def secure_url(value):
    parts = urlsplit(tidy(value))
    return parts.scheme == "https" and bool(parts.hostname) and not (parts.username or parts.password)


def identity(record):
    name = re.sub(r"[^\w]+", "", tidy(record.get("name")).casefold())
    host = domain(record.get("website"))
    return {"name:" + name, "domain:" + host} - {"name:", "domain:"}


def read_jsonl(path):
    records = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError("expected object")
        except (ValueError, TypeError) as exc:
            raise ValueError(f"{path}:{number}: invalid JSON object: {exc}") from exc
        records.append(row)
    return records


def triage(row):
    issues = []
    category = tidy(row.get("type"))
    evidence_kind = tidy(row.get("evidence_kind"))
    if not tidy(row.get("name")) or not tidy(row.get("country")):
        issues.append("missing name/country")
    if category not in TYPES:
        issues.append("invalid investor class")
    if category == "sovereign_fund":
        issues.append("sovereign fund: not a small-project lead")
    if evidence_kind not in EVIDENCE:
        issues.append("no documented US deal or public US mandate")
    if not secure_url(row.get("evidence_url")):
        issues.append("missing HTTPS evidence link")
    if not secure_url(row.get("official_source_url")):
        issues.append("missing official HTTPS source")
    if row.get("source_verified") is not True or not tidy(row.get("verified_by")) or not tidy(row.get("verified_at")):
        issues.append("official sources not human-verified")
    else:
        try:
            date.fromisoformat(tidy(row["verified_at"]))
        except ValueError:
            issues.append("invalid source-verification date")
    contact_method = tidy(row.get("contact_method"))
    contact = tidy(row.get("contact"))
    if contact_method not in {"email", "form", "phone"} or not contact:
        issues.append("missing public contact route")
    elif contact_method == "form" and not secure_url(contact):
        issues.append("contact form must have HTTPS link")
    elif contact_method == "email" and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", contact):
        issues.append("invalid public email")
    scale_fit = tidy(row.get("scale_fit"))
    if scale_fit != "yes" or not tidy(row.get("scale_fit_reason")):
        issues.append("small-project scale fit not supported")
    if tidy(row.get("sanctions_status")) in {"possible_match", "blocked", "escalated"}:
        issues.append("sanctions escalation: human review required")
    if tidy(row.get("cfius_status")) in {"escalated", "blocked"}:
        issues.append("CFIUS escalation: human review required")
    if tidy(row.get("country")).casefold() in HIGH_REVIEW and tidy(row.get("cross_border_legal_review")) != "completed":
        issues.append("China/Hong Kong: transaction-specific legal review pending")
    # A historical purchase, fund AUM, loan size or subscription minimum must not
    # be converted into a confirmed minimum direct-equity cheque.
    minimum = None
    raw_min = row.get("min_check_usd")
    if raw_min not in (None, ""):
        try:
            amount = float(raw_min)
            if (amount > 0 and amount < 1e12 and
                tidy(row.get("minimum_context")) == "direct_equity_check" and
                secure_url(row.get("minimum_source_url"))):
                minimum = round(amount)
            else:
                issues.append("minimum cheque suppressed: wrong context or no source")
        except (ValueError, TypeError):
            issues.append("minimum cheque suppressed: not numeric")
    score = ({"direct_investor": 5, "gatekeeper": 3, "lender": 3,
              "platform": 2, "strategic": 2, "community": 1}.get(category, 0)
             + (3 if evidence_kind == "us_closed_deal" else 2)
             + (2 if scale_fit == "yes" else 0)
             + (1 if minimum is not None else 0))
    # READY means suitable for an *uncommitted research inquiry only*.
    # Neither READY nor a draft grants regulatory, KYC, OFAC or offering clearance.
    return {"state": "RESEARCH_READY" if not issues else "HOLD", "issues": issues,
            "score": score, "confirmed_min_check_usd": minimum}


def outreach_draft(row):
    firm, focus = tidy(row["name"]), tidy(row.get("focus"))
    category = tidy(row.get("type"))
    opening = {
        "direct_investor": "Your U.S. investment activity and real-estate focus",
        "gatekeeper": "Your work connecting investment offices and capital partners",
        "platform": "Your work with investment platforms and eligible participants",
        "lender": "Your U.S. real-estate credit activity",
        "strategic": "Your U.S. real-estate partnerships",
        "community": "Your international capital-partner network",
    }.get(category, "Your work in U.S. real assets")
    topic = f" in {focus}" if focus else ""
    destination = ("To: " if row.get("contact_method") == "email" else "Official form: ")
    return (f"{destination}{tidy(row.get('contact'))}\n"
            "Subject: Exploratory partner fit — Pegasus Private Network\n\n"
            f"Hello {firm} team,\n\n"
            f"{opening}{topic} prompted us to reach out. Pegasus Private Network is researching "
            "cross-border relationships relevant to privately sponsored U.S. residential real assets. "
            "We would welcome a brief conversation about your current U.S. geographic focus, "
            "project-size criteria, and your preferred process for reviewing potential partners.\n\n"
            "This is an introductory inquiry only, not an offering of securities, "
            "a request for funds, or a statement of investment returns or liquidity.\n\n"
            "Best regards,\nPegasus Private Network\n\nSTATUS: UNSENT — HUMAN REVIEW REQUIRED\n")


def run(input_path, history_paths, out_dir, run_date):
    if not history_paths:
        raise ValueError("At least one historic ledger is mandatory (use an empty file for a first run)")
    date.fromisoformat(run_date)
    previous = set()
    for history in history_paths:
        for row in read_jsonl(history):
            previous |= identity(row)
    seen = set(previous)
    new, duplicates = [], 0
    for row in read_jsonl(input_path):
        identifiers = identity(row)
        if not identifiers:
            raise ValueError("candidate without identifying name or website")
        if seen.intersection(identifiers):
            duplicates += 1
            continue
        seen |= identifiers
        evaluation = triage(row)
        new.append({**row, "evaluation": evaluation, "outreach_status": "UNSENT",
                    "reply_status": "NOT_CHECKED"})
    new.sort(key=lambda item: (-item["evaluation"]["score"], tidy(item.get("name"))))
    overflow = max(0, len(new) - 15)
    new = new[:15]
    shortlist = [r for r in new if r["evaluation"]["state"] == "RESEARCH_READY"
                 and r.get("contact_method") in ("email", "form")][:5]
    out = Path(out_dir)
    repository_root = Path(__file__).resolve().parents[1]
    if out.resolve() == repository_root or repository_root in out.resolve().parents:
        raise ValueError("Private investor outputs must be outside the public Git repository")
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(out, 0o700)
    # Exports are local only, never uploaded or published by this program.
    exports = {
        "candidates.json": json.dumps(new, ensure_ascii=False, indent=2),
        "drafts_UNSENT.txt": "\n\n---\n\n".join(outreach_draft(r) for r in shortlist),
        "brief_ru.md": report(new, shortlist, duplicates, overflow, run_date),
        "history_additions.jsonl": "\n".join(json.dumps({"name": r.get("name"),
                         "website": r.get("website")}, ensure_ascii=False) for r in new) + ("\n" if new else ""),
    }
    for filename, data in exports.items():
        p = out / filename
        p.write_text(data, encoding="utf-8")
        os.chmod(p, 0o600)
    return {"unique": len(new), "duplicates": duplicates, "overflow": overflow,
            "research_ready": len(shortlist), "output": str(out)}


def report(new, shortlist, duplicates, overflow, run_date):
    lines = [f"# Pegasus Private Network — {run_date}", "",
             f"Новых уникальных: {len(new)}. Повторов исключено: {duplicates}. "
             f"Сверх дневного лимита (не экспортировано): {overflow}.",
             f"Приоритетных кандидатов с ручной проверкой источников: {len(shortlist)}.",
             "Все письма — UNSENT. Ответы — NOT_CHECKED, пока не проверены по почте.",
             "RESEARCH_READY означает только исследовательский контакт, не допуск к размещению.", ""]
    for row in new:
        result = row["evaluation"]
        money = (f" · подтверждённый минимальный прямой equity-чек ${result['confirmed_min_check_usd']:,}"
                 if result["confirmed_min_check_usd"] is not None else " · минимальный чек неизвестен")
        lines.extend([f"## {tidy(row.get('name'))} — {result['state']}",
                      f"{tidy(row.get('country'))} · {tidy(row.get('type'))}{money}",
                      f"US evidence: {tidy(row.get('evidence_kind'))} — {tidy(row.get('evidence_url'))}",
                      f"Official: {tidy(row.get('official_source_url'))} (human-verified: {row.get('source_verified') is True})",
                      f"Контакт: {tidy(row.get('contact_method'))} — {tidy(row.get('contact'))}",
                      f"Дальше: {tidy(row.get('next_step')) or 'Запросить критерии US-project fit'}",
                      f"Контроль: {', '.join(result['issues']) if result['issues'] else 'только introductory outreach; KYC/OFAC/securities/CFIUS не одобрены'}", ""])
    lines.append("Не выполнять отправку, публикацию, платные услуги или изменения production.")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="Daily candidates JSONL, verified manually")
    ap.add_argument("--history", nargs="+", required=True, help="Prior JSONL ledger(s), may be empty")
    ap.add_argument("--out", required=True, help="Private local output directory")
    ap.add_argument("--date", required=True, help="Run date in ISO YYYY-MM-DD")
    args = ap.parse_args()
    print(json.dumps(run(args.input, args.history, args.out, args.date), ensure_ascii=False))


if __name__ == "__main__":
    main()