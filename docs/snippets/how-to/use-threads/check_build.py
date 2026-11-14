from __future__ import annotations

# --8<-- [start:example]
import sys
import sysconfig

free_threaded = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
gil_enabled = getattr(sys, "_is_gil_enabled", lambda: True)()
print(f"free-threaded build: {free_threaded}, GIL enabled: {gil_enabled}")
# --8<-- [end:example]
