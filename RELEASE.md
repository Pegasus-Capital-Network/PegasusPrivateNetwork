# Preview review and production release

## Normal change

1. Branch from current `main`, make the scoped change, and open a PR to `main`.
2. GitHub runs **Site integrity**: cinematic sections, six projects, legal
   notices, original form schema, referenced assets and SHA-256 of the 14
   protected binary assets. The regression tests reject the original class of
   one-page replacement, missing media, form rerouting and removed disclosures.
3. Netlify builds a Deploy Preview on **the existing project**. **Preview smoke**
   waits for its `ppn-commit` marker to match the PR HEAD, then checks content,
   form markup and every protected asset over HTTPS. A stale preview fails.
   CI sends no form submissions and requires no Netlify secret.
4. Open `https://deploy-preview-PR_NUMBER--vermillion-bavarois-9a6182.netlify.app/`.
   Review video playback and poster, all six property examples and gallery,
   desktop and 390px mobile layout, Tokenization 101, FAQ, risk notices and form
   validation. A real submission is optional, requires owner authorization and
   must be clearly marked TEST. Confirm exactly one record in the existing
   form, check Spam if needed, and do not delete historical records.
5. Record the reviewed commit, preview URL, screenshots and results in the PR.
   The owner opens its Actions run, chooses **Review deployments**, selects
   `preview-review` and approves after inspecting that exact preview. New
   commits cancel the old run and require a new smoke check and approval.
6. Merge only after **Site integrity**, **Preview smoke**, and **Preview approval**
   pass. `main` rejects direct pushes, force pushes and deletion, including by
   administrators. Conversation resolution and an up-to-date branch are required.

## Publish a reviewed release

Auto publishing in Netlify stays **locked**. Merge does not change the domain.
The owner explicitly authorizes publishing the reviewed change.

1. Find the new `main` build in the existing project's Deploys list. Confirm
   the GitHub commit and successful build; do not publish another branch/site.
2. Inspect that build's immutable permalink. Confirm it includes the approved
   changes, renders correctly, and its `ppn-commit` equals its `main` SHA.
   A squash/merge SHA differs from the PR SHA, so verify the resulting `main`
   snapshot again. If other changes entered `main`, review them too.
3. Publish this **new verified build** using Netlify's Publish deploy action.
   Do not unlock continuous auto publishing or restore an older deployment.
4. Confirm the project reports that exact deploy as current, fetch the actual
   production domain, check video/images/form, and report commit, deploy ID,
   preview/permalink and test results. Keep the published deploy locked.

Identity: `Pegasus-Capital-Network/PegasusPrivateNetwork` / `main`;
site `fcb47e1e-3195-4bfd-be13-20b52b5addf5`,
`vermillion-bavarois-9a6182`, `https://pegasusprivatenetwork.com/`.
Never modify the separate Pegasus Capital Network project in this process.

## Administration and limits

- Required checks are bound to the GitHub Actions app. The `preview-review`
  environment requires owner `@westccmortgage` and disallows administrator
  bypass of that environment's protection rule.
- Owner self-review is allowed in the environment because this repository has
  one human collaborator and agents use the same GitHub account. Agents are
  expressly forbidden to exercise this approval on the owner's behalf.
- GitHub/Netlify owners can still deliberately change protection settings or
  manually publish elsewhere in their dashboards. These safeguards prevent
  accidental/ordinary workflow overwrites; they are not a separation of
  privileges from an agent holding the owner's administrator credentials.
- Keep production credentials out of GitHub Actions. The CI cannot publish.
- Legitimate content/media/baseline changes must explain the owner-authorized
  change to the contract and receive the same preview approval. Do not weaken
  a test solely to make missing/replacement content pass.
- If a bad version is ever published, fix forward in Git and review the new
  build. A failed build never replaces the current production deployment.
