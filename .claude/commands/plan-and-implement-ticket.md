# Plan and Implement Ticket

Plan and implement a Linear ticket following the Template Sense project workflow.

## Inputs
- Linear ticket ID (e.g., BAT-17)

## Workflow

### Phase 0: Setup

1. **Sync with main:**
   ```bash
   git checkout main
   git pull origin main
   ```

### Phase 1: Planning (REQUIRED - Must wait for user confirmation)

1. **Fetch ticket:** `mcp__linear-server__get_issue("<ticket-id>")` - Extract `gitBranchName`, review description and acceptance criteria

2. **Explore codebase:** Use Task tool (Explore agent) to understand affected areas, find similar patterns, identify reusable utilities

3. **Assess strategic value:**
   - Does this align with project goals (CLAUDE.md)?
   - Is the timing right (dependencies complete)?
   - Provide honest opinion: ✅ Proceed / ⚠️ Reconsider / 🔄 Defer
   - **WAIT for user's perspective**

4. **Review ticket quality:**
   - Check architecture alignment (layer dependencies)
   - Identify missing acceptance criteria
   - Suggest improvements if needed
   - **WAIT for user confirmation if changes suggested**

5. **Create implementation plan:**
   - Files to create/modify
   - Functions/classes to implement
   - Constants to use/add (from `constants.py`)
   - Integration points (following layer rules)
   - Testing strategy (what to test, what to mock)
   - Risks and edge cases

6. **Present plan:**
   - Include: Strategic assessment, codebase context, technical plan
   - **WAIT for user approval - DO NOT proceed without it**

7. **Document changes (if any):** If improvements were accepted, add Linear comment summarizing agreed changes

### Phase 2: Implementation (Only after user confirms plan)

8. **Setup branch:**
   ```bash
   git checkout -b <gitBranchName-from-linear>
   ```

9. **Update status:** `mcp__linear-server__update_issue(id, state="In Progress")`

10. **Create todos:** Use TodoWrite for implementation tasks, testing, commit, PR, ticket updates

11. **Implement:**
    - Follow CLAUDE.md guidelines
    - Import constants from `constants.py` (never hard-code)
    - Follow layer dependency rules (import only from layers below)
    - Update todos as you progress

12. **Validate:**
    ```bash
    pytest tests/ -v              # All tests must pass
    black .                       # Auto-format
    ruff check .                  # No linting errors
    python -c "import template_sense.<module>"  # Verify imports
    ```
    - Check: No circular dependencies, no hard-coded constants
    - Verify all acceptance criteria met

13. **Commit:**
    ```bash
    git add <files>
    git commit -m "$(cat <<'EOF'
<type>: <description> (<ticket-id>)

- Bullet points of changes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
    ```

14. **Create PR:**
    ```bash
    git push -u origin <branch-name>
    gh pr create --title "<type>: <title> (<ticket-id>)" --body "..."
    ```

15. **Monitor CI:** Wait for all checks to pass - fix failures immediately, **DO NOT proceed if failing**

16. **Complete ticket:**
    - Update status: `mcp__linear-server__update_issue(id, state="Done")`
    - Add comment: Summary, PR URL (with ✅), validation results, CI status

## Critical Guidelines

**Planning:**
- ✅ ALWAYS use Explore agent to understand codebase
- ✅ ALWAYS provide honest strategic opinion
- ✅ ALWAYS wait for user approval before implementing
- ✅ ALWAYS document accepted changes in Linear

**Implementation:**
- ✅ ALWAYS use exact `gitBranchName` from Linear
- ✅ ALWAYS import from `constants.py` (never hard-code)
- ✅ ALWAYS follow layer dependencies (bottom-up only)
- ✅ ALWAYS run all tests + black + ruff before committing
- ✅ ALWAYS validate imports and check for circular deps
- ✅ ALWAYS create PR and wait for CI to pass

**Completion:**
- ❌ NEVER mark Done if CI is failing
- ✅ ALWAYS include PR URL in completion comment
- ✅ ALWAYS use TodoWrite for non-trivial tasks

## Common Commit Types
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code restructure
- `test` - Add/update tests
- `docs` - Documentation
- `chore` - Maintenance

## Quick Reference

**Key Architecture Principles (from CLAUDE.md):**
- Layer flow: Adapters → Extraction → AI Providers → AI → Translation → Mapping → Output → API
- Each layer imports only from layers below (no circular deps)
- All config values in `constants.py`
- Provider-agnostic design throughout
- Mock external dependencies in tests (AI, file I/O)

**Anti-Patterns to Avoid:**
- ❌ Logging sensitive data (API keys, invoice values)
- ❌ Hard-coding secrets or config values
- ❌ Using `print()` (use logger)
- ❌ Importing AI providers directly (use interface)
- ❌ Returning internal dataclasses from public API
- ❌ Swallowing exceptions silently
