# very-decorated

Useful decorators for logging and timing functions with support for both sync and async functions.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/xiveere/very-decorated.git
```

## Features

- **`@log`** - Decorator for logging function entry, exit, and exceptions
- **`@timer`** - Decorator for measuring and logging function execution time
- Full support for both synchronous and asynchronous functions
- Customizable logging modes and parameter inclusion

## Usage

### Basic Logging

```python
from very-decorated import log

@log()
async def my_function():
    # Your code here
    pass
```

### Logging with Arguments

```python
from very-decorated import log

@log(include_args=["user_id", "name"])
def process_user(user_id: int, name: str):
    # Logs will include user_id and name values
    pass
```

### Logging with Instance Variables

```python
from very-decorated import log

class MyService:
    @log(include_vars=["self.request.style", "self.project_id"])
    async def process(self):
        # Logs will include self.request.style and self.project_id
        pass
```

### Full Logging Mode

```python
from very-decorated import log

@log(mode="full")  # Logs both start and end
def my_function():
    pass
```

By default, `mode="partial"` only logs the end or errors.

### Timer Decorator

```python
from very-decorated import timer

@timer()
async def slow_function():
    # Execution time will be logged
    pass

@timer(display_name="Custom Name")
def another_function():
    pass
```

## API Reference

### `@log(display_name=None, include_args=None, include_vars=None, mode="partial")`

Decorator to log function entry, exit, and any exceptions.

**Parameters:**
- `display_name` (str, optional): Custom name to display in logs instead of function name
- `include_args` (list[str], optional): List of argument names to include in logs (e.g., `['id', 'name']`)
- `include_vars` (list[str], optional): List of variable paths to include from instance (e.g., `['self.request.style', 'self.project_id']`)
- `mode` (str): Logging mode - `"full"` logs start and end, `"partial"` only logs end or error (default: `"partial"`)

### `@timer(display_name=None)`

Decorator to measure and log function execution time.

**Parameters:**
- `display_name` (str, optional): Custom name to display in logs instead of function name

## Requirements

- Python >= 3.8
- loguru >= 0.6.0

## License

MIT License

