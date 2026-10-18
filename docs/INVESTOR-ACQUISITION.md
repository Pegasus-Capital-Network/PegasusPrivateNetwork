# Pegasus Private Network — international investor acquisition, Phase 1

**Development-only operator tool, not an offering or an active investment portal.**
Do not commit real investor records, contacts, correspondence, prospect lists or
KYC materials to this **public** GitHub repository. This repo publishes only the
validated educational website in `dist/`; this operator tool must not be added to
that build or served from the public site.

## What is implemented

`tools/investor_pipeline.py` is a dependency-free offline CLI for daily source
review, classification, deduplication, basic scale-fit scoring, hold flags,
Russian research reporting and at most five **UNSENT** English introductory
drafts. It sends no mail, accesses no network, updates no database and does not
change Netlify. All generated files must be **outside the repository**, with
private directory/file permissions. The script *does not verify websites*; it
requires a named human to attest that an official primary source was checked.

**Segmentation**: `direct_investor`, `gatekeeper`, `platform`, `community`,
`lender`, `strategic`, `sovereign_fund`. A sovereign fund is on hold as a
small-project target without specific smaller-deal substantiation. Loan/fund size
cannot be mislabeled as a minimum direct-equity investment. Source evidence must
be `us_closed_deal` or `us_public_mandate`, with HTTPS evidence and official URLs.

**Research-ready is not permission to solicit securities.** No prospect is
"KYC approved", "OFAC clear", "CFIUS approved" or eligible to invest because this
tool produces a row or draft. Escalations are flagged for an appropriately
qualified reviewer. China/Hong Kong receive additional transaction-specific
legal-review hold; this is a review rule, not a nationality ban.

## Run (local development, with synthetic/test data first)

Create outside the repo: `daily.jsonl`, `history.jsonl`, private output folder.
JSONL means one JSON object per line, each record manually documented. For the
first run, `history.jsonl` can be **empty**; every subsequent run should include
all prior names/domains, using the generated `history_additions.jsonl` appended
to the private master ledger after reviewing the output. Never overwrite prior
history or re-import an unverified spreadsheet as "verified".

```bash
python3 tools/investor_pipeline.py \
  --input /private/pegasus/daily.jsonl \
  --history /private/pegasus/history.jsonl \
  --out /private/pegasus/run-2026-10-18 \
  --date 2026-10-18
python3 -m unittest discover -s tests -p 'test_investor_pipeline.py' -v
```

Required research record fields (example uses **fictional** `.test` URLs):

```json
{"name":"Example Family Office","website":"https://example.test","country":"Canada","type":"direct_investor","evidence_kind":"us_closed_deal","evidence_url":"https://example.test/deals","official_source_url":"https://example.test","source_verified":true,"verified_by":"research analyst","verified_at":"2026-10-18","contact_method":"form","contact":"https://example.test/contact","focus":"U.S. residential real estate","scale_fit":"yes","scale_fit_reason":"specific US residential joint-venture precedent","sanctions_status":"not_screened","cfius_status":"not_reviewed","next_step":"Ask about US small-project criteria"}
```

Optional minimum investment fields **only** when publicly verified: `min_check_usd`,
`minimum_context="direct_equity_check"`, and `minimum_source_url` (HTTPS).
`us_closed_deal` history value, loan-limit or platform subscription minimum is
not a confirmed minimum direct-equity cheque.

Output is `candidates.json`, `brief_ru.md`, `drafts_UNSENT.txt`, and
`history_additions.jsonl`. `reply_status=NOT_CHECKED` is deliberately not a
claim of zero replies. No reply handling is implemented.

## Operating policy and next-phase integration

1. Keep Private Network public site educational only: existing Netlify
   `request-access` submissions, 6 property examples, 14 media assets, risk
   disclosures, and previews must remain intact. Never dual-write its form.
2. Capital Network is the operating system for private profiles, deal rooms,
   capital matching and authenticated administration. A future investor pipeline
   UI belongs behind Capital Network admin auth/RLS, **not** as public investor
   contact listings or prospect JSON on either website.
3. Import historic unique keys from Oct 15–18 daily workbooks **privately**.
   Normalize legal entities and aliases. The historical workbooks are research,
   not proof of confirmed receipt or subscription. Incorporate newly verified
   replies only from actual email records.
4. Later phases need: restricted server-side storage and RLS, audit log,
   ownership/beneficial-owner and sanctions review workflows, proper deal/sponsor
   legal review, controlled jurisdiction-specific eligibility, and a **human
   approval gate** for every sending/investment action. No tokenized ROI or
   trading/liquidity guarantees.
5. For cross-border distribution, counsel must select the applicable US and
   destination-country securities regimes before any offering-oriented material.
   Introducers receiving transaction-dependent compensation need specific
   broker-dealer analysis. The site must not call speculative features live.

Official reference starting points (revalidate for each deal and jurisdiction):

- SEC Rule 506(b): https://www.sec.gov/resources-small-businesses/exempt-offerings/private-placements-rule-506b
- SEC Rule 506(c) investor verification: https://www.sec.gov/resources-small-businesses/capital-raising-building-blocks/assessing-accredited-investors-under-regulation-d
- SEC broker/dealer issues for finders: https://www.sec.gov/about/divisions-offices/division-trading-markets/division-trading-markets-compliance-guides/guide-broker-dealer-registration
- SEC Regulation S offshore placements: https://www.sec.gov/divisions/corpfin/internatl/foreign-private-issuers-overview.shtml
- Treasury CFIUS real-estate FAQ: https://home.treasury.gov/faq-item/international-affairs/are-all-real-estate-transactions-covered-if-they-fall-within-the-specific-geographic-areas-described-in-the-regulations
- OFAC list search: https://ofac.treasury.gov/sanctions-list-search-tool

No real outreach, production modification, paid third-party service, securities
marketing, contact publication, brokerage compensation or investment commitment
is authorized by this development module.