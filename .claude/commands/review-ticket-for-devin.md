# Review Ticket for Devin

Review a Linear ticket that Devin has concerns about and propose improvements to address those concerns.

## Inputs
- Linear ticket ID (e.g., BAT-20)

## Steps

### 1. Fetch ticket and Devin's comments

```
Use mcp__linear-server__get_issue("<ticket-id>") to get ticket details
Use mcp__linear-server__list_comments("<ticket-id>") to get all comments
```

### 2. Analyze Devin's concerns

Review Devin's scoping comments (usually marked with +++ sections) and identify:
- **Key concerns** - What is causing uncertainty or ambiguity?
- **Confidence level** - Why is Devin's confidence Medium/Low instead of High?
- **Alternative interpretations** - What ambiguities exist in the ticket?
- **Design decisions needed** - What questions need answers before implementation?

Common concern categories:
- Contradictions with existing code or documentation
- Ambiguous values or requirements (e.g., "e.g." suggesting flexibility)
- Missing context or unclear scope
- Conflicting patterns or strategies
- Undefined features or requirements

### 3. Research the codebase

For each concern, investigate:
- Check relevant existing files mentioned by Devin
- Review CLAUDE.md and docs/ for project patterns
- Check pyproject.toml for dependencies and configuration
- Look at similar completed tasks for precedent
- Verify assumptions against actual code

Use appropriate tools:
- `Read` for specific files
- `Glob` for finding related files
- `Grep` for searching patterns

### 4. Propose ticket improvements

Create a structured "Additional Clarifications" section that includes:

**For each concern:**
- Clear resolution/decision
- Concrete values instead of "e.g." or "such as"
- Rationale explaining why this approach
- References to existing code/docs that support the decision
- Examples showing correct implementation

**Structure template:**
```markdown
## Additional Clarifications (Addressing Implementation Concerns)

### 1. [Concern Title]
- **Decision:** [Clear, specific decision]
- **Rationale:** [Why this approach]
- **Reference:** [Existing code/docs that support this]
- **Example:** [Code snippet if helpful]

### 2. [Next Concern]
...
```

### 5. Show proposed changes to user

Present the proposed "Additional Clarifications" section to the user with:
- Summary of what concerns are being addressed
- Key decisions being made
- Any assumptions or questions for the user

**DO NOT update the ticket yet** - wait for user approval.

### 6. Update ticket after approval

Once user approves:
```
Use mcp__linear-server__update_issue(id="<ticket-id>", description="<updated-description>")
```

Append the clarifications section to the existing ticket description, keeping all original content.

### 7. Tag Devin in a comment

```
Use mcp__linear-server__create_comment(issueId="<ticket-id>", body="...")
```

Comment structure:
```markdown
@Devin

I've updated the ticket with detailed clarifications to address all your concerns:

## Key Changes:

✅ [Concern 1]: [How it was resolved]
✅ [Concern 2]: [How it was resolved]
...

## New Section Added:

The "Additional Clarifications" section now includes:
1. [Summary of subsection 1]
2. [Summary of subsection 2]
...

All your concerns should now be addressed. Please review and let me know if you need any additional clarification!
```

## Guidelines

### Research Best Practices
- **Always check existing code first** - Don't make assumptions
- **Look for patterns** - See what similar tasks have done
- **Verify against docs** - CLAUDE.md, architecture.md, dev-setup.md
- **Consider downstream impact** - How will other modules use this?

### Writing Clarifications
- **Be specific** - Replace "e.g.", "such as", "for example" with exact values
- **Provide rationale** - Explain the "why" behind each decision
- **Use code examples** - Show concrete implementation patterns
- **Reference existing code** - Build on what's already there
- **Think about consumers** - How will Tako (or other users) interact with this?

### Common Patterns to Address

**Ambiguous values:**
```markdown
❌ Bad: "DEFAULT_TIMEOUT (e.g. 30 seconds)"
✅ Good: "DEFAULT_TIMEOUT = 30  # Exact value - timeout in seconds for AI requests"
```

**Missing context:**
```markdown
❌ Bad: "Support multiple file types"
✅ Good: "Support .xlsx and .xls to align with file_validation module (BAT-19). Reference: src/template_sense/file_validation.py line 27"
```

**Unclear strategy:**
```markdown
❌ Bad: "Add API key configuration"
✅ Good: "Use provider-specific env vars (OPENAI_API_KEY, ANTHROPIC_API_KEY) not generic. Rationale: Matches existing docs/dev-setup.md pattern and allows Tako to switch providers easily."
```

**Undefined scope:**
```markdown
❌ Bad: "Add feature flags"
✅ Good: "No feature flags in this task. Scope: Configuration constants only. Future feature flags will be separate task."
```

### Red Flags to Watch For

- "e.g.", "such as", "for example" - Replace with exact values
- "TBD", "TODO", "decide later" - Make the decision now
- Contradictions between ticket and existing code
- Missing dependency information
- Unclear success criteria

## Output Format

After user approval, provide a summary:

```markdown
## ✅ Ticket Updated: <TICKET-ID>

### Concerns Addressed:
1. ✅ [Concern 1]
2. ✅ [Concern 2]
...

### Clarifications Added:
- [Key clarification 1]
- [Key clarification 2]
...

### Devin Tagged:
Comment added at [Linear URL]

Devin should now have all the information needed to proceed with high confidence!
```

## Notes

- This command is for when Devin has **already scoped** the ticket and expressed concerns
- If Devin hasn't scoped yet, wait for Devin's initial scoping comment
- Focus on removing ambiguity and providing concrete, actionable guidance
- Always wait for user approval before updating the ticket
- The goal is to increase Devin's confidence from Medium/Low to High
