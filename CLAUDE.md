# Contributing to cryptography-skills

## Resources

**Official Anthropic documentation:**

- [Claude Code Plugins](https://code.claude.com/docs/en/plugins)
- [Agent Skills](https://code.claude.com/docs/en/skills)
- [Best Practices](https://code.claude.com/docs/en/skills#best-practices)

**Reference repositories:**

- [trailofbits/skills](https://github.com/trailofbits/skills) — Security skills marketplace (model for this repo)
- [ZippelLabs/zkVMs-Security](https://github.com/ZippelLabs/zkVMs-Security) — Public zkVM audit reports

## Plugin Structure

```
plugins/
  <plugin-name>/
    .claude-plugin/
      plugin.json         # Plugin metadata
    skills/
      <skill-name>/
        SKILL.md          # Entry point with frontmatter
        references/       # Detailed docs, patterns, examples
        workflows/        # Step-by-step guides (optional)
    README.md             # Plugin documentation
```

**Important**: The `skills/` directory must be at the plugin root, NOT inside `.claude-plugin/`.

## Skill Frontmatter

```yaml
---
name: skill-name              # kebab-case, max 64 chars
description: "Third-person description of what it does and when to use it"
allowed-tools:                # Optional: restrict to needed tools
  - Read
  - Grep
  - Bash
---
```

## Naming Conventions

- **kebab-case**: `zkvm-security`, not `zkVMSecurity`
- **Descriptive**: `constraint-soundness-audit`, not `csa`
- **Avoid vague names**: `helper`, `utils`, `tools`

## Required Sections

Every SKILL.md must include:

```markdown
## When to Use
[Specific scenarios where this skill applies]

## When NOT to Use
[Scenarios where another approach is better]
```

For security/audit skills, also include:

```markdown
## Rationalizations to Reject
[Common shortcuts that lead to missed findings]
```

## Content Guidelines

### Value-Add

Skills should provide guidance Claude doesn't already have:

- **Behavioral guidance over reference dumps** — Don't paste specs; teach when and how to look things up
- **Explain WHY, not just WHAT** — Include trade-offs, decision criteria, judgment calls
- **Document anti-patterns WITH explanations** — Say why something is wrong

### Content Organization

- Keep SKILL.md **under 500 lines** — split into `references/`, `workflows/`
- Use **progressive disclosure** — quick start first, details in linked files
- **One level deep** — SKILL.md links to files, files don't chain to more files

### Security Skills

For cryptographic and ZK audit skills:

- Ground patterns in real audit reports when possible
- Link to the source reports in `references/`
- Explain the trust boundary that failed
- Show what malicious input exploits the issue

## Adding a New Skill

1. Create plugin structure under `plugins/<plugin-name>/`
2. Add `SKILL.md` with required sections
3. Add symlink under `.codex/skills/` for Codex discovery
4. Register in `.claude-plugin/marketplace.json`
5. Update root `README.md` table

## Codex Compatibility

Every plugin with a `skills/` directory must have a corresponding symlink:

```sh
ln -sfn ../../plugins/<plugin-name>/skills/<skill-name> .codex/skills/<skill-name>
```

## PR Checklist

**Technical:**
- [ ] Valid YAML frontmatter with `name` and `description`
- [ ] Name is kebab-case, ≤64 characters
- [ ] All referenced files exist
- [ ] No hardcoded paths

**Quality:**
- [ ] Description triggers correctly (third-person, specific)
- [ ] "When to use" and "When NOT to use" sections present
- [ ] Examples are concrete
- [ ] Explains WHY, not just WHAT

**Documentation:**
- [ ] Plugin has README.md
- [ ] Added to root README.md table
- [ ] Registered in `.claude-plugin/marketplace.json`
- [ ] Codex symlink created under `.codex/skills/`
