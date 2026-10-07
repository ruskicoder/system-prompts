---
name: deployment
description: Deploy applications, configure cloud hosting targets (Vercel, Netlify, GitHub Pages, S3), manage build pipelines, and verify post-deployment health. Trigger with "deploy app", "publish release", "setup hosting", or when configuring production rollout workflows.
argument-hint: "<target platform or service>"
---

# Skill: Deployment

## Purpose
Deploy applications, expose services, and manage release workflows.

## Tools Required
- Deployment CLI tools (Netlify, Vercel, gh-pages, etc.)
- Shell commands
- Port exposure tools

## General Principles
- Read deployment config before attempting to deploy
- Ensure all required files exist before deployment
- Verify build succeeds before deploy
- Check deployment status after deploying
- NEVER auto-deploy to production without user confirmation

## Deployment Workflow

### Pre-Deployment Checklist
- [ ] Read deployment configuration (if exists)
- [ ] Verify all source files are present
- [ ] Build succeeds locally
- [ ] Environment variables configured
- [ ] Required service accounts / API keys available

### Common Platforms

| Platform | Tool | Setup |
|----------|------|-------|
| GitHub Pages | `gh-pages` package or Actions | Push to gh-pages branch |
| Netlify | Netlify CLI / manual | Connect repo + configure build |
| Vercel | Vercel CLI | `vercel` for project setup |
| Static hosting | rsync / scp / s3 | Copy build output to host |

### Deployment Steps
1. Build the project
2. If deploying new site: use project_id empty
3. If updating existing site: use existing project_id
4. Run deploy command
5. Check deployment status
6. Provide access URL to user

## Service Exposure
- For temporary services: expose local ports
- For permanent services: deploy to cloud hosting
- Provide access links after deployment
- Monitor deployed applications

## PR/MR Workflow
For implementation tasks in collaborative projects:
1. Create feature branch from updated main
2. Make changes
3. Commit with descriptive message
4. Push branch
5. Create Pull/Merge Request
6. Include summary of changes in PR description

## Environment Configuration
- Use environment variables for config
- Provide .env.example file with placeholder values
- Document required environment variables
- Never commit real secrets to version control

## Rollback
- Know how to roll back a deployment
- For git-based deploys: revert commit and redeploy
- For platform deploys: use platform's rollback feature
- Always keep previous deployment artifacts
