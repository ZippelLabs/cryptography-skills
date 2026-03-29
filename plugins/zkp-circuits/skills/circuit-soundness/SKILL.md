---
name: circuit-soundness
description: "Detects under-constrained circuits in ZKP systems that allow false proofs to pass verification."
---

# Circuit Soundness Audit

Use this skill when reviewing zero-knowledge circuit implementations for soundness bugs — constraints that fail to prevent invalid witnesses from producing valid proofs.

## When to Use

Use this skill when:

- auditing Circom, halo2, Noir, Cairo, or GNARK circuits for under-constraint bugs
- reviewing witness generation code for non-determinism or missing validation
- checking that all code paths produce equivalent constraint counts
- validating arithmetic operations against field overflow/underflow
- inspecting component integrations where library assumptions may be violated

## When NOT to Use

Do not use this skill for:

- proving system (backend) bugs like Fiat-Shamir issues — see `fiat-shamir` skill
- zkVM-specific bugs like emulator correctness — see `zkvm-security` skill
- smart contract vulnerabilities unrelated to circuit soundness
- performance optimization without security implications

## Rationalizations to Reject

Reject these shortcuts:

- "The witness generator enforces this, so the circuit doesn't need to."
- "This value is always positive in practice, so we don't need range checks."
- "The library handles this internally."
- "This constraint is redundant because another one covers it."
- "Honest provers won't provide malformed inputs."
- "The compiler optimizes away unnecessary constraints."

## Bug Classes

### 1. Assigned but Not Constrained

The most common soundness bug. A signal is computed but never enforced.

**Circom Example:**
```circom
// BUG: assigned but not constrained
signal output out;
out <-- in * in;  // Only assigns, doesn't constrain!

// FIXED
out <== in * in;  // Assigns AND constrains
```

**halo2 Example:**
```rust
// BUG: advice assigned but no gate constrains it
region.assign_advice(|| "value", col, row, || Value::known(x))?;

// FIXED: gate must reference the cell
meta.create_gate("check", |cells| {
    let value = cells.query_advice(col, Rotation::cur());
    vec![value - expected]
});
```

**What to look for:**
- Circom: `<--` without corresponding `===`
- halo2: `assign_advice` without gate referencing the cell
- GNARK: `frontend.Variable` used but not in constraint

### 2. Arithmetic Overflow/Underflow

Field arithmetic wraps at the modulus. Operations may produce unexpected results.

**Example:**
```circom
// BUG: subtraction can underflow
signal diff;
diff <== a - b;  // If b > a, diff wraps to huge value

// FIXED: range check first
component lt = LessThan(252);
lt.in[0] <== b;
lt.in[1] <== a;
lt.out === 1;  // Enforce a >= b
diff <== a - b;
```

**What to look for:**
- Subtraction without prior comparison
- Multiplication that may exceed field size
- Division by values that could be zero
- Bit decomposition assuming specific bit-widths

### 3. Mismatched Types/Lengths

Different components assume different data sizes or formats.

**Example:**
```circom
// BUG: component expects 256 bits, input is 254 bits
component hash = Poseidon(1);
hash.inputs[0] <== some_254_bit_value;  // May truncate or behave unexpectedly
```

**What to look for:**
- Array length assumptions not enforced
- Bit-width mismatches across components
- Field element vs byte array confusion
- Big-endian vs little-endian interpretation

### 4. Non-Determinism

Multiple valid witnesses exist for the same public inputs.

**Example:**
```circom
// BUG: two different witnesses can satisfy this
signal x;
x * x === 4;  // Both x=2 and x=-2 (field equivalent) work

// FIXED: enforce canonical choice
signal x;
x * x === 4;
component isPositive = LessThan(252);
isPositive.in[0] <== x;
isPositive.in[1] <== HALF_FIELD;
isPositive.out === 1;
```

**What to look for:**
- Square root computations
- Modular inverse operations
- Division where multiple quotients are valid
- Bit decomposition without ordering constraints

### 5. Logic Bugs in Branching

Different code paths have different constraint semantics.

**Example:**
```circom
// BUG: one branch has fewer constraints
if (condition) {
    out <== a + b;
} else {
    out <-- c;  // Not constrained in this branch!
}
```

