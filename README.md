# cronlens

> Human-readable cron expression parser and next-run visualizer for the terminal

---

## Installation

```bash
pip install cronlens
```

Or with [pipx](https://pypa.github.io/pipx/) for isolated installs:

```bash
pipx install cronlens
```

---

## Usage

Parse a cron expression and see what it means in plain English:

```bash
$ cronlens "*/15 9-17 * * 1-5"

Expression : */15 9-17 * * 1-5
Description: Every 15 minutes, between 09:00 and 17:00, Monday through Friday

Next 5 runs:
  1. Mon, 14 Jul 2025 09:00:00
  2. Mon, 14 Jul 2025 09:15:00
  3. Mon, 14 Jul 2025 09:30:00
  4. Mon, 14 Jul 2025 09:45:00
  5. Mon, 14 Jul 2025 10:00:00
```

Show more upcoming runs with `--next`:

```bash
$ cronlens "0 0 * * *" --next 10
```

Validate an expression without output:

```bash
$ cronlens "invalid expression" --validate
Error: invalid cron expression
```

---

## Options

| Flag | Description |
|------|-------------|
| `--next N` | Show next N scheduled run times (default: 5) |
| `--validate` | Validate expression and exit |
| `--utc` | Display times in UTC |

---

## License

MIT © cronlens contributors