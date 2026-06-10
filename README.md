# Tulip documentation

The source for **[tulipagents.ai](https://tulipagents.ai/)** — the
documentation site for [Tulip](https://github.com/tuliplabs-ai/sdk-python),
the open-source SDK for building auditable agent teams.

Built with [MkDocs](https://www.mkdocs.org/) +
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/). The API
reference is generated from the SDK's docstrings via
[mkdocstrings](https://mkdocstrings.github.io/).

## Local development

Everything is managed by [Hatch](https://hatch.pypa.io/) via
`pyproject.toml`. The API reference imports the `tulip` package, so the
SDK has to be installed into the env. With the [`sdk-python`][sdk] repo
checked out next to this one:

```bash
hatch run sdk      # install the SDK (TULIP_SDK_DIR overrides ../tulip-agents)
hatch run serve    # → http://127.0.0.1:8000
hatch run build    # strict production build into site/
```

## Deploying

Every push to `main` builds with `hatch run build` (strict mkdocs) and
publishes to GitHub Pages via `.github/workflows/deploy.yml`. The custom domain is
pinned by [`docs/CNAME`](docs/CNAME) (`tulipagents.ai`).

For the deploy job to build the API reference it needs read access to the
SDK repo. If `sdk-python` is private, add a repo-scoped
`SDK_READ_TOKEN` secret; for a public SDK the default `GITHUB_TOKEN` is
enough.

## Structure

| Path | What it holds |
|---|---|
| `docs/` | All Markdown content, notebooks, images, CSS/JS |
| `overrides/` | Material theme overrides (title, social cards, header) |
| `mkdocs.yml` | Navigation, theme, plugins |
| `pyproject.toml` | Hatch env — toolchain deps and the `sdk`/`serve`/`build` scripts |
| `scripts/` | `gen_notebook_pages.py` — scaffolds `docs/notebooks/` pages for new SDK notebooks |

When a new notebook lands in the SDK repo, scaffold its page and then
edit the prose (the script finds the SDK via `TULIP_SDK_DIR`, falling
back to `../tulip-agents`; existing pages are hand-curated and never
overwritten):

```bash
python scripts/gen_notebook_pages.py
```

## License

Documentation prose © 2026 Tulip Labs, released under
[Apache-2.0](LICENSE) (see [`NOTICE`](NOTICE) for provenance). Code samples
are offered under the same terms as the SDK.

[sdk]: https://github.com/tuliplabs-ai/sdk-python
