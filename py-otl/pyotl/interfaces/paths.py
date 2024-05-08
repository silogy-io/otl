from enum import Enum
from dataclasses import dataclass


class OtlPathType(Enum):

    TargetRelative = 1
    """
    Relative to the created target directory
    """

    GitRelative = 2
    """ 
    Path that is relative to git root 
    """

    Basic = 3
    """
    Path that is intepreted relative to the cwd -- a leading slash will be interpreted as an absolute path 
    """
    OtlRootRelative = 4
    """ 
    Path that is relative to the otl root 
    """


@dataclass
class OtlPath:
    path_type: OtlPathType
    path: str

    @classmethod
    def basic_path(cls, path: str):
        return cls(path_type=OtlPathType.Basic, path=path)

    @classmethod
    def target_relative(cls, path: str):
        return cls(path_type=OtlPathType.TargetRelative, path=path)

    @classmethod
    def git_relative(cls, path: str):
        return cls(path_type=OtlPathType.GitRelative, path=path)

    def __str__(self):
        return self.to_string()

    def to_string(self):
        if self.path_type == OtlPathType.GitRelative:
            return f"${{GIT_ROOT}}/{self.path}"
        elif self.path_type == OtlPathType.TargetRelative:
            return f"${{TARGET_ROOT}}/{self.path}"
        elif self.path_type == OtlPathType.OtlRootRelative:
            return f"${{OTL_ROOT}}/{self.path}"
        elif self.path_type == OtlPathType.Basic:
            return f"{self.path}"
        else:
            raise NotImplementedError(f"Unhandled variant {self.path_type}")
