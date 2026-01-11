<# 
tools/auto_push.ps1

What this script does:
1) Finds your becky repo folder automatically (even if you run it from the wrong place)
2) Checks out the "work" branch (creates it if needed)
3) Ensures the Git remote "origin" points to the right GitHub repo
4) Runs safety checks:
   - tools/precommit_guard.py (if present)
   - python -m compileall .
   - pytest -q
5) Optionally auto-commits changes
6) Pushes to GitHub
7) Confirms the branch exists on GitHub and prints the PR link
#>

param(
  [string]$RepoUrl = "https://github.com/megelisebender-cmd/becky-ootp26-assistant.git",
  [string]$Branch = "work",
  [switch]$AutoCommit,
  [string]$CommitMessage = "Automated verify + push",
  [switch]$DeepSearch
)

$ErrorActionPreference = "Stop"

function Say($msg) { Write-Host $msg -ForegroundColor Cyan }
function Ok($msg)  { Write-Host "✅ $msg" -ForegroundColor Green }
function Warn($msg){ Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Die($msg) { Write-Host "❌ $msg" -ForegroundColor Red; exit 1 }

function Is-GitRepo($path) {
  return (Test-Path (Join-Path $path ".git"))
}

function Find-RepoFolder($targetUrl) {
  # 1) If you're already inside a repo, try that first
  try {
    $top = git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -eq 0 -and $top) {
      $top = $top.Trim()
      $url = git -C $top remote get-url origin 2>$null
      if ($LASTEXITCODE -eq 0 -and $url -and ($url.Trim() -like "*becky-ootp26-assistant*")) {
        return $top
      }
    }
  } catch {}

  # 2) Search common dev folders (fast)
  $roots = @(
    "$env:USERPROFILE\OneDrive\Documents\GitHub",
    "$env:USERPROFILE\Documents\GitHub",
    "$env:USERPROFILE\source\repos"
  ) | Where-Object { Test-Path $_ }

  if (-not $roots) { return $null }

  $maxDepth = 4
  if ($DeepSearch) { $maxDepth = 8 }

  foreach ($root in $roots) {
    # Look for folders named like the repo first (fast)
    $candidates = @()
    $candidates += Get-ChildItem $root -Directory -Recurse -ErrorAction SilentlyContinue |
      Where-Object { $_.Name -match "becky-ootp26-assistant" } |
      Select-Object -First 25

    foreach ($c in $candidates) {
      if (Is-GitRepo $c.FullName) {
        $url = git -C $c.FullName remote get-url origin 2>$null
        if ($LASTEXITCODE -eq 0 -and $url -and ($url.Trim() -like "*becky-ootp26-assistant*")) {
          return $c.FullName
        }
      }
    }
  }

  return $null
}

# ---- Start ----
Say "Auto Push starting..."

# Check git exists
git --version *> $null
if ($LASTEXITCODE -ne 0) { Die "Git is not available in this PowerShell window. Install Git or reopen PowerShell." }
Ok "Git is available"

# Find repo folder
$repo = Find-RepoFolder $RepoUrl
if (-not $repo) {
  Die "I couldn't find the repo folder automatically. Run this script from inside the repo folder, or place it in tools/ and run it there."
}
Ok "Found repo folder: $repo"

Set-Location $repo

# Make sure origin points to correct repo
$origin = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0 -or -not $origin) {
  Warn "No origin remote found. Adding origin..."
  git remote add origin $RepoUrl
  Ok "Added origin = $RepoUrl"
} else {
  $origin = $origin.Trim()
  if ($origin -ne $RepoUrl -and -not ($origin -like "*becky-ootp26-assistant*")) {
    Warn "Origin exists but doesn't look like becky repo. Setting origin to $RepoUrl"
    git remote set-url origin $RepoUrl
  }
  Ok "origin = $((git remote get-url origin).Trim())"
}

# Checkout branch (create if needed)
$hasBranch = git show-ref --verify --quiet "refs/heads/$Branch"
if ($LASTEXITCODE -ne 0) {
  Warn "Branch '$Branch' does not exist locally. Creating it..."
  git checkout -b $Branch
} else {
  git checkout $Branch
}
Ok "On branch: $Branch"

# Show status
git status -sb

# Run precommit guard if present
if (Test-Path "tools\precommit_guard.py") {
  Say "Running repo safety guard..."
  python tools\precommit_guard.py
  if ($LASTEXITCODE -ne 0) { Die "precommit_guard failed. Fix that before pushing." }
  Ok "precommit_guard OK"
} else {
  Warn "tools\precommit_guard.py not found (skipping)"
}

# Compile check
Say "Running python compile check..."
python -m compileall .
if ($LASTEXITCODE -ne 0) { Die "compileall failed. Fix Python syntax errors first." }
Ok "compileall OK"

# Tests
Say "Running tests..."
pytest -q
if ($LASTEXITCODE -ne 0) { Die "pytest failed. Fix tests before pushing." }
Ok "pytest OK"

# Commit logic
$dirty = (git status --porcelain).Length -gt 0
if ($dirty) {
  Warn "You have uncommitted changes."
  if ($AutoCommit) {
    Say "AutoCommit is ON. Committing changes..."
    git add -A
    git commit -m $CommitMessage
    if ($LASTEXITCODE -ne 0) { Die "Commit failed. Resolve Git issues and try again." }
    Ok "Committed: $CommitMessage"
  } else {
    Die "Stopping to keep you safe. Re-run with -AutoCommit if you want this script to commit for you."
  }
} else {
  Ok "Working tree clean (nothing to commit)"
}

# Push
Say "Pushing branch '$Branch' to GitHub..."
git push -u origin $Branch
if ($LASTEXITCODE -ne 0) { Die "Push failed. Usually this is authentication. If you paste the error, I'll give you the exact fix." }
Ok "Push succeeded"

# Confirm remote has the branch
Say "Confirming branch exists on GitHub..."
git ls-remote --heads origin $Branch *> $null
if ($LASTEXITCODE -ne 0) { Warn "Couldn't confirm with ls-remote, but push succeeded." }
else { Ok "Confirmed: origin/$Branch exists" }

# Print PR link
# Convert repo URL to PR link base
$prBase = $RepoUrl
$prBase = $prBase -replace "\.git$", ""
$prLink = "$prBase/pull/new/$Branch"

Ok "All done!"
Write-Host ""
Write-Host "Next step: open this link to create a PR:" -ForegroundColor White
Write-Host $prLink -ForegroundColor Magenta
Write-Host ""
