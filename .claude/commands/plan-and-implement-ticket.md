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

2. **Review current codebase state:**
   - Use the Task tool with subagent_type=Explore to understand affected areas
   - Check existing implementations in relevant modules
   - Identify any similar patterns already implemented
   - Look for reusable utilities or helpers

3. **Analyze requirements:**
   - Review CLAUDE.md for relevant architecture patterns
   - Identify which modules/layers will be affected (refer to Module Boundaries section)
   - Check for dependencies on other tickets or modules
   - Review anti-patterns to avoid (especially the ❌ NEVER Do This section)
   - Verify constants usage: ensure all thresholds/configs will come from `constants.py`

4. **Assess ticket value and strategic alignment:**
   - **Evaluate if this ticket helps with the project direction:**
     - Does it align with the project's stated goals in CLAUDE.md?
     - Does it move the project forward toward the end-to-end pipeline?
     - Is this the right time to implement this (dependencies completed)?
     - Are there higher-priority items that should be done first?
   - **Provide your honest opinion:**
     - State whether this ticket is valuable and well-timed
     - Explain your reasoning based on project context
     - If you have concerns, clearly articulate them
   - **WAIT for user's perspective** before proceeding with technical assessment

5. **Assess ticket quality and suggest improvements:**
   - Review ticket against project architecture and current codebase
   - Check if ticket aligns with layer dependencies (bottom-up flow)
   - Identify any missing acceptance criteria or edge cases
   - Check if similar functionality already exists that can be reused
   - **If improvements are needed:** Present suggestions to user and wait for confirmation
   - **If ticket is good as-is:** Note that in the plan and proceed

6. **Create implementation plan:**
   - Break down the ticket checklist into concrete implementation steps
   - Identify files to create/modify
   - List specific functions/classes to implement
   - Specify which constants from `constants.py` will be used or need to be added
   - List integration points with existing modules
   - Include detailed testing strategy:
     - What to test (functions, edge cases, error handling)
     - What to mock (external dependencies, AI providers, file I/O)
     - Expected test coverage
   - Note any potential risks or edge cases
   - Identify any circular dependency risks

7. **Present plan to user:**
   - Show the implementation plan in a clear, structured format
   - Include:
     - Ticket quality assessment and any suggested improvements
     - Codebase context (related implementations, reusable utilities)
     - Files to create/modify
     - Key functions/classes to implement
     - Constants usage (existing and new)
     - Integration points with existing modules
     - Testing approach
     - Estimated steps
   - **WAIT for user confirmation or feedback**
   - **DO NOT proceed to Phase 2 without explicit user approval**
   - Be prepared to iterate on the plan based on user feedback

8. **Document accepted changes (if any):**
   - **If ticket improvements or plan modifications were accepted by user:**
     - Use `mcp__linear-server__create_comment()` to add a comment to the ticket
     - Summarize what changes/improvements were agreed upon
     - Document any deviations from original ticket description
     - Include the finalized implementation approach
   - **If no changes:** Skip this step and proceed to Phase 2
   - Example comment format:
     ```
     ## Planning Notes - Changes Accepted

     The following improvements/changes were agreed upon before implementation:

     - <Change 1>
     - <Change 2>

     ### Finalized Approach:
     - <Summary of final implementation approach>
     ```

### Phase 2: Implementation (Only after user confirms plan)

9. **Set up branch:**
   - Create and checkout the branch using the exact `gitBranchName` from Linear
   - Example: `git checkout -b jideokus/bat-12-task-9-create-project-folder-structure`
   - Note: Main branch was already synced in Phase 0

10. **Update ticket status:**
   - Use `mcp__linear-server__update_issue(id="<ticket-id>", state="In Progress")`

11. **Create todo list:**
   - Use `TodoWrite` tool to create a comprehensive task list including:
     - Implementation tasks from the approved plan
     - Testing and validation tasks
     - Git commit task
     - Pull request creation task
     - Linear ticket update tasks (status to Done, add completion comment)

12. **Implement the feature:**
   - Follow guidelines from CLAUDE.md
   - Follow the approved implementation plan
   - Update todos as you progress (mark in_progress, then completed)
   - Ensure all constants are imported from `constants.py` (never hard-coded)
   - Follow layer dependency rules (import only from layers below)

13. **Validate implementation:**
   - Run ALL tests: `pytest tests/ -v`
   - Verify all tests pass
   - Run code quality tools:
     - `black .` (auto-format code)
     - `ruff check .` (linting)
   - Verify all acceptance criteria from the ticket are met
   - Ensure no linting errors before proceeding
   - Check for circular dependencies (imports should only go down the layer stack)
   - Verify no hard-coded constants (all should be from `constants.py`)
   - Test import validation: `python -c "import template_sense.<module>"`

14. **Commit changes:**
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

15. **Create pull request:**
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

