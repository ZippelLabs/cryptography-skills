# Real-World ZKP Vulnerabilities

Documented case studies from public audit reports and vulnerability disclosures.

> **Purpose**: Each case provides concrete details for understanding how vulnerabilities manifest in production code.

---

## Circuit Bugs

### Case 1: Circom-Pairing — Missing Output Check Constraint

| Field | Value |
|-------|-------|
| **Project** | circom-pairing |
| **Severity** | High |
| **Bug Class** | Assigned but Not Constrained |
| **Finder** | Veridise |
| **Status** | [Fixed](https://github.com/yi-sun/circom-pairing/pull/21) |

**Background**: The circom-pairing library implements BLS12-381 curve pairings for ZK systems. It's used to verify BLS signatures in SNARKs.

**Vulnerability**: The `CoreVerifyPubkeyG1` template uses `BigLessThan` components to validate that inputs are less than the curve prime `q`. However, the outputs of these comparisons were never constrained:

```circom
// VULNERABLE CODE
component lt[10];
for(var i=0; i<10; i++){
    lt[i] = BigLessThan(n, k);
    for(var idx=0; idx<k; idx++)
        lt[i].b[idx] <== q[idx];
}
// lt[i].out is NEVER CHECKED!
```

**Impact**: An attacker could provide inputs larger than `q` (the curve prime) or malformed big integers, potentially breaking signature verification soundness.

**Fix**:
```circom
var r = 0;
for(var i=0; i<10; i++){
    r += lt[i].out;
}
r === 10;  // All comparisons must pass
```

**Lesson**: Always constrain component outputs. A component's output signal must be connected to the constraint system, not just computed.

---

### Case 2: Scroll zkTrie — Type Truncation Allows Hash Collisions

| Field | Value |
|-------|-------|
| **Project** | Scroll zkTrie |
| **Severity** | High |
| **Bug Class** | Mismatched Types/Lengths |
| **Finder** | Trail of Bits |
| **Status** | [Fixed](https://github.com/scroll-tech/zktrie/commit/9d28429589c4703d7d20e01d82f280c37e4022a6) |

**Background**: zkTrie is Scroll's sparse binary Merkle Patricia trie used for state storage.

**Vulnerability**: The Rust FFI code casts `usize` to `c_int` without bounds checking:

```rust
// VULNERABLE CODE
impl ZkTrieNode {
    pub fn parse(data: &[u8]) -> Self {
        Self {
            trie_node: unsafe { 
                NewTrieNode(data.as_ptr(), data.len() as c_int)  // TRUNCATION!
            },
        }
    }
}
```

When `data.len()` exceeds `c_int::MAX`, the cast wraps around. Two different byte arrays with the same prefix but different padding can produce identical hashes:

```rust
// EXPLOIT
let common_prefix = /* 64 bytes */;

// Node 1: prefix + zeros (length wraps to 0)
let mut vec1 = common_prefix.to_vec();
vec1.append(&mut vec![0u8; (c_int::MAX as usize) * 2 + 2]);

// Node 2: prefix + ones (length also wraps to 0)
let mut vec2 = common_prefix.to_vec();
vec2.append(&mut vec![1u8; (c_int::MAX as usize) * 2 + 2]);

// COLLISION: node1.hash() == node2.hash()
```

**Impact**: Merkle proof forgery via hash collisions.

**Fix**: Use checked conversion:
```rust
let len = c_int::try_from(data.len())
    .expect("data length exceeds c_int::MAX");
```

**Lesson**: Always use checked type conversions, especially at FFI boundaries.

---

### Case 3: Scroll zkTrie — Missing Domain Separation

| Field | Value |
|-------|-------|
| **Project** | Scroll zkTrie |
| **Severity** | High |
| **Bug Class** | Lack of Domain Separation |
| **Finder** | Trail of Bits |
| **Status** | Fixed |

**Background**: Merkle trees require domain separation between leaf and branch nodes to prevent collision attacks.

**Vulnerability**: Branch and leaf nodes used the same hash structure:

```go
// Branch node hash
nodeHash = H(childL, childR)

// Leaf node hash  
nodeHash = H(H(1, nodeKey), valueHash)
```

An attacker could construct a leaf whose `nodeKey` and `valueHash` match a branch's `childL` and `childR`, creating a collision.

**Impact**: An attacker can substitute a branch node for a leaf node (or vice versa) in a Merkle proof, forging state proofs.

**Fix**: Use distinct domain separators:
```go
// Branch: domain = 0
branchHash = H_domain0(childL, childR)

// Leaf: domain = 1  
leafHash = H_domain1(nodeKey, valueHash)
```

**Lesson**: Always use domain separation when the same hash function processes different data types.

---

## Proving System Bugs

### Case 4: Frozen Heart — PlonK, Bulletproofs, Girault

| Field | Value |
|-------|-------|
| **Projects** | Multiple PlonK implementations, Bulletproofs, Girault |
| **Severity** | Critical |
| **Bug Class** | Fiat-Shamir Transcript Binding |
| **Finder** | Trail of Bits |
| **Date** | April 2022 |
| **Status** | Fixed in affected libraries |

**Background**: The Fiat-Shamir transform derives verifier challenges from a transcript. If public parameters aren't included, the prover can manipulate them.

**Vulnerability**: Multiple implementations didn't include the verification key or statement in the Fiat-Shamir transcript:

```rust
// VULNERABLE: vk not in transcript
let challenge = transcript.squeeze();
verify(vk, proof, challenge);
```

**Attack**:
1. Prover sees challenge derivation algorithm
2. Computes challenge for statement S
3. Finds a different verification key `vk'` that makes the same proof valid
4. Claims the proof is for `vk` instead of `vk'`

**Affected Libraries**:
- Aztec PLONK
- Zcash Halo
- gnark
- Multiple Bulletproofs implementations

**Fix**:
```rust
transcript.absorb(&vk.to_bytes());
transcript.absorb(&public_inputs);
let challenge = transcript.squeeze();
```

**Lesson**: Always absorb ALL public parameters into the Fiat-Shamir transcript before deriving challenges.

---

### Case 5: Nova Folding Scheme Soundness Break

| Field | Value |
|-------|-------|
| **Project** | Nova (Microsoft Research) |
| **Severity** | Critical |
| **Bug Class** | Fiat-Shamir Transcript Binding |
| **Finder** | zkSecurity |
| **Date** | July 2023 |
| **Status** | Fixed |

**Background**: Nova is a recursive SNARK using folding schemes for incremental computation.

**Vulnerability**: The folding step didn't properly bind the accumulated instance to the transcript. The random linear combination challenge could be manipulated.

**Impact**: Complete soundness break — proofs for false statements could be generated.

**Lesson**: Recursive proof schemes require extra care in transcript construction. Each folding step must bind ALL accumulated state.

**Reference**: [The zero-knowledge attack of the year](https://www.zksecurity.xyz/blog/posts/nova-attack/)

---

### Case 6: zkSync Era — $1.9B Soundness Bug

| Field | Value |
|-------|-------|
| **Project** | zkSync Era |
| **Severity** | Critical |
| **Bug Class** | Circuit Under-Constraint |
| **Finder** | ChainLight |
| **Date** | November 2023 |
| **Bounty** | $1.9M (potential impact) |
| **Status** | Fixed |

**Background**: zkSync Era is a zkEVM Layer 2 rollup on Ethereum.

**Vulnerability**: The zkEVM circuit had an under-constraint that allowed invalid state transitions to produce valid proofs.

**Impact**: Potential theft of all funds in the rollup ($1.9B at time of discovery).

**Lesson**: zkEVM circuits are extremely complex. Formal verification and extensive fuzzing are essential.

**Reference**: [ChainLight disclosure](https://medium.com/chainlight/uncovering-a-zk-evm-soundness-bug-in-zksync-era-f3bc1b2a66d8)

---

### Case 7: Zcash Counterfeiting Vulnerability

| Field | Value |
|-------|-------|
| **Project** | Zcash |
| **Severity** | Critical |
| **Bug Class** | Proving System Bug |
| **Finder** | Zcash team (internal) |
| **Date** | February 2019 |
| **Status** | Fixed |

**Background**: Zcash uses zk-SNARKs for private transactions.

**Vulnerability**: A bug in the Sprout circuit allowed creation of Zcash out of thin air (infinite mint).

**Impact**: If exploited, attacker could have counterfeited unlimited ZEC.

**Resolution**: Fixed without exploitation. Vulnerability existed for ~2 years before discovery.

**Lesson**: Even well-audited cryptographic systems can have critical bugs. Defense in depth and continuous review are essential.

**Reference**: [Zcash disclosure](https://electriccoin.co/blog/zcash-counterfeiting-vulnerability-successfully-remediated/)

---

## zkVM Bugs

### Case 8: SP1 Multiple Vulnerabilities

| Field | Value |
|-------|-------|
| **Project** | SP1 (Succinct) |
| **Severity** | High |
| **Bug Classes** | Multiple (statement binding, padding, unsafe code) |
| **Finders** | KALOS, rkm0959, internal |
| **Date** | January 2025 |
| **Status** | Fixed |

**Vulnerabilities Found**:

1. **Statement Binding**: `chip_ordering` not bound to proof
2. **Padding Bugs**: `is_real=0` rows not fully constrained
3. **Unsafe Code**: Memory writes before proof validation
4. **Challenger Issues**: Full sponge state output

**Reference**: [SP1 Security Update](https://blog.succinct.xyz/sp1-security-update-1-27-25/)

**Lesson**: zkVMs have unique vulnerability surfaces beyond traditional circuits.

---

## Summary: Common Patterns

| Pattern | Occurrences | Prevention |
|---------|-------------|------------|
| Assigned but not constrained | Circom-Pairing, many others | Circomspect, code review |
| Missing domain separation | Scroll zkTrie, others | Explicit domain tags |
| Fiat-Shamir binding failures | PlonK, Bulletproofs, Nova | Absorb all public params |
| Type truncation | Scroll zkTrie | Checked conversions |
| zkVM statement binding | SP1, OpenVM | Bind all metadata to proof |

---

## References

- [Trail of Bits Frozen Heart Series](https://blog.trailofbits.com/2022/04/13/part-1-coordinated-disclosure-of-vulnerabilities-affecting-girault-bulletproofs-and-plonk/)
- [Veridise Circom-Pairing Bug](https://medium.com/veridise/circom-pairing-a-million-dollar-zk-bug-caught-early-c5624b278f25)
- [zkSecurity Nova Attack](https://www.zksecurity.xyz/blog/posts/nova-attack/)
- [ChainLight zkSync Era Bug](https://medium.com/chainlight/uncovering-a-zk-evm-soundness-bug-in-zksync-era-f3bc1b2a66d8)
- [ZippelLabs zkVMs-Security Reports](https://github.com/ZippelLabs/zkVMs-Security)
