#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
.. module:: __init__
    :synopsis: the top-level module of Mockintosh.
"""

import atexit
import json
import logging
import os
import shutil
import signal
import sys
from os import path, environ
from typing import (
    Union,
    Tuple,
    List,
    Dict,
    Any,
    Optional
)

from prance import ValidationError  # type: ignore
from prance.util.url import ResolutionError  # type: ignore

from .constants import PROGRAM
from .definition import Definition
from .helpers import _nostderr, _import_from
from .replicas import Request, Response  # noqa: F401
from .servers import HttpServer, TornadoImpl
from .templating import RenderingQueue, RenderingJob
from .transpilers import OASToConfigTranspiler

__location__ = path.abspath(path.dirname(__file__))
with open(os.path.join(__location__, "res", "version.txt")) as fp:
    __version__ = fp.read().strip()

should_cov = environ.get('COVERAGE_PROCESS_START', False)
cov_no_run = environ.get('COVERAGE_NO_RUN', False)


def get_schema() -> Dict[str, Any]:
    """Load and return the JSON schema for validation."""
    schema_path = path.join(__location__, 'schema.json')
    try:
        with open(schema_path, 'r') as file:
            schema_text = file.read()
            logging.debug('JSON schema: %s', schema_text)
            return json.loads(schema_text)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error('Failed to load schema: %s', e)
        raise


def import_interceptors(interceptors: Optional[List[List[str]]]) -> List[Any]:
    """Import interceptor modules dynamically."""
    imported_interceptors = []
    if interceptors is not None:
        if 'unittest' in sys.modules.keys():
            tests_dir = path.join(__location__, '../tests')
            sys.path.append(tests_dir)
        for interceptor in interceptors:
            module, name = interceptor[0].rsplit('.', 1)
            imported_interceptors.append(_import_from(module, name))
    return imported_interceptors


def start_render_queue() -> Tuple[RenderingQueue, RenderingJob]:
    """Start the rendering queue and job thread."""
    queue = RenderingQueue()
    render_job = RenderingJob(queue)
    render_job.daemon = True
    render_job.start()
    return queue, render_job


def setup_signal_handlers(http_server: HttpServer, render_thread: RenderingJob) -> List[bool]:
    """Setup signal handlers for graceful shutdown and restart."""
    do_restart = [False]  # mutable list for closure
    
    try:
        prev_handler = signal.getsignal(signal.SIGHUP)

        def sighup_handler(num: int, frame: Any) -> None:
            """Handle SIGHUP signal for graceful restart."""
            logging.info("Received SIGHUP")
            http_server.stop()
            render_thread.kill()
            signal.signal(signal.SIGHUP, prev_handler)
            do_restart[0] = True

        signal.signal(signal.SIGHUP, prev_handler)
    except AttributeError:
        logging.info("No SIGHUP support on this machine")
    
    return do_restart


def run(
        source: str,
        is_file: bool = True,
        debug: bool = False,
        interceptors: tuple = (),
        address: str = '',
        services_list: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        load_override: Optional[Dict[str, Any]] = None
) -> bool:
    """Main server run function."""
    if services_list is None:
        services_list = []
    if tags is None:
        tags = []
    
    queue, render_thread = start_render_queue()

    if address:
        logging.info('Bind address: %s', address)
    
    schema = get_schema()

    try:
        definition = Definition(source, schema, queue, is_file=is_file, load_override=load_override)
        http_server = HttpServer(
            definition,
            TornadoImpl(),
            debug=debug,
            interceptors=interceptors,
            address=address,
            services_list=tuple(services_list),  # Convert to tuple as expected
            tags=tags
        )
    except Exception as e:
        logging.exception('Mock server loading error: %s', e)
        with _nostderr():
            raise

    do_restart = setup_signal_handlers(http_server, render_thread)
    http_server.run()
    return do_restart[0]


def _gracefully_exit(num: int, frame: Any) -> None:
    """Handle graceful exit with coverage cleanup."""
    atexit._run_exitfuncs()
    if should_cov:
        sys.exit()


def _cov_exit(cov: Any) -> None:
    """Handle coverage cleanup on exit."""
    if should_cov:
        logging.debug('Stopping coverage')
        cov.stop()
        cov.save()


def _setup_coverage() -> Optional[Any]:
    """Setup coverage monitoring if enabled."""
    if not should_cov:
        return None
    
    signal.signal(signal.SIGTERM, _gracefully_exit)
    logging.debug('Starting coverage')
    
    try:
        from coverage import Coverage
        cov = Coverage(data_suffix=True, config_file='.coveragerc')
        cov._warn_no_data = True
        cov._warn_unimported_source = True
        cov.start()
        atexit.register(_cov_exit, cov)
        return cov
    except ImportError:
        logging.warning('Coverage module not available')
        return None


def create_sample_config(filename: str) -> int:
    """Create a sample configuration file."""
    try:
        fname = os.path.abspath(filename)
        shutil.copy(os.path.join(__location__, "res", "sample.yml"), fname)
        logging.info("Created sample configuration file in %r", fname)
        logging.info("To run it, use the following command:\n    mockintosh %s", os.path.basename(fname))
        return 0
    except (FileNotFoundError, PermissionError) as e:
        logging.error("Failed to create sample config: %s", e)
        return 1


def handle_conversion(source: str, convert_args: List[str]) -> Union[str, Dict[str, Any]]:
    """Handle OpenAPI to Mockintosh config conversion."""
    if len(convert_args) < 2:
        convert_args.append('yaml')
    elif convert_args[1] != 'json':
        convert_args[1] = 'yaml'

    logging.info(
        "Converting OpenAPI Specification %s to ./%s in %s format...",
        source,
        convert_args[0],
        convert_args[1].upper()
    )
    target_path = _handle_oas_input(source, convert_args)
    logging.info("The transpiled config %s is ready at %s", convert_args[1].upper(), target_path)
    return target_path


def _handle_oas_input(source: str, convert_args: List[str], direct: bool = False) -> Union[str, dict]:
    """Handle OpenAPI Specification input and conversion."""
    oas_transpiler = OASToConfigTranspiler(source, convert_args)
    return oas_transpiler.transpile(direct=direct)


def handle_auto_conversion(source: str) -> Optional[Dict[str, Any]]:
    """Handle automatic OpenAPI to Mockintosh config conversion."""
    try:
        load_override = _handle_oas_input(source, ['config.yaml', 'yaml'], True)
        if isinstance(load_override, dict):
            logging.info("Automatically transpiled the config YAML from OpenAPI Specification.")
            return load_override
        else:
            logging.debug("OpenAPI conversion returned non-dict, defaulting to Mockintosh config.")
            return None
    except (ValidationError, AttributeError):
        logging.debug("The input is not a valid OpenAPI Specification, defaulting to Mockintosh config.")
        return None
    except ResolutionError:
        logging.debug("OpenAPI resolution error, continuing with Mockintosh config.")
        return None


def run_server(
    config_file: str,
    services: Optional[List[str]] = None,
    debug: bool = False,
    interceptors: Optional[List[str]] = None,
    bind_address: Optional[str] = None,
    tags: Optional[List[str]] = None,
    load_override: Optional[Dict[str, Any]] = None
) -> int:
    """Run the Mockintosh server with the given configuration."""
    # Setup coverage if enabled
    _setup_coverage()
    
    # Check debug mode
    debug_mode = debug or environ.get('DEBUG', False) or environ.get('MOCKINTOSH_DEBUG', False)
    if debug_mode:
        logging.debug('Tornado Web Server\'s debug mode is enabled!')

    # Handle auto-conversion or normal startup
    if load_override is None:
        load_override = handle_auto_conversion(config_file)
    
    logging.info("%s v%s is starting...", PROGRAM.capitalize(), __version__)

    if not cov_no_run:
        while run(config_file, debug=bool(debug_mode), interceptors=tuple(interceptors or ()), 
                  address=bind_address or '', services_list=services, tags=tags, 
                  load_override=load_override):
            logging.info("Restarting...")
    
    return 0


def demo_run() -> None:
    """Generate demo config and run it immediately (Windows compatibility)."""
    import tempfile
    fname = tempfile.mktemp(prefix="mock-config-", suffix=".yaml")
    try:
        create_sample_config(fname)
        run_server(fname)
    finally:
        # Cleanup temp file
        try:
            os.unlink(fname)
        except OSError:
            pass
