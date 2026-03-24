# Development Leads

- Doug Blank \<doug.blank@gmail.com>
- Steven Silvester \<steven.silvester@ieee.org>

# Patches and Suggestions

- Daniel Mendler @minad
- Thomas Kluyver @takluyver

# Release Process

Releases are handled by the `release.yml` GitHub Actions workflow, triggered manually via `workflow_dispatch`.

The `version` input accepts a version number (e.g. `1.0.0rc4`) or one of: `patch`, `minor`, `major`, `prepatch`, `preminor`, `premajor`, `prerelease`.

## Using the GitHub UI

1. Go to **Actions > Release** in the repository.
1. Click **Run workflow**.
1. Fill in the **version** field (e.g. `patch`, `minor`, `1.0.0`).
1. Optionally fill in the **changelog_body** field with custom release notes. Use `\n` for newlines since the GitHub web UI input is single-line.
1. Optionally check **Dry run** to test without publishing.
1. Click **Run workflow**.

## Using the CLI

### Basic release

```bash
gh workflow run release.yml -f version=patch
```

### Release with custom changelog

You can provide a custom changelog body using the `changelog_body` input:

```bash
gh workflow run release.yml \
  -f version=patch \
  -f changelog_body="## Highlights

MetaKernel 1.0 is a major release.

## New Features

- DisplayData() for raw MIME bundle display (#211)"
```

### Dry run

To test the release process without publishing:

```bash
gh workflow run release.yml -f version=patch -f dry_run=true
```

A dry run creates a draft release then deletes it, and does not push changes or publish to PyPI.
