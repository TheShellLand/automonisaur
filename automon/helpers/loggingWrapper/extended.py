import inspect
import logging
import warnings


class ExtendedLogger(logging.Logger):
    """
    A custom logger class that extends the standard logging.Logger.

    This class enhances the standard logger by automatically capturing the
    calling function name and line number even when the log message is
    generated from within a helper function.

    Usage:
        # Create an instance of ExtendedLogger
        logger = ExtendedLogger("my_custom_logger")

        # Example of logging a message (funcName and lineno will be automatically captured)
        logger.info("This is a log message from my_custom_logger.")
    """

    warnings.warn(f"Do not use. This does not work")

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        """
        Internal logging method, overriding the original to automatically
        capture calling function name and line number.

        Args:
            level: The logging level (e.g., logging.INFO, logging.ERROR).
            msg: The log message format string.
            args: Arguments to the log message format string.
            exc_info: Exception info (if any).
            extra: Extra information to include in the log record.
            stack_info: Whether to include stack info.
            stacklevel:  The stack level to use to determine where the log call happened.
                         Increase this to move further up the call stack.  Critical to get correct
                         funcName and lineno!
        """
        # Get frame info.  We start looking 2 frames up because _log itself is on the stack, and
        # it's being called by a method of ExtendedLogger.
        frame, filename, lineno, function_name, lines, index = inspect.getouterframes(inspect.currentframe())[
            stacklevel]

        if extra is None:
            extra = {}
        # Add calling function name and line number to extra information
        extra.setdefault('func', function_name)
        extra.setdefault('lineno', lineno)

        # Call the original _log method with the modified extra information
        super()._log(level, msg, args, exc_info, extra, stack_info)
