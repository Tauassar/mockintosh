#!/usr/bin/env python3
"""Command-line interface for Mockintosh using Click."""

import click
import logging
import os
from typing import List, Optional

from . import create_sample_config, handle_conversion, run_server


def setup_logging(quiet: bool, verbose: bool, logfile: Optional[str]) -> None:
    """Configure logging based on CLI options."""
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    fmt = "[%(asctime)s %(name)s %(levelname)s] %(message)s"
    logging.basicConfig(level=level, format=fmt)
    
    # Set critical level for noisy loggers
    for logger_name in ['pika', 'rsmq', 'botocore', 'boto3', 'urllib3.connectionpool']:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    
    # Add file handler if logfile specified
    if logfile:
        handler = logging.FileHandler(logfile)
        handler.setFormatter(logging.Formatter(fmt))
        logging.getLogger('').addHandler(handler)


@click.group()
@click.option('--quiet', '-q', is_flag=True, help='Less logging messages, only warnings and errors')
@click.option('--verbose', '-v', is_flag=True, help='More logging messages, including debug')
@click.option('--logfile', '-l', help='Also write log into a file')
@click.option('--bind', '-b', help='Address to specify the network interface')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def cli(ctx, quiet: bool, verbose: bool, logfile: Optional[str], bind: Optional[str], debug: bool):
    """Mockintosh - HTTP/API Mocking Framework
    
    A powerful tool for creating mock APIs and services for development and testing.
    """
    # Setup logging
    setup_logging(quiet, verbose, logfile)
    
    # Store context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['bind_address'] = bind
    ctx.obj['debug'] = debug


@cli.command()
@click.argument('filename', default='sample-config.yaml')
def sample_config(filename: str):
    """Generate a sample configuration file."""
    exit(create_sample_config(filename))


@cli.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
@click.argument('format', type=click.Choice(['json', 'yaml']), default='yaml')
def convert(source: str, output: str, format: str):
    """Convert OpenAPI Specification to Mockintosh config."""
    result = handle_conversion(source, [output, format])
    exit(0 if result else 1)


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--services', '-s', multiple=True, help='Specific services to run')
@click.option('--interceptors', '-i', multiple=True, help='Interceptor modules to load')
@click.option('--tags', '-t', multiple=True, help='Tags to enable')
@click.pass_context
def serve(ctx, config_file: str, services: List[str], interceptors: List[str], tags: List[str]):
    """Start the Mockintosh server with a configuration file."""
    debug_mode = ctx.obj.get('debug', False)
    bind_address = ctx.obj.get('bind_address')
    
    # Check for environment variables
    debug_mode = debug_mode or os.environ.get('DEBUG', False) or os.environ.get('MOCKINTOSH_DEBUG', False)
    
    exit(run_server(
        config_file=config_file,
        services=services,
        debug=bool(debug_mode),
        interceptors=interceptors,
        bind_address=bind_address,
        tags=tags
    ))


if __name__ == '__main__':
    cli()
