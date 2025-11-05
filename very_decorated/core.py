import functools
import time
from typing import Callable, Any
from loguru import logger
import asyncio

def _get_args_and_vars(func: Callable, args: tuple, kwargs: dict, include_args: list[str] = None, include_vars: list[str] = None) -> list[str]:
    """Extract function arguments and instance variables for logging.
    
    Args:
        func: The function being decorated
        args: Function positional arguments
        kwargs: Function keyword arguments
        include_args: List of argument names to include
        include_vars: List of variable paths to include from instance
    
    Returns:
        List of formatted argument/variable strings
    """
    msg_parts = []
    
    # Get function signature to map args to names
    import inspect
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    
    # Add function arguments
    if include_args:
        for arg_name in include_args:
            if arg_name in bound_args.arguments:
                value = bound_args.arguments[arg_name]
                # Keep full values
                value_str = str(value)
                msg_parts.append(f"{arg_name}: {value_str}")
    
    # Add instance variables (like self.request.style)
    if include_vars and args and hasattr(args[0], '__dict__'):
        self_instance = args[0]  # First argument is usually 'self'
        for var_path in include_vars:
            try:
                # Handle dot notation like 'self.request.style'
                if var_path.startswith('self.'):
                    var_path = var_path[5:]  # Remove 'self.' prefix
                
                # Navigate the attribute path
                value = self_instance
                for attr in var_path.split('.'):
                    value = getattr(value, attr)
                
                # Keep full values
                value_str = str(value)
                msg_parts.append(f"{var_path}: {value_str}")
            except (AttributeError, TypeError):
                # Skip if attribute doesn't exist or can't be accessed
                continue
    
    return msg_parts


def log(display_name: str = None, include_args: list[str] = None, include_vars: list[str] = None, mode: str = "partial", output_name: str = None):
    """Decorator to log function entry, exit, and any exceptions.
    
    Args:
        display_name: Optional custom name to display in logs instead of function name
        include_args: List of argument names to include in the start log (e.g., ['id', 'name'])
        include_vars: List of variable paths to include from instance (e.g., ['self.request.style', 'self.project_id'])
        mode: Logging mode - "full" logs start and end, "partial" only logs end or error (default: "partial")
        output_name: Optional name for logging function output. If provided, logs return value as "<output_name>: <output>"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            func_name = display_name or func.__name__
            
            # Validate mode parameter
            if mode not in ["full", "partial"]:
                raise ValueError(f"mode must be 'full' or 'partial', got '{mode}'")
            
            # Only build and log start message if mode is "full"
            if mode == "full":
                start_msg = f"Starting {func_name}"
                msg_parts = _get_args_and_vars(func, args, kwargs, include_args, include_vars)
                if msg_parts:
                    start_msg += f". {', '.join(msg_parts)}"
                logger.opt(depth=1).info(start_msg)
            
            try:
                result = await func(*args, **kwargs)
                
                # Build success message
                success_msg = f"Finished {func_name}"
                msg_parts = []
                
                # In full mode, only show output_name; in partial mode, show args/vars too
                if mode == "partial":
                    msg_parts = _get_args_and_vars(func, args, kwargs, include_args, include_vars)
                
                # Add output if output_name is provided
                if output_name is not None:
                    msg_parts.append(f"{output_name}: {result}")
                
                if msg_parts:
                    success_msg += f". {', '.join(msg_parts)}"
                
                logger.opt(depth=1).info(success_msg)
                return result
                
            except Exception as e:
                # Build error message with args and vars
                error_msg = f"Error in {func_name}: {str(e)}"
                msg_parts = _get_args_and_vars(func, args, kwargs, include_args, include_vars)
                if msg_parts:
                    error_msg += f". {', '.join(msg_parts)}"
                
                logger.opt(depth=1).error(error_msg)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            func_name = display_name or func.__name__
            
            # Validate mode parameter
            if mode not in ["full", "partial"]:
                raise ValueError(f"mode must be 'full' or 'partial', got '{mode}'")
            
            # Only build and log start message if mode is "full"
            if mode == "full":
                start_msg = f"Starting {func_name}"
                msg_parts = _get_args_and_vars(func, args, kwargs, include_args, include_vars)
                if msg_parts:
                    start_msg += f". {', '.join(msg_parts)}"
                logger.opt(depth=1).info(start_msg)
            
            try:
                result = func(*args, **kwargs)
                
                # Build success message
                success_msg = f"Finished {func_name}"
                msg_parts = []
                
                # In full mode, only show output_name; in partial mode, show args/vars too
                if mode == "partial":
                    msg_parts = _get_args_and_vars(func, args, kwargs, include_args, include_vars)
                
                # Add output if output_name is provided
                if output_name is not None:
                    msg_parts.append(f"{output_name}: {result}")
                
                if msg_parts:
                    success_msg += f". {', '.join(msg_parts)}"
                
                logger.opt(depth=1).info(success_msg)
                return result
                
            except Exception as e:
                # Build error message with args and vars
                error_msg = f"Error in {func_name}: {str(e)}"
                msg_parts = _get_args_and_vars(func, args, kwargs, include_args, include_vars)
                if msg_parts:
                    error_msg += f". {', '.join(msg_parts)}"
                
                logger.opt(depth=1).error(error_msg)
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator


def timer(display_name: str = None):
    """Decorator to measure and log function execution time.
    
    Args:
        display_name: Optional custom name to display in logs instead of function name
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            func_name = display_name or func.__name__
            
            start_time = time.perf_counter()
            result = await func(*args, **kwargs)
            execution_time = time.perf_counter() - start_time
            logger.opt(depth=1).info(f"Finished {func_name} in {execution_time:.6f} seconds")
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            func_name = display_name or func.__name__
            
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            execution_time = time.perf_counter() - start_time
            logger.opt(depth=1).info(f"Finished {func_name} in {execution_time:.6f} seconds")
            return result
        

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator


