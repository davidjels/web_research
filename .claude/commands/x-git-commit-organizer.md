# x-commit-organizer.md

Analyze staged git files and intelligently organize them into logical commit groups with appropriate commit messages. Then execute the commits.

## Instructions

**IMPORTANT**: First, check if we're running with appropriate permissions for multiple git operations.

You are a git commit organizer. Your task is to:

0. **Branch Safety Check** (CRITICAL - Always First):
   ```bash
   current_branch=$(git branch --show-current)
   if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ] || [ "$current_branch" = "staging" ] || [ "$current_branch" = "stg" ]; then
       echo ""
       echo "🚨 CRITICAL ERROR: Cannot commit to protected branch '$current_branch'"
       echo ""
       echo "Protected branches: main, master, staging, stg"
       echo "These branches should only receive changes via Pull Requests."
       echo ""
       echo "Create a feature branch instead:"
       echo "  git checkout -b feature/your-feature-name"
       echo "  git checkout -b fix/bug-description"  
       echo "  git checkout -b refactor/component-name"
       echo ""
       echo "❌ Commit organizer aborted for safety."
       exit 1
   fi
   
   echo "✅ Safe to proceed on branch: $current_branch"
   ```

1. **Check execution mode**:
   - Check if running under `--dangerously-skip-permissions` mode
   - If NOT, warn the user:
     ```
     ⚠️  Warning: This command will execute multiple git commits.

     Without --dangerously-skip-permissions, you'll need to approve each commit individually.

     Recommended: Exit and run:
     claude --dangerously-skip-permissions
     Then: /x-commit-organizer

     Continue with individual approvals? (yes/no)
     ```
   - If they say "no" or anything other than "yes", stop execution
   - If they say "yes", proceed but remind them before each commit that they'll need to approve

2. **Check staged files**: Use `git status` and `git diff --staged` to see what's currently staged for commit.

3. **Clean staging area**: Remove any files that shouldn't be committed:
    - `celerybeat-schedule*` files (Celery beat scheduler files)
    - `*.pyc`, `__pycache__` directories
    - IDE-specific files (`.vscode`, `.idea`)
    - OS-specific files (`.DS_Store`, `Thumbs.db`)
    - Log files, temporary files

4. **Organize into logical groups**: Group the remaining staged files by:
    - **Database migrations**: Django migration files should be grouped by app and purpose
    - **Feature additions**: New functionality (new files, major new features)
    - **Bug fixes**: Fixes to existing functionality
    - **Refactoring**: Code improvements without functional changes
    - **Documentation**: README, comments, documentation files
    - **Configuration**: Settings, environment, build configuration
    - **Tests**: Test files and test-related changes
    - **Dependencies**: Package.json, requirements.txt, etc.

5. **Generate commit messages**: For each group, create semantic commit messages following this format:
   ```
   <type>: <description>

   <optional body explaining the changes>
   ```

   Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `style`

6. **Execute commits**: Run the git commit commands for each group using heredoc format for multi-line commit messages.

   **Handle pre-commit failures**:
   - If a commit fails due to pre-commit hooks, analyze the output
   - Common issues:
     - **Formatting issues**: Run the formatter (`ruff format .` or `black .`)
     - **Linting errors**: Fix the specific issues or run `ruff check . --fix`
     - **Type errors**: Fix type hints or add `# type: ignore` if appropriate
     - **Import sorting**: Run `isort .`
   - After fixing, re-stage the files and retry the commit
   - If pre-commit issues persist after fixes:
     - Option 1: Fix the underlying issues (preferred)
     - Option 2: Suggest `git commit --no-verify` (only if issues are non-critical)
     - Option 3: Temporarily disable specific hooks in `.pre-commit-config.yaml`

7. **Branch Safety Check Before Push**: Verify we're not pushing to protected branches:
   ```bash
   current_branch=$(git branch --show-current)
   if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ] || [ "$current_branch" = "staging" ] || [ "$current_branch" = "stg" ]; then
       echo "🚨 CRITICAL ERROR: Cannot push to protected branch '$current_branch'"
       echo "This should never happen - workflow should have been blocked earlier!"
       exit 1
   fi
   ```

8. **Push changes**: After all commits are successful, push the changes to the remote repository:
   ```bash
   git push
   ```
   If the branch doesn't have an upstream set, use:
   ```bash
   git push -u origin <branch-name>
   ```

9. **Summary**: Provide a final summary of what was committed and pushed.

## Special handling for $ARGUMENTS:
- If `--dry-run` is provided, show what would be committed but don't execute
- If `--interactive` is provided, ask for confirmation before each commit
- If a specific commit type is provided (e.g., `feat`, `fix`), prioritize that type of grouping

## Example commit message formats:
- `feat: Add user notification system with email and push support`
- `fix: Resolve authentication token expiration handling`
- `refactor: Simplify database query logic in user service`
- `docs: Update API documentation for auth endpoints`
- `chore: Update dependencies and clean up unused imports`

Be thorough in analyzing the changes and create meaningful, descriptive commit messages that explain both what was changed and why it matters.

## Pre-commit Hook Handling

When commits fail due to pre-commit hooks:

1. **Auto-fix when possible**:
   ```bash
   # For formatting issues
   ruff format . && git add -u

   # For import sorting
   isort . && git add -u

   # For linting (auto-fixable)
   ruff check . --fix && git add -u
   ```

2. **Manual fixes needed**:
   - Show the specific errors
   - Fix the issues in the code
   - Re-stage and retry

3. **Skip hooks (last resort)**:
   - Only suggest `--no-verify` for non-critical issues
   - Example: "Documentation formatting in a hotfix"
   - Always explain why skipping is okay in this case

## Important: Human Authorship
- **NEVER** add "Generated with Claude Code" or any AI attribution to commit messages
- **NEVER** add "Co-Authored-By: Claude" or similar AI co-authorship
- All commits must appear to be authored entirely by the human developer
- Keep commit messages natural and professional as if written by the developer
