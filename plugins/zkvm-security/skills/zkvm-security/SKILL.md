---
name: zkvm-security
description: "Analyzes zkVMs and zero-knowledge proof systems for soundness, witness, transcript, recursion, and verifier bugs."
---

# zkVM Security

Use this skill when reviewing zero-knowledge virtual machines, proving systems, recursive proof pipelines, or verifier implementations.

## When to Use

Use this skill when:

- auditing a zkVM, proving system, or verifier for security flaws
- reviewing guest/host boundaries, witness generation, or public input handling
- checking constraint systems, arithmetization, or transcript construction
- validating recursion, aggregation, or proof composition logic
- comparing the intended VM semantics with the compiled circuit or execution trace

## When NOT to Use

Do not use this skill for:

- ordinary application debugging that does not involve a proof system
- basic cryptography theory questions that do not involve implementation risk
- pure performance tuning with no soundness, integrity, or verifier impact
- non-ZK smart contract auditing unless the contract is part of the proof stack

## Rationalizations to Reject

Reject these shortcuts:

- "The prover is trusted, so witness checks do not matter."
- "The circuit generator is automated, so soundness is guaranteed."
- "The verifier only checks public outputs, so host inputs are irrelevant."
- "The field is large enough, so arithmetic wraparound cannot hurt us."
- "Passing honest tests means malicious witnesses are safe."
- "Serialization is just plumbing, so it cannot affect security."

## Quick Start

1. Identify the proof stack.
   Determine the guest language, circuit backend, prover, verifier, recursion layer, and any off-chain host services.

2. Map the trust boundaries.
   Separate trusted code from untrusted inputs, witness data, public commitments, and verifier assumptions.

3. Check the arithmetic model.
   Look for field conversion bugs, modular reduction mistakes, overflow/underflow, and mismatches between VM integers and circuit field elements.

4. Inspect witness flow.
   Trace how secrets, public values, and derived values enter the circuit and how malformed witnesses are rejected.

5. Review transcript and randomness handling.
   Verify Fiat-Shamir challenge derivation, domain separation, nonces, and replay resistance.

6. Validate proof and verifier equivalence.
   Ensure the verifier checks the same statement that the prover proved, with no missing public inputs or serialization gaps.

7. Try malicious cases.
   Look for false proofs, truncated inputs, reordered fields, stale recursion data, malformed commitments, and boundary-condition failures.

## Report-Informed Patterns

Public zkVM audit reports in this repository repeatedly surface the same families of bugs:

- verifier metadata that is not bound tightly enough, such as chip ordering, `vk` hashing, or scope metadata
- padding-row logic that forgets to zero or freeze state when `is_real = 0`
- local/global interaction mismatches where the prover and verifier disagree about which statement is being proven
- memory and register transitions that are underconstrained in load, jump, or syscall paths
- transcript/challenger mistakes that expose too much state or let inputs overwrite the full sponge
- arithmetic encoding bugs in felt/var/bit conversions, especially around canonicality and modulus boundaries
- recursion-specific statement binding failures, such as missing cumulative sums or missing equality checks across cycles
- unsafe executor-side memory writes that can undermine the proof model even before circuit soundness is considered

See [report patterns](references/report-patterns.md) for concrete examples drawn from the public zkVM reports.

## Common zkVM Bug Classes

**Core constraint bugs:**
- constraint omission that lets invalid states pass
- witness malleability or unconstrained witness bytes
- incorrect guest-to-field encoding
- range-check failures that turn invalid arithmetic into valid field elements

**Protocol and transcript bugs:**
- transcript collisions or reused challenge domains
- inconsistent serialization between prover and verifier
- recursion bugs that accept a child proof for the wrong statement

**Platform-specific patterns:**

| Platform Type | Characteristic Bugs |
|---------------|---------------------|
| **STARK-based (SP1, RISC Zero)** | AIR constraint evaluation skips, padding row handling, interaction scope confusion |
| **Memory argument** | Timestamp ordering, initialization state, read-after-write semantics |
| **Continuations** | Segment boundary binding, deferred proof ordering, cross-segment state |
| **Syscalls/precompiles** | Unconstrained host outputs, precompile semantic mismatches |

See [platform comparison](references/platform-comparison.md) for SP1 vs RISC Zero vs OpenVM architectural differences.

## What Good Findings Look Like

Strong findings explain:

- the exact assumption that breaks
- the path from attacker-controlled input to invalid proof acceptance
- why honest-path tests miss the issue
- the security impact on the system using the zkVM

See [the audit workflow reference](references/zkvm-audit-workflow.md) for a more detailed checklist.

## Reference Documents

### zkVM-Specific

| Document | Description |
|----------|-------------|
| [Threat Taxonomy](references/threat-taxonomy.md) | 18 security issues organized by layer (guest, proving, verification) |
| [Report Patterns](references/report-patterns.md) | Vulnerability patterns extracted from public zkVM audits |
| [Audit Workflow](references/zkvm-audit-workflow.md) | Step-by-step checklist for zkVM security reviews |

### Shared Resources

| Document | Description |
|----------|-------------|
| [Vulnerability Taxonomy](../../../shared/vulnerability-taxonomy.md) | Comprehensive ZKP bug classification |
| [Security Tools](../../../shared/security-tools.md) | Circomspect, Picus, halo2-analyzer, etc. |
| [Audit Checklist](../../../shared/audit-checklist.md) | Universal ZKP security checklist |
| [External Resources](../../../shared/external-resources.md) | Courses, papers, talks, CTFs |
