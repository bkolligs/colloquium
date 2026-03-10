# Releasing Colloquium

This document is the manual checklist for a release.

## Release checklist

1. Make sure `main` is clean and up to date.
2. Update the version in:
   - [`pyproject.toml`](./pyproject.toml)
   - [`colloquium/__init__.py`](./colloquium/__init__.py)
3. Move notable changes from `Unreleased` into a dated release section in [`CHANGELOG.md`](./CHANGELOG.md).
4. Run verification:

   ```bash
   uv run pytest
   uv run python docs/build.py
   uv run colloquium build examples/hello/hello.md
   uv run colloquium export examples/hello/hello.md
   ```

5. Commit the version/changelog update.
6. Tag the release:

   ```bash
   git tag v0.1.0
   git push origin main --tags
   ```

7. Build and publish manually:

   ```bash
   uv build
   uv publish
   ```

8. Confirm the `Website` workflow has deployed the latest site.

## Changelog convention

Every PR must add a line to the `[Unreleased]` section of `CHANGELOG.md` (enforced by CI).
Format: one line per PR, ending with the PR number.

```
- Short description of the change (#42)
```

At release time, move the `[Unreleased]` lines into a dated section. The flat list copies directly into GitHub release notes.

## Notes

- `uv build` writes distributions to `dist/`.
- Generated example HTML/PDF/PPTX files should remain untracked.
- If `uv publish` is not configured locally yet, finish PyPI setup before tagging.
