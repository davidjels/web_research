# x-pr-manager.md

Generate comprehensive pull request descriptions by analyzing commits on the current branch compared to the base branch. Synthesizes your semantic commits into a cohesive PR story.

## Instructions

You are a PR description generator. Your task is to:

1. **Batched Git Information Gathering** (for optimal performance):
   ```bash
   # Collect all git information in a single batched operation
   git_info=$(cat <<'EOF'
   {
     echo "=== BRANCH_INFO ==="
     git rev-parse --abbrev-ref HEAD
     git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "no-upstream"
     git config --get init.defaultBranch 2>/dev/null || echo "main"

     echo "=== REMOTE_BRANCHES ==="
     git branch -r --format='%(refname:short)' | grep -v HEAD

     echo "=== MERGE_BASE_ANALYSIS ==="
     current_branch=$(git rev-parse --abbrev-ref HEAD)
     for branch in $(git branch -r --format='%(refname:short)' | grep -v "origin/$current_branch" | sed 's/origin\///'); do
       if git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
         merge_base=$(git merge-base HEAD "origin/$branch" 2>/dev/null)
         if [[ -n "$merge_base" ]]; then
           echo "$branch:$merge_base"
         fi
       fi
     done

     echo "=== PR_CHECK ==="
     gh pr list --head $(git rev-parse --abbrev-ref HEAD) --json number,title,url,state 2>/dev/null || echo "[]"
   }
   EOF
   )

   # Parse batched results
   eval "$git_info"
   ```

2. **Push current branch to remote** (ensure remote has latest changes):
```bash
# Push the current branch to ensure remote is up to date
git push 2>/dev/null || git push -u origin $(git rev-parse --abbrev-ref HEAD)
```

3. **Analyze changes and detect patterns** (batched for performance):
   ```bash
   # CRITICAL: Always fetch and use REMOTE branches for comparison
   git fetch origin

   # Once destination branch is determined, batch all change analysis
   # ALWAYS use origin/$destination_branch for accurate comparison
   change_analysis=$(cat <<EOF
   {
     echo "=== COMMIT_ANALYSIS ==="
     git log origin/$destination_branch..HEAD --pretty=format:"%H|%s|%b|%an|%ae"

     echo "=== FILE_CHANGES ==="
     git diff --stat origin/$destination_branch..HEAD
     git diff --name-only origin/$destination_branch..HEAD
     git diff --name-status origin/$destination_branch..HEAD

     echo "=== CHANGE_METRICS ==="
     total_files=\$(git diff --name-only origin/$destination_branch..HEAD | wc -l)
     additions=\$(git diff --numstat origin/$destination_branch..HEAD | awk '{add+=\$1} END {print add+0}')
     deletions=\$(git diff --numstat origin/$destination_branch..HEAD | awk '{del+=\$2} END {print del+0}')
     echo "files:\$total_files|additions:\$additions|deletions:\$deletions"

     echo "=== FILE_CATEGORIES ==="
     changed_files=\$(git diff --name-only origin/$destination_branch..HEAD)
     echo "test_files:\$(echo "\$changed_files" | grep -E "(test|spec)" | wc -l)"
     echo "ui_files:\$(echo "\$changed_files" | grep -E "\.(tsx?|vue|svelte|html|css|scss)" | wc -l)"
     echo "api_files:\$(echo "\$changed_files" | grep -E "(api|endpoint|view|controller)" | wc -l)"
     echo "doc_files:\$(echo "\$changed_files" | grep -E "\.(md|rst|txt)" | wc -l)"
     echo "config_files:\$(echo "\$changed_files" | grep -E "(config|setting|env)" | wc -l)"
     echo "security_files:\$(echo "\$changed_files" | grep -E "(auth|security|permission|middleware)" | wc -l)"
   }
   EOF
   )

   # Parse results and set variables
   eval "$change_analysis"
   ```

