# Commit and Create PR

Commit changes, create PR, and monitor CI.

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

4. **Monitor CI:** Wait for checks - fix failures immediately

5. **Write state file:** `.claude/command-output/ticket-pr-<ticket-id>.md`

## Output File

`.claude/command-output/ticket-pr-<ticket-id>.md`:
```markdown
# PR: <ticket-id>

**PR URL:** https://github.com/.../pull/XX
**Branch:** `<gitBranchName>` → `main`

## CI Status
- Build: ✅ / ❌
- Tests: ✅ / ❌
- Linting: ✅ / ❌

**Last Check:** <timestamp>

---
Next: `/complete-ticket <ticket-id>` (only after CI passes)
```

## Commit Types
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code restructure
- `test` - Add/update tests
- `docs` - Documentation
- `chore` - Maintenance

## Next Command
`/complete-ticket <ticket-id>` (wait for CI to pass first)
