# zkVM Platform Comparison

Architectural differences between major zkVM implementations and their security implications.

---

## Architecture Overview

| zkVM | Proof System | Memory Model | Recursion | ISA |
|------|--------------|--------------|-----------|-----|
| **SP1** | Plonky3 (STARK) | Timestamp-based | STARK→Groth16 | RISC-V RV32IM |
| **RISC Zero** | Custom STARK | Address-based | STARK→STARK | RISC-V RV32IM |
| **OpenVM** | Plonky3 + extensions | Timestamp-based | Configurable | RISC-V RV32IM |
| **Jolt** | Lasso/Jolt | N/A (stateless) | SNARK-based | RISC-V RV32I |
| **Valida** | STARK | Custom | STARK-based | Custom ISA |

---

## Security Implications by Feature

### 1. Proof System Backend

#### Plonky3-based (SP1, OpenVM)

Uses AIR constraints with interaction arguments (logup).

**Common bugs:**
- `send_table` / `receive_table` not zeroed on padding rows
- `InteractionScope` confusion (Local vs Global)
- Cumulative sum not initialized to zero
- Interaction kind not bound to verifier hash

**What to audit:**
```rust
// Check all interaction calls handle is_real = 0
fn eval(&self, builder: &mut Builder) {
    // BAD: interaction sent unconditionally
    builder.send(AirInteraction::new(...));
    
    // GOOD: interaction gated on is_real
    builder.when(is_real).send(AirInteraction::new(...));
}
```

#### Custom STARK (RISC Zero)

Custom constraint system with sessions/segments.

**Common bugs:**
- Verifier metadata (cycle count, po2) not bound to statement
- Memory argument initialization not checked
- Receipt serialization/deserialization mismatches

#### Jolt/Lasso Lookups

Lookup-centric design using Lasso arguments.

**Common bugs:**
- Lookup table initialization
- Multiset check failures
- Read-only memory commitment binding

---

### 2. Memory Arguments

#### Timestamp-based (SP1, OpenVM)

Memory ordered by `(addr, timestamp)` pairs.

**Security concerns:**
- Clock/timestamp must be strictly increasing
- Initialization state (all memory = 0) must be enforced
- Finalization requires timestamp exhaustion check

**What to audit:**
```rust
// Memory chip must verify:
// 1. First access to each address reads 0
// 2. Timestamps are strictly increasing per address
// 3. All timestamps are consumed (no gaps)
```

#### Address-based (RISC Zero)

Memory ordered by address, with read/write sequencing.

**Security concerns:**
- Read-before-write vs read-after-write semantics
- Multiple writes to same address must be ordered
- Address range must be validated

---

### 3. Recursion Strategies

#### STARK → SNARK (SP1 default)

Wraps final STARK proof in Groth16 for efficient on-chain verification.

**Security concerns:**
- Public input binding between STARK and SNARK layers
- Trusted setup parameters for Groth16
- Proof malleability in SNARK layer

#### STARK → STARK (RISC Zero, OpenVM option)

Purely STARK-based recursion.

**Security concerns:**
- Recursive verifier circuit correctness
- Accumulation of verification errors across levels

---

### 4. Continuations and Sharding

#### SP1 Continuations

Long programs split into segments, proven separately.

**Security concerns:**
- Segment boundary state commitment
- Deferred proof collection and ordering
- Cross-segment register/memory consistency

**What to audit:**
```rust
// Each segment must commit to:
// 1. Initial register state
// 2. Initial memory state hash
// 3. Final register state
// 4. Final memory state hash
// 5. Segment index in sequence
```

#### RISC Zero Sessions

Similar segment-based proving.

**Security concerns:**
- Session finalization checks
- Journal (public output) binding across segments

---

### 5. Syscalls and I/O

#### Host-Guest Boundary (All platforms)

Guest programs call host functions for expensive ops (e.g., SHA-256, secp256k1).

**Security concerns:**
- Syscall output must be constrained in circuit
- Prover can lie about syscall results if not checked
- Side-channel: syscall count/timing may leak information

**Common bug:** Syscall output used as unconstrained witness.

```rust
// BAD: syscall result not verified
let hash = syscall_sha256(data);
// Prover could return any value!

// GOOD: syscall result verified in circuit
let hash = syscall_sha256(data);
// Circuit constrains: SHA256(data) == hash
```

#### SP1-specific: Precompiles

Native acceleration for crypto ops (Keccak, secp256k1, BN254).

Each precompile is a complex circuit requiring independent verification.

---

### 6. ISA Differences

#### RISC-V RV32IM (SP1, RISC Zero, OpenVM, Jolt)

- Standard 32-bit RISC-V with integer multiply/divide
- Well-tested compiler toolchain (LLVM/GCC)
- Security: Compiler bugs less likely but still possible

#### Custom ISA (Valida)

- Designed specifically for proving efficiency
- Custom compiler required
- Security: Higher compiler bug risk, less battle-tested

---

## Platform-Specific Auditing Focus

### When Auditing SP1

1. ✓ Check `send_table`/`receive_table` zeroing on padding rows (`is_real = 0`)
2. ✓ Verify `InteractionScope` correctness for all chips
3. ✓ Review cumulative sum initialization and finalization
4. ✓ Check deferred proof verification logic
5. ✓ Validate timestamp ordering in memory chip
6. ✓ Audit each precompile circuit independently

### When Auditing RISC Zero

1. ✓ Check verifier metadata binding (cycle count, segments)
2. ✓ Verify memory argument initialization
3. ✓ Review receipt (proof) serialization/deserialization
4. ✓ Check journal commitment binding
5. ✓ Audit session finalization logic

### When Auditing OpenVM

1. ✓ All SP1 checks (Plonky3-based)
2. ✓ Custom extension chips (if any)
3. ✓ Configurable recursion correctness
4. ✓ Memory argument customizations

### When Auditing Jolt

1. ✓ Lookup table initialization
2. ✓ Multiset argument soundness
3. ✓ Read-only memory commitment

---

## Common Cross-Platform Bugs

Despite architectural differences, some bugs appear everywhere:

| Bug Pattern | Description | Prevalence |
|-------------|-------------|------------|
| **Padding rows** | `is_real = 0` rows not constrained | Very High |
| **Public input binding** | Verifier doesn't check all statement parameters | High |
| **Transcript construction** | Challenge derivation missing domain separation | High |
| **Encoding bugs** | Field element ↔ bytes conversion inconsistencies | Medium |
| **Unsafe Rust** | Memory safety bugs in performance-critical code | Medium |
| **Syscall validation** | Host outputs accepted without constraint | High |

---

## References

- [SP1 Documentation](https://docs.succinct.xyz/)
- [RISC Zero Documentation](https://dev.risczero.com/)
- [OpenVM Documentation](https://github.com/openvm-org/openvm)
- [Jolt Documentation](https://jolt.a16zcrypto.com/)
- [Plonky3 Technical Docs](https://github.com/Plonky3/Plonky3)
- [ZippelLabs zkVMs-Security Reports](https://github.com/ZippelLabs/zkVMs-Security)