4. **Smart target branch detection** (using batched merge-base data with explicit defaults):
```bash
# Default to 'dev' as base for PRs; if missing, use 'main'; else use remote HEAD
destination_branch="dev"
if ! git ls-remote --exit-code --heads origin "$destination_branch" >/dev/null 2>&1; then
  if git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
    destination_branch="main"
  else
    destination_branch=$(git remote show origin | awk '/HEAD branch/ {print $NF}')
  fi
fi

# Optional: override by merge-base analysis only if it resolves to 'dev' or 'main'
# (Prevents accidental targeting of random branches.)
```

5. **Auto-draft detection and PR flags**:
```bash
# Determine if PR should be draft based on intelligent patterns
   draft_flag=""
   labels=()

   # Draft detection logic
   if [[ $branch_name =~ (wip/|draft/|experimental/|temp/) ]] ||
      [[ $commit_messages =~ (WIP|TODO|FIXME|DRAFT) ]] ||
      [[ $branch_name =~ (spike/|poc/|prototype/) ]] ||
      [[ $total_files -gt 50 ]] ||  # Large changesets often need review
      grep -q "TODO\|FIXME\|XXX" $(git diff --name-only $destination_branch..HEAD) 2>/dev/null; then
     draft_flag="--draft"
     echo "🚧 Auto-detected as draft PR due to:"
     [[ $branch_name =~ (wip/|draft/|experimental/) ]] && echo "  - Branch name indicates work in progress"
     [[ $commit_messages =~ (WIP|TODO|FIXME) ]] && echo "  - Commit messages contain WIP/TODO/FIXME"
     [[ $total_files -gt 50 ]] && echo "  - Large changeset ($total_files files)"
   fi

   # Smart labeling based on actual changes
   [[ $ui_files -gt 0 ]] && labels+=("ui")
   [[ $test_files -gt 0 ]] && labels+=("has-tests")
   [[ $test_files -eq 0 && $api_files -gt 0 ]] && labels+=("needs-tests")
   [[ $api_files -gt 0 ]] && labels+=("api")
   [[ $doc_files -gt 0 ]] && labels+=("documentation")
   [[ $config_files -gt 0 ]] && labels+=("configuration")
   [[ $security_files -gt 0 ]] && labels+=("security-review")
   [[ $deletions -gt $additions ]] && labels+=("cleanup")
   [[ $commit_messages =~ "BREAKING" ]] && labels+=("breaking-change")

   # Performance-related detection
   if git diff $destination_branch..HEAD | grep -q -E "(index|query|cache|performance|optimization)"; then
     labels+=("performance")
   fi

   # Dependencies detection
   if git diff --name-only $destination_branch..HEAD | grep -q -E "(requirements|package|Pipfile|pyproject)"; then
     labels+=("dependencies")
   fi
   ```

8. **Create or update PR from CURRENT branch** (no new branches are created here):
```bash
branch_name=$(git rev-parse --abbrev-ref HEAD)
git push 2>/dev/null || git push -u origin "$branch_name"

if command -v gh >/dev/null 2>&1; then
  existing=$(gh pr list --head "$branch_name" --json number -q '.[0].number' 2>/dev/null || true)
  if [ -n "$existing" ]; then
    gh pr edit "$existing" --base "$destination_branch" $draft_flag >/dev/null || true
  else
    gh pr create --base "$destination_branch" --head "$branch_name" $draft_flag --title "$pr_title" --body "$pr_body" --fill || true
  fi
else
  echo "⚠️ gh not installed; open a PR from $branch_name → $destination_branch using GitHub UI."
fi
```

6. **Smart template selection based on change type**:
   ```bash
   # Select appropriate PR template based on change patterns
   template_type="standard"

   if [[ $doc_files -gt 0 && $total_files -eq $doc_files ]]; then
     template_type="docs-only"
   elif [[ $config_files -gt 0 && $total_files -lt 5 ]]; then
     template_type="configuration"
   elif [[ $total_files -eq 1 && $changed_files =~ (requirements|package|Pipfile) ]]; then
     template_type="dependency-update"
   elif [[ $security_files -gt 0 ]]; then
     template_type="security"
   elif [[ $test_files -gt 0 && $test_files -eq $total_files ]]; then
     template_type="testing"
   elif [[ $commit_messages =~ "hotfix|urgent|critical" ]]; then
     template_type="hotfix"
   fi

   echo "📝 Using template: $template_type"
   ```

