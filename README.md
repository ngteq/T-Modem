# T-Modem

**T-Modem = Terminal-Modem** — A Non-profit standard|reference modem board for host stacks and terminals

**AS-IS:** no support · no warranty · [LICENSE](LICENSE) (GPLv3)

This repository’s **`main`** branch is an **index only**: releases and development branches. Product trees live on **topic branches** — see [BRANCHES.md](BRANCHES.md) / [CONTRIBUTING.md](CONTRIBUTING.md).

**Glossary:** [docs/TERMS.md](docs/TERMS.md) — uncommon technical terms and acronyms (**`main` only**).

---

## Branches

| Branch | Role |
|--------|------|
| **[`c12s24`](https://github.com/ngteq/T-Modem/tree/c12s24)** | **Active development** — **T-Modem-c12s24**: chip **1200** + software **2400**. Full hardware/docs/KiCad tree. |
| **`main`** | This page — releases + branch list + [TERMS](docs/TERMS.md) |
| *Future topic branches* | Optional; branch from `c12s24`, merge back there, then **add a row here** |

```bash
git clone git@github.com:ngteq/T-Modem.git
cd T-Modem
git checkout c12s24
```

---

## Releases (tags)

| Tag | What it is |
|-----|------------|
| **[`v0.25`](https://github.com/ngteq/T-Modem/releases/tag/v0.25)** | Hardware-only standard reference snapshot at tag time. **No** firmware. |

New releases: tag from **`c12s24`**, then update this table on **`main`**.

---

## Identity (c12s24)

| Mark | Meaning |
|------|---------|
| **c12** | Chip **1200** AFSK (TCM3105-class) |
| **s24** | Software **2400** on Pico (after HW prototype) |

Not BayCom / SER12 / PC-COM.

---

## License

[GNU GPLv3](LICENSE) · non-profit · **AS-IS**.
