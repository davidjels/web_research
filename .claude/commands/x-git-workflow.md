# x-git-workflow.md

Complete git workflow: review → organize commits → create/update PR. Runs all three commands with intelligent stopping points only for critical decisions.

## Instructions

You are a complete git workflow orchestrator. Your task is to run the full development workflow with minimal friction:

**IMPORTANT**: This command assumes `--dangerously-skip-permissions` mode for smooth operation. If not running in this mode, exit with:
```
⚠️  This workflow requires --dangerously-skip-permissions to avoid multiple approval prompts.

Exit and run:
claude --dangerously-skip-permissions
Then: /x-git-workflow

This prevents 10+ individual permission requests during the workflow.
```

## Workflow Steps

### 0. **Branch Safety Check** (CRITICAL)
```bash
echo "🛡️  Step 0/3: Checking branch safety..."

current_branch=$(git branch --show-current)
if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ] || [ "$current_branch" = "staging" ] || [ "$current_branch" = "stg" ]; then
    echo ""
    echo "🚨 CRITICAL ERROR: Cannot run workflow on protected branch '$current_branch'"
    echo ""
    echo "Protected branches: main, master, staging, stg"
    echo "These branches should only receive changes via Pull Requests."
    echo ""
    echo "Create a feature branch instead:"
    echo "  git checkout -b feature/your-feature-name"
    echo "  git checkout -b fix/bug-description"  
    echo "  git checkout -b refactor/component-name"
    echo ""
    echo "❌ Workflow aborted for safety."
    exit 1
fi

echo "✅ Safe to proceed on branch: $current_branch"
```

### 1. **Code Review Phase** (x-git-review logic)
```bash
echo "🔍 Step 1/3: Reviewing staged changes for issues..."

# Run code review on staged files
git diff --staged --name-only | head -1 > /dev/null
if [ $? -eq 0 ]; then
  # Review staged changes
  review_scope="staged"
else
  # Review last commit if nothing staged
  review_scope="last_commit"
fi
```

**Auto-fix minor issues without stopping:**
- Formatting issues: `ruff format . && git add -u`
- Import sorting: `isort . && git add -u`
- Auto-fixable linting: `ruff check . --fix && git add -u`
- Unused imports removal

**Stop only for critical issues:**
```markdown
🛑 Critical Issues Found (workflow paused):

🚨 SECURITY RISKS:
- Line 42: Hardcoded API key detected
- Line 156: SQL injection vulnerability

⚠️ DATA LOSS RISKS:
- Line 89: Database drop command in migration

Options:
1. Fix manually and continue workflow
2. View full review report (/x-git-review)
3. Continue anyway (--force mode)
4. Exit workflow

Choose (1-4):
```

### 2. **Commit Organization Phase** (x-commit-organizer logic)
```bash
echo "📦 Step 2/3: Organizing commits..."

# Only run if we have staged files
if git diff --staged --quiet; then
  echo "ℹ️  No staged changes to commit"
else
  # Run commit organizer logic
  # - Clean staging area
  # - Group files logically into SMALL, FOCUSED commits
  # - Create multiple atomic commits, not one massive commit
  # - Generate semantic commits for each logical group
  # - Handle pre-commit hooks with auto-fixes
  # - Push changes incrementally
fi
```

**CRITICAL: Piecemeal Commits Philosophy**

The workflow MUST create multiple small, atomic commits rather than one massive commit. Each commit should represent a single logical change that:

- **Can be reviewed independently** (max 5-10 files per commit)
- **Can be reverted safely** without affecting unrelated functionality  
- **Has a clear, specific purpose** described in the commit message
- **Builds and tests successfully** on its own

**Bad Example (Avoid):**
```
❌ feat: Add FCM notifications, deep linking, media system, auth updates, and config changes
   52 files changed, 1,847 insertions(+), 156 deletions(-)
```

