# deploy-diff

> Generate human-readable changelogs between deployments by diffing git tags and annotating config changes.

---

## Installation

```bash
pip install deploy-diff
```

Or install from source:

```bash
git clone https://github.com/yourorg/deploy-diff.git && pip install -e .
```

---

## Usage

Compare two deployment tags and generate a changelog:

```bash
deploy-diff --from v1.4.2 --to v1.5.0
```

Output a changelog to a file:

```bash
deploy-diff --from v1.4.2 --to v1.5.0 --output changelog.md
```

Include config file annotations:

```bash
deploy-diff --from v1.4.2 --to v1.5.0 --config-dir ./config
```

**Example output:**

```
## Changes: v1.4.2 → v1.5.0

### Features
- Add retry logic for failed API requests (#112)

### Bug Fixes
- Fix timeout handling in worker queue (#118)

### Config Changes
- config/settings.yaml: MAX_RETRIES changed from 3 → 5
- config/db.yaml: CONNECTION_POOL_SIZE changed from 10 → 20
```

---

## Configuration

`deploy-diff` looks for a `.deploydiff.yml` file in your project root for default settings:

```yaml
config_dir: ./config
output_format: markdown  # or "json", "plain"
tag_prefix: "v"
```

---

## License

MIT © 2024 Your Name