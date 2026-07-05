# PR Repair And Merge Reference

Use this when the publish loop reaches live GitHub state, review feedback, CI failures, or merge readiness.

## Live PR State

Prefer GitHub app/plugin tools for structured PR data when available. Use local `gh` for gaps such as PR creation, edits, branch pushes, Actions logs, and merge commands.

Useful shell fallbacks:

```bash
gh pr status
gh pr view --json number,title,url,state,isDraft,headRefName,baseRefName,mergeStateStatus,reviewDecision,statusCheckRollup
gh pr checks --watch
gh pr checks
```

If `gh pr view --json` rejects a field, retry with a smaller supported field set instead of abandoning the workflow.

## Review Threads

Flat comments are not enough for review repair. Prefer thread-aware GitHub connector tools if exposed. Shell fallback:

```bash
gh pr view --json number,comments,reviews,reviewDecision,url
gh api graphql -f owner='<owner>' -f name='<repo>' -F number='<pr-number>' -f query='
query($owner:String!, $name:String!, $number:Int!) {
  repository(owner:$owner, name:$name) {
    pullRequest(number:$number) {
      reviewThreads(first:100) {
        nodes {
          id
          isResolved
          path
          line
          comments(first:20) {
            nodes { author { login } body url }
          }
        }
      }
    }
  }
}'
```

Treat unresolved review threads as the actionable unit. Patch code/docs, validate, push, then resolve only when the thread is plainly addressed or resolution is required to merge.

### Closeout Rules

- Fetch unresolved review threads before editing and again after the final push.
- Do not mark a thread resolved because you intend to fix it; resolve only after the fix is visible in the PR diff.
- If a thread points at stale docs or renamed handoff files, verify the current repo path before patching.
- If a thread is outdated but still unresolved, leave a brief rationale or resolve only when the current code/docs make the old comment non-actionable.
- If connector tools expose review-thread APIs, prefer them over flat `gh pr view` comments for final closeout.

## CI Repair

For failing checks:

```bash
gh run list --branch "$(git branch --show-current)" --limit 10
gh run view <run-id> --log-failed
```

Map each failure to one of these buckets:

- **Code regression**: patch code, add/update tests, rerun local gate.
- **Doc or generated artifact drift**: regenerate/update docs, rerun the repo gate.
- **Environment/transient**: rerun once if logs support that conclusion; do not call it transient without evidence.
- **Branch/base drift**: fetch/rebase or merge base only when safe for the branch and repo policy.

After every repair push, re-check PR checks and review state live.

## PR Body

Use or update this structure:

```markdown
## Summary
- ...

## Documentation
- ...

## Validation
- ...

## Review/CI Repair
- ...

## Merge Readiness
- ...
```

## Merge Gate

Before merging, verify:

```bash
git status --short
~/.codex/skills/github-pr-shipper/scripts/sync_local_main.sh
gh pr view --json number,url,state,isDraft,mergeStateStatus,reviewDecision,statusCheckRollup
gh pr checks
```

Required state:

- Working tree has no unstaged/staged task changes left behind.
- PR is open and non-draft.
- Required checks are success, skipped, or neutral.
- `reviewDecision` is approved or not blocking.
- No actionable unresolved review thread remains.
- Branch protection does not require a missing human action.

Merge with the repo's established method. If no method is evident and this is single-branch feature work:

```bash
gh pr merge --squash --delete-branch
```

If checks are still running but all local gates passed and GitHub allows auto-merge:

```bash
gh pr merge --auto --squash --delete-branch
```

After a successful merge, run local main sync again without asking:

```bash
~/.codex/skills/github-pr-shipper/scripts/sync_local_main.sh
```

If the current branch was deleted by the merge command, switch to `main` after sync.
