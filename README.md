# cryptography-skills

A comprehensive AI skills marketplace for zero-knowledge proof security — circuits, proving systems, zkVMs, and DSL-specific auditing.

> **Bug Pattern Sources**:
> - [ZippelLabs/zkVMs-Security](https://github.com/ZippelLabs/zkVMs-Security) — Public zkVM audit reports
> - [timimm/awesome-zero-knowledge-proofs-security](https://github.com/timimm/awesome-zero-knowledge-proofs-security) — Vulnerability classification

## Available Skills

### By Layer

| Layer | Skill | Description |
|-------|-------|-------------|
| **Circuit (Frontend)** | [circuit-soundness](plugins/zkp-circuits/skills/circuit-soundness/) | Under-constraint detection across Circom, halo2, Noir, GNARK |
| **Proving System (Backend)** | [fiat-shamir](plugins/zkp-proving-systems/skills/fiat-shamir/) | Transcript binding, domain separation, challenge derivation |
| **zkVM** | [zkvm-security](plugins/zkvm-security/skills/zkvm-security/) | SP1, RISC Zero, OpenVM emulator, circuit, witness bugs |

### By DSL

| DSL | Skill | Description |
|-----|-------|-------------|
| **Circom** | [circom-audit](plugins/circom-security/skills/circom-audit/) | Signal constraints, component usage, snarkjs integration |

### Shared References

| Resource | Description |
|----------|-------------|
| [vulnerability-taxonomy.md](shared/vulnerability-taxonomy.md) | Comprehensive bug classification by layer |
| [security-tools.md](shared/security-tools.md) | Circomspect, Picus, halo2-analyzer, etc. |
| [audit-checklist.md](shared/audit-checklist.md) | Step-by-step security review checklist |
| [external-resources.md](shared/external-resources.md) | Courses, papers, talks, CTFs |

## Installation

### Claude Code Marketplace

```sh
/plugin marketplace add ZippelLabs/cryptography-skills
```

Then browse and install:

```sh
/plugin menu
```

### Codex

```sh
git clone https://github.com/ZippelLabs/cryptography-skills.git ~/.codex/cryptography-skills
~/.codex/cryptography-skills/.codex/scripts/install-for-codex.sh
```

This installs symlinks under `~/.codex/skills/`.

### Local Development

```sh
cd /path/to/parent  # parent directory of the repo
/plugins marketplace add ./cryptography-skills
```

## Repository Structure

```
cryptography-skills/
├── plugins/
│   ├── zkp-circuits/              # Circuit-level security
│   │   └── skills/circuit-soundness/
│   ├── zkp-proving-systems/       # Backend proving bugs
│   │   └── skills/fiat-shamir/
│   ├── zkvm-security/             # zkVM-specific
│   │   └── skills/zkvm-security/
│   └── circom-security/           # Circom DSL
│       └── skills/circom-audit/
├── shared/                        # Cross-cutting references
│   ├── vulnerability-taxonomy.md
│   ├── security-tools.md
│   ├── audit-checklist.md
│   └── external-resources.md
└── .codex/skills/                 # Codex discovery symlinks
```

## Scope

This marketplace focuses on **cryptographic implementation security**:

- Zero-knowledge proof systems (zkVMs, SNARKs, STARKs)
- Circuit constraint correctness (soundness, completeness, ZK property)
- Proving system backends (Fiat-Shamir, polynomial, curve crypto)
- DSL-specific patterns (Circom, halo2, Cairo, Noir)
- Protocol-level design (front-running, replay, nullifiers)

**Not in scope**: General smart contract auditing, web app security, non-ZKP cryptography.

## Roadmap

- [ ] **Cairo security** — StarkNet/Cairo VM-specific patterns
- [ ] **halo2 security** — Lookup tables, copy constraints, selectors  
- [ ] **Noir security** — Aztec's DSL patterns
- [ ] **Curve crypto** — Point validation, cofactor attacks
- [ ] **Polynomial bugs** — FFT, evaluation, commitment issues

## Contributing

See [CLAUDE.md](CLAUDE.md) for contribution guidelines.

## Related Resources

- [ZippelLabs/zkVMs-Security](https://github.com/ZippelLabs/zkVMs-Security) — Public zkVM audit reports
- [trailofbits/skills](https://github.com/trailofbits/skills) — Trail of Bits security skills
- [timimm/awesome-zero-knowledge-proofs-security](https://github.com/timimm/awesome-zero-knowledge-proofs-security) — Bug taxonomy
- [zkSecurity/zkbugs](https://github.com/zksecurity/zkbugs/) — Reproducible vulnerability dataset