**Template Definitions**:

```bash
# docs-only template
generate_pr_body_docs-only() {
  cat <<EOF
## 📚 Documentation Update

Brief description of documentation changes.

### Changes Made
- Updated documentation files
- Improved clarity and accuracy

### Files Modified
$(git diff --name-only $destination_branch..HEAD | grep -E '\.(md|rst|txt)' | sed 's/^/- /')

**Type**: Documentation only - no code changes
EOF
}

# dependency-update template
generate_pr_body_dependency-update() {
  cat <<EOF
## 📦 Dependency Update

$(git log $destination_branch..HEAD --pretty=format:"- %s" | head -5)

### Dependencies Changed
$(git diff $destination_branch..HEAD --name-only | grep -E '(requirements|package|Pipfile|pyproject)' | sed 's/^/- /')

**Type**: Dependency update - minimal risk
**Testing**: Automated dependency checks passing
EOF
}

# security template
generate_pr_body_security() {
  cat <<EOF
## 🔒 Security Enhancement

**⚠️ Security-related changes - requires careful review**

### Security Changes
$(git log $destination_branch..HEAD --pretty=format:"- %s")

### Files Modified
$(git diff --name-only $destination_branch..HEAD | sed 's/^/- /')

### Security Checklist
- [ ] No hardcoded secrets or credentials
- [ ] Authentication/authorization properly implemented
- [ ] Input validation added/maintained
- [ ] Security tests updated

**Reviewer Note**: Please pay special attention to authentication and authorization logic.
EOF
}

# hotfix template
generate_pr_body_hotfix() {
  cat <<EOF
## 🚨 Hotfix

**Urgent fix - expedited review requested**

### Issue Fixed
$(git log $destination_branch..HEAD --pretty=format:"- %s" | head -3)

### Root Cause
[Brief explanation of what caused the issue]

### Fix Applied
[Specific changes made to resolve the issue]

### Risk Assessment
- **Scope**: $(echo $changed_files | wc -w) files changed
- **Testing**: [How this was tested]
- **Rollback**: [How to rollback if needed]

**Type**: Critical hotfix
EOF
}
```

7. **Analyze commit patterns**: Group commits by their semantic type:
    - `feat:` → Features section
    - `fix:` → Bug Fixes section
    - `refactor:` → Code Improvements section
    - `docs:` → Documentation section
    - `test:` → Testing section
    - `chore:` → Maintenance section
    - `perf:` → Performance section

4. **Determine what changes to analyze** (CRITICAL - avoid describing already-merged content):
   ```bash
   # ALWAYS compare against the REMOTE target branch to see what would actually be merged
   # This ensures we only describe changes that are NEW to the target branch

   # Fetch latest remote state
   git fetch origin

   # Check if PR already exists for this branch comparison
   existing_pr=$(gh pr list --head <source_branch> --base <target_branch> --json number,title,url,state)

   if [[ ! -z "$existing_pr" && "$existing_pr" != "[]" ]]; then
     # PR exists - still compare against remote target to see what's actually different
     echo "📝 Updating existing PR - analyzing changes vs origin/<target_branch>..."
     commit_range="origin/<target_branch>..HEAD"
   else
     # No existing PR - analyze all commits vs remote target branch
     echo "📝 Creating new PR - analyzing changes vs origin/<target_branch>..."
     commit_range="origin/<target_branch>..HEAD"
   fi

   # CRITICAL: Always use the remote target branch for comparison
   # This shows ONLY what would be merged, not the entire branch history

   # Use the determined range for all analysis
   git log $commit_range --pretty=format:"%H|%s|%b|%an|%ae"
   git diff --stat $commit_range
   git diff --shortstat $commit_range
   git diff --name-only $commit_range
   ```

