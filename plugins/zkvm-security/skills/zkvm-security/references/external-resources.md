# ZKP Security Resources

A curated collection of external resources for zero-knowledge proof security research.

> **Source**: Many of these links are adapted from [Awesome-ZKP-Security](https://github.com/0xPARC/zk-security-resources) and other community resources.

## Learning Resources

### Courses

- [Zero Knowledge Proofs MOOC](https://zk-learning.org/) — Comprehensive ZKP course
- [MIT's Modern Zero Knowledge Cryptography](https://zkiap.com/) — Academic course materials
- [0xParc's Circom and Halo2 learning groups](https://learn.0xparc.org/) — Hands-on learning

### Books

- [The MoonMath Manual to zk-SNARKs](https://leastauthority.com/community-matters/moonmath-manual) — Minimal cryptography prerequisites
- [Proofs, Arguments, and Zero-Knowledge](https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.pdf) (Justin Thaler, 2022)
- [A Graduate Course in Applied Cryptography](http://toc.cryptobook.us/book.pdf) (Boneh & Shoup)
- [Building Cryptography Proofs from Hash Functions](https://github.com/hash-based-snargs-book/hash-based-snargs-book/blob/main/snargs-book.pdf) (Chiesa & Yogev, 2024)

### Curated Lists

- [Xor0v0/awesome-zero-knowledge-proofs-security](https://github.com/Xor0v0/awesome-zero-knowledge-proofs-security)
- [matter-labs/awesome-zero-knowledge-proofs](https://github.com/matter-labs/awesome-zero-knowledge-proofs)
- [ventali/awesome-zk](https://github.com/ventali/awesome-zk)
- [Zero Knowledge Canon by a16z](https://a16zcrypto.com/zero-knowledge-canon/)
- [ZKP Knowledge Base by Delendum](https://kb.delendum.xyz/)

## Security Blogs

### Research Teams

| Blog | Focus |
|------|-------|
| [zkSecurity Blog](https://www.zksecurity.xyz/blog/) | ZKP vulnerability research |
| [Trail of Bits Blog](https://blog.trailofbits.com/) | Security research, Circomspect |
| [Veridise Blog](https://veridise.medium.com/) | Formal verification, Picus |
| [Zellic Blog](https://www.zellic.io/blog/) | ZK audits, vulnerability disclosures |
| [OpenZeppelin Security Insights](https://blog.openzeppelin.com/tag/security-insights) | Smart contract + ZK security |
| [0xParc Blog](https://0xparc.org/blog) | ZK infrastructure and tools |

### Key Vulnerability Disclosures

| Title | Date | Impact |
|-------|------|--------|
| [The Frozen Heart vulnerability in PlonK](https://blog.trailofbits.com/2022/04/18/the-frozen-heart-vulnerability-in-plonk/) | Apr 2022 | Fiat-Shamir |
| [The Frozen Heart vulnerability in Bulletproofs](https://blog.trailofbits.com/2022/04/15/the-frozen-heart-vulnerability-in-bulletproofs/) | Apr 2022 | Fiat-Shamir |
| [It pays to be Circomspect](https://blog.trailofbits.com/2022/09/15/it-pays-to-be-circomspect/) | Sep 2022 | Circom bugs |
| [Disarming Fiat-Shamir footguns](https://blog.trailofbits.com/2024/06/24/disarming-fiat-shamir-footguns/) | Jun 2024 | Transcript issues |
| [Circom-Pairing: A Million-Dollar ZK Bug](https://medium.com/veridise/circom-pairing-a-million-dollar-zk-bug-caught-early-c5624b278f25) | Jan 2023 | Underconstraint |
| [The zero-knowledge attack of the year (Nova)](https://www.zksecurity.xyz/blog/posts/nova-attack/) | Jul 2023 | Soundness break |
| [SP1 Security Update](https://blog.succinct.xyz/sp1-security-update-1-27-25/) | Jan 2025 | Multiple vulns |
| [Patch Thursday: zkSync Era Soundness Bug](https://medium.com/chainlight/uncovering-a-zk-evm-soundness-bug-in-zksync-era-f3bc1b2a66d8) | Nov 2023 | $1.9B at risk |
| [Zcash Counterfeiting Vulnerability](https://electriccoin.co/blog/zcash-counterfeiting-vulnerability-successfully-remediated/) | Feb 2019 | Infinite mint |

## Academic Papers

### Vulnerability Analysis

| Paper | Year | Focus |
|-------|------|-------|
| [SoK: What don't we know? Understanding Security Vulnerabilities in SNARKs](https://arxiv.org/pdf/2402.15293) | 2024 | Comprehensive survey |
| [Zero-Knowledge Proof Vulnerability Analysis and Security Auditing](https://eprint.iacr.org/2024/514.pdf) | 2024 | Audit methodology |
| [Weak Fiat-Shamir Attacks on Modern Proof Systems](https://eprint.iacr.org/2023/691.pdf) | 2023 | Transcript attacks |
| [The Last Challenge Attack](https://eprint.iacr.org/2024/398) | 2024 | KZG Fiat-Shamir |
| [How to Prove False Statements: Practical Attacks on Fiat-Shamir](https://eprint.iacr.org/2025/118) | 2025 | Fiat-Shamir attacks |

### Formal Verification

| Paper | Year | Focus |
|-------|------|-------|
| [Practical Security Analysis of Zero-Knowledge Proof Circuits](https://www.cs.utexas.edu/~isil/zkap.pdf) | 2023 | ZKAP methodology |
| [Automated Detection of Under-Constrained Circuits](https://dl.acm.org/doi/pdf/10.1145/3591282) | 2023 | Static analysis |
| [Certifying Zero-Knowledge Circuits with Refinement Types](https://eprint.iacr.org/2023/547.pdf) | 2023 | Type systems |
| [Formal Verification of Zero-Knowledge Circuits](https://arxiv.org/pdf/2311.08858) | 2023 | General techniques |
| [Compositional Formal Verification of ZK Circuits](https://eprint.iacr.org/2023/1278.pdf) | 2023 | Modular verification |

### Tools & Techniques

| Paper | Year | Focus |
|-------|------|-------|
| [Automated Analysis of Halo2 Circuits](https://eprint.iacr.org/2023/1051.pdf) | 2023 | Halo2 analysis |
| [SMT Solving over Finite Field Arithmetic](https://arxiv.org/pdf/2305.00028) | 2023 | SMT for ZK |
| [zkFuzz: Fuzzing Zero-Knowledge Circuits](https://arxiv.org/pdf/2504.11961) | 2025 | Fuzzing |
| [MTZK: Testing ZK Compilers](https://www.ndss-symposium.org/wp-content/uploads/2025-530-paper.pdf) | 2025 | Metamorphic testing |
| [fAmulet: Finding Bugs in Polygon zkRollup](https://arxiv.org/pdf/2410.12210) | 2024 | zkEVM fuzzing |

## Talks & Videos

| Talk | Event | Topic |
|------|-------|-------|
| [ZKP MOOC Lecture 15: Secure ZK Circuits with Formal Methods](https://www.youtube.com/watch?v=av7Wq742GIA) | MOOC | Formal methods |
| [ZK Security Research Workshop](https://www.youtube.com/watch?v=nYifGRRikh8) | 0xParc | Security research |
| [Are Your Zero-Knowledge Proofs Correct?](https://www.youtube.com/watch?v=ettgm3ZVYOk) | Devcon Bogotá | General security |
| [ZK10: ZK Vulnerabilities and Attacks](https://www.youtube.com/watch?v=CNxNe9-UySs) | ZK Summit | Vulnerability survey |
| [ZK11: Taxonomy of ZKP Vulnerabilities](https://www.youtube.com/watch?v=Gfa4BIMMXhk) | ZK Summit | Classification |
| [SoK: Security Vulnerabilities in SNARKs](https://www.youtube.com/watch?v=6-aeTlREYZo) | ZKProof 6 | Survey presentation |

## Audit Reports

### Report Collections

- [ZippelLabs/zkVMs-Security](https://github.com/ZippelLabs/zkVMs-Security) — zkVM-specific reports
- [nullity00/zk-security-reviews](https://github.com/nullity00/zk-security-reviews) — General ZK reviews
- [zkSecurity Reports](https://www.zksecurity.xyz/reports/)
- [OpenZeppelin Audits](https://www.openzeppelin.com/research#security-audits)
- [Veridise Audits](https://veridise.com/past-security-audits/)

## Bug Trackers & Datasets

- [0xPARC/zk-bug-tracker](https://github.com/0xPARC/zk-bug-tracker) — Community bug tracker
- [zkSecurity/zkbugs](https://github.com/zksecurity/zkbugs/) — Reproducible vulnerability dataset

## CTFs & Puzzles

- [ZKHACK Puzzles](https://zkhack.dev/puzzles/)
- [RareSkills ZK Puzzles](https://github.com/RareSkills/zero-knowledge-puzzles)
- [Ingonyama CTF](https://github.com/ingonyama-zk/zkctf-2023-writeups)
- [CryptoHack ZKP Challenges](https://cryptohack.org/challenges/zkp/)
