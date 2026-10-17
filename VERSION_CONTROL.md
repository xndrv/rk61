# Version control

## Repository layout

`/home/xander/rk61-recovery/` is the Git repository; the branch is `main`.
`smk/` is **ordinary tracked firmware source**, not a submodule or nested repo.
The initial checkpoint captures the working layout-v5 state. Earlier development
was not committed; Git cannot recreate those edits retroactively. Preserved
source snapshots and firmware artifacts provide the available earlier milestones.

SMK provenance: https://github.com/karstx/smk, original checkout commit
`69373bbb633bd1159f4541f486ff7506563a38ec`. Its license and upstream files are
preserved under `smk/`. The old checkout's Git metadata was moved, not deleted,
to `.git/smk-upstream.git`; its HEAD and pre-migration status are saved in
`.git/smk-upstream-HEAD.txt` and `.git/smk-original-status.txt`. This local metadata
backup is not part of a future clone; upstream URL/commit above are tracked.

## Tracked

- Firmware source, Meson definitions, upstream docs/tests/tools and license.
- Project instructions, handoff/analysis/keymap notes, Python tests and helpers.
- Corne layout export and matrix information.
- Reviewed recovery firmware, checksums and source snapshots in `known-working/`.
  Layout v5 is preserved as `known-working/layout-v5.bin`, `.hex`, source archive
  and its own SHA-256 manifest. Initial working tag: `working-layout-v5`.

## Deliberately not tracked

Shared rules are in `.gitignore`:

- Extracted `toolchain/`, `venv/`, build directories, Cargo targets and caches.
- Generated root `candidate-*.bin/.hex` and duplicate old `rk61-*.bin` outputs.
- Device-specific `stock-*.bin`, `stock.asm`, and `radio.asm`.
- `known-working/baseline-all-modes-handoff.tar.gz`, because it embeds those stock
  dumps/disassemblies. The pure source snapshots and application images remain tracked.
- Environment secrets/private keys and temporary editor/OS files.

These files are **not deleted**. Keep separate offline backups of stock dumps
and the old handoff archive: a clone of this repo will not contain them. Existing
integrity manifests may reference local-only files; verify them from the original
working directory with those files available.

Machine/session-specific exclusions live in `.git/info/exclude`, including the
current `smk/.clangd` (absolute machine-local SDK paths), IDE settings, agent state,
`scratch/`, and `local-notes/`. This file is local Git metadata, not cloned.
The editor config does not control the actual SDCC build.

`.gitattributes` prevents line-ending conversion of tested firmware and archives,
especially `.hex` files whose exact byte checksums must remain unchanged.

## Recording changes

Run Git from this root (Git also resolves here when run inside `smk/`):

```sh
git status --short
git diff
# After the appropriate build/tests:
git add <the-changed-files>
git diff --cached --stat
git commit -m "Describe the completed change"
git log --oneline -5
```

Git notices working-tree edits, but **history requires commits**; there is no
per-keystroke autosave or automatic background committer. Project instructions
ask the coding agent to make a focused commit after each completed, validated
change unless told otherwise, without including unrelated edits or pushing.

To verify tracked files: `git ls-files`. To explain an ignored path:
`git check-ignore -v <path>`. Do not force-add caches, secrets or raw stock dumps.
Place a reviewed recovery candidate under a new name in `known-working/` when it
needs preservation, never over an existing tested image.

## Remote backup

**No remote is configured and nothing was uploaded or pushed.** This is currently
a local repository, not protection against disk failure. Configure your own
(preferably private, until recovery artifacts are reviewed) remote separately;
never use the original SMK upstream as the push destination for this project.
