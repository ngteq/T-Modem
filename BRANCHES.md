# Branch model (settled)

**GitHub:** keep this layout. Do **not** dump product trees onto `main`.

| Branch / tag | Role |
|--------------|------|
| **`main`** | **Index only** — releases, branch list, [docs/TERMS.md](docs/TERMS.md). No active product tree. |
| **`c12s24`** | **Active product tree** — T-Modem-c12s24 (chip 1200 + software 2400). Checkout this to build/docs/KiCad. |
| **`v0.25`** (tag) | Settled hardware-only snapshot at tag time. |
| **Future topic branches** | Optional (`feature/…`, `docs/…`). Branch from **`c12s24`** (or from a release tag). Merge back into **`c12s24`**. Do **not** merge product code into `main`. |

## Operator workflow

```bash
git clone git@github.com:ngteq/T-Modem.git
cd T-Modem
git checkout c12s24          # daily work
# optional:
git checkout -b feature/foo  # from c12s24
```

When a release is ready: tag from `c12s24` (or a release commit). Update the **`main`** README tables only (branch list / new tag links). Keep **[docs/TERMS.md](docs/TERMS.md)** on **`main` only**.

## Rules

| Do | Don't |
|----|-------|
| Develop on **`c12s24`** (or short-lived branches off it) | Commit hardware/firmware into **`main`** |
| Keep **`main`** as portal + TERMS glossary | Make `main` the working product tree again |
| Add future branches to the **`main`** branch table when they exist | Orphan long-lived forks without listing on `main` |
| Prefer wording **baseline** / **settled** | Overuse *freeze* in operator-facing prose |

**AS-IS** · GPLv3 · standard reference only.