5. **Extract key information**:
    - Total files changed: Use commit_range from step 3
    - Lines added/removed: Use commit_range from step 3
    - File types changed (frontend/backend/config/tests)
    - Potential breaking changes (look for: API changes, model changes, removed functions)

6. **Generate PR description** using this template:
   ```markdown
   # <PR Title based on main feature>

   ## 📋 Overview
   <2-3 sentence summary of what this PR accomplishes>

   ## 🔄 Changes Made

   ### ✨ Features
   <List from feat: commits with bullet points>

   ### 🐛 Bug Fixes
   <List from fix: commits>

   ### ♻️ Code Improvements
   <List from refactor: commits>

   ### 📚 Documentation
   <List from docs: commits>

   ### ✅ Tests
   <List from test: commits>

   ## 📊 Impact Summary
   - **Files changed**: X files (+Y lines, -Z lines)
   - **Test coverage**: <Check if test files were added/modified>
   - **Database changes**: <Yes/No - check for migration files>
   - **API changes**: <List any API endpoint changes>
   - **Dependencies**: <List any package.json/requirements.txt changes>

   ## 🧪 Testing Instructions
   1. <Step-by-step testing based on the changes>
   2. <Include any specific test scenarios>
   3. <Mention any manual testing needed>

   ## ⚠️ Breaking Changes
   <List any breaking changes or "None" if there aren't any>

   ## 🚀 Deployment Notes
   <Any special deployment steps, env vars, migrations>

   ## 📸 Screenshots/Demos
   <Reminder to add screenshots if UI changes detected>

   ## 🔗 Related Issues
   <Scan commit messages for #XXX references>
   Closes #<issue_number>

   ## ✔️ Checklist
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] No sensitive data exposed
   - [ ] Follows project coding standards
   - [ ] Tested on: <relevant platforms/browsers>

   ---
   ```

7. **Check for existing PR and handle automatically**:
   ```bash
   # Check if PR already exists for this branch comparison
   gh pr list --head <source_branch> --base <target_branch> --json number,title,url,state
   ```

   **If PR exists**:
   ```
   Found existing PR #123: "Previous PR Title"
   URL: https://github.com/user/repo/pull/123
   State: open

   What would you like to do?
   1. Stop (don't modify anything)
   2. Update PR description (replace body with new content)
   3. Append to PR description (add new changes to existing body)
   4. Create new PR anyway (force new PR)

   Choose option (1-4):
   ```

   **Handle user choice**:
   - **Option 1**: Stop execution, show existing PR URL
   - **Option 2**: Use `gh pr edit <PR_number> --body "<new_description>"`
   - **Option 3**: Get existing body with `gh pr view <PR_number> --json body`, append new content
   - **Option 4**: Continue with normal PR creation (will create duplicate)

8. **Intelligent PR creation** (with auto-detected flags and labels):
   ```bash
   # First, ensure branch is pushed to remote
   git push origin <source_branch>

   # Generate PR title automatically from branch name and commits
   pr_title=$(generate_pr_title)

   # Build labels string for gh command
   label_flags=""
   for label in "${labels[@]}"; do
     label_flags="$label_flags --label $label"
   done

   # Create PR with intelligent detection
   echo "🚀 Creating PR with auto-detected settings:"
   echo "  Draft: ${draft_flag:+YES}"
   echo "  Labels: ${labels[*]}"
   echo "  Template: $template_type"

   gh pr create \
     --title "$pr_title" \
     --body "$(generate_pr_body_$template_type)" \
     --base "$destination_branch" \
     --head "$source_branch" \
     $draft_flag \
     $label_flags
   ```

   **PR Title Generation Logic**:
   ```
   1. Extract from branch name:
      - feature/add-notifications → "Add Notifications"
      - bugfix/fix-auth-bug → "Fix Auth Bug"
      - hotfix/security-patch → "Security Patch"
      - chore/update-deps → "Update Dependencies"

   2. From most significant commit:
      - If multiple feat: commits → "Multiple Feature Updates"
      - If single major feat: → Use that commit subject
      - If mostly fix: commits → "Bug Fixes"
      - If mixed → "Development Updates"

   3. Fallback patterns:
      - "<Branch_Name> Updates"
      - "Development Branch Updates"
   ```

