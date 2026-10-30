export const meta = {
  name: 'pr-sweep',
  description: 'Review several PRs or diffs in parallel with the harness reviewer agent and return one ranked report',
  whenToUse: 'The user asks to review a list of PRs, branches or diffs at once. Pass args as a list of PR numbers, URLs, branches or diff ranges.',
  phases: [
    { title: 'Review', detail: 'one reviewer per PR or diff' },
    { title: 'Consolidate', detail: 'merge and rank all findings' },
  ],
}

const FINDINGS = {
  type: 'object',
  required: ['target', 'verdict', 'findings'],
  properties: {
    target: { type: 'string' },
    verdict: { type: 'string', enum: ['approve', 'approve-with-nits', 'changes-needed'] },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['severity', 'location', 'issue', 'fix'],
        properties: {
          severity: { type: 'string', enum: ['blocking', 'should-fix', 'nit'] },
          location: { type: 'string' },
          issue: { type: 'string' },
          fix: { type: 'string' },
        },
      },
    },
  },
}

const targets = Array.isArray(args) ? args : (args ? [args] : [])
if (!targets.length) {
  log('No PRs or diffs given. Pass a list such as ["#12", "#15"] or ["main..feature"].')
  return { reviews: [], report: 'nothing to review' }
}

const reviews = (await pipeline(targets, target =>
  agent(`Review ${target}. Fetch it with gh (PR) or git diff (range or branch), then review with fresh context for correctness, security, missing tests and convention breaks. Do not edit files and do not post comments.`,
    { label: `review ${target}`, phase: 'Review', agentType: 'reviewer', schema: FINDINGS })
)).filter(Boolean)

phase('Consolidate')
const report = await agent(
  `Merge these PR reviews into one report: a table of PR, verdict and blocking count, then blocking findings first across all PRs, then should-fix, then nits. Keep file:line locations. Reviews: ${JSON.stringify(reviews)}`,
  { label: 'consolidate', phase: 'Consolidate', effort: 'medium' })
return { reviews, report }
