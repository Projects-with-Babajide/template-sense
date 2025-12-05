# Release Process

This document explains how to create and publish new releases of Template Sense.

## Overview

Template Sense uses automated GitHub Actions workflows to:
1. Test the code across Python 3.10, 3.11, 3.12, and 3.13
2. Build distribution packages (wheel and source)
3. Create a GitHub release with changelog
4. Publish to PyPI automatically

All of this happens when you push a version tag (e.g., `v0.1.0`).

---

## Prerequisites (One-Time Setup)

### 1. PyPI Account
- Create an account at https://pypi.org/account/register/
- Verify your email address
- (Optional but recommended) Enable 2FA

### 2. Configure PyPI Trusted Publishing

This is **required** for the automated PyPI publishing to work. Trusted publishing is more secure than API tokens.

**Steps:**

1. Go to https://pypi.org/manage/account/publishing/
2. Click **"Add a new pending publisher"**
3. Fill in the form:
   - **PyPI Project Name:** `template-sense`
   - **Owner:** `Projects-with-Babajide`
   - **Repository name:** `template-sense`
   - **Workflow name:** `release.yml`
   - **Environment name:** `pypi`
4. Click **"Add"**

**Important:** You must do this **before** your first release. After the first successful release, PyPI will automatically trust future releases from this workflow.

### 3. Verify Package Name Availability

Check that `template-sense` is available on PyPI:
- Visit: https://pypi.org/project/template-sense/
- If it shows "Not Found" or is available, you're good to go
- If taken, you'll need to choose a different name in `pyproject.toml`

---

## Creating a Release

### Step 1: Update the Version Number

Edit `pyproject.toml` and update the version:

```toml
[project]
name = "template-sense"
version = "0.2.0"  # Update this line
```

**Version Numbering Guide** (Semantic Versioning):
- **Patch** (0.1.0 → 0.1.1): Bug fixes, no new features
- **Minor** (0.1.1 → 0.2.0): New features, backward compatible
- **Major** (0.2.0 → 1.0.0): Breaking changes, not backward compatible

### Step 2: Commit the Version Change

```bash
git add pyproject.toml
git commit -m "chore: Bump version to 0.2.0"
git push origin main
```

### Step 3: Create and Push a Git Tag

```bash
# Create the tag (must start with 'v')
git tag v0.2.0

# Push the tag to GitHub
git push origin v0.2.0
```

**Important:** The tag must match the pattern `v*.*.*` (e.g., `v0.1.0`, `v1.2.3`) to trigger the release workflow.

### Step 4: Monitor the Workflow

1. Go to: https://github.com/Projects-with-Babajide/template-sense/actions
2. Click on the "Release" workflow run
3. Watch the progress through these jobs:
   - **Test** - Runs linting and tests across all Python versions
   - **Build** - Creates wheel and source distributions
   - **Create Release** - Generates changelog and creates GitHub release
   - **Publish to PyPI** - Uploads to PyPI

### Step 5: Verify the Release

Once the workflow completes:

1. **Check GitHub Release:**
   - Visit: https://github.com/Projects-with-Babajide/template-sense/releases
   - You should see your new release with changelog and downloadable files

2. **Check PyPI:**
   - Visit: https://pypi.org/project/template-sense/
   - Your new version should appear
   - Test installation: `pip install template-sense==0.2.0`

---

## Workflow Details

### What Happens Automatically

When you push a tag:

1. **Testing** (runs in parallel for Python 3.10, 3.11, 3.12, 3.13):
   - Black formatting check
   - Ruff linting
   - Pytest unit tests with coverage

2. **Building** (only if tests pass):
   - Creates wheel file (`.whl`)
   - Creates source distribution (`.tar.gz`)

3. **GitHub Release** (only if build succeeds):
   - Generates changelog from git commits since last tag
   - Creates release page with:
     - Version number
     - Changelog
     - Downloadable distribution files
     - GitHub's auto-generated release notes

4. **PyPI Publishing** (only if release created):
   - Uploads wheel and source to PyPI
   - Uses trusted publishing (no API tokens needed)
   - Makes package installable via `pip install template-sense`

### Changelog Generation

- **First release:** Uses a default template listing features
- **Subsequent releases:** Automatically generated from git commits between tags
- **Format:** Lists all commit messages with short hashes
- **Excludes:** Merge commits

---

## Troubleshooting

### Workflow Fails on Test Job

**Problem:** Tests fail, preventing release.

**Solution:**
1. Check the workflow logs to see which test failed
2. Fix the issue locally
3. Delete the tag: `git tag -d v0.2.0` and `git push origin :refs/tags/v0.2.0`
4. Fix the code, commit, and try again

### PyPI Publishing Fails

