# zkVM Security Skill

A comprehensive skill for auditing zero-knowledge virtual machines and related proving systems.

## Overview

This skill helps security researchers and auditors identify vulnerabilities in zkVM implementations. It covers:

- **Constraint soundness** — Missing or incorrect AIR constraints that allow invalid state transitions
- **Witness handling** — Malleability, unconstrained bytes, and improper validation
- **Transcript security** — Fiat-Shamir challenges, domain separation, and challenger state
- **Memory arguments** — Initialization, finalization, and cross-shard consistency
- **Recursion** — Statement binding, cumulative sums, and proof composition
- **Verifier correctness** — Public input handling and metadata binding

## Report-Informed Patterns

This skill is informed by public audit reports from major zkVM implementations:

| zkVM | Auditors | Key Bug Classes |
|------|----------|-----------------|
| SP1 | Kalos, Veridise, Zellic, Cantina | Constraint omission, challenger issues, interaction scope bugs |
| OpenVM | Cantina | Memory arguments, padding row bugs, scope mismatches |
| RISC Zero | Hexens, Veridise | Verifier metadata, encoding issues |
| Pico | Sherlock | Constraint completeness |

See [references/report-patterns.md](skills/zkvm-security/references/report-patterns.md) for detailed patterns extracted from these reports.

## Usage

This skill activates when you're working on:

- zkVM codebases (SP1, RISC Zero, OpenVM, Pico, Jolt, etc.)
- STARK/SNARK proving systems
- Recursive proof pipelines
- On-chain verifier contracts
- Circuit constraint implementations

## Quick Start

1. **Map the architecture** — Identify guest, prover, verifier, and recursion layers
2. **Review constraints** — Check AIR `eval()` functions for completeness
3. **Trace witness flow** — Follow data from host inputs to circuit values
4. **Check padding** — Verify `is_real = 0` rows are properly constrained
5. **Test malicious inputs** — Try to construct false proofs

## Related Resources

- [ZippelLabs/zkVMs-Security](https://github.com/ZippelLabs/zkVMs-Security) — Source audit reports and checklists
- [SP1 Security Advisories](https://github.com/succinctlabs/sp1/security/advisories)
- [Plonky3 Documentation](https://github.com/Plonky3/Plonky3)
