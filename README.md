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
Prod
```bash
uv run python -m solver
```

Test
```bash
uv run python -m solver --test
```

Debug
```bash
uv run python -m solver <image-path>
```
