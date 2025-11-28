# Commit, PR, and Complete

Commit changes, create PR, monitor CI, and mark ticket as done.

## Inputs
- `<ticket-id>` - Linear ticket ID
- Reads from: `.claude/command-output/ticket-implementation-<ticket-id>.md`

## Workflow

1. **Verify implementation validated** - Read implementation file, confirm all checks passed

2. **Commit:**
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

3. **Push and create PR:**
   ```bash
   git push -u origin <branch-name>
   gh pr create --title "<type>: <title> (<ticket-id>)" --body "..."
   ```

4. **Monitor CI:** Wait for all checks to pass - fix failures immediately

5. **Verify CI passing** - Confirm all checks passed (build, tests, linting)

6. **Update Linear to Done:** `mcp__linear-server__update_issue(id, state="Done")`

7. **Add completion comment to Linear:**
   ```markdown
   Implementation complete! ✅

   **PR:** <pr-url>
   **Validation:** All tests passing, code formatted
   **CI:** All checks passing

   <Summary of changes>
   ```

## Commit Types
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code restructure
- `test` - Add/update tests
- `docs` - Documentation
- `chore` - Maintenance

## Critical Guidelines
- ❌ NEVER mark Done if CI is failing
- ✅ ALWAYS include PR URL in Linear comment
- ✅ ALWAYS wait for CI to pass before marking Done
- ✅ Fix CI failures immediately