**What to look for:**
- `if/else` with different constraint counts
- Early returns that skip constraints
- Loop edge cases (empty, single element)
- Component instantiation inside conditionals

### 6. Compiler Optimization Issues

Compiler removes constraints it considers redundant.

**Example:**
```circom
// May be optimized away if compiler thinks it's redundant
signal dummy;
dummy <== 0;
dummy === 0;
```

**What to look for:**
- Constraints that depend on optimizer behavior
- Dead code elimination removing security checks
- Constant propagation changing semantics

### 7. Public Input Binding Failures

Public inputs not properly bound to the proof statement.

**Circom Example:**
```circom
// BUG: public input used but not constrained
signal input publicRoot;
signal private leafValue;
// ... Merkle proof logic that doesn't actually use publicRoot
output <== leafValue;  // Root can be any value!
```

**halo2 Example:**
```rust
// BUG: instance column not actually constrained to witness
let instance = meta.instance_column();
// Missing: no gate links instance to advice
```

**GNARK Example:**
```go
// BUG: public variable declared but not constrained
api.AssertIsLessOrEqual(privateWitness, api.Constant(100))
// publicOutput never actually bound to computation
```

### 8. Boolean Constraint Bypass

Signal declared boolean but constraint is insufficient.

**Example:**
```circom
// BUG: doesn't actually enforce 0 or 1
signal isValid;
isValid * isValid === isValid;  // Also satisfied by any field element!

// FIXED: correct boolean constraint
isValid * (1 - isValid) === 0;
```

**Noir Example:**
```noir
// BUG: assertion only in unconstrained code
fn check(b: Field) {
    assert(b == 0 || b == 1);  // This may not generate constraints!
}
```

### 9. Lookup Table Soundness

Lookup arguments don't cover all required values.

**halo2 Example:**
```rust
// BUG: lookup table missing entries
let lookup_table = vec![0, 1, 2, 3]; // Missing 4-255 for byte range
meta.lookup(|cells| {
    let value = cells.query_advice(col, Rotation::cur());
    vec![(value, table)]
});
// Values 4-255 will fail lookup but circuit may still pass!
```

**What to look for:**
- Incomplete lookup tables
- Lookup not applied to all required cells
- Dynamic vs static table contents
- Table initialization in wrong phase

### 10. Division by Zero

Division operations without zero-check on divisor.

**Example:**
```circom
// BUG: divisor could be zero
signal quotient;
signal divisor;
quotient <== dividend / divisor;  // Undefined if divisor == 0

// FIXED: enforce non-zero
component isZero = IsZero();
isZero.in <== divisor;
isZero.out === 0;  // Divisor must be non-zero
quotient <== dividend / divisor;
```

**GNARK Example:**
```go
// BUG: api.Div doesn't check for zero
quotient := api.Div(dividend, divisor)

// FIXED
api.AssertIsDifferent(divisor, 0)
quotient := api.Div(dividend, divisor)
```

## Real-World Vulnerability Examples

