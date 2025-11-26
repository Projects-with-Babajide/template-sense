# Plan and Implement Ticket

Plan and implement a Linear ticket following the Template Sense project workflow.

## Inputs
- Linear ticket ID (e.g., BAT-17)

## Steps

1. **Fetch ticket details:**
   - Use `mcp__linear-server__get_issue("<ticket-id>")` to get ticket information
   - Extract the `gitBranchName` field from the ticket response
   - Review the ticket description, checklist, and acceptance criteria

2. **Set up branch:**
   - Switch to main branch first: `git checkout main`
   - Create and checkout the branch using the exact `gitBranchName` from Linear
   - Example: `git checkout -b jideokus/bat-12-task-9-create-project-folder-structure`

3. **Update ticket status:**
   - Use `mcp__linear-server__update_issue(id="<ticket-id>", state="In Progress")`

4. **Create todo list:**
   - Use `TodoWrite` tool to create a comprehensive task list including:
     - Implementation tasks from the ticket checklist
     - Testing and validation tasks
     - Git commit task
     - Pull request creation task
     - Linear ticket update tasks (status to Done, add completion comment)

5. **Implement the feature:**
   - Follow guidelines from CLAUDE.md
   - Update todos as you progress (mark in_progress, then completed)

6. **Validate implementation:**
   - Run code quality tools as needed
   - Run tests if applicable
   - Verify all acceptance criteria from the ticket are met

7. **Commit changes:**
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

8. **Create pull request:**
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

9. **Update Linear ticket to Done:**
   - Use `mcp__linear-server__update_issue(id="<ticket-id>", state="Done")`

10. **Add completion comment:**
    - Use `mcp__linear-server__create_comment()` with:
      - Summary of what was completed
      - Link to the PR
      - Any validation results (e.g., test output, import verification)

## Guidelines

- **ALWAYS** use the exact `gitBranchName` from Linear - never create your own branch names
- **ALWAYS** update the Linear ticket status at each stage (In Progress, Done)
- **ALWAYS** create a pull request after committing - never skip this step
- **ALWAYS** include the PR URL in the Linear completion comment
- **ALWAYS** use the TodoWrite tool to track progress for non-trivial tasks

## Output Format

Provide clear status updates to the user throughout the process:

```markdown
## Starting work on <TICKET-ID>

**Ticket:** <Title>
**Branch:** <branch-name>

### Progress Updates:
- ✅ Fetched ticket details
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