9. **Post-creation actions**:
   ```bash
   # After successful PR creation
   echo "✅ PR created successfully!"
   echo "URL: <PR_URL>"
   echo "Title: <PR_Title>"

   # Optional: Add labels based on content
   if [[ $has_breaking_changes == "true" ]]; then
     gh pr edit <PR_number> --add-label "breaking-change"
   fi

   if [[ $files_changed -gt 50 ]]; then
     gh pr edit <PR_number> --add-label "large"
   elif [[ $files_changed -gt 10 ]]; then
     gh pr edit <PR_number> --add-label "medium"
   else
     gh pr edit <PR_number> --add-label "small"
   fi
   ```

10. **Error handling and safety checks**:
   ```bash
   # Before creating PR, verify:
   1. GitHub CLI is installed and authenticated: `gh auth status`
   2. Remote origin exists: `git remote get-url origin`
   3. Branch has commits ahead of target: `git rev-list --count <target>..HEAD`
   4. No uncommitted changes: `git status --porcelain`

   # Handle common errors:
   - If `gh` not installed: Show installation instructions
   - If not authenticated: Run `gh auth login`
   - If no commits: "No changes to create PR for"
   - If uncommitted changes: Ask to commit or stash first
   ```

11. **Special handling for $ARGUMENTS**:
    - `--target=<branch>` or `--base=<branch>`: Explicitly set destination branch
    - `--source=<branch>`: Explicitly set source branch (default: current branch)
    - `--format=<github|gitlab|bitbucket>`: Adjust markdown for platform
    - `--brief`: Generate a condensed version
    - `--copy`: Copy to clipboard after generation (using `pbcopy` on Mac, `xclip` on Linux)
    - `--no-create`: Generate description only, don't create PR
    - `--force-create`: Create new PR even if one exists
    - `--update-existing`: Automatically update existing PR without prompting
    - `--title="<custom_title>"`: Override automatic title generation
    - `--draft`: Create PR as draft

12. **Smart detection features**:
    - If Django migration files present → Add migration commands to deployment notes
    - If package files changed → List added/removed dependencies
    - If API files changed → Suggest API documentation update
    - If only documentation changed → Use simplified template
    - If security-related files → Add "Security Review Needed" tag

13. **Enhance with context**:
    - Pull request title from branch name (feature/add-notifications → "Add Notifications")
    - If commit messages reference issues, validate they exist with `gh issue view` if available
    - Detect PR size and add appropriate labels (small/medium/large)

## Branch Detection Logic

The tool uses smart detection to identify branches:

1. **Source branch** (where your changes are):
    - Always the current branch you're on

