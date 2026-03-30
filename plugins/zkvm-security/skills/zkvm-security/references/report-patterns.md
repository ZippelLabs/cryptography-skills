# zkVM Report Patterns

This document summarizes recurring vulnerability patterns extracted from public zkVM audit reports.

> **Source Reports**: The patterns below are derived from audit reports collected at [ZippelLabs/zkVMs-Security](https://github.com/ZippelLabs/zkVMs-Security), including audits of SP1, OpenVM, RISC Zero, Pico, and related systems.

## Report Index

| zkVM | Report | Auditor | Key Findings |
|------|--------|---------|--------------|
| SP1 v1 | sp1-kalos.md | Kalos/rkm0959 | Poseidon2 memory write, constraint omissions, padding bugs |
| SP1 v3 | sp1-v3-rkm0959.md | rkm0959 | Challenger issues, cumulative sum bugs, encoding issues |
| SP1 v4 | sp1-v4.md | rkm0959 | Interaction kind confusion, vk hash omissions |
| SP1 | sp1-cantina.pdf | Cantina | Various constraint issues |
| SP1 | sp1-veridise.pdf | Veridise | Constraint completeness |
| SP1 | sp1-zellic.pdf | Zellic | Multiple findings |
| OpenVM v1 | openvm-v1-cantina-report.pdf | Cantina | Memory arguments, scope bugs |
| OpenVM v1.1-1.4 | Various | Cantina | Incremental fixes |
| RISC Zero | risc0-hexens_zkVM.pdf | Hexens | zkVM implementation bugs |
| RISC Zero | risc0-veridise_zkVM.pdf | Veridise | Constraint issues |
| Pico | Pico-Sherlock.pdf | Sherlock | Various findings |

## Recurrent Bug Families

### 1. Statement binding and verifier metadata

Examples include:

- missing chip ordering checks in Rust verifiers
- missing `is_complete` enforcement
- verifier hashes that omit important metadata such as initial cumulative sums
- prover-controlled scope fields that let the verifier derive the wrong Fiat-Shamir transcript

What to look for:

- Is every verifier input committed to the statement?
- Can the prover alter the statement by changing metadata that is not hashed or checked?
- Are the same fields used on both the proving and verifying sides?

### 2. Local/global interaction mismatches

Examples include:

- `InteractionScope` confusion
- syscall chips that contribute to global sums but are marked local
- missing checks that cumulative sums are zero when there are no interactions
- missing propagation of underlying interaction kinds

What to look for:

- Does each chip use the correct interaction scope?
- Are local and global transitions both constrained?
- Is the same interaction kind included in hashing and accumulation?

### 3. Padding and row lifecycle bugs

Examples include:

- `send_to_table` not being forced to zero on padding rows
- selectors or registers remaining unconstrained when `is_real = 0`
- first/last-row handling bugs in stacked tables
- missing initialization of `clk` and `pc`

What to look for:

- Which values must freeze on padding rows?
- Are row transitions valid at the start and end of a table?
- Are boolean flags constrained everywhere they matter?

### 4. Memory, register, and opcode underconstraint

Examples include:

- arbitrary memory writes during Poseidon2 hashing
- load opcodes not constraining the loaded register value
- jump opcodes leaving `op_a` or `fp` underconstrained
- recursion VM register write issues in incrementing branch opcodes

What to look for:

- Does the opcode constrain all state it is responsible for?
- Is the observed memory/register value tied to the right row?
- Are branch-specific invariants enforced even when the opcode is not the common path?

### 5. Challenger and transcript soundness

Examples include:

- using the full sponge state for output
- overwriting the entire challenger state with new input
- compression built from a permutation in a way that is fine for the current system but dangerous as a generic primitive

What to look for:

- Does input observation preserve prior transcript history?
- Is output limited to the intended rate portion?
- Can the prover control more of the challenger state than intended?

### 6. Field/bit/var encoding issues

Examples include:

- combining felts into larger variables with the wrong base
- non-canonical bit decompositions
- reduction logic that is correct only if range assumptions hold

What to look for:

- Is the encoding injective in the field being used?
- Are bit decompositions canonical?
- Are the range assumptions actually enforced in-circuit?

### 7. Executor safety bugs that feed proof bugs

Examples include:

- writing through uninitialized memory in recursion executors

What to look for:

- Can unsafe host-side code corrupt the prover's internal state?
- Does the bug affect the soundness model or only implementation robustness?

## Practical Use

When reviewing a new zkVM report or codebase, start by mapping findings into one of these families. That makes it easier to ask the right follow-up questions and to spot variants of old bugs in new code.

The goal is not to memorize every past report. The goal is to recognize the shape of the failure quickly enough to test the same trust boundary from a new angle.
