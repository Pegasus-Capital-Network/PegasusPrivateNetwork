# Pegasus Private Network — instructions for Claude

Read `AGENTS.md` and `RELEASE.md` before editing or deploying.

This repository is the restored **cinematic Pegasus Private Network** website,
not Pegasus Capital Network, MDAI, a placeholder, or a replacement landing page.
Preserve the drone hero video, actual binary photos, six project examples,
tokenization education, risk disclosures, FAQ and investor registration.
Never replace the website with a simplified page to satisfy another task.

## Fixed identity

- Repository: `Pegasus-Capital-Network/PegasusPrivateNetwork`, base branch `main`.
- Netlify project: `vermillion-bavarois-9a6182`.
- Netlify site ID: `fcb47e1e-3195-4bfd-be13-20b52b5addf5`.
- Production: `https://pegasusprivatenetwork.com/`.
- Recovery baseline: `c22038a8719724ea0154de5df131a22886f0b5e1`.
- Separate Capital Network project must not be edited by work in this repository.

## Required delivery path

1. Work on a feature branch; never push directly or force-push to `main`.
2. Preserve a Git backup before destructive edits. Inspect the existing site first.
3. Run `python3 -m unittest discover -s tests -v`, `node tests/form-behavior.cjs`
   and `python3 scripts/build_site.py`.
4. Open a PR. Wait for **Site integrity** and **Preview smoke** for its exact HEAD.
5. Supply the preview URL, commit, screenshots, media/mobile/form results and
   any limitations. A green build alone does not approve the visual result.
6. The owner reviews the preview and approves the GitHub `preview-review`
   environment. **Never approve that environment on the owner's behalf**, use
   the approval API, bypass checks, or weaken protection to finish a task.
7. Merge only after the three required checks pass. Production remains locked.
8. Only after an explicit owner instruction to publish that reviewed change,
   follow `RELEASE.md` and publish its verified `main` build in the same site.
   Leave auto publishing locked afterward.

Do not run `netlify deploy --prod`, unlock auto publishing, change production
branch, create another Netlify site, upload an unrelated ZIP, or publish an
unreviewed deploy. Do not add `[skip ci]` / `[skip netlify]` to evade checks.
Do not rewrite `config/site-contract.json`, tests, workflow, approval settings or
these instructions merely to make a failing replacement pass. Changes to those
controls need an explicit owner request and a visible explanation in the PR.

## Registration and data

The restored site uses the existing Netlify form `request-access`, ID
`6a98af918cf7db00085efcba`. Preserve its name, existing field names and submissions,
including Spam. Never delete/recreate it or silently migrate to Supabase.
Do not dual-write to Netlify and Supabase. Do not resubmit on ambiguous failure.
A real test submission needs explicit authorization and a unique TEST marker;
read-only CI never sends a lead. Same-session duplicate guards do not provide
server-side cross-device idempotency.

If a task touches Supabase, inspect RLS first. Do not modify tables, policies,
secrets, or submissions under a website-only task. Never publish a service key.

Education is not an offering. Preserve principal-loss/liquidity risk, no-offer,
no-return-guarantee and no-broker/custody disclosures. Planned dashboards, tokens,
trading and payments must not be presented as live functionality.
