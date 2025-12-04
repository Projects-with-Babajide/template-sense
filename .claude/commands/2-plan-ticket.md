# Plan Ticket

Plan and analyze a Linear ticket.

## Inputs
- `<ticket-id>` - Linear ticket ID (e.g., BAT-17)

## Workflow

1. **Fetch ticket:** `mcp__linear-server__get_issue("<ticket-id>")` - Extract `gitBranchName`, description, acceptance criteria

2. **Explore codebase:** Use Task tool (Explore agent) to understand affected areas, find patterns, identify utilities

3. **Identify affected tests:** Search for existing tests that will need updates:
   - Use Grep to find test files that import or test the modules being changed
   - Look for integration tests that may be affected by the changes
   - Identify mocks/patches that may need to be updated
   - Document which test files need modifications in the plan

4. **Strategic assessment:**
   - Present alignment with CLAUDE.md goals, timing, dependencies
   - **ASK USER:** "Does this align with current priorities? Should we proceed?"
   - Wait for confirmation or feedback
   - Iterate if needed

5. **Review ticket quality:**
   - Check architecture alignment, missing criteria
   - Suggest improvements if needed
   - **ASK USER:** "Are these improvements acceptable?"
   - Wait for confirmation

6. **Create implementation plan:**
   - Files to modify/create
   - Functions/classes to implement
   - Constants from `constants.py`
   - Integration points
   - Testing strategy (include existing tests that need updates)
   - Risks

7. **Present plan and get approval:**
   - **ASK USER:** "Does this plan look good? Any changes needed?"
   - Wait for explicit approval
   - Iterate until approved

8. **Document changes:** If ticket improvements accepted, add Linear comment

9. **Write state file:** `.claude/command-output/ticket-plan-<ticket-id>.md`

## Output File

`.claude/command-output/ticket-plan-<ticket-id>.md`:
```markdown
# Plan: <ticket-id>

**Branch:** `<gitBranchName>`
**Title:** ...

## Files
- `src/...` - create/modify - purpose

## Implementation
- Function/class changes
- Constants: import X, add Y to constants.py
- Integration: layer A → layer B

## Tests

### New Tests
- Test X - mock Y
- Test Z - verify W

### Existing Tests to Update
- `tests/test_module.py` - Update mocks/patches for refactored code
- `tests/integration/test_feature.py` - Adjust integration test expectations

## Risks
- Edge case A
- Consideration B

**Approved:** ✅ <timestamp>
**Linear Updated:** ✅ / N/A

---
Next: `/3-implement-ticket <ticket-id>`
```

## Next Command
`/3-implement-ticket <ticket-id>`