16. **Monitor CI checks:**
   - Wait for CI to complete: `gh pr view <pr-number> --json statusCheckRollup`
   - Check for failures: `gh run view <run-id> --log-failed` (if CI fails)
   - **If CI fails:**
     - Fix the issues locally
     - Re-run validation (tests, black, ruff)
     - Commit and push the fixes
     - Wait for CI to pass
   - **DO NOT proceed** until all CI checks pass
   - Verify the PR shows all green checkmarks

17. **Update Linear ticket to Done:**
    - Use `mcp__linear-server__update_issue(id="<ticket-id>", state="Done")`

18. **Add completion comment:**
    - Use `mcp__linear-server__create_comment()` with:
      - Summary of what was completed
      - Link to the PR (with all CI checks passing ✅)
      - Any validation results (e.g., test output, import verification)
      - Confirmation that all CI checks passed

## Guidelines

- **ALWAYS** start with Phase 0 (Setup) to sync with main branch before any other work
- **ALWAYS** use the Task tool with Explore agent to understand the codebase context during planning
- **ALWAYS** provide honest opinion on ticket value and strategic alignment before technical assessment
- **ALWAYS** assess ticket quality and suggest improvements if needed before creating the plan
- **ALWAYS** complete Phase 1 (Planning) and wait for user confirmation before proceeding to Phase 2 (Implementation)
- **ALWAYS** document accepted changes/improvements in a Linear comment before starting implementation
- **NEVER** start implementation without explicit user approval of the plan
- **BE PREPARED** to iterate on the plan based on user feedback
- **ALWAYS** use the exact `gitBranchName` from Linear - never create your own branch names
- **ALWAYS** import constants from `constants.py` - never hard-code configuration values
- **ALWAYS** follow layer dependency rules (import only from layers below in the stack)
- **ALWAYS** run ALL tests before committing: `pytest tests/ -v`
- **ALWAYS** run code quality tools before committing: `black .` and `ruff check .`
- **ALWAYS** verify no linting errors and no circular dependencies before creating PR
- **ALWAYS** validate imports work: `python -c "import template_sense.<module>"`
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

### Strategic Alignment & Value Assessment:

**My Opinion:** <State whether this ticket is valuable and well-timed>

**Reasoning:**
- **Project Goals Alignment:** <Does it align with CLAUDE.md goals?>
- **Pipeline Progress:** <Does it move toward end-to-end functionality?>
- **Timing:** <Is this the right time? Are dependencies complete?>
- **Priority:** <Are there more critical items?>

**Recommendation:** ✅ Proceed / ⚠️ Reconsider / 🔄 Defer

---

**Waiting for your perspective before proceeding with technical assessment.**

### Ticket Quality Assessment:
- ✅ **Ticket is good as-is** — Aligns with architecture, has clear acceptance criteria
  OR
- ⚠️ **Suggested Improvements:**
  - <Improvement 1>
  - <Improvement 2>
  - **Waiting for user confirmation on these suggestions before proceeding**

### Codebase Context:
- **Related Implementations:** <List similar patterns/modules already in codebase>
- **Reusable Utilities:** <List existing utilities that can be leveraged>
- **Layer Affected:** <Which layer in the architecture: Adapters/Extraction/AI/etc.>

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

#### Constants Usage:
- **Existing constants to use:**
  - `CONSTANT_NAME` from `constants.py` — <Purpose>
- **New constants to add:**
  - `NEW_CONSTANT_NAME` — <Purpose and value>

#### Integration Points:
- Imports from: `<module1>`, `<module2>` (following layer dependency rules)
- Used by: `<module3>`, `<module4>`
- No circular dependencies detected

#### Testing Strategy:
- Unit tests in `tests/test_<module>.py`
- Test cases:
  - <Test case 1>
  - <Test case 2>
  - Error handling cases
  - Edge cases
- Mock dependencies: <list>
- Expected coverage: >80%

#### Potential Risks/Edge Cases:
- <Risk 1 and mitigation>
- <Edge case 1 and handling>

#### Estimated Steps:
- X implementation tasks
- Y test tasks
- Z validation tasks

---

**Please review this plan and provide feedback or approval to proceed with implementation.**

**Note:** If any improvements or changes are accepted, they will be documented in a Linear comment before implementation begins.
```

### Phase 2: Implementation Output

```markdown
## Implementing <TICKET-ID>

**Status:** Implementation approved ✅

### Progress Updates:
- ✅ Synced with main branch (Phase 0)
- ✅ Assessed ticket strategic value and alignment
- ✅ Fetched ticket details and created plan
- ✅ Plan approved by user
- ✅ Documented accepted changes in Linear comment (if applicable)
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
- Import validation: ✅ `python -c "import template_sense.<module>"` successful
- Constants check: ✅ No hard-coded values (all from constants.py)
- Circular dependencies: ✅ None detected
- CI Status: All checks passed ✅

**All acceptance criteria met!**
```
