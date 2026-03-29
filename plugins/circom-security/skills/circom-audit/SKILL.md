---
name: circom-audit
description: "Audits Circom circuits for DSL-specific bugs including signal constraints, component usage, and snarkjs integration issues."
---

# Circom Security Audit

Use this skill when reviewing Circom circuits for security vulnerabilities, with focus on DSL-specific patterns and common mistakes.

> **SoK Context**: Circom is the most common DSL in audit reports. The top 3 root causes are: (1) wrong logic translation (34%), (2) missing input constraints (25%), (3) assigned-but-not-constrained (14%). See [SoK Classification](../../../shared/sok-vulnerability-classification.md).

## When to Use

Use this skill when:

- auditing `.circom` circuit files for soundness bugs
- reviewing witness generation JavaScript files
- checking component library usage (circomlib, etc.)
- validating snarkjs proof generation and verification
- inspecting input handling and public/private signal boundaries

## When NOT to Use

Do not use this skill for:

- non-Circom circuit DSLs (halo2, Cairo, Noir) — use appropriate skills
- proving system internals unrelated to Circom — see `fiat-shamir` skill
- smart contract verification logic — use Solidity/smart contract skills
- general cryptography questions without Circom code

## Rationalizations to Reject

Reject these shortcuts:

- "The `<--` is fine because the witness generator validates it."
- "Circomlib components are audited, so I don't need to check preconditions."
- "The input is from a trusted source, so range checks aren't needed."
- "The compiler will catch constraint issues."
- "Non-quadratic constraints are just warnings, not errors."

## Circom-Specific Bug Patterns

### 1. Assigned but Not Constrained (`<--` without `===`)

The most common Circom bug. Using `<--` assigns a witness value but doesn't create a constraint.

```circom
// BUG: assigned but not constrained
signal output out;
out <-- in * in;  // No constraint!

// FIXED: use <== for assign + constrain
out <== in * in;

// ALTERNATIVE: separate assignment and constraint
out <-- in * in;
out === in * in;
```

**Tool Detection:** Run `circomspect` — it flags `<--` without `===`.

### 2. Non-Quadratic Constraints

Circom R1CS only supports quadratic constraints. Higher-degree expressions silently produce incorrect constraints.

```circom
// BUG: cubic expression
signal out;
out <== a * b * c;  // Not quadratic!

// FIXED: intermediate signal
signal ab;
ab <== a * b;
out <== ab * c;
```

**Tool Detection:** Circom compiler warns but doesn't error. Check warnings!

### 3. Component Output Reuse / Signal Aliasing

Reusing a component output in conflicting constraints creates contradictions.

```circom
// BUG: component output used in conflicting ways
component mult = Multiplier();
mult.a <== x;
mult.b <== y;
signal z1 <== mult.out;  
signal z2 <== mult.out;
z1 === 10;
z2 === 20;  // Contradiction! mult.out can't be both

// FIXED: use component output once, or separate components
component mult = Multiplier();
mult.a <== x;
mult.b <== y;
mult.out === 10;  // Use output directly in constraint
```

### 4. Component Output Not Constrained

Using a component but ignoring its output or not connecting it to the constraint system.

```circom
// BUG: hash output unused
component hasher = Poseidon(2);
hasher.inputs[0] <== a;
hasher.inputs[1] <== b;
// hasher.out is never used!

// FIXED: bind output
commitment === hasher.out;
```

### 5. Array Bounds

Array indexing without bounds checking can access undefined signals.

```circom
// BUG: index could be out of bounds
signal arr[10];
signal output selected;
selected <== arr[index];  // What if index >= 10?

// FIXED: constrain index range
component lt = LessThan(8);
lt.in[0] <== index;
lt.in[1] <== 10;
lt.out === 1;
selected <== arr[index];
```

### 6. Division and Modular Inverse

Division in finite fields is multiplication by inverse, which may not exist.

```circom
// BUG: division by zero undefined
signal quotient;
quotient <-- a / b;  // What if b == 0?
quotient * b === a;

// FIXED: assert b != 0
component isZero = IsZero();
isZero.in <== b;
isZero.out === 0;  // Ensure b != 0
quotient <-- a / b;
quotient * b === a;
```

### 7. Bit Decomposition Without Range Checks

Decomposing a field element to bits without ensuring each bit is 0 or 1.

