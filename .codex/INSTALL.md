# Installing cryptography-skills for Codex

This repository exposes Codex-native skills under `.codex/skills/`.

## Install

1. Clone the repository:
   ```sh
   git clone https://github.com/ZippelLabs/cryptography-skills.git ~/.codex/cryptography-skills
   ```

2. Link the Codex skill directories into your Codex skills directory:
   ```sh
   ~/.codex/cryptography-skills/.codex/scripts/install-for-codex.sh
   ```

3. Restart Codex so it discovers the new skills.

## Verify

```sh
ls -la ~/.codex/skills | grep cryptography-
```

You should see:
```
cryptography-zkvm-security -> /path/to/.codex/cryptography-skills/.codex/skills/zkvm-security
```

## Uninstall

```sh
rm ~/.codex/skills/cryptography-*
rm -rf ~/.codex/cryptography-skills
```

## Notes

- Claude Code discovery uses `.claude-plugin/marketplace.json`
- Codex uses the `.codex/skills/` tree, which symlinks to plugin skill directories
- Both discovery methods use the same underlying `SKILL.md` files
