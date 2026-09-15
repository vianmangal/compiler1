# Consolidate Phase 1 on main

1. Restore the LLVM prototype and matching P01 planning from codex/iris-phase1; retain the proposal PDF, quick-task history, and existing commits. The prototype branch is already an ancestor, so a normal merge alone would not restore its removed files.
2. Run the unit tests, publish the consolidated main branch, and verify matching remote revisions.
3. Delete the remote prototype branch and detach its clean local worktree before deleting that local branch. Keep the worktree files recoverable; rename local master to main.

Verification: 21 unit tests pass, GitHub remains private with only main, and the proposal remains tracked. Preserve the unstaged local PDF deletion.