```circom
// BUG: bits not constrained to binary
signal bits[254];
var sum = 0;
for (var i = 0; i < 254; i++) {
    bits[i] <-- (in >> i) & 1;  // Assigned, not constrained!
    sum += bits[i] * (1 << i);
}
sum === in;

// FIXED: constrain each bit
for (var i = 0; i < 254; i++) {
    bits[i] <-- (in >> i) & 1;
    bits[i] * (bits[i] - 1) === 0;  // Ensures 0 or 1
    sum += bits[i] * (1 << i);
}
sum === in;
```

### 8. Field Overflow in Arithmetic

Field arithmetic wraps at the prime modulus. Large computations may overflow.

```circom
// The BN254 scalar field has prime:
// p = 21888242871839275222246405745257275088548364400416034343698204186575808495617

// BUG: potential overflow not considered
signal product;
product <== largeValue1 * largeValue2;  // May wrap!
```

### 9. Component Library Preconditions

Circomlib components have implicit preconditions that aren't enforced.

```circom
// BUG: LessThan requires inputs < 2^n
component lt = LessThan(252);
lt.in[0] <== arbitraryValue;  // Could be >= 2^252!
lt.in[1] <== threshold;

// FIXED: range check first
component n2b = Num2Bits(252);
n2b.in <== arbitraryValue;  // This constrains to < 2^252
lt.in[0] <== arbitraryValue;
lt.in[1] <== threshold;
```

**Common Circomlib Preconditions:**
- `LessThan(n)`: inputs must be < 2^n
- `Num2Bits(n)`: input must be < 2^n  
- `IsZero()`: works on full field
- `Poseidon(n)`: inputs should be field elements

### 10. Public vs Private Signal Confusion

Signals declared `input` are private by default. Use `public` keyword for public inputs.

```circom
// Private input (hidden in proof)
signal input secretKey;

// Public input (visible to verifier)
signal input publicCommitment;
// Must be marked public in main component instantiation:
// component main { public [ publicCommitment ] } = MyCircuit();
```

### 11. Non-Deterministic Square Root

Field square root has two valid values (+x and -x). Without canonicalization, provers can choose either.

```circom
// BUG: sqrt is non-deterministic
signal root;
root <-- sqrt(input);  // Which root?
root * root === input;

// FIXED: enforce canonical choice (smaller value)
signal root;
root <-- sqrt(input);
root * root === input;
// Ensure root < (p+1)/2 (positive square root)
component lt = LessThan(254);
lt.in[0] <== root;
lt.in[1] <== HALF_PRIME;
lt.out === 1;
```

### 12. Template Parameter Misuse

Template parameters affect constraint generation but aren't constrained values.

```circom
// BUG: n is a compile-time parameter, not a signal
template VariableSum(n) {
    signal input values[n];
    signal output sum;
    var acc = 0;
    for (var i = 0; i < n; i++) {  // n is fixed at compile time
        acc += values[i];
    }
    sum <== acc;
}
// Attacker cannot change n at runtime, but different
// instantiations may have inconsistent behavior
```

### 13. Division Operation Semantics

Circom division is field inverse multiplication, not integer division.

```circom
// BUG: division doesn't work like integer division
signal quotient;
quotient <== 7 / 3;  // NOT 2! It's 7 * inverse(3) mod p

// For integer division, use QuotientReminder gadget:
component qr = QuotientRemainder(252);
qr.dividend <== 7;
qr.divisor <== 3;
// qr.quotient == 2, qr.remainder == 1
// Constraint: dividend == quotient * divisor + remainder
```

### 14. Variable-Length Array Access

Dynamic array indexing can access out-of-bounds if index isn't range-checked.

```circom
// BUG: index could be >= len
signal input index;
signal input arr[10];
signal output selected;
selected <== arr[index];  // What if index = 100?

// FIXED: range check index
component lt = LessThan(8);  // 8 bits enough for < 256
lt.in[0] <== index;
lt.in[1] <== 10;
lt.out === 1;
selected <== arr[index];
```

### 15. Weak Equality Through Multiplication

Checking equality via product can be bypassed.

```circom
// BUG: if either a or b is 0, constraint passes regardless of other
signal diff;
diff <== (a - target) * (b - target);
diff === 0;  // Attacker: set a = 0, any b works

// FIXED: check each independently
a === target;
b === target;
```

## Quick Start Workflow

1. **Run Circomspect**
   ```bash
   circomspect path/to/circuit.circom
   ```
   Fix all warnings before manual review.

2. **Grep for `<--`**
   Every `<--` needs a corresponding `===` or a very good reason.
   ```bash
   grep -n '<--' circuit.circom
   ```

