from typing import Dict, ClassVar, List, Optional
from pyotl.interfaces import Target, TargetRef


class OtlRegistrar:
    registered_targets: ClassVar[Dict[str, "Target"]] = {}


def register_target(target: Target):
    OtlRegistrar.registered_targets[target.name] = target


def get_registered_target(target_ref: TargetRef) -> Optional[Target]:
    if target_ref in OtlRegistrar.registered_targets:
        return OtlRegistrar.registered_targets[target_ref]


def clear_registrar():
    OtlRegistrar.registered_targets = {}
