# Contributing to the Tulip docs

Fixes and improvements to [tulipagents.ai](https://tulipagents.ai/) are welcome
— typos, broken links, clearer explanations, new notebook pages.

## Development setup

```bash
git clone https://github.com/tuliplabs-ai/docs.git
cd docs
pip install hatch
hatch run sdk      # install the SDK the API reference imports (TULIP_SDK_DIR overrides ../tulip-agents)
hatch run serve    # live preview at http://127.0.0.1:8000
hatch run build    # strict production build — must pass before a PR
```

The repo's Python tooling (mkdocs hooks, the notebook-page scaffolder) is
tested; run `hatch run test:check` if you touch `hooks/` or `scripts/`.

## Writing guidelines

- The docs are about **agentic AI generally** — disciplines (security,
  payments, ITSM, …) appear as examples only, never as the framing.
- Explain the mechanism; keep copy concise. One pass per argument.
- General concept pages use general agentic examples; domain-specific content
  belongs on the dedicated pages for that domain.
- New SDK notebooks get a page scaffolded with
  `python scripts/gen_notebook_pages.py`, then hand-edit the prose.

## Pull requests

- `hatch run build` (strict) must pass — it fails on broken links and nav.
- Conventional Commit titles (`docs:`, `fix:` …).

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).

## Security

See [SECURITY.md](SECURITY.md) for coordinated disclosure.
