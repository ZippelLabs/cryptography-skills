# ZKP Security Audit Checklist

A comprehensive checklist for auditing zero-knowledge proof implementations.

> **Source**: Adapted from [timimm/awesome-zero-knowledge-proofs-security](https://github.com/timimm/awesome-zero-knowledge-proofs-security/blob/main/check_list.md) and industry practices.

---

## 1. Base Circuit Checks

### Completeness

- [ ] All constraints correctly defined and covering all input variables
- [ ] Circuits pass correct computation and reject incorrect computation
- [ ] Each variable contributes directly or indirectly to a constraint

### Soundness

- [ ] No under-constrained signals (assigned but not constrained)
- [ ] All code paths produce equivalent constraint counts
- [ ] No signals can take arbitrary values without affecting proof validity

### Input Validation

- [ ] Input variables fall within expected ranges
- [ ] Overflow/underflow prevention on both inputs and operations
- [ ] Bit decomposition constraints are complete (all bits are 0 or 1)

### Consistency

- [ ] Multiple paths computing the same variable yield the same result
- [ ] No non-determinism in witness generation
- [ ] Padding rows properly constrained (is_real = 0 enforced)

### Zero-Knowledge Property

- [ ] Circuit doesn't leak private information via public outputs
- [ ] Intermediate values don't expose witness bits
- [ ] Hash preimages are not recoverable from commitments

---

## 2. Integration Checks

### Library Usage

- [ ] All library assumptions documented and verified
- [ ] Implicit preconditions on inputs are enforced
- [ ] High-performance libraries don't skip security checks

### Smart Contract Integration

- [ ] Verifier contract correctly validates all public inputs
- [ ] Proof freshness/uniqueness enforced (no replay)
- [ ] On-chain/off-chain data consistency verified

### Cross-Component Boundaries

- [ ] Serialization matches between prover and verifier
- [ ] Field element encoding is consistent
- [ ] Endianness assumptions are documented and correct

---

## 3. Architecture Design Checks

### Protocol Security

- [ ] Front-running prevention mechanisms in place
- [ ] Nullifier mechanism prevents double-spending (if applicable)
- [ ] Replay attacks prevented via nonces or timestamps

### Cryptographic Assumptions

- [ ] Security parameters meet minimum requirements (≥128 bits)
- [ ] Trusted setup (if any) was performed correctly
- [ ] Random oracle model assumptions are valid

---

## 4. Proving System Checks

### Fiat-Shamir Transform

- [ ] All public parameters included in transcript
- [ ] Domain separation between different protocol phases
- [ ] Transcript state properly absorbed before squeezing challenges
- [ ] No challenge reuse across different proofs

### Polynomial Arithmetic

- [ ] Trailing zeros normalized after arithmetic operations
- [ ] Degree calculations account for edge cases
- [ ] Polynomial evaluations checked at all required points

### Elliptic Curve Operations

- [ ] All points validated to be on curve and in correct subgroup
- [ ] Point-at-infinity handled correctly
- [ ] Cofactor multiplication applied where needed

---

## 5. zkVM-Specific Checks

### Guest Program

- [ ] STF implementation matches specification
- [ ] Compilation target tested thoroughly
- [ ] Precompile implementations constrained correctly

### Emulator

- [ ] ISA compliance verified via test suites
- [ ] Edge cases (overflow, division by zero) handled correctly
- [ ] Syscall implementations are secure

### Circuit

- [ ] All opcodes fully constrained
- [ ] Memory reads/writes properly ordered and constrained
- [ ] Register transitions complete

---

## 6. Code Quality Checks

### Optimization vs Security

- [ ] No redundant constraints removed without security review
- [ ] Compiler optimizations don't remove necessary checks
- [ ] Performance improvements don't compromise soundness

### Third-Party Dependencies

- [ ] Cryptographic libraries are well-audited
- [ ] No known vulnerabilities in dependencies
- [ ] License compatibility verified

### Documentation

- [ ] All assumptions documented
- [ ] Security considerations documented
- [ ] Threat model defined

---

## 7. Testing Requirements

### Unit Testing

- [ ] All constraint paths tested
- [ ] Edge cases covered (zero, max values, boundary conditions)
- [ ] Invalid witness detection verified

### Integration Testing

- [ ] End-to-end proof generation and verification
- [ ] Cross-implementation compatibility (if applicable)
- [ ] Performance under adversarial inputs

### Fuzz Testing

- [ ] Witness generation fuzzed for crashes
- [ ] Constraint satisfaction fuzzed for soundness
- [ ] Serialization fuzzed for parsing bugs

---

## Quick Reference: Common Mistakes by DSL

### Circom

- [ ] No `<--` without corresponding `===`
- [ ] Quadratic constraint enforcement
- [ ] Signal aliasing prevention
- [ ] Component instantiation correctness

### halo2

- [ ] All advice cells constrained by gates
- [ ] Copy constraints for cross-region equality
- [ ] Selector activation patterns correct
- [ ] Lookup table bounds verified

### Cairo

- [ ] Felt arithmetic bounds checked
- [ ] Storage operations revocable where needed
- [ ] Syscall return values validated

### Noir

- [ ] `assert` vs `constrain` usage correct
- [ ] Witness computation deterministic
- [ ] Array bounds enforced

### GNARK

- [ ] All frontend.Variables used in constraints
- [ ] api.AssertIs* called for all validations
- [ ] Commitment binding verified
- [ ] R1CS vs Plonk backend compatibility

### Plonky3/AIR (zkVMs)

- [ ] Interactions zeroed on padding rows (is_real = 0)
- [ ] InteractionScope (Local vs Global) correct
- [ ] Cumulative sum initialized to zero
- [ ] Segment boundary state binding

---

## Related Resources

- **Vulnerability taxonomy**: [vulnerability-taxonomy.md](vulnerability-taxonomy.md) — Detailed classification of ZKP bugs
- **Security tools**: [security-tools.md](security-tools.md) — Static analyzers, fuzzers, formal verification
- **Case studies**: [case-studies.md](case-studies.md) — Real-world vulnerability examples
- **External resources**: [external-resources.md](external-resources.md) — Courses, papers, talks, CTFs

## Skills by Bug Type

| Checklist Section | Primary Skill |
|-------------------|---------------|
| Base Circuit Checks | `circuit-soundness` |
| Cryptographic Primitives | `fiat-shamir` |
| zkVM-Specific Checks | `zkvm-security` |
| Circom Checks | `circom-audit` |
