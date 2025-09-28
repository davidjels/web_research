# x-git-review.md
# Git Changes Review

Perform automated code review on staged changes or recent commits, checking for security issues, performance problems, and code quality concerns.

**Scope**: Git-related changes only (staged files, commits, branches)
**For full codebase analysis**: Use `/x-codebase-audit` instead

## Instructions

You are a code review assistant. Your task is to:

1. **Determine scope of review**:
    - Default: Review staged changes with `git diff --staged`
    - If no staged changes: Review last commit with `git diff HEAD~1 HEAD`
    - If `--commits=N` specified: Review last N commits
    - If `--branch` specified: Review all changes vs base branch

2. **Security Analysis**:
    - **Secrets/Credentials**: Search for patterns:
        - API keys: `['\"]?api[_-]?key['\"]?\s*[:=]\s*['\"][^'\"]+['\"]`
        - AWS keys: `AKIA[0-9A-Z]{16}`
        - Private keys: `-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----`
        - Passwords: `password\s*=\s*['"][^'"]+['"]`
        - Database URLs with credentials
    - **SQL Injection**: Look for:
        - String concatenation in SQL queries
        - Missing parameterized queries
        - Raw SQL with user input
    - **XSS Vulnerabilities**: Check for:
        - Unescaped output in templates
        - `innerHTML` usage
        - Missing input sanitization
    - **Authentication/Authorization**: Flag:
        - Missing permission checks
        - Commented out auth middleware
        - Hardcoded user roles

3. **Performance Analysis**:
    - **Database Issues**:
        - N+1 queries (loops with DB calls)
        - Missing `select_related()`/`prefetch_related()` in Django
        - Large data loads without pagination
        - Missing database indexes on foreign keys
    - **Memory Issues**:
        - Loading entire files into memory
        - Unbounded caches
        - Memory leaks in closures
    - **Algorithm Complexity**:
        - Nested loops with large datasets
        - Inefficient sorting/searching
        - Unnecessary repeated calculations

4. **Code Quality Checks**:
    - **Error Handling**:
        - Missing try-catch blocks
        - Broad except clauses (`except:` or `except Exception:`)
        - Swallowed exceptions without logging
    - **Code Duplication**:
        - Repeated code blocks (DRY violations)
        - Similar functions that could be consolidated
    - **Complexity**:
        - Functions > 50 lines
        - Cyclomatic complexity > 10
        - Deeply nested code (> 4 levels)
    - **Best Practices**:
        - Magic numbers without constants
        - Missing type hints (Python)
        - Unused imports/variables
        - TODO/FIXME comments

5. **Framework-Specific Checks**:

   **Django**:
    - Missing migrations for model changes
    - Signals without error handling
    - Missing `db_index` on filtered fields
    - Template security issues
    - Missing CSRF protection

   **React/Next.js**:
    - Missing key props in lists
    - Direct state mutations
    - useEffect missing dependencies
    - Memory leaks in subscriptions

   **Node.js**:
    - Callback hell (suggest async/await)
    - Missing error handling in promises
    - Synchronous file operations

6. **Generate Review Report**:
   ```markdown
   # Code Review Report

   **Scope**: <files reviewed>
   **Risk Level**: 🟢 Low | 🟡 Medium | 🔴 High

   ## 🚨 Critical Issues (Must Fix)

   ### Security Vulnerabilities
   <List critical security issues with file:line and suggested fixes>

   ### Data Loss Risks
   <Any code that could cause data loss>

   ## ⚠️ Important Issues (Should Fix)

   ### Performance Problems
   <List with impact and solutions>

   ### Error Handling
   <Missing or poor error handling>

   ## 💡 Suggestions (Consider Fixing)

   ### Code Quality
   <Refactoring suggestions, better patterns>

   ### Best Practices
   <Framework-specific improvements>

   ## ✅ Good Practices Noticed
   <Positive feedback on well-written code>

   ## 📊 Metrics
   - Files changed: X
   - Lines added/removed: +Y -Z
   - Test coverage impact: <estimate>
   - Complexity score: <before> → <after>

   ## 🔧 Automated Fixes Available
   <List any issues that can be auto-fixed>
   ```

7. **Provide actionable fixes**: For each issue, provide:
    - Why it's a problem
    - How to fix it (with code example)
    - Link to relevant documentation

8. **Special handling for $ARGUMENTS**:
    - `--security-only`: Focus only on security issues
    - `--performance-only`: Focus only on performance issues
    - `--auto-fix`: Generate a script to fix simple issues
    - `--severity=<critical|high|medium|low>`: Only show issues above threshold
    - `--commits=N`: Review last N commits
    - `--branch`: Review entire branch vs base

## Example Issues and Fixes:

### Security Issue:
```python
# ❌ Problem: SQL Injection vulnerability
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# ✅ Fix: Use parameterized queries
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, [user_input])
```

### Performance Issue:
```python
# ❌ Problem: N+1 query in Django
for order in Order.objects.all():
    print(order.customer.name)  # New query for each order!

# ✅ Fix: Use select_related
for order in Order.objects.select_related('customer'):
    print(order.customer.name)  # Single query with JOIN
```

### Code Quality:
```javascript
// ❌ Problem: Missing error handling
async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}

// ✅ Fix: Add proper error handling
async function fetchUser(id) {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
}
```

Always prioritize security issues and data loss risks. Be specific about line numbers and provide concrete solutions.