| Bug | Project | Impact | Reference |
|-----|---------|--------|-----------|
| Under-constrained hash inputs | Circom-Pairing | Forged proofs of invalid pairings | [Veridise 2023](https://medium.com/veridise/circom-pairing-a-million-dollar-zk-bug-caught-early-c5624b278f25) |
| Missing leaf/branch domain separation | Scroll zkTrie | Proof of membership for non-existent leaves | [Trail of Bits](https://github.com/ZippelLabs/zkVMs-Security) |
| Non-deterministic sqrt | Various | Multiple valid witnesses for same statement | Common pattern |
| Lookup table initialization | Various halo2 | Invalid values pass verification | Common pattern |

## Quick Start Workflow

1. **Map all signals/cells**
   List every signal, advice column, or variable. Check each has at least one constraint.

2. **Trace witness flow**
   Follow each witness value from input to output. Identify where it's computed vs constrained.

3. **Check arithmetic boundaries**
   For every arithmetic operation, verify overflow/underflow is handled.

4. **Verify component assumptions**
   For each library component, document its preconditions and verify they're enforced.

5. **Test with adversarial witnesses**
   Construct witnesses that should fail. Verify the circuit rejects them.

## DSL-Specific Patterns

### Circom

| Pattern | Risk |
|---------|------|
| `<--` alone | Critical: assigned not constrained |
| `component.out` unused | High: output not bound |
| `for` with variable bounds | Medium: constraint count varies |
| `signal input` range | High: no automatic bounds |

### halo2

| Pattern | Risk |
|---------|------|
| `assign_advice` without gate | Critical: unconstrained cell |
| Missing copy constraint | High: values can diverge |
| Wrong rotation | High: references wrong row |
| Selector off | Medium: gate not active |

### Cairo

| Pattern | Risk |
|---------|------|
| Unchecked felt arithmetic | High: wrap-around |
| Missing `assert` | Critical: unconstrained |
| Dict without squash | High: inconsistent state |

### Noir

| Pattern | Risk |
|---------|------|
| `unconstrained fn` returning values | Critical: no constraints generated |
| `assert()` in non-constrained context | Medium: may be compile-time only |
| Array bounds without range proof | High: index can be any field value |
| Missing `#[recursive]` attribute | Medium: proof composition fails |

**Noir Example (unconstrained function):**
```noir
// BUG: unconstrained functions don't generate constraints
unconstrained fn compute_sqrt(x: Field) -> Field {
    // This is just a hint to the prover!
    std::field::sqrt(x)
}

fn main(x: Field, y: pub Field) {
    let root = compute_sqrt(x);
    // MISSING: constraint that root * root == x
}
```

### GNARK

| Pattern | Risk |
|---------|------|
| `frontend.Variable` assigned but unused | Critical: unconstrained |
| Missing `api.AssertIs*` | High: no enforcement |
| `api.Select` without boolean check | High: selector not 0/1 |
| `api.ToBinary` output not constrained | Medium: bits not used |

**GNARK Example (unconstrained variable):**
```go
func (c *Circuit) Define(api frontend.API) error {
    // BUG: intermediate variable not constrained to output
    intermediate := api.Add(c.A, c.B)
    _ = intermediate  // Never used in constraint!
    
    // FIXED: use result in constraint
    api.AssertIsEqual(c.Output, api.Add(c.A, c.B))
    return nil
}
```

## Testing Guidance

### Adversarial Witness Generation

For each bug class, construct witnesses that exploit the vulnerability:

**1. Under-constrained signals:**
```javascript
// For Circom circuits, use circom_tester
const w = await circuit.calculateWitness({
    in: 5,
    // malicious: override unconstrained output
    out: 999  // Should be 25, but if unconstrained...
});
await circuit.checkConstraints(w);  // Should FAIL if bug exists
```

**2. Arithmetic overflow:**
```javascript
// Test with values near field boundary
const FIELD_SIZE = 21888242871839275222246405745257275088548364400416034343698204186575808495617n;
const w = await circuit.calculateWitness({
    a: 100n,
    b: FIELD_SIZE - 50n  // Large value that wraps
});
```

**3. Non-determinism:**
```javascript
// For sqrt circuits, test both roots
const w1 = await circuit.calculateWitness({ x: 4n }, { root: 2n });
const w2 = await circuit.calculateWitness({ x: 4n }, { root: FIELD_SIZE - 2n });
// Both should NOT produce valid proofs if properly constrained
```

### Tool-Assisted Testing

| Tool | Usage |
|------|-------|
| **Circomspect** | `circomspect --level warning circuit.circom` |
| **ZKAP** | Static analysis for under-constrained signals |
| **Picus** | Formal verification: `picus check --circuit main.r1cs` |
| **halo2-analyzer** | `cargo test --features mock-prover` with MockProver |

## What Good Findings Look Like

Strong soundness findings explain:

1. **The unconstrained path**: exactly which witness values are free
2. **The attack**: a concrete malicious witness that produces a valid proof
3. **The impact**: what false statement can now be "proven"
4. **The fix**: the missing constraint(s)

**Example:**
> "The Merkle proof circuit constrains leaf hashing but not sibling ordering. An attacker can swap sibling positions to prove membership of a different leaf. Impact: false membership proofs. Fix: Add `position` signal constrained to 0/1 and use it to order hash inputs."

## References

- [Shared Vulnerability Taxonomy](../../../shared/vulnerability-taxonomy.md)
- [Audit Checklist](../../../shared/audit-checklist.md)
- [Security Tools](../../../shared/security-tools.md)
