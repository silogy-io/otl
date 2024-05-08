from dataclasses import dataclass, field
from pyotl.interfaces import Target, OtlPath, OtlTargetType, TargetRef
from typing import List, Dict, Optional, cast
from pyotl.fusesoc_utils import CompactFusesocData
from pyotl.registrar import get_registered_target, register_target


@dataclass
class fusesoc_build(Target):
    target: str
    core_name: str
    build_root: Optional[str] = None
    backend_args: List[str] = []

    # populated at runtime

    def __post_init__(self):
        register_target(self)

    @staticmethod
    def rule_type() -> OtlTargetType:
        return OtlTargetType.Build

    def gen_script(self, debug: bool) -> List[str]:
        backend_args = " ".join(self.backend_args) if self.backend_args else ""

        return [
            f"fusesoc run --build --target={self.target} {self.core_name} {backend_args}"
        ]

    def get_outputs(self) -> Dict[str, OtlPath]:
        fusesoc_data = CompactFusesocData.get_data(self.target, self.core_name)
        build_root = fusesoc_data.build_root
        return {"build_dir": OtlPath.basic_path(build_root)}


@dataclass
class simple_fusesoc_verilator_run(Target):
    fusesoc_build: TargetRef
    runtime_args: Dict[str, str]
    """
    """

    # populated at runtime

    @staticmethod
    def rule_type() -> OtlTargetType:
        return OtlTargetType.Build

    def dependencies(self) -> List[TargetRef]:
        return [self.fusesoc_build]

    def gen_script(self, debug: bool) -> List[str]:

        build_target = cast(
            Optional[fusesoc_build], get_registered_target(self.fusesoc_build)
        )

        if not build_target:
            raise RuntimeError(f"No build target named{self.fusesoc_build} found")
        else:
            fusesoc_data = CompactFusesocData.get_data(
                build_target.target, build_target.core_name
            )

            edam = fusesoc_data.edam

            toplevel = edam["toplevel"]
            all_parameters = edam["parameters"]
            sim_path = f"{fusesoc_data.build_root}/V{toplevel}"

            formatted_args = []
            for arg, val in self.runtime_args:
                if arg not in all_parameters:
                    raise RuntimeError(f"Supplied incorrent argument {arg}")
                else:
                    param_type = all_parameters[arg]["paramtype"]
                    if param_type == "plusarg":
                        formatted_args += ["+{}={}".format(arg, val)]
                    elif param_type == "cmdlinearg":
                        formatted_args += ["--{}={}".format(arg, val)]

            # for key, value in self.plusarg.items():
            #
            # for key, value in self.cmdlinearg.items():
            #    self.args += ["--{}={}".format(key, self._param_value_str(value))]

            arg_string = " ".join(formatted_args)
            return [f"{sim_path} {arg_string}"]
