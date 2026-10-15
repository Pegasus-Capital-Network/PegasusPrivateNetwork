# Repository instructions for all coding agents

`CLAUDE.md` defines the site identity, protected content, data boundaries and
release rules for every agent, not only Claude. Read it and `RELEASE.md` first.

All changes use a feature branch and pull request. Keep the cinematic page and
its real video/photos intact. Use the existing Netlify project only. Leave its
auto publishing locked. Do not publish production without the owner's explicit
instruction for a reviewed preview. Never self-approve the owner's GitHub
`preview-review` gate or bypass/disable required checks.

The build validates `config/site-contract.json` and publishes only `dist/`.
Source instructions, tests and config are not public-site assets. `.netlify/`,
`dist/` and credentials stay untracked. A missing/corrupt media file, stripped
section or changed form destination is a failure to fix, not a check to remove.

The initial protection installation is activated by repository settings after
its own PR has passed automated checks and its preview has been inspected. It
does not authorize any new production publication.
