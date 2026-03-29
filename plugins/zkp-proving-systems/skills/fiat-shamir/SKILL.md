---
name: fiat-shamir
description: "Audits Fiat-Shamir transform implementations for transcript binding, domain separation, and challenge derivation bugs."
---

# Fiat-Shamir Transform Security

Use this skill when reviewing the Fiat-Shamir transform — the mechanism that converts interactive proofs to non-interactive by deriving challenges from a transcript.

> **SoK Context**: Backend layer has 23 vulnerabilities (16% of total), with "Unsafe Verifier" being the most common (16 bugs). Frozen Heart and other Fiat-Shamir bugs affected multiple production systems including PlonK, Bulletproofs, and Nova. See [SoK Classification](../../../shared/sok-vulnerability-classification.md).

## When to Use

Use this skill when:

- auditing SNARK/STARK prover and verifier implementations
- reviewing transcript construction and challenge derivation
- checking that public parameters are bound to the proof
- validating domain separation between protocol phases
- inspecting recursive proof verification where transcripts nest

## When NOT to Use

Do not use this skill for:

- circuit-level bugs (under-constraints) — see `circuit-soundness` skill
- zkVM-specific implementation bugs — see `zkvm-security` skill
- general hash function weakness unrelated to transcripts
- smart contract bugs not involving proof verification

## Rationalizations to Reject

Reject these shortcuts:

- "The prover is trusted, so transcript binding doesn't matter."
- "We hash the proof at the end, so intermediate values don't need binding."
- "The verifier checks everything, so the prover can't cheat."
- "Domain separation is just for cleanliness, not security."
- "The transcript is deterministic, so there's no attack surface."
- "This is the same as the paper, so it must be correct."

## Bug Classes

### 1. Frozen Heart (Missing Statement Binding)

The most critical Fiat-Shamir bug. Public parameters or the statement are not included in the transcript, allowing the prover to choose them after seeing the challenge.

**What it is:** The challenge is derived without binding the verification key, public inputs, or other statement parameters.

**Real-World Examples:**
- PlonK implementations (Trail of Bits, 2022)
- Bulletproofs implementations (Trail of Bits, 2022)
- Girault protocol (Trail of Bits, 2022)
- Nova recursive proofs (zkSecurity, 2023)

**What to look for:**
```rust
// BUG: vk not included in transcript
let challenge = transcript.squeeze_challenge();
verifier.verify(vk, proof, public_inputs, challenge);

// FIXED: bind vk before deriving challenge
transcript.absorb(&vk);
transcript.absorb(&public_inputs);
let challenge = transcript.squeeze_challenge();
```

**Attack:** The prover:
1. Sees the challenge derivation algorithm
2. Chooses a favorable verification key
3. Constructs a proof that validates with that key
4. Claims the proof is valid for the "official" key

### 2. Missing Domain Separation

Different protocol phases or different protocols use the same transcript domain, allowing cross-protocol attacks.

**What it is:** The transcript doesn't differentiate between:
- Different rounds of the same protocol
- Different protocols using the same hash
- Different message types

**What to look for:**
```rust
// BUG: no domain separator
transcript.absorb(commitment_1);
let challenge_1 = transcript.squeeze_challenge();
transcript.absorb(commitment_2);
let challenge_2 = transcript.squeeze_challenge();

// FIXED: domain separators
transcript.absorb(b"round-1");
transcript.absorb(commitment_1);
let challenge_1 = transcript.squeeze_challenge();
transcript.absorb(b"round-2");
transcript.absorb(commitment_2);
let challenge_2 = transcript.squeeze_challenge();
```

**Attack:** The prover can construct messages that work for multiple interpretations.

### 3. Transcript State Leakage

The full internal state of the sponge/hash is exposed, breaking security assumptions.

**What it is:** Sponges like Poseidon have a capacity portion that should never be output. Outputting the full state enables attacks.

**What to look for:**
```rust
// BUG: outputting full sponge state
let challenge = sponge.state.clone();  // Includes capacity!

// FIXED: squeeze only the rate portion
let challenge = sponge.squeeze();  // Only rate output
```

### 4. Challenge Reuse

The same challenge value is used in different contexts.

**What it is:** A challenge derived once is reused for multiple purposes.

**What to look for:**
```rust
// BUG: same challenge for different checks
let challenge = transcript.squeeze_challenge();
check_polynomial_1(challenge);
check_polynomial_2(challenge);  // Should use fresh challenge!

// FIXED: fresh challenges
let challenge_1 = transcript.squeeze_challenge();
check_polynomial_1(challenge_1);
let challenge_2 = transcript.squeeze_challenge();
check_polynomial_2(challenge_2);
```

### 5. Prover/Verifier Transcript Mismatch

The prover and verifier construct different transcripts.

**What it is:** The prover absorbs data in a different order or with different encoding than the verifier expects.

**What to look for:**
```rust
// PROVER
transcript.absorb(&commitment);
transcript.absorb(&evaluation);

// VERIFIER (BUG: different order)
transcript.absorb(&evaluation);
transcript.absorb(&commitment);
```

### 6. Insufficient Challenge Entropy

The challenge space is too small.

**What it is:** Challenges are truncated or taken from a small field.

**What to look for:**
```rust
// BUG: only 32 bits of challenge
let challenge = transcript.squeeze_challenge() & 0xFFFFFFFF;

// FIXED: full field element challenge
let challenge = transcript.squeeze_challenge();  // 254+ bits
```