**Good Example (Follow):**
```
✅ Commit 1: feat: Add FCM service and user token storage
   3 files changed, 156 insertions(+), 2 deletions(-)

✅ Commit 2: feat: Add FCM token registration API endpoint  
   2 files changed, 67 insertions(+), 1 deletion(-)

✅ Commit 3: feat: Implement FCM push notification channel
   2 files changed, 89 insertions(+), 23 deletions(-)

✅ Commit 4: feat: Add deep linking URL generation system
   4 files changed, 234 insertions(+), 5 deletions(-)

✅ Commit 5: chore: Update dependencies for Firebase integration
   2 files changed, 12 insertions(+), 3 deletions(-)
```

**Commit Grouping Strategy:**

1. **Database/Model Changes First**: Migrations, model updates
2. **Core Services**: New service classes, business logic  
3. **API Endpoints**: Individual API endpoints and schemas
4. **Integration**: Connecting systems together
5. **Configuration**: Environment, dependencies, settings
6. **Documentation**: README updates, usage examples

**Auto-handle common pre-commit issues:**
- Formatting failures → auto-fix and retry
- Linting failures → auto-fix and retry
- Import sorting → auto-fix and retry

**Only stop for persistent failures:**
```markdown
❌ Pre-commit hooks failed after auto-fixes:

Type errors in authentication/models.py:
- Line 45: Missing return type annotation
- Line 62: Incompatible type assignment

Options:
1. Fix manually and continue
2. Skip pre-commit hooks (--no-verify)
3. Exit workflow

Choose (1-3):
```

### 3. **PR Management Phase** (x-pr-manager logic)
```bash
echo "🚀 Step 3/3: Managing pull request..."

# Branch Safety Check Before Push (Double-check)
current_branch=$(git branch --show-current)
if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ] || [ "$current_branch" = "staging" ] || [ "$current_branch" = "stg" ]; then
    echo "🚨 CRITICAL ERROR: Cannot push to protected branch '$current_branch'"
    echo "This should never happen - workflow should have been blocked in Step 0!"
    exit 1
fi

# Always work with the CURRENT branch (no new branches are created here)
current_branch=$(git branch --show-current)

# Push if not already done in step 2 (set upstream if missing)
git push 2>/dev/null || git push -u origin "$current_branch"

# Default PR base is 'dev'. Fallback to 'main' if 'dev' doesn't exist, else remote HEAD.
destination_branch="dev"
if ! git ls-remote --exit-code --heads origin "$destination_branch" >/dev/null 2>&1; then
  if git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
    destination_branch="main"
  else
    destination_branch=$(git remote show origin | awk '/HEAD branch/ {print $NF}')
  fi
fi

echo "📌 Creating or updating PR: $current_branch -> $destination_branch"

# Create or update PR for the CURRENT branch only
if command -v gh >/dev/null 2>&1; then
  # Try to find existing PR for this head
  existing=$(gh pr list --head "$current_branch" --json number,url,state -q '.[0].number' 2>/dev/null || true)
  if [ -n "$existing" ]; then
    echo "🔄 Updating existing PR #$existing"
    gh pr edit "$existing" --base "$destination_branch" >/dev/null || true
  else
    echo "🆕 Creating PR via gh"
    gh pr create --base "$destination_branch" --head "$current_branch" --title "$(git log -1 --pretty=%s)" --body "Automated PR for $current_branch" --fill || true
  fi
else
  echo "⚠️ gh not installed; the PR manager will attempt API or prompt you to open a PR in the UI."
fi
```

**Auto-handle routine decisions:**
- Branch detection (use smart defaults)
- PR title generation (from branch/commits)
- Push to remote (always push)
- ALWAYS create/update PR from the CURRENT branch (no branch creation here)
- Default base branch is `dev` (fallback to `main` → remote HEAD)

