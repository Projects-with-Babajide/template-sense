# Plan and Implement Ticket

Plan and implement a Linear ticket following the Template Sense project workflow.

## Inputs
- Linear ticket ID (e.g., BAT-17)

## Steps

### Phase 0: Setup (REQUIRED - Do this first)

1. **Sync with main branch:**
   - Switch to main branch: `git checkout main`
   - Pull latest changes: `git pull origin main`
   - This ensures you're working with the latest codebase before planning

### Phase 1: Planning (REQUIRED - Must wait for user confirmation)

1. **Fetch ticket details:**
   - Use `mcp__linear-server__get_issue("<ticket-id>")` to get ticket information
   - Extract the `gitBranchName` field from the ticket response
   - Review the ticket description, checklist, and acceptance criteria

2. **Analyze requirements:**
   - Review CLAUDE.md for relevant architecture patterns
   - Identify which modules/layers will be affected
   - Check for dependencies on other tickets or modules
   - Review anti-patterns to avoid

3. **Create implementation plan:**
   - Break down the ticket checklist into concrete implementation steps
   - Identify files to create/modify
   - List specific functions/classes to implement
   - Include testing strategy
   - Note any potential risks or edge cases

4. **Present plan to user:**
   - Show the implementation plan in a clear, structured format
   - Include:
     - Files to create/modify
     - Key functions/classes to implement
     - Testing approach
     - Estimated steps
   - **WAIT for user confirmation or feedback**
   - **DO NOT proceed to Phase 2 without explicit user approval**
   - Be prepared to iterate on the plan based on user feedback

### Phase 2: Implementation (Only after user confirms plan)

5. **Set up branch:**
   - Create and checkout the branch using the exact `gitBranchName` from Linear
   - Example: `git checkout -b jideokus/bat-12-task-9-create-project-folder-structure`
   - Note: Main branch was already synced in Phase 0

6. **Update ticket status:**
   - Use `mcp__linear-server__update_issue(id="<ticket-id>", state="In Progress")`

7. **Create todo list:**
   - Use `TodoWrite` tool to create a comprehensive task list including:
     - Implementation tasks from the approved plan
     - Testing and validation tasks
     - Git commit task
     - Pull request creation task
     - Linear ticket update tasks (status to Done, add completion comment)

8. **Implement the feature:**
   - Follow guidelines from CLAUDE.md
   - Follow the approved implementation plan
   - Update todos as you progress (mark in_progress, then completed)

9. **Validate implementation:**
   - Run ALL tests: `pytest tests/ -v`
   - Verify all tests pass
   - Run code quality tools:
     - `black .` (auto-format code)
     - `ruff check .` (linting)
   - Verify all acceptance criteria from the ticket are met
   - Ensure no linting errors before proceeding

10. **Commit changes:**
   - Stage relevant files: `git add <files>`
   - Use conventional commit format:
     ```
     <type>: <description> (<ticket-id>)

     - Bullet point of changes
     - Another change

     🤖 Generated with [Claude Code](https://claude.com/claude-code)

     Co-Authored-By: Claude <noreply@anthropic.com>
     ```
   - Common types: feat, fix, docs, refactor, test, chore

11. **Create pull request:**
   - Push branch: `git push -u origin <branch-name>`
   - Create PR using gh CLI:
     ```bash
     gh pr create --title "<type>: <title> (<ticket-id>)" --body "$(cat <<'EOF'
     ## Summary
     - Bullet points describing changes

     ## Test plan
     - How to test these changes

     🤖 Generated with [Claude Code](https://claude.com/claude-code)
     EOF
     )"
     ```
   - Capture the PR URL from the output

12. **Monitor CI checks:**
   - Wait for CI to complete: `gh pr view <pr-number> --json statusCheckRollup`
   - Check for failures: `gh run view <run-id> --log-failed` (if CI fails)
   - **If CI fails:**
     - Fix the issues locally
     - Re-run validation (tests, black, ruff)
     - Commit and push the fixes
     - Wait for CI to pass
   - **DO NOT proceed** until all CI checks pass
   - Verify the PR shows all green checkmarks

