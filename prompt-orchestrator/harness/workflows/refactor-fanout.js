export const meta = {
  name: 'refactor-fanout',
  description: 'Split a refactor into independent parts, run each in its own worktree with the harness refactor agent, verify every result, and stop before any merge',
  whenToUse: 'The user asks for a large refactor or migration as a workflow. Pass args as {goal, parts: [{name, scope}], check} where check is the command that must pass.',
  phases: [
    { title: 'Refactor', detail: 'one refactor agent per part, isolated worktrees' },
    { title: 'Verify', detail: 'claim-verifier re-runs the check on each branch' },
  ],
}

const RESULT = {
  type: 'object',
  required: ['part', 'branch', 'worktree', 'commits', 'checkPassed', 'summary'],
  properties: {
    part: { type: 'string' },
    branch: { type: 'string' },
    worktree: { type: 'string' },
    commits: { type: 'array', items: { type: 'string' } },
    checkPassed: { type: 'boolean' },
    summary: { type: 'string' },
  },
}
const VERDICT = {
  type: 'object',
  required: ['part', 'verified', 'evidence'],
  properties: {
    part: { type: 'string' },
    verified: { type: 'boolean' },
    evidence: { type: 'string' },
    problems: { type: 'array', items: { type: 'string' } },
  },
}

const goal = args && args.goal
const parts = (args && args.parts) || []
const check = (args && args.check) || 'the repository test command'
if (!goal || !parts.length) {
  log('Pass {goal, parts: [{name, scope}], check}. Nothing was changed.')
  return { results: [], note: 'missing goal or parts' }
}

const results = await pipeline(parts,
  part => agent(
    `Refactor goal: ${goal}\nYour part: ${part.name}\nScope (only touch these paths): ${part.scope}\nAcceptance check: ${check} must pass.\nWork only in this worktree, commit on its branch with plain messages and no AI attribution, never merge or push. Return the branch name and worktree path.`,
    { label: `refactor ${part.name}`, phase: 'Refactor', agentType: 'refactor', isolation: 'worktree', schema: RESULT }),
  (result, part) => result && agent(
    `Verify the claims in this refactor report by re-running "${check}" inside worktree ${result.worktree} (branch ${result.branch}), and add one negative check. Report: ${JSON.stringify(result)}`,
    { label: `verify ${part.name}`, phase: 'Verify', agentType: 'claim-verifier', schema: VERDICT })
      .then(verdict => ({ ...result, verdict })),
)

log('Stopped before merge. Merging any branch needs the user\'s approval.')
return { results: results.filter(Boolean), mergeRequiresApproval: true }
