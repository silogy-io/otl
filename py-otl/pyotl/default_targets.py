from dataclasses import dataclass, field
from pyotl.interfaces import Target, OtlPath, OtlTargetType, TargetRef
from typing import List, Dict, Optional


@dataclass
class raw_bash(Target):
    """
    Simple target for embedding raw bash commands in Otl

    Environment variables avaible are:
        * ${GIT_ROOT}: the git root of the current git workspace
        * ${OTL_ROOT}: the root of the otl-workspace -- by default, this will be ${GIT_ROOT}/otl
        * ${TARGET_ROOT}: the working space of the current target
    """

    cmds: List[str] = field(default_factory=list)
    deps: List[TargetRef] = field(default_factory=list)
    outputs: Dict[str, str] = field(default_factory=dict)
    debug_cmds: Optional[List[str]] = None

    def gen_script(self, debug: bool) -> List[str]:
        if debug and self.debug_cmds:
            return self.debug_cmds
        return self.cmds

    def dependencies(self) -> List[TargetRef]:
        return self.deps

    def get_outputs(self) -> Dict[str, OtlPath]:
        return {
            out_name: OtlPath.basic_path(out_path)
            for out_name, out_path in self.outputs.items()
        }


@dataclass
class run_spi(Target):
    """
    sanity test -- will move this to examples, eventually
    """

    seed: int

    def gen_script(self, debug: bool) -> List[str]:
        return ['echo "hello world"']

    def get_outputs(self) -> Dict[str, OtlPath]:
        return {"log": OtlPath.basic_path(f"{self.name}.log")}


@dataclass
class raw_bash_build(Target):
    cmds: List[str] = field(default_factory=list)

    @staticmethod
    def rule_type() -> OtlTargetType:
        return OtlTargetType.Build

    def gen_script(self, debug: bool) -> List[str]:
        return self.cmds
