# Zander (PREN HSLU)
**Zämesetze and der HSLU**

Minimal Python project scaffold using uv and Python 3.11.

## Structure
| Route | Description |
| :-- | :-- |
| /data | Datasets and artifacts (example data) |
| /solver | Puzzle solver |

## Setup
### Install dependencies
```bash
uv sync
```

### Add packages
```bash
uv add <package>
uv add --group dev <package>
```

## Start
### Solver
```bash
uv run python -m solver
```

## TODOs PREN2
- Also rotate into frame (currently only transpose)
- Edges can be matched with 90 degrees as well (if there are no corners)
- Try with different values (roughening, ...)
