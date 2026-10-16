"""Use the configured Blender Streamable HTTP server through its existing SDK."""

import asyncio
from contextlib import asynccontextmanager
from datetime import timedelta
import importlib.util
import ipaddress
import json
import os
from pathlib import Path
import site
import sys
import tomllib
from urllib.parse import urlsplit


def _load_sdk():
    if importlib.util.find_spec('mcp') is None:
        configured = os.environ.get('QCBLENDER_MCP_RUNTIME')
        if configured:
            candidates = [Path(configured)]
        else:
            base = Path(os.environ.get('APPDATA', Path.home() / 'AppData/Roaming'))
            candidates = sorted((base / 'Blender Foundation/Blender').glob(
                '*/extensions/*/blender_mcp_integration/_vendor/runtime'), reverse=True)
        for runtime in candidates:
            if not (runtime / 'mcp/client/streamable_http.py').is_file():
                continue
            native = list((runtime / 'pydantic_core').glob('*.pyd'))
            tag = f'cp{sys.version_info.major}{sys.version_info.minor}'
            if native and not any(tag in path.name for path in native):
                continue
            sys.path.insert(0, str(runtime))
            site.addsitedir(str(runtime))
            break
        else:
            raise RuntimeError('No compatible existing MCP SDK found. Use Blender bundled Python '
                               'or set QCBLENDER_MCP_RUNTIME to an installed compatible runtime; '
                               'no dependencies were installed.')
    import httpx
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client
    return httpx, ClientSession, streamable_http_client


def _connection(config_path=None):
    path = Path(config_path) if config_path else Path.home() / '.codex/config.toml'
    with path.open('rb') as stream:
        config = tomllib.load(stream).get('mcp_servers', {}).get('blender', {})
    url = config.get('url', '')
    parsed = urlsplit(url)
    try:
        loopback = parsed.hostname == 'localhost' or ipaddress.ip_address(parsed.hostname).is_loopback
    except ValueError:
        loopback = False
    if (parsed.scheme not in {'http', 'https'} or not loopback or parsed.username
            or parsed.password or parsed.query or parsed.fragment):
        raise ValueError('mcp_servers.blender.url must be a loopback HTTP endpoint without credentials or query')
    headers = dict(config.get('http_headers', {}))
    for name, variable in config.get('env_http_headers', {}).items():
        if variable not in os.environ:
            raise ValueError('A configured Blender MCP header environment variable is missing')
        headers[name] = os.environ[variable]
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in headers.items()):
        raise ValueError('Blender MCP HTTP headers must contain string names and values')
    return url, headers


@asynccontextmanager
async def _session(config_path, timeout):
    httpx, ClientSession, streamable_http_client = _load_sdk()
    url, headers = _connection(config_path)
    async with httpx.AsyncClient(headers=headers, trust_env=False, timeout=timeout) as http:
        async with streamable_http_client(url, http_client=http) as (read, write, _):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=timeout)) as session:
                await session.initialize()
                yield session


async def _tools(session):
    tools = []
    cursor = None
    while True:
        page = await session.list_tools(cursor=cursor)
        tools.extend(tool.model_dump(mode='json', by_alias=True, exclude_none=True) for tool in page.tools)
        cursor = page.nextCursor
        if not cursor:
            return tools


def _run(coroutine):
    try:
        return asyncio.run(coroutine)
    except (OSError, ValueError, RuntimeError, ImportError):
        raise
    except Exception as error:
        # SDK transport exceptions can contain request headers. Do not print their text.
        pending, kinds = [error], []
        while pending:
            item = pending.pop()
            if isinstance(item, BaseExceptionGroup):
                pending.extend(item.exceptions)
                continue
            status = getattr(getattr(item, 'response', None), 'status_code', None)
            kinds.append(type(item).__name__ + (f' HTTP {status}' if status else ''))
        raise RuntimeError(f'Blender MCP request failed ({", ".join(kinds)}); '
                           'check that the configured service is running and authenticated') from None


def discover(config_path=None, timeout=30):
    """Return tools/list metadata from the real configured MCP server."""
    async def execute():
        async with _session(config_path, timeout) as session:
            return await _tools(session)
    return _run(execute())


def call_tool(name, arguments=None, config_path=None, timeout=120):
    """Return the MCP CallToolResult as JSON data, including isError/content."""
    async def execute():
        async with _session(config_path, timeout) as session:
            return (await session.call_tool(name, arguments or {})).model_dump(
                mode='json', by_alias=True, exclude_none=True)
    return _run(execute())


def run_operation(request, repo, config_path=None, timeout=120):
    """Discover the interactive Python tool and execute blender_ops.dispatch(request)."""
    script = Path(repo).resolve() / 'tools/dev_workflow/blender_ops.py'
    if not script.is_file():
        raise FileNotFoundError(f'Blender operation dispatcher not found: {script}')
    code = (
        'import importlib.util, json, sys\n'
        f'_spec = importlib.util.spec_from_file_location("qcblender_dev_ops", {str(script)!r})\n'
        '_ops = importlib.util.module_from_spec(_spec)\n'
        'sys.modules[_spec.name] = _ops\n'
        '_spec.loader.exec_module(_ops)\n'
        f'result = _ops.dispatch(json.loads({json.dumps(request, ensure_ascii=False)!r}))\n'
    )
    async def execute():
        async with _session(config_path, timeout) as session:
            tools = await _tools(session)
            tool = next((item for item in tools if item['name'] == 'execute_blender_code'), None)
            if tool is None or 'code' not in tool.get('inputSchema', {}).get('properties', {}):
                raise RuntimeError('Configured MCP server has no interactive execute_blender_code(code) tool')
            response = await session.call_tool(tool['name'], {'code': code})
            if response.isError:
                raise RuntimeError('Blender MCP Python execution failed; operation did not complete')
            data = response.structuredContent
            if data is None:
                texts = [item.text for item in response.content if item.type == 'text']
                if not texts:
                    raise RuntimeError('Blender MCP returned no structured operation result')
                data = json.loads(texts[0])
            if data.get('status') != 'ok':
                raise RuntimeError(f"Blender operation failed: {data.get('message', 'unknown execution error')}")
            return data['result']
    return _run(execute())