**Problem:** "Trusted publishing not configured" or similar error.

**Solution:**
1. Ensure you completed the "Configure PyPI Trusted Publishing" setup (see Prerequisites)
2. Check that all details match exactly:
   - Repository: `Projects-with-Babajide/template-sense`
   - Workflow: `release.yml`
   - Environment: `pypi`
3. For first-time publish, PyPI might need a few minutes to activate trusted publishing

**Problem:** "Project name already exists" on PyPI.

**Solution:**
1. Someone else is using `template-sense` on PyPI
2. Choose a different name in `pyproject.toml`
3. Update the PyPI trusted publishing configuration with the new name

### Wrong Version Released

**Problem:** You pushed the wrong tag or version.

**Solution for GitHub Release:**
1. Delete the GitHub release from the releases page
2. Delete the tag: `git tag -d v0.2.0` and `git push origin :refs/tags/v0.2.0`
3. Fix the version and create a new tag

**Solution for PyPI:**
- **Cannot delete** versions from PyPI (they're permanent)
- You can "yank" a version (marks it as unavailable but keeps it for historical purposes):
  ```bash
  pip install twine
  twine upload --repository pypi --skip-existing dist/*
  ```
- Best practice: Just release the next patch version with fixes

### Re-running a Failed Workflow

If the workflow fails for a transient reason (network issue, etc.):

1. Go to the workflow run page
2. Click "Re-run failed jobs"
3. Or delete and re-push the tag to start fresh

---

## Version History Best Practices

### Commit Messages

Write clear commit messages since they become your changelog:

**Good:**
```
feat: Add support for multi-sheet Excel files
fix: Handle empty cells in header detection
docs: Update API usage examples
```

**Bad:**
```
update stuff
fix bug
wip
```

### Pre-Release Versions

For testing releases before making them official:

```bash
# Tag with pre-release suffix
git tag v0.2.0-beta.1
git push origin v0.2.0-beta.1
```

Mark as pre-release in GitHub, or use PyPI's `--pre` flag.

### Hotfix Releases

For urgent bug fixes:

1. Create a hotfix branch from the release tag
2. Fix the bug
3. Bump to next patch version (e.g., 0.2.0 → 0.2.1)
4. Create and push tag
5. Merge hotfix back to main

---

## Rolling Back a Release

### If You Haven't Published Yet

Delete the tag before the workflow completes:

```bash
git tag -d v0.2.0
git push origin :refs/tags/v0.2.0
```

### If Already Published to GitHub

1. Delete the GitHub release (via web UI)
2. Delete the tag (see above)
3. Users who already downloaded remain unaffected

### If Already Published to PyPI

**You cannot delete from PyPI**, but you can:

1. **Yank the version** (makes it unavailable for new installs):
   - Go to https://pypi.org/manage/project/template-sense/releases/
   - Click on the version
   - Click "Options" → "Yank release"
   - Provide a reason (e.g., "Critical bug - use v0.2.1 instead")

2. **Release a fixed version**:
   - Fix the issue
   - Bump to the next patch version (0.2.0 → 0.2.1)
   - Release normally

---

## Installation Instructions for Users

After publishing, users can install Template Sense in three ways:

### From PyPI (Recommended)

```bash
# Latest version
pip install template-sense

# Specific version
pip install template-sense==0.2.0
```

### From GitHub Release

```bash
# Latest release
pip install git+https://github.com/Projects-with-Babajide/template-sense.git@main

# Specific release
pip install git+https://github.com/Projects-with-Babajide/template-sense.git@v0.2.0
```

### In requirements.txt

```txt
# PyPI
template-sense==0.2.0

# GitHub
template-sense @ git+https://github.com/Projects-with-Babajide/template-sense.git@v0.2.0
```

---

## Checklist for Releases

Use this checklist every time you create a release:

- [ ] All tests pass locally (`pytest`)
- [ ] Code is formatted (`black .`) and linted (`ruff check .`)
- [ ] Version number updated in `pyproject.toml`
- [ ] Version follows semantic versioning rules
- [ ] Changes committed to main branch
- [ ] PyPI trusted publishing configured (first release only)
- [ ] Git tag created with `v` prefix (e.g., `v0.2.0`)
- [ ] Tag pushed to GitHub
- [ ] Workflow completed successfully
- [ ] GitHub release created with changelog
- [ ] Package published to PyPI
- [ ] Installation tested: `pip install template-sense==0.2.0`

---

## Questions or Issues?

- **GitHub Actions logs:** Check workflow runs at https://github.com/Projects-with-Babajide/template-sense/actions
- **PyPI project page:** https://pypi.org/project/template-sense/
- **Report issues:** https://github.com/Projects-with-Babajide/template-sense/issues
