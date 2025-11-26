# Plan and Implement Ticket

Plan and implement a Linear ticket following the Template Sense project workflow.

## Inputs
- Linear ticket ID (e.g., BAT-17)

## Steps

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
   - Switch to main branch first: `git checkout main`
   - Create and checkout the branch using the exact `gitBranchName` from Linear
   - Example: `git checkout -b jideokus/bat-12-task-9-create-project-folder-structure`

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
   - Run code quality tools as needed
   - Run tests if applicable
   - Verify all acceptance criteria from the ticket are met

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

12. **Update Linear ticket to Done:**
    - Use `mcp__linear-server__update_issue(id="<ticket-id>", state="Done")`

13. **Add completion comment:**
    - Use `mcp__linear-server__create_comment()` with:
      - Summary of what was completed
      - Link to the PR
      - Any validation results (e.g., test output, import verification)

## Guidelines

- **ALWAYS** complete Phase 1 (Planning) and wait for user confirmation before proceeding to Phase 2 (Implementation)
- **NEVER** start implementation without explicit user approval of the plan
- **BE PREPARED** to iterate on the plan based on user feedback
- **ALWAYS** use the exact `gitBranchName` from Linear - never create your own branch names
- **ALWAYS** update the Linear ticket status at each stage (In Progress, Done)
- **ALWAYS** create a pull request after committing - never skip this step
- **ALWAYS** include the PR URL in the Linear completion comment
- **ALWAYS** use the TodoWrite tool to track progress for non-trivial tasks

## Output Format

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
- ✅ Fetched ticket details and created plan
- ✅ Plan approved by user
- ✅ Created branch and updated status to In Progress
- ✅ Created todo list with X tasks
- 🔄 Implementing feature...
- ✅ Implementation complete
- ✅ Validation complete
- ✅ Changes committed
- ✅ Pull request created: <PR URL>
- ✅ Ticket updated to Done

### Summary:
<Brief summary of what was accomplished>

**All acceptance criteria met!**
```
