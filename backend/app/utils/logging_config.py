"""Logging Configuration"""
import logging
import sys

def setup_logging(app):
    """Setup logging configuration for the application."""
    
    # Get log level from config
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    
    # Create formatter
    formatter = logging.Formatter(app.config.get('LOG_FORMAT'))
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Configure app logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)
    
    # Configure root logger
    logging.getLogger().setLevel(log_level)
    logging.getLogger().addHandler(console_handler) 