**Stop only for ambiguous scenarios:**
```markdown
📋 Existing PR Found:

PR #145: "Development Branch Updates"
URL: https://github.com/user/repo/pull/145
State: OPEN

What should I do?
1. Update PR description (recommended)
2. Append new changes to existing description
3. Create new PR anyway
4. Skip PR step

Choose (1-4):
```

## Special Arguments

**Flow Control:**
- `--review-only`: Stop after review step
- `--skip-review`: Skip review, go to commits
- `--no-pr`: Stop after commits, don't create/update PR
- `--force`: Continue through all stops (dangerous!)

**Auto-fixes:**
- `--auto-fix`: Auto-fix all minor issues (default: true)
- `--no-auto-fix`: Ask before fixing anything

**Review Sensitivity:**
- `--strict`: Stop for performance issues too
- `--security-only`: Only stop for security issues
- `--permissive`: Only stop for critical security/data loss

## Workflow Examples

### Happy Path (no issues):
```
🔍 Step 1/3: Reviewing staged changes for issues...
✅ Auto-fixed 3 formatting issues
✅ No critical issues found

📦 Step 2/3: Organizing commits...
✅ Organized into 2 semantic commits:
  - feat: Add user notification preferences API
  - test: Add comprehensive notification tests
✅ All commits successful, pushed to remote

🚀 Step 3/3: Managing pull request...
✅ Created PR #156: "Add User Notification System"
🔗 https://github.com/user/repo/pull/156

🎉 Workflow complete! Ready for review.
```

### Critical Issues Found:
```
🔍 Step 1/3: Reviewing staged changes for issues...
✅ Auto-fixed 2 import sorting issues

🛑 Critical security issue found:
- config.py:23 - Hardcoded database password

Choose: (1) Fix manually (2) View report (3) Force continue (4) Exit
User choice: 1

⏸️  Workflow paused. Fix the issues and re-run /x-git-workflow
```

### Force Mode:
```bash
/x-git-workflow --force

🔍 Step 1/3: Reviewing staged changes for issues...
⚠️  Found 2 critical issues (FORCE MODE: continuing anyway)
📦 Step 2/3: Organizing commits...
⚠️  Pre-commit failed (FORCE MODE: using --no-verify)
🚀 Step 3/3: Managing pull request...
✅ Created PR with warnings noted in description
```

## Error Handling

**Graceful degradation:**
- If `x-git-review` logic fails → continue with warning
- If `x-commit-organizer` fails → manual commit fallback
- If `x-pr-manager` fails → show manual PR creation steps

**Clear recovery instructions:**
```markdown
❌ Workflow failed at step 2 (commit organization)

What happened: Pre-commit hooks are blocking commits

Recovery options:
1. Run individual commands:
   - Fix issues manually
   - /x-commit-organizer --no-verify
   - /x-pr-manager

2. Restart workflow:
   - /x-git-workflow --skip-review

3. Get help:
   - /x-git-review --security-only (diagnose issues)
```

## Smart Defaults

**Permission Model:**
- Requires `--dangerously-skip-permissions` (explained upfront)
- No individual approvals for routine git operations
- Only stops for critical decision points

**Auto-fix Philosophy:**
- Fix formatting/linting issues silently
- Show what was auto-fixed in summary
- Only ask permission for ambiguous changes

**Stopping Criteria:**
- 🔴 **Always stop**: Security vulnerabilities, data loss risks
- 🟡 **Sometimes stop**: Persistent pre-commit failures, ambiguous PR scenarios
- 🟢 **Never stop**: Formatting, imports, routine linting, branch detection

This creates a smooth developer experience that "just works" for 95% of cases while intelligently stopping only when human judgment is truly needed.

## Important: Human Authorship
- **NEVER** add "Generated with Claude Code" or AI attribution to commits/PRs
- **NEVER** add "Co-Authored-By: Claude" or similar AI co-authorship
- All commits and PRs must appear authored entirely by the human developer
- Keep all messages natural and professional
