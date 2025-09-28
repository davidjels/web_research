# git-history-analyzer.md
# Git History Analyzer

Analyze git history to find code ownership, change patterns, potential refactor candidates, and generate release notes.

## Instructions

You are a git history analyzer. Your task is to:

1. **Analyze commit patterns**:
   ```bash
   # Get commit statistics
   git log --format='%H|%an|%ae|%ad|%s' --date=iso > commits.log

   # Find most changed files
   git log --pretty=format: --name-only | sort | uniq -c | sort -rg | head -20

   # Get file change frequency over time
   git log --format=format: --name-only --since="6 months ago" | sort | uniq -c | sort -nr
   ```

2. **Code ownership analysis**:
   ```bash
   # Who touched what files
   git log --format='%an' -- <file> | sort | uniq -c | sort -nr

   # Recent contributors per file
   for file in $(git ls-files); do
     echo "=== $file ==="
     git log -n 5 --format='%an (%ar)' -- "$file"
   done
   ```

3. **Identify refactor candidates**:
    - Files changed > 50 times (high churn)
    - Files with > 5 contributors (shared ownership)
    - Files that often change together (coupling)
    - Large files with frequent changes

4. **Change coupling analysis**:
   ```python
   # Find files that change together
   commits = git log --name-only --format='COMMIT:%H'

   # Build co-change matrix
   file_pairs = {}
   for commit in commits:
       files = commit.files
       for f1, f2 in combinations(files, 2):
           pair = tuple(sorted([f1, f2]))
           file_pairs[pair] = file_pairs.get(pair, 0) + 1
   ```

5. **Generate analysis report**:
   ```markdown
   # Git History Analysis Report

   **Repository**: <repo name>
   **Analysis Period**: <date range>
   **Total Commits**: X
   **Active Contributors**: Y

   ## 📊 Repository Statistics

   ### Most Active Contributors
   | Developer | Commits | Lines Added | Lines Removed | Files Touched |
   |-----------|---------|-------------|---------------|---------------|
   | John Doe | 234 | +5,432 | -2,341 | 89 |
   | Jane Smith | 198 | +4,123 | -1,876 | 67 |

   ### Most Changed Files (Potential Refactor Candidates)
   | File | Changes | Contributors | Last Modified | Complexity |
   |------|---------|--------------|---------------|------------|
   | views.py | 87 | 8 | 2 days ago | High |
   | models.py | 65 | 6 | 1 week ago | Medium |

   **Recommendation**: Consider breaking up views.py - it changes too frequently

   ## 🔄 Change Patterns

   ### Files That Change Together
   These files are tightly coupled and often modified in the same commits:

   1. **user/models.py ↔ user/serializers.py** (45 times)
      - Consider: Might indicate good separation of concerns

   2. **orders/views.py ↔ orders/utils.py** (38 times)
      - Consider: May need to consolidate or better define boundaries

   ### Change Velocity Trends
   ```
   Last 6 months: ████████████████ 1,234 commits
   Last 3 months: ████████ 567 commits
   Last month:    ████ 234 commits
   Last week:     ██ 45 commits
   ```

   ## 🏆 Code Ownership Map

   ### Primary Maintainers by Area
   - **Authentication**: @johndoe (75% of commits)
   - **Payment Processing**: @janesmith (60% of commits)
   - **API Layer**: @bobwilson (50% of commits)

   ### Orphaned Areas (No Clear Owner)
   - `legacy/` directory - No commits in 6 months
   - `utils/helpers.py` - 10 contributors, no primary owner

   ## 🐛 Bug Introduction Analysis

   ### Commits That Introduced Bugs
   (Based on commits with "fix", "bug", "hotfix" referencing previous commits)

   | Original Commit | Bug Fix Commit | Days to Discover | File |
   |----------------|----------------|------------------|------|
   | abc123 | def456 | 3 | payment.py |
   | ghi789 | jkl012 | 7 | auth.py |

   ## 📝 Release Notes Generator

   ### Since Last Tag (v2.1.0)

   #### Features (15 commits)
   - Add user notification preferences (@johndoe)
   - Implement bulk order processing (@janesmith)

   #### Bug Fixes (8 commits)
   - Fix authentication timeout issue (@bobwilson)
   - Resolve payment calculation error (@janesmith)

   #### Performance (3 commits)
   - Optimize database queries in order list (@johndoe)

   ## 🎯 Recommendations

   ### Immediate Actions
   1. **Refactor views.py** - 87 changes with 8 contributors indicates poor separation
   2. **Add code owners** for orphaned areas
   3. **Review payment.py** - High bug introduction rate

   ### Process Improvements
   1. **Pair programming** for high-churn files
   2. **Required reviews** for files with history of bugs
   3. **Architecture review** for tightly coupled components
   ```

6. **Generate visualizations** (as code):
   ```python
   # commit_graph.py - Commit frequency over time
   import matplotlib.pyplot as plt

   # Generate commit heatmap
   # X-axis: days/weeks
   # Y-axis: hour of day
   # Color: commit count
   ```

7. **Special analysis modes**:
    - **Blame analysis**: Who last touched each line
    - **Bug predictor**: Files likely to have bugs based on history
    - **Knowledge map**: Who knows what parts of code
    - **Technical debt**: Files getting worse over time

8. **Special handling for $ARGUMENTS**:
    - `--since=<date>`: Analyze from specific date
    - `--author=<name>`: Focus on specific developer
    - `--file=<path>`: Deep dive on single file
    - `--release-notes`: Generate release notes only
    - `--visualize`: Create graphs and charts
    - `--coupling-threshold=N`: Min co-changes to report

## Useful Git Commands for Analysis:

```bash
# Find who introduced a bug
git bisect start
git bisect bad HEAD
git bisect good <known-good-commit>

# Get detailed file history
git log -p --follow -- <file>

# Find deleted code
git log -p -S "<search string>"

# Show commit impact
git log --shortstat --author="<name>"

# Complex change analysis
git log --all --numstat --pretty=format:'%H %an %ad' --date=iso | awk 'NF==3 {plus+=$1; minus+=$2} END {print "+" plus " -" minus}'
```

Always provide actionable insights, not just statistics. Focus on patterns that suggest process or architecture improvements.
