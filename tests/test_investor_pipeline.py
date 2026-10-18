"""Offline checks: dedupe, evidence gates, privacy and no-mail contract."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from investor_pipeline import identity, outreach_draft, run, triage


def candidate(**changes):
    r = dict(name="Example Family Office", website="https://example.test", country="Canada",
             type="direct_investor", evidence_kind="us_closed_deal",
             evidence_url="https://example.test/deals", official_source_url="https://example.test",
             source_verified=True, verified_by="human reviewer", verified_at="2026-10-18",
             contact_method="form", contact="https://example.test/contact",
             scale_fit="yes", scale_fit_reason="public direct project case", focus="residential real estate",
             sanctions_status="not_screened", cfius_status="not_reviewed", next_step="Request criteria")
    r.update(changes)
    return r


class PipelineTest(unittest.TestCase):
    def test_qualified_candidate_only_intro(self):
        r = candidate()
        self.assertEqual(triage(r)["state"], "RESEARCH_READY")
        d = outreach_draft(r)
        self.assertIn("UNSENT", d)
        self.assertIn("not an offering of securities", d)
        self.assertNotIn("guaranteed", d)

    def test_source_provenance_required(self):
        for change in ({"source_verified": False}, {"evidence_kind": "rumor"},
                       {"official_source_url": "http://test.com"}, {"verified_by": ""}):
            self.assertEqual(triage(candidate(**change))["state"], "HOLD")

    def test_no_sovereign_shortcut_or_china_assumption(self):
        self.assertEqual(triage(candidate(type="sovereign_fund"))["state"], "HOLD")
        china = candidate(country="China")
        self.assertEqual(triage(china)["state"], "HOLD")
        self.assertIn("legal review pending", " ".join(triage(china)["issues"]))
        self.assertEqual(triage(candidate(country="China", cross_border_legal_review="completed"))["state"], "RESEARCH_READY")

    def test_minimum_is_not_deal_volume(self):
        r = candidate(min_check_usd=750000, minimum_context="loan_size", minimum_source_url="https://example.test")
        self.assertIsNone(triage(r)["confirmed_min_check_usd"])
        r.update(minimum_context="direct_equity_check")
        self.assertEqual(triage(r)["confirmed_min_check_usd"], 750000)

    def test_identity_domain_alias_and_duplicate_history(self):
        self.assertEqual(identity(candidate(website="http://www.EXAMPLE.test/welcome")),
                         identity(candidate()))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            daily = root / "daily.jsonl"
            history = root / "history.jsonl"
            history.write_text(json.dumps(candidate()) + "\n", encoding="utf-8")
            daily.write_text("\n".join(json.dumps(candidate(**c)) for c in [
                {"name": "Example Family Office", "website": "https://www.example.test/x"},
                {"name": "New Fund", "website": "https://new.test"},
                {"name": "New Fund", "website": "https://new.test/copy"}]), encoding="utf-8")
            result = run(daily, [history], root / "out", "2026-10-18")
            self.assertEqual((result["unique"], result["duplicates"]), (1, 2))
            self.assertIn("UNSENT", (root / "out/drafts_UNSENT.txt").read_text())
            self.assertEqual((root / "out/history_additions.jsonl").read_text().count("\n"), 1)

    def test_no_private_exports_inside_public_repo(self):
        with tempfile.TemporaryDirectory() as d:
            inp = Path(d) / "daily.jsonl"
            hist = Path(d) / "history.jsonl"
            inp.write_text(json.dumps(candidate()), encoding="utf-8")
            hist.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside the public Git repository"):
                run(inp, [hist], Path(__file__).resolve().parents[1] / "leads", "2026-10-18")

    def test_sanctions_escalation_and_contact_validation(self):
        self.assertEqual(triage(candidate(sanctions_status="possible_match"))["state"], "HOLD")
        self.assertEqual(triage(candidate(contact_method="form", contact="javascript:alert(1)"))["state"], "HOLD")

    def test_no_history_not_allowed_and_no_external_actions(self):
        with self.assertRaises(ValueError):
            run("no_such_file", [], "nowhere", "2026-10-18")
        source = (Path(__file__).resolve().parents[1] / "tools/investor_pipeline.py").read_text()
        for forbidden in ("smtplib", "requests.post", "urllib.request", "subprocess.run", "send_email("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()