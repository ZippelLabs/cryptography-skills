# zkVM/zkEVM Threat Taxonomy

A comprehensive catalog of security issues for zero-knowledge virtual machines and zkEVMs.

> **Source**: Adapted from [Ethereum Foundation zkEVM Security Overview](https://blog.zkev.me/zkevm-security-overview/) (Jan 2025) by Cody Gunton, combined with patterns from public audit reports.

---

## Overview

This taxonomy organizes security concerns into three layers:

1. **Guest Program Layer** — Issues in the STF implementation compiled for proving
2. **Proving Layer** — Issues in the zkVM circuit, prover, and witness generation
3. **Verification Layer** — Issues in proof verification and protocol soundness

Each issue includes a severity indicator based on the EF assessment:
- 🔴 **High** — Likely vector for critical exploits
- 🟡 **Medium** — Significant concern, requires mitigation
- 🟢 **Low** — Minor concern with existing mitigations

---

## Guest Program Layer

### Issue 1: STF Implementation Bugs 🟡

**What it is:** The State Transition Function (STF) implementation may have bugs introduced during modification for zkVM compatibility or inherited from upstream.

**Why it matters:** A bug in the STF means the zkVM proves the *wrong* state transition. Even if the proof is cryptographically valid, it attests to incorrect behavior.

**What to look for:**
- Code divergence between the proven guest program and battle-tested execution clients
- Unnecessary refactoring that changes semantics
- Missing edge-case handling when adapting for constrained environments

**Mitigations:**
- Minimize code changes from production clients
- Maintain comprehensive test suites (e.g., EEST framework)
- Formal verification of compiled guest programs against EVM specs

---

### Issue 2: Compilation Target Mismatch 🔴

**What it is:** zkVMs require compilation to constrained ISAs (e.g., RV32IM) that differ from production targets (x86-64, ARM). The compiler may emit code with different semantics.

**Why it matters:** If the compiled guest program behaves differently from the original, proofs attest to different state transitions than intended.

**Real example:** Certora documented cases where LLVM optimizations produced incorrect code for unusual targets.

**What to look for:**
- Code compiled to Tier 2 or Tier 3 Rust targets (less testing)
- Use of language features with target-specific behavior
- Floating-point operations on targets without FP hardware
- Syscall assumptions that don't hold in the zkVM environment

**Mitigations:**
- Target well-tested ISAs (RV64GC has more testing than RV32IM)
- Fuzz compiled guest programs
- Validate instruction/syscall subsets in CI
- Require compiler diversity in multiproof strategies

---

### Issue 3: Custom ISA Risk 🟡

**What it is:** Some zkVMs use bespoke ISAs (e.g., Valida) designed for efficient proving but requiring custom compilers.

**Why it matters:** Custom compilers lack the extensive testing and scrutiny of mainstream compilers like GCC and LLVM.

**What to look for:**
- Non-standard instruction semantics
- Missing edge-case handling in the custom compiler
- Lack of compiler fuzzing or formal verification

**Mitigations:**
- Thorough testing and auditing of custom compilers
- Extended "time in the wild" before high-stakes deployment
- Prefer standard ISAs when possible

---

### Issue 4: Precompile Complexity 🟡

**What it is:** zkVM precompiles optimize proving for expensive operations (Keccak, modexp, elliptic curves) but add attack surface.

**Why it matters:** Each precompile is a complex circuit that must be independently verified. Bugs in precompiles can break soundness.

**What to look for:**
- Custom circuits for cryptographic operations
- Mismatch between precompile semantics and EVM precompile semantics
- Missing edge-case constraints (e.g., point-at-infinity handling)

**Mitigations:**
- Formal verification of precompile circuits
- Reduce precompile surface area via compositional approaches
- Consider "autoprecompiles" with verified generation

---

## Proving Layer

### Issue 5: Emulator Correctness 🟡

**What it is:** Each zkVM implements a custom emulator to execute the guest program. Emulator bugs lead to incorrect witness generation.

**Why it matters:** If the emulator misexecutes, the witness will be wrong, but the circuit may still accept it (under-constraint) or reject valid executions.

**What to look for:**
- Non-compliance with ISA specifications
- Missing instruction implementations
- Incorrect handling of edge cases (overflow, division by zero)

**Mitigations:**
- Run ISA compliance test suites (e.g., RISC-V Architectural Test Suite)
- Differential testing against reference emulators
- Track compliance in continuous monitoring

---

### Issue 6: Circuit Correctness 🔴

**What it is:** The zkVM circuit encodes the rules of the VM. Under-constrained circuits allow invalid executions to produce valid proofs.

**Why it matters:** This is the most critical layer. A soundness bug in the circuit can allow arbitrary state transitions to be "proven."

**Real examples:**
- SP1 v3 audits found chip_ordering not bound to proof
- OpenVM audits found InteractionScope mismatches
- zkSync Era $1.9B bug from circuit under-constraint

**What to look for:**
- Signals constrained only in some code paths
- Padding rows with is_real=0 not fully constrained
- Interaction/lookup columns not checked at boundaries
- Missing constraints on opcode side effects

**Mitigations:**
- Use static analysis tools (Circomspect, halo2-analyzer)
- Formal verification of circuit constraints
- Extensive fuzzing with property-based testing

---

### Issue 7: Witness Generation Bugs 🔴

**What it is:** The prover generates a witness (execution trace) that must satisfy circuit constraints. Bugs in witness generation can expose soundness issues or cause invalid proofs.

**Why it matters:** Witness generation involves complex deterministic computation. Non-determinism or bugs can either break soundness or cause spurious proof failures.

**What to look for:**
- Non-deterministic operations in witness generation
- Unsafe memory operations (especially in Rust)
- Mismatched assumptions between circuit and witness generator

**Real example:** SP1 audits identified unsafe Rust code writing values to uninitialized memory before proof validation.

**Mitigations:**
- Use safe abstractions for witness construction
- Validate witnesses against circuit constraints before proving
- Sanitizer-enabled fuzzing of witness generators

---

### Issue 8: Challenger/Fiat-Shamir Bugs 🔴

**What it is:** The Fiat-Shamir transform converts interactive proofs to non-interactive by deriving challenges from a transcript. Bugs allow proof manipulation.

**Why it matters:** If the challenger can be manipulated, the prover can construct proofs for false statements.

**Real examples:**
- Frozen Heart vulnerabilities in PlonK and Bulletproofs
- Nova attack from transcript binding failure
- "Last Challenge Attack" in KZG-based SNARKs

**What to look for:**
- Statement parameters not included in transcript
- Transcript state not properly absorbed before squeezing
- Domain separators missing or colliding
- Full sponge state not output when required

**Mitigations:**
- Audit transcript construction carefully
- Formal verification of Fiat-Shamir implementation
- Use well-audited cryptographic libraries

---

### Issue 9: Encoding/Serialization Bugs 🟡

**What it is:** Data must be encoded consistently when crossing boundaries (field elements, bytes, bits). Inconsistencies cause soundness issues.

**Why it matters:** Non-canonical encodings or base mismatches allow different inputs to produce the same proof or vice versa.

**What to look for:**
- Felt-to-variable conversions with wrong base
- Non-unique bit decompositions
- Endianness inconsistencies
- Missing canonicalization checks

**Mitigations:**
- Document encoding conventions explicitly
- Fuzz encode/decode roundtrips
- Verify canonicalization in circuits

---

### Issue 10: Protocol-Level Optimizations 🟡

**What it is:** Optimizations to proving (batching, aggregation, recursion) can introduce new attack surfaces.

**Why it matters:** An optimization that's correct in isolation may break soundness when composed with other components.

**What to look for:**
- Aggregation schemes that don't bind all statement parameters
- Recursive verification that doesn't check all sub-proof properties
- Batching that allows mixing of incompatible proof types

**Mitigations:**
- Formal security analysis of optimized protocols
- End-to-end testing of optimized paths
- Gradual rollout with monitoring

---

## Verification Layer

### Issue 11: Verifier Implementation Bugs 🔴

**What it is:** The verifier checks proofs. Bugs allow invalid proofs to be accepted.

**Why it matters:** The verifier is the trust anchor. If it's wrong, all security guarantees are void.

**Real examples:**
- Zcash counterfeiting vulnerability (2019)
- Multiple zkSync Era verifier issues

**What to look for:**
- Missing checks (public input validation, curve point validation)
- Integer overflow in field arithmetic
- Incorrect pairing equation checks

**Mitigations:**
- Formal verification of verifier logic
- Independent verifier implementations
- Multiproof strategies requiring multiple verifiers to agree

---

### Issue 12: Proof Malleability 🟡

**What it is:** Some proof systems allow multiple valid proofs for the same statement, which can be exploited in certain contexts.

**Why it matters:** If proofs can be transformed, replay or substitution attacks may be possible.

**What to look for:**
- Missing uniqueness constraints on proof elements
- Groth16 without proper malleability protections
- Proof identifiers that don't bind all components

**Mitigations:**
- Use proof systems with non-malleability
- Add application-level binding if needed
- Document assumptions about proof uniqueness

---

### Issue 13: Public Input Handling 🔴

**What it is:** Public inputs must be correctly bound to the proof. Errors allow proofs to be valid for unintended statements.

**Why it matters:** The public inputs define *what* is being proven. If they're not bound correctly, proofs prove nothing useful.

**What to look for:**
- Public inputs not included in Fiat-Shamir transcript
- Hash collisions in public input commitment
- Missing validation of public input format

**Mitigations:**
- Audit public input binding carefully
- Use structured public inputs with domain separation
- Verify public inputs match expected format before accepting proof

---

### Issue 14: Security Parameter Choices 🟡

**What it is:** Cryptographic security depends on parameter choices (field size, hash output size, number of rounds). Poor choices weaken security.

**Why it matters:** Parameters that are too small allow brute-force attacks. Unusual parameters may not have been analyzed.

**What to look for:**
- Field sizes below 128 bits of security
- Non-standard elliptic curves
- Reduced rounds for performance
- Missing security margin analysis

**Mitigations:**
- Use standard, well-analyzed parameters
- Document security assumptions explicitly
- Conservative parameter choices for high-stakes applications

---

## Ecosystem Layer

### Issue 15: Dependency Vulnerabilities 🟡

**What it is:** zkVMs depend on cryptographic libraries, compilers, and other infrastructure. Vulnerabilities propagate.

**What to look for:**
- Shared cryptographic libraries across multiple zkVMs
- Unaudited dependencies
- Outdated dependencies with known vulnerabilities

**Mitigations:**
- Track dependency provenance
- Diversity of implementations
- Regular dependency audits

---

### Issue 16: Unsafe Code 🔴

**What it is:** Performance-critical zkVM code often uses unsafe language features (unsafe Rust, raw C).

**Why it matters:** Unsafe code can have memory safety bugs that corrupt witness generation or break cryptographic guarantees.

**Real example:** SP1 audits found unsafe Rust writing to uninitialized memory.

**What to look for:**
- `unsafe` blocks in Rust
- Manual memory management
- FFI boundaries without proper validation

**Mitigations:**
- Minimize unsafe code
- Audit all unsafe code carefully
- Use memory sanitizers in CI

---

### Issue 17: Transpilation Bugs 🟡

**What it is:** Some zkEVM approaches transpile EVM bytecode to zkVM ISA. Bugs in transpilation break equivalence.

**What to look for:**
- Missing opcode implementations
- Incorrect stack/memory semantics
- Gas metering discrepancies

**Mitigations:**
- Differential testing against reference implementations
- Formal verification of transpiler
- Comprehensive opcode coverage testing

---

### Issue 18: Diversity and Client Concentration 🟡

**What it is:** Reliance on few zkVM implementations or few EL clients reduces resilience to bugs.

**Why it matters:** A bug in a dominant implementation affects the entire ecosystem.

**Mitigations:**
- Multiproof strategies requiring agreement from diverse implementations
- Incentivize development of alternative implementations
- Track and monitor client/prover diversity metrics

---

## Summary Table

| Issue | Layer | Severity | Primary Mitigation |
|-------|-------|----------|-------------------|
| STF Implementation Bugs | Guest | 🟡 | Testing, minimal changes |
| Compilation Target Mismatch | Guest | 🔴 | Compiler diversity, fuzzing |
| Custom ISA Risk | Guest | 🟡 | Standard ISAs preferred |
| Precompile Complexity | Guest | 🟡 | Formal verification |
| Emulator Correctness | Proving | 🟡 | Compliance testing |
| Circuit Correctness | Proving | 🔴 | Static analysis, formal methods |
| Witness Generation Bugs | Proving | 🔴 | Safe abstractions, fuzzing |
| Challenger/Fiat-Shamir Bugs | Proving | 🔴 | Transcript audits |
| Encoding/Serialization Bugs | Proving | 🟡 | Canonicalization |
| Protocol Optimizations | Proving | 🟡 | Security analysis |
| Verifier Bugs | Verification | 🔴 | Formal verification |
| Proof Malleability | Verification | 🟡 | Non-malleable schemes |
| Public Input Handling | Verification | 🔴 | Binding audits |
| Security Parameters | Verification | 🟡 | Standard parameters |
| Dependency Vulnerabilities | Ecosystem | 🟡 | Diversity, audits |
| Unsafe Code | Ecosystem | 🔴 | Minimize, audit |
| Transpilation Bugs | Ecosystem | 🟡 | Differential testing |
| Diversity/Concentration | Ecosystem | 🟡 | Multiproof strategies |

---

## Further Reading

- [SoK: What don't we know? Understanding Security Vulnerabilities in SNARKs](https://arxiv.org/pdf/2402.15293)
- [Zero-Knowledge Proof Vulnerability Analysis and Security Auditing](https://eprint.iacr.org/2024/514.pdf)
- [The Frozen Heart vulnerability in PlonK](https://blog.trailofbits.com/2022/04/18/the-frozen-heart-vulnerability-in-plonk/)
- [zk-bug-tracker](https://github.com/0xPARC/zk-bug-tracker)
- [zkbugs Dataset](https://github.com/zksecurity/zkbugs/)
