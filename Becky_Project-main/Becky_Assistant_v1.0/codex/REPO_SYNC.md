# GitHub repo sync checklist

If you want Codex to pull/push changes from GitHub, give it:
- Repo URL (https)
- Default branch name
- Whether it should open PRs or push directly
- Any required secrets (never commit them)

Recommended approach:
1) Add `.gitignore` (include `.venv/`, `__pycache__/`, `dist/`, `build/`, `*.spec`)
2) Store secrets in environment variables
3) Use GitHub Actions for tests (optional)

If you paste your repo URL here later, we can tailor:
- exact clone/push commands
- CI workflow file
- release/build steps (PyInstaller)