13. **Update Linear ticket to Done:**
    - Use `mcp__linear-server__update_issue(id="<ticket-id>", state="Done")`

14. **Add completion comment:**
    - Use `mcp__linear-server__create_comment()` with:
      - Summary of what was completed
      - Link to the PR (with all CI checks passing ✅)
      - Any validation results (e.g., test output, import verification)
      - Confirmation that all CI checks passed

## Guidelines

- **ALWAYS** start with Phase 0 (Setup) to sync with main branch before any other work
- **ALWAYS** complete Phase 1 (Planning) and wait for user confirmation before proceeding to Phase 2 (Implementation)
- **NEVER** start implementation without explicit user approval of the plan
- **BE PREPARED** to iterate on the plan based on user feedback
- **ALWAYS** use the exact `gitBranchName` from Linear - never create your own branch names
- **ALWAYS** run ALL tests before committing: `pytest tests/ -v`
- **ALWAYS** run code quality tools before committing: `black .` and `ruff check .`
- **ALWAYS** verify no linting errors before creating PR
- **ALWAYS** create a pull request after committing - never skip this step
- **ALWAYS** monitor CI checks and wait for them to pass before marking ticket as Done
- **NEVER** mark a ticket as Done if CI checks are failing
- **ALWAYS** fix any CI failures immediately and wait for green checkmarks
- **ALWAYS** update the Linear ticket status at each stage (In Progress, Done)
- **ALWAYS** include the PR URL in the Linear completion comment
- **ALWAYS** use the TodoWrite tool to track progress for non-trivial tasks

## Output Format

### Phase 0: Setup Output

```markdown
## Setup for <TICKET-ID>

- ✅ Switched to main branch
- ✅ Pulled latest changes from origin/main
- Ready to proceed with planning
```

### Phase 1: Planning Output

```markdown
## Planning for <TICKET-ID>: <Title>

**Branch:** <branch-name>
**Dependencies:** <list any dependent tasks>

### Requirements Analysis:
- <Key requirement 1>
- <Key requirement 2>

### Implementation Plan:

#### Files to Create:
- `path/to/file1.py` — <Purpose>
- `path/to/file2.py` — <Purpose>

#### Files to Modify:
- `path/to/existing.py` — <What changes>

#### Key Functions/Classes:
1. `function_name(params) -> return_type`
   - Purpose: <description>
   - Implementation approach: <brief explanation>

2. `ClassName`
   - Purpose: <description>
   - Key methods: <list>

#### Testing Strategy:
- Unit tests in `tests/test_<module>.py`
- Test cases:
  - <Test case 1>
  - <Test case 2>
- Mock dependencies: <list>

#### Potential Risks/Edge Cases:
- <Risk 1 and mitigation>
- <Edge case 1 and handling>

#### Estimated Steps:
- X implementation tasks
- Y test tasks
- Z validation tasks

---

**Please review this plan and provide feedback or approval to proceed with implementation.**
```

### Phase 2: Implementation Output

```markdown
## Implementing <TICKET-ID>

**Status:** Implementation approved ✅

### Progress Updates:
- ✅ Synced with main branch (Phase 0)
- ✅ Fetched ticket details and created plan
- ✅ Plan approved by user
- ✅ Created branch and updated status to In Progress
- ✅ Created todo list with X tasks
- 🔄 Implementing feature...
- ✅ Implementation complete
- ✅ Validation complete (all tests pass, no linting errors)
- ✅ Changes committed
- ✅ Pull request created: <PR URL>
- ✅ CI checks passed (all green ✅)
- ✅ Ticket updated to Done

### Summary:
<Brief summary of what was accomplished>

### Validation Results:
- Tests: X/X passed
- Code quality: All checks passed (Black, Ruff)
- CI Status: All checks passed ✅

**All acceptance criteria met!**
```
