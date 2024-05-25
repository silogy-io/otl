use allocative::Allocative;
use dice::DiceError;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::PyErr;

use thiserror::Error;

#[derive(Error, Debug)]
pub enum OtlErr {
    #[error("unknown error")]
    Unknown,
    #[error("Dice failure {0}")]
    DiceFail(#[from] DiceError),
    #[error("IoError {0}")]
    IoError(#[from] std::io::Error),
    #[error("Serde yaml error {0}")]
    SerdeYamlError(#[from] serde_yaml::Error),
    #[error("Serde json error {0}")]
    SerdeJsonError(#[from] serde_json::Error),
    #[error("Command cache miss")]
    CommandCacheMiss,
    #[error("Invalid target type {0}")]
    BadTargetType(String),
    #[error("Executor failed to execute with error : {0}")]
    ExecutorFailed(String),
    #[error("Dependency for a command named {missing_dep_name} was found, but no such command was declared")]
    MissingCommandDependency { missing_dep_name: String },
    #[error("Dependency for a command named {missing_file_name} was found, but no such command was declared")]
    MissingFileDependency { missing_file_name: String },
    #[error("Setting commands failed; reason is {reason}")]
    CommandSettingFailed { reason: String },
}

impl Allocative for OtlErr {
    fn visit<'a, 'b: 'a>(&self, visitor: &'a mut allocative::Visitor<'b>) {
        let vis = visitor.enter_self(&self);
        vis.exit();
    }
}

impl From<OtlErr> for PyErr {
    fn from(otl_err: OtlErr) -> Self {
        let otl_string = otl_err.to_string();
        PyRuntimeError::new_err(otl_string)
    }
}
