from fusesoc.main import Fusesoc, Config
from fusesoc.capi2.core import Core
from fusesoc.edalizer import Edalizer
from fusesoc.coremanager import DependencyError
import os
from importlib import import_module
from edalize.edatool import get_edatool
import os, sys
from typing import Dict, Any, Optional
from dataclasses import dataclass


def _get_core_friendly(cm: Fusesoc, name: str):
    matches = set()
    if not ":" in name:
        for core in cm.get_cores():
            (v, l, n, _) = core.split(":")
            if n.lower() == name.lower():
                matches.add(f"{v}:{l}:{n}")
        if len(matches) == 1:
            name = matches.pop()
        elif len(matches) > 1:
            _s = f"'{name}' is ambiguous. Potential matches: "
            _s += ", ".join(f"'{x}'" for x in matches)
            raise RuntimeError(_s)

    core = None
    try:

        core = cm.get_core(name)
    except RuntimeError as e:
        raise e
    except DependencyError as e:
        raise RuntimeError(
            f"{name!r} or any of its dependencies requires {e.value!r}, but "
            "this core was not found"
        )

    except SyntaxError as e:
        raise RuntimeError(f"Syntax error {str(e)}")

    return core


def get_edalizer(
    fs: Fusesoc, core: Core, flags: Dict[str, str], build_root: str
) -> Dict[str, Any]:

    work_root = fs.get_work_root(core, flags)

    if not fs.config.no_export:
        export_root = os.path.join(work_root, "src")

    else:
        export_root = None

    edam_file = os.path.join(work_root, core.name.sanitized_name + ".eda.yml")

    flow = core.get_flow(flags)

    backend_class = None
    if flow:
        try:
            backend_class = getattr(
                import_module(f"edalize.flows.{flow}"), flow.capitalize()
            )
        except ModuleNotFoundError:
            raise RuntimeError(f"Flow {flow!r} not found")
        except ImportError:
            raise RuntimeError("Selected Edalize version does not support the flow API")

    else:
        try:
            backend_class = get_edatool(flags["tool"])
        except ImportError:
            raise RuntimeError(f"Backend {flags['tool']!r} not found")

    print(backend_class)

    edalizer = Edalizer(
        toplevel=core.name,
        flags=flags,
        core_manager=fs.cm,
        work_root=work_root,
        export_root=export_root,
        system_name=fs.config.system_name,
        resolve_env_vars=fs.config.resolve_env_vars_early,
    )
    edam = edalizer.run()
    backend = backend_class(
        edam=edalizer.edam, work_root=build_root, verbose=fs.config.verbose
    )

    return edam


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stdout


def _memoize(func):
    cache = dict()

    def memoized_func(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return memoized_func


@dataclass(frozen=True)
class CompactFusesocData:
    """
    Compact collection of relevant fusesoc data, to be used by dependant tools
    """

    build_root: str
    edam: Dict[str, Any]
    actual_core_name: str

    @classmethod
    @_memoize
    def get_data(cls, target: str, core: str, inpbuild_root: Optional[str] = None):
        with HiddenPrints():
            target = "verilator_tb"
            config = Config(None)
            config.args_no_export = True
            if inpbuild_root:
                config.args_build_root = inpbuild_root
            fs = Fusesoc(config)
            core = _get_core_friendly(fs, core)
            build_root = os.path.join(fs.config.build_root, core.name.sanitized_name)
            flags = {"target": target}
            edam = get_edalizer(fs, core, flags, build_root)
            actual_core_name = core.name.sanitized_name
        return cls(build_root=build_root, edam=edam, actual_core_name=actual_core_name)


target = "verilator_tb"
name = "servant"
val = CompactFusesocData.get_data(target, core=name)
import pdb

pdb.set_trace()
CompactFusesocData.get_data(target, core=name)
CompactFusesocData.get_data(target, core=name)

# print(edalizer.run())
# print(config.build_root)