### 7. Last Challenge Attack

The final challenge in a multi-round protocol is not properly bound to the complete proof state.

**What it is:** In protocols with multiple challenge rounds, the last challenge may skip binding critical data committed in earlier rounds.

**Real-World Examples:**
- KZG-based SNARKs with batch openings
- PlonK's final evaluation challenge
- Recursive proof verification where outer proof challenge doesn't bind inner proof data

**What to look for:**
```rust
// BUG: last challenge doesn't bind all commitments
transcript.absorb(&commitment_1);
let challenge_1 = transcript.squeeze_challenge();
transcript.absorb(&commitment_2);
let challenge_2 = transcript.squeeze_challenge();
// Missing: final binding of all data before last use
verifier.verify_final(challenge_2);  // vulnerable!

// FIXED: bind all state before final challenge
transcript.absorb(&commitment_1);
let challenge_1 = transcript.squeeze_challenge();
transcript.absorb(&commitment_2);
transcript.absorb(&all_prior_commitments);  // re-bind all prior state
let final_challenge = transcript.squeeze_challenge();
verifier.verify_final(final_challenge);
```

**Reference:** [The Last Challenge Attack](https://eprint.iacr.org/2024/398)

## Weak vs. Strong Fiat-Shamir

Understanding this distinction is critical for security:

| Type | Challenge Derivation | Security |
|------|---------------------|----------|
| **Weak** | `H(protocol_messages)` | Vulnerable to statement manipulation |
| **Strong** | `H(vk ‖ statement ‖ protocol_messages)` | Secure against Frozen Heart |

**Rule:** Always use Strong Fiat-Shamir. If the paper says "Fiat-Shamir" without clarifying, assume Strong Fiat-Shamir is required.

## Quick Start Workflow

> **Note on API Terminology:** Code examples use generic `.absorb()` and `.squeeze_challenge()` for clarity. Real implementations vary:
> - **Plonky2/Winterfell**: `.observe_*()` and `.get_challenge()`
> - **Arkworks**: `.absorb_*()` and `.squeeze_challenge()`
> - **Merlin**: `.append_message()` and `.challenge_bytes()`

1. **Map the transcript flow**
   Create a diagram of what gets absorbed and when challenges are squeezed.

2. **Check statement binding**
   Verify that `vk`, public inputs, and all protocol parameters are absorbed before first challenge.

3. **Verify domain separation**
   Confirm each protocol phase has unique domain separators.

4. **Compare prover and verifier**
   Ensure both construct identical transcripts.

5. **Check sponge usage**
   Verify only rate portion is output, capacity is never exposed.

6. **Test with malicious inputs**
   Try to construct proofs where statement parameters differ from transcript binding.

## Protocol-Specific Patterns

### Groth16

- Verification key must be bound
- Public inputs must be bound before challenge
- Pairing inputs must match transcript

### PlonK

- Round 1: commitment to witness polynomials
- Round 2: permutation challenges
- Round 3: quotient polynomial
- Round 4: evaluation points
- Round 5: opening proofs

Each round must include prior commitments before deriving challenges.

### STARK

- Multiple rounds of FRI
- Each FRI fold challenge must bind prior layer
- AIR constraints must be bound to trace commitment

### KZG-based Systems

- Commitment must be bound before evaluation challenge
- Batch opening challenges must be independent
- Multi-point openings need distinct challenges per point

## What Good Findings Look Like

Strong Fiat-Shamir findings explain:

1. **The missing binding**: what data is not absorbed
2. **The malleability**: what the prover can choose after seeing the challenge
3. **The concrete attack**: a step-by-step exploit
4. **The impact**: what false statement can be proven

**Example:**
> "The verification key is not absorbed into the transcript before deriving the first challenge. An attacker can compute the challenge, then find a different verification key that produces a valid proof for the same challenge. Impact: proofs valid for one statement can be claimed valid for a different statement. Fix: absorb `vk.to_bytes()` before first `squeeze_challenge()`."

## Common Vulnerable Patterns

| Pattern | Risk Level |
|---------|------------|
| `squeeze` before any `absorb` | 🔴 Critical |
| Public inputs absorbed after challenge | 🔴 Critical |
| No domain separator strings | 🟡 High |
| Full sponge state output | 🟡 High |
| Challenge truncation | 🟡 Medium |
| Prover/verifier ordering mismatch | 🔴 Critical |

## References

- [The Frozen Heart vulnerability in PlonK](https://blog.trailofbits.com/2022/04/18/the-frozen-heart-vulnerability-in-plonk/)
- [Coordinated disclosure of vulnerabilities affecting Girault, Bulletproofs, and PlonK](https://blog.trailofbits.com/2022/04/13/part-1-coordinated-disclosure-of-vulnerabilities-affecting-girault-bulletproofs-and-plonk/)
- [The zero-knowledge attack of the year might just have happened, or how Nova got broken](https://www.zksecurity.xyz/blog/posts/nova-attack/)
- [Weak Fiat-Shamir Attacks on Modern Proof Systems](https://eprint.iacr.org/2023/691.pdf)
- [How to Prove False Statements: Practical Attacks on Fiat-Shamir](https://eprint.iacr.org/2025/118)
- [The Last Challenge Attack](https://eprint.iacr.org/2024/398)
- [Shared Vulnerability Taxonomy](../../../shared/vulnerability-taxonomy.md)
