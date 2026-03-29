# ZKP Security Tools

A reference of tools for analyzing zero-knowledge proof implementations.

> **Source**: Adapted from [Awesome-ZKP-Security](https://github.com/0xPARC/zk-security-resources) and tool documentation.

## Tool Landscape

| Tool | Target | Analysis Type | Maintenance |
|------|--------|---------------|-------------|
| [Circomspect](https://github.com/trailofbits/circomspect) | Circom | Static Analysis | Active |
| [ZKAP](https://github.com/whbjzzwjxq/ZKAP) | Circom | Static Analysis | Research |
| [halo2-analyzer](https://github.com/quantstamp/halo2-analyzer) | halo2 | Static + Symbolic | Active |
| [Picus](https://github.com/Veridise/Picus) | Circom, GNARK | Formal Verification | Active |
| [Ecne](https://github.com/franklynwang/EcneProject) | Circom (R1CS) | Formal Verification | Research |
| [Coda](https://github.com/Veridise/coda) | Circom | Formal (Coq) | Active |
| [circom_civer](https://github.com/costa-group/circom_civer) | Circom | Formal (SMT) | Research |
| [gnark-lean-extractor](https://github.com/reilabs/gnark-lean-extractor) | Gnark | Formal (Lean) | Active |
| [zkFuzz](https://github.com/Koukyosyumei/zkFuzz) | Circom | Fuzzing | Research |
| [SNARKProbe](https://github.com/BARC-Purdue/SNARKProbe) | R1CS | Fuzzing | Research |
| [Circuzz](https://github.com/Rigorous-Software-Engineering/circuzz) | Multi | Metamorphic Fuzzing | Active |
| [sierra_analyzer](https://github.com/FuzzingLabs/sierra-analyzer) | Cairo | Static + Symbolic | Active |
| [Pilspector](https://github.com/Schaeff/pilspector/) | PIL | Symbolic | Research |
| [zkwasm-fv](https://github.com/CertiKProject/zkwasm-fv) | zkWasm | Formal (Coq) | Active |

## Static Analysis

### Circomspect (Trail of Bits)

The most mature static analyzer for Circom circuits.

```bash
# Install
cargo install circomspect

# Run on circuit
circomspect path/to/circuit.circom
```

**Detects:**
- Under-constrained signals
- Unused signals and components
- Unconstrained less-than comparisons
- Signal assignments in control flow branches
- Non-quadratic constraints

**When to use:** First-pass analysis of any Circom circuit.

### ZKAP

Research tool for property-based analysis of Circom circuits.

**Detects:**
- Under-constrained circuits
- Unsatisfiable constraints
- Redundant constraints

### halo2-analyzer (Quantstamp)

Static and symbolic analysis for halo2 circuits.

**Detects:**
- Unused gates and columns
- Unconstrained cells
- Missing copy constraints

## Formal Verification

### Picus (Veridise)

Push-button verification for R1CS circuits.

```bash
# Clone and build
git clone https://github.com/Veridise/Picus
cd Picus && cargo build --release

# Verify circuit
./target/release/picus verify circuit.r1cs
```

**Verifies:**
- Uniqueness of witness (determinism)
- Under-constraint detection via SMT

**Limitation:** Does not handle large circuits well due to SMT complexity.

### Ecne

Automated verification using SMT solving.

**Approach:**
1. Extract R1CS constraints
2. Encode as SMT formulas
3. Check for multiple valid witnesses

### Coda (Veridise)

Coq-based verification for Circom.

**Approach:**
1. Compile Circom to Coq
2. Write specifications in Coq
3. Prove equivalence

**Tradeoff:** High assurance but requires Coq expertise.

### gnark-lean-extractor (Reilabs)

Extract Gnark circuits to Lean for verification.

**Use case:** Proving correctness of Gnark implementations against specifications.

## Fuzzing

### zkFuzz

Mutation-based fuzzing for Circom circuits.

**Approach:**
1. Generate random witnesses
2. Mutate constraint inputs
3. Check for constraint violations or unexpected passes

### SNARKProbe

Fuzzing for R1CS-based systems.

**Detects:**
- Implementation bugs in proving systems
- Constraint generation issues

### Circuzz

Metamorphic testing across multiple ZK DSLs (Circom, Corset, GNARK, Noir).

**Approach:**
1. Generate equivalent circuits
2. Compare outputs across implementations
3. Detect compiler/DSL bugs

## Tool Selection Guide

### For Circom Projects

1. **Start with Circomspect** — fast, catches common issues
2. **Add Picus** — for under-constraint detection
3. **Consider Coda** — for high-assurance components

### For halo2 Projects

1. **Use halo2-analyzer** — static + symbolic analysis
2. **Manual review** — halo2 tooling is less mature

### For GNARK Projects

1. **gnark-lean-extractor** — if Lean expertise available
2. **Picus** — supports R1CS from GNARK
3. **Manual review** — primary approach

### For Cairo/Starknet

1. **sierra_analyzer** — FuzzingLabs tool for Cairo 1.0
2. **Manual review** — limited tooling

## Running Tools in CI

### Example: Circomspect in GitHub Actions

```yaml
name: ZK Security Check
on: [push, pull_request]

jobs:
  circomspect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Circomspect
        run: cargo install circomspect
      - name: Run Circomspect
        run: |
          find circuits -name "*.circom" -exec circomspect {} \;
```

### Example: Picus for CI

```yaml
  picus:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Picus
        run: |
          git clone https://github.com/Veridise/Picus
          cd Picus && cargo build --release
      - name: Compile circuit to R1CS
        run: circom circuit.circom --r1cs
      - name: Verify
        run: ./Picus/target/release/picus verify circuit.r1cs
```

## Limitations

**No silver bullet:** Static analysis and formal verification catch specific bug classes. They do not guarantee absence of all vulnerabilities.

**Coverage gaps:**
- Most tools focus on Circom; other DSLs have less coverage
- zkVM-specific circuits (SP1, RISC Zero) need manual review
- Protocol-level issues (Fiat-Shamir) often require manual analysis

**Recommendation:** Use tools as part of a defense-in-depth strategy that includes manual audits, fuzzing, and formal verification where feasible.
