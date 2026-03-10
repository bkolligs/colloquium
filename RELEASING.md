# Releasing Colloquium

This document is the manual checklist for a release.

## Before the first release

1. Enable GitHub Pages for the repository.
2. Configure PyPI trusted publishing for the `Release` workflow.
3. Confirm the examples site workflow can deploy from `main`.

## Release checklist

1. Make sure `main` is clean and up to date.
2. Update the version in:
   - [`pyproject.toml`](./pyproject.toml)
   - [`colloquium/__init__.py`](./colloquium/__init__.py)
3. Move notable changes from `Unreleased` into a dated release section in [`CHANGELOG.md`](./CHANGELOG.md).
4. Run verification:

   ```bash
   uv run pytest
   uv run python scripts/build_examples_site.py
   uv run colloquium build examples/hello/hello.md
   uv run colloquium export examples/hello/hello.md
   ```

5. Commit the version/changelog update.
6. Tag the release:

   ```bash
   git tag v0.1.0
   git push origin main --tags
   ```

7. Confirm the `Release` workflow publishes to PyPI.
8. Confirm the `Examples site` workflow has deployed the latest examples/docs site.

## Notes

- `uv build` writes distributions to `dist/`.
- Generated example HTML/PDF/PPTX files should remain untracked.
- If the PyPI publish step fails, fix the workflow or trusted publishing settings before retagging.