2. **Destination branch** (where you're merging to):
    - First checks if you have an upstream tracking branch set
    - Then checks your Git config for default branch
    - Then looks for common branch names (main, master, develop)
    - Uses branch naming patterns:
        - `feature/*` → develop (if exists) → main
        - `hotfix/*` → main/master (production)
        - `bugfix/*` → develop → main
        - `release/*` → main/master
    - Falls back to asking you

3. **Override options**:
   ```bash
   # Explicitly set target branch
   claude-code /pr-description --target=develop

   # For non-standard workflows
   claude-code /pr-description --source=feature/auth --target=staging
   ```

## Example detection scenarios:

### For feature branch:
```
# Add User Notification System

## 📋 Overview
Implements a complete notification system with email and push support, allowing users to manage their notification preferences and receive timely updates.

## 🔄 Changes Made
### ✨ Features
- Add user notification preferences API with CRUD operations
- Implement email template system with variable substitution
- Add push notification support via FCM
...
```

### For hotfix:
```
# Fix Critical Authentication Bug

## 📋 Overview
Resolves authentication token expiration issue causing users to be logged out unexpectedly.

## 🔄 Changes Made
### 🐛 Bug Fixes
- Fix token refresh logic in auth middleware
- Handle edge case for expired refresh tokens
...
```

## Critical Analysis Guidelines

**ALWAYS analyze the actual file changes, not just commit messages or branch history:**

### The Most Common Mistake: Analyzing Branch History Instead of PR Changes

**THE PROBLEM**: When you run `git log origin/main..dev`, you see ALL commits that exist on `dev` but not on `main`. This includes:
- Commits that were already merged to main in previous PRs
- Commits from other branches that were merged into dev
- Old work that has nothing to do with the current changes

**THE SOLUTION**: ALWAYS compare against the REMOTE target branch to see what would ACTUALLY be merged:

```bash
# ❌ WRONG - Shows entire branch history
git log main..dev --oneline  # Shows 88 commits about Django apps
git diff main..dev  # Shows changes that might already be in main

# ✅ CORRECT - Shows only what would be merged
git fetch origin  # Get latest remote state
git diff origin/main..HEAD  # Shows ONLY changes not yet in origin/main
git log origin/main..HEAD  # Shows ONLY commits not yet in origin/main
```

### Real Example:
```bash
# Scenario: dev branch has 58 commits ahead of local main
# But origin/main was updated and already has 57 of those commits

# ❌ WRONG approach:
git log main..dev --oneline | wc -l  # Shows 58 commits
# PR description: "Massive Django app refactor with 58 commits"

# ✅ CORRECT approach:
git fetch origin
git diff --name-only origin/main..HEAD  # Shows: README.md
# PR description: "Update README documentation"
```

### Key Rules:
1. **ALWAYS fetch before analyzing**: `git fetch origin`
2. **ALWAYS compare against origin/<target>**: Use `origin/main` not `main`
3. **VERIFY with file diff**: Check `git diff --name-only origin/<target>..HEAD`
4. **Match description to files**: If only README.md changed, don't describe authentication systems

**Key principle**: The PR description must match what reviewers will actually see in the GitHub file diffs tab.

Always analyze the actual changes, not just commit messages, to ensure accuracy. Be specific about what changed and why it matters.

## Automated Workflow Examples

### Example 1: New PR Creation
```
🔍 Analyzing branch 'feature/user-profiles'...
📊 Found 15 commits, 23 files changed (+847 -45 lines)
🎯 Target branch: main

No existing PR found.
📝 Generated title: "Add User Profile Management System"
🚀 Creating PR...

✅ PR created successfully!
🔗 URL: https://github.com/user/repo/pull/156
📋 Title: "Add User Profile Management System"
🏷️ Labels: medium, breaking-change
```

### Example 2: Existing PR Handling
```
🔍 Analyzing branch 'dev'...
📊 Found 8 new commits since last push

⚠️ Found existing PR #145: "Development Branch Updates"
🔗 URL: https://github.com/user/repo/pull/145
📊 State: open

What would you like to do?
1. Stop (don't modify anything)
2. Update PR description (replace body with new content)
3. Append to PR description (add new changes to existing body)
4. Create new PR anyway (force new PR)

Choose option (1-4): 3

📝 Appending new changes to existing PR...
✅ PR #145 updated successfully!
```

### Example 3: Error Handling
```
❌ Error: GitHub CLI not authenticated
💡 Fix: Run 'gh auth login' to authenticate

❌ Error: Branch has no commits ahead of main
💡 Nothing to create PR for

❌ Error: Uncommitted changes detected
💡 Commit or stash changes first: git add . && git commit -m "message"
```

## Important: Human Authorship
- **NEVER** add "Generated with Claude Code" or any AI attribution to PR descriptions
- **NEVER** include "Co-Authored-By: Claude" or similar AI attribution
- All PR descriptions must appear to be written entirely by the human developer
- Keep language natural and professional as if written by the developer
- Remove any AI-generated footers or signatures from the final output
