"""Start the existing enabled Blender MCP integration after loading a project.

Pass this file to ``session start --script``. Verify readiness using ``mcp``;
this script changes service state only, never preferences or client credentials.
"""
import importlib
import json
import os


def start_enabled_service():
    import bpy
    names = [addon.module for addon in bpy.context.preferences.addons
             if addon.module.endswith('.blender_mcp_integration')]
    if len(names) != 1:
        raise RuntimeError('Expected one enabled Blender MCP integration')
    module = importlib.import_module(names[0])
    running = module.SERVICE.process is not None
    if not running:
        module.start_service()
    return dict(status='Passed', pid=os.getpid(), service_requested=True, already_running=running)


def _start():
    try:
        result = start_enabled_service()
    except Exception as error:
        result = dict(status='Failed', error_type=type(error).__name__,
                      reason='MCP service start failed; inspect the integration preferences')
    print(json.dumps(result), flush=True)
    return None


if __name__ == '__main__':
    import bpy
    bpy.app.timers.register(_start, first_interval=3)