3. **Check Component Preconditions**
   For each Circomlib component, verify inputs meet requirements.

4. **Trace Public Inputs**
   Ensure all public inputs reach constraints that bind them to outputs.

5. **Test Edge Cases**
   - Zero values
   - Maximum field values
   - Boundary conditions (array edges, bit limits)

6. **Verify Witness Generation**
   Check that `generate_witness.js` matches circuit logic.

## Circomspect Integration

Circomspect detects many common issues automatically:

| Check | Description | Severity |
|-------|-------------|----------|
| `assigned-not-constrained` | `<--` without `===` | Critical |
| `unused-signal` | Signal never used in constraint | High |
| `unconstrained-less-than` | LessThan without input bounds | High |
| `signal-in-branching` | Different constraints per branch | High |
| `non-strict-binary` | Missing binary constraint on bits | High |
| `unconstrained-division` | Division without zero check | Medium |
| `component-output-unused` | Component output not connected | High |
| `non-quadratic-constraint` | Constraint degree > 2 (R1CS violation) | Critical |

```bash
# Install
cargo install circomspect

# Run with all checks
circomspect --level info path/to/circuit.circom

# Output to JSON for CI integration
circomspect --output-format json circuit.circom > report.json
```

## Testing Adversarial Witnesses

For each vulnerability type, construct test cases that should fail:

```javascript
// Using circom_tester (npm install circom_tester)
const { wasm: circomWasm } = require("circom_tester");

describe("Merkle Circuit Security", () => {
    let circuit;
    
    before(async () => {
        circuit = await circomWasm("circuits/merkle.circom");
    });
    
    it("rejects swapped siblings (if properly constrained)", async () => {
        // This should fail if the circuit is sound
        const maliciousWitness = {
            leaf: validLeaf,
            siblings: validSiblings.reverse(),  // Swapped!
            pathIndices: validIndices  // Same indices
        };
        
        await expect(
            circuit.calculateWitness(maliciousWitness)
        ).to.be.rejected;
    });
    
    it("rejects out-of-range values", async () => {
        const FIELD_SIZE = 21888242871839275222246405745257275088548364400416034343698204186575808495617n;
        const overflowWitness = {
            input: FIELD_SIZE + 1n  // Wraps to 1
        };
        
        // If circuit has proper range checks, this fails
        await expect(
            circuit.calculateWitness(overflowWitness)
        ).to.be.rejected;
    });
});
```

### Manual Witness Manipulation

For bugs not caught by automated testing:

```bash
# Generate valid witness
node generate_witness.js circuit.wasm input.json witness.wtns

# Convert to JSON for inspection
snarkjs wtns export json witness.wtns witness.json

# Manually edit witness.json to create malicious values
# Then check if constraints still pass:
snarkjs wtns check circuit.r1cs witness.wtns
# If this passes with malicious witness, you found a bug!
```

## Common Vulnerable Patterns

| Pattern | Risk | Tool Detection |
|---------|------|----------------|
| `<--` alone | 🔴 Critical | Circomspect |
| Cubic constraints | 🟡 High | Compiler warning |
| Unused component output | 🟡 High | Circomspect |
| Missing range check | 🟡 High | Manual |
| Array index unbounded | 🟡 High | Manual |
| Division without zero check | 🟡 High | Manual |

## What Good Findings Look Like

Strong Circom findings explain:

1. **The specific signal**: which signal is under-constrained
2. **The attack witness**: concrete values that pass proof but shouldn't
3. **The false statement**: what the malicious proof claims
4. **The fix**: exact constraint to add

**Example:**
> "Signal `merkleRoot` in `verify_membership.circom:45` is assigned via `<--` but never constrained. An attacker can provide any root value and generate a valid proof. Impact: arbitrary Merkle membership claims. Fix: Add `merkleRoot === hasher.out` after line 47."

## References

- [It pays to be Circomspect](https://blog.trailofbits.com/2022/09/15/it-pays-to-be-circomspect/) — Trail of Bits
- [Circom-Pairing: A Million-Dollar ZK Bug](https://medium.com/veridise/circom-pairing-a-million-dollar-zk-bug-caught-early-c5624b278f25) — Veridise
- [Best Practices for Large Circom Circuits](https://hackmd.io/V-7Aal05Tiy-ozmzTGBYPA)
- [Circomlib Documentation](https://github.com/iden3/circomlib)
- [Shared Vulnerability Taxonomy](../../../shared/vulnerability-taxonomy.md)
- [Audit Checklist](../../../shared/audit-checklist.md)
