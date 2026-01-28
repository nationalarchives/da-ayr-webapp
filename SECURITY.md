# Security Policy

## Automated Workflows and Pull Request Approval

This repository uses automated workflows for specific, limited purposes. Understanding these automations and their boundaries is critical for maintaining security.

### Auto-Approval Policy

#### What Gets Auto-Approved?

**ONLY** Dependabot pull requests for minor and patch dependency updates are automatically approved and merged.

Specifically, auto-approval applies when ALL of these conditions are met:
1. The PR is created by `dependabot[bot]`
2. The repository is `nationalarchives/da-ayr-beta-webapp`
3. The update type is `version-update:semver-minor` OR `version-update:semver-patch`

#### What Requires Human Review?

**ALL** other pull requests require human review and approval, including:
- Major version dependency updates
- Code changes from contributors
- AI-generated code changes
- Configuration changes
- Documentation changes
- Workflow modifications
- Any PR not created by Dependabot

### Why These Restrictions?

- **Dependabot Only**: Dependabot PRs are automated, well-tested dependency updates that undergo security scanning
- **Minor/Patch Only**: These updates typically contain bug fixes and minor improvements without breaking changes
- **Major Versions Excluded**: Major version updates can introduce breaking changes and require human evaluation
- **Human Code Requires Review**: All human and AI-generated code must be reviewed for quality, security, and correctness

### Modifying Auto-Approval Workflows

⚠️ **CRITICAL**: Changes to workflows that perform auto-approval (`.github/workflows/dependabot_approve_and_enable_auto_merge_for_minor_and_patch_prs.yml`) require:

1. **Team Discussion**: Propose changes in a team meeting or discussion thread
2. **Security Review**: Ensure changes maintain or strengthen security boundaries
3. **Documented Rationale**: Clearly document why the change is necessary
4. **Never Remove Safeguards**: Do not remove or weaken these checks:
   - User login verification (`dependabot[bot]`)
   - Repository verification
   - Update type restrictions

### Reporting Security Issues

If you discover a security vulnerability in this repository:

1. **Do NOT** create a public issue
2. Contact The National Archives security team directly
3. Provide details about the vulnerability and potential impact
4. Allow time for the team to address the issue before public disclosure

### AI Agent Policy

When AI agents (such as GitHub Copilot or other automation tools) are used to generate code changes:

- AI-generated code is **NEVER** auto-approved or auto-merged
- All AI-generated changes must be reviewed by a human maintainer
- AI agents should not modify auto-approval workflows without explicit human instruction and review
- AI agents must adhere to the principle of minimal changes

## Security Best Practices

When contributing to this repository:

1. **Sign Your Commits**: All commits must be signed (see [CONTRIBUTING.md](CONTRIBUTING.md))
2. **Keep Dependencies Updated**: Regularly review and update dependencies
3. **Run Security Scans**: Use the provided tools to scan for vulnerabilities
4. **Follow Coding Standards**: Adhere to the project's linting and testing requirements
5. **Review Dependencies**: Check new dependencies for security issues before adding them

## Security Updates

This policy is reviewed periodically and updated as needed to reflect current best practices and team decisions.

Last updated: 2026-01-28
