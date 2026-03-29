# zkVM Audit Workflow

## 1. System Inventory

Record the guest program, circuit backend, proof system, verifier, recursion layer, and any host-side services that feed data into the prover.

## 2. Statement Definition

Write down exactly what the proof claims. Check whether the statement covers:

- all public inputs
- the guest program hash or version
- the expected execution trace
- recursion metadata, if present

If the statement is underspecified, the verifier may accept proofs for the wrong computation.

## 3. Trust Boundary Review

Separate:

- trusted prover code
- untrusted witness data
- untrusted host inputs
- public commitments
- verifier inputs

If any boundary is implicit, make it explicit before auditing deeper.

## 4. Arithmetic and Encoding Checks

Look for:

- field modulus mismatches
- signed/unsigned conversion bugs
- truncation during serialization
- endian confusion
- range-check gaps

These bugs often turn "impossible" values into valid proof inputs.

## 5. Constraint Completeness

Verify that every security-relevant state transition is constrained.

Common misses include:

- branches that are only checked in the host, not in the circuit
- memory reads that are not tied to a committed trace
- "debug" or "fast path" logic that skips constraints

## 6. Transcript and Randomness

Check challenge generation carefully:

- domain separation
- nonce uniqueness
- replay resistance
- hash-to-field conversion
- transcript ordering

## 7. Negative Testing

Try to produce:

- invalid witnesses that still verify
- proofs with reordered or truncated inputs
- stale recursion data
- malformed commitments
- boundary values around zero, one, and field modulus limits

## 8. Reporting

Document the exploit path in three parts:

1. what the system claims to prove
2. what the attacker can actually make it prove
3. why the verifier accepts the wrong statement
