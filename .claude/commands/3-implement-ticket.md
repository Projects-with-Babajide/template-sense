# Implement Ticket

Execute implementation and validation for an approved ticket.

## Inputs
- `<ticket-id>` - Linear ticket ID
- Reads from: `.claude/command-output/ticket-plan-<ticket-id>.md`

## Workflow

1. **Verify plan exists and is approved** - Read plan file, confirm approval status

2. **Setup branch:**
   ```bash
   git checkout -b <gitBranchName-from-plan>
   ```

3. **Update Linear status:** `mcp__linear-server__update_issue(id, state="In Progress")`

4. **Create todos:** Use TodoWrite for implementation tasks from plan

5. **Implement:**
   - Follow CLAUDE.md guidelines
   - Import constants from `constants.py` (never hard-code)
   - Follow layer dependency rules
   - Update todos as you progress

6. **Validate:**
   ```bash
   pytest tests/ -v              # All tests must pass
   black .                       # Auto-format
   ruff check .                  # No linting errors
   python -c "import template_sense.<module>"  # Verify imports
   ```
   - Check: No circular dependencies, no hard-coded constants
   - Verify all acceptance criteria met

7. **Write state file:** `.claude/command-output/ticket-implementation-<ticket-id>.md`

## Output File

`.claude/command-output/ticket-implementation-<ticket-id>.md`:
```markdown
# Implementation: <ticket-id>

**Branch:** `<gitBranchName>`
**Status:** Ready for Commit

## Files Modified/Created
- `file1.py`
- `file2.py`

## Validation
- Tests: ✅ XX passed
- Black: ✅ Formatted
- Ruff: ✅ Clean
- Imports: ✅ No circular deps

## Acceptance Criteria
- [x] Criterion 1
- [x] Criterion 2

---
Next: `/4-commit-pr-complete <ticket-id>`
```

## Critical Guidelines
- ✅ Use exact `gitBranchName` from plan
- ✅ Import from `constants.py` (never hard-code)
- ✅ Follow layer dependencies (bottom-up only)
- ✅ All tests + black + ruff must pass
- ✅ Use TodoWrite for tracking

## Next Command
`/4-commit-pr-complete <ticket-id>`
