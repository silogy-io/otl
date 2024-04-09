from dataclasses import dataclass
from typing import Dict


@dataclass
class RuntimeRequirements:
    num_cpus: int
    # This number is in MB
    max_memory_mb: int
    # timeout in seconds
    timeout: int
    env: Dict[str, str]

    @classmethod
    def default(cls, env: Dict[str, str]):
        return cls(num_cpus=1, max_memory_mb=1024, timeout=600, env=env)

    @classmethod
    def from_dict(cls, indict: dict[str, str]):
        num_cpus = indict['num_cpus']
        max_memory_mb = indict['max_memory_mb']
        timeout = indict['timeout']
        env = indict['env']

        return cls(num_cpus=num_cpus, max_memory_mb=max_memory_mb, timeout=timeout, env=env)
