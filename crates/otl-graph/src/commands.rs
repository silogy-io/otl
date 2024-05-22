use allocative::Allocative;
use dupe::Dupe;
use hex::FromHexError;
use serde::{Deserialize, Serialize};
use sha1::{Digest, Sha1};

use std::{
    fmt,
    path::{Path, PathBuf},
    str::FromStr,
    sync::Arc,
};

use otl_core::OtlErr;
pub use otl_data::CommandOutput;
#[derive(Serialize, Deserialize, Clone, PartialEq, Eq, Hash, Debug, Allocative)]
pub struct Command {
    pub name: String,
    pub target_type: TargetType,
    pub script: Vec<String>,
    #[serde(default)]
    pub dependent_files: Vec<PathBuf>,
    #[serde(default)]
    pub dependencies: Vec<String>,
    #[serde(default)]
    pub outputs: Vec<String>,
    pub runtime: Runtime,
}

#[derive(Clone, PartialEq, Eq, Hash, Debug, Allocative)]
pub enum CommandRtStatus {
    /// This command, nor its dependencies, have started running
    Unscheduled,
    //
    Scheduled {
        scheduled_time: std::time::Instant,
    },
    Running {
        scheduled_time: std::time::Instant,
        started_time: std::time::Instant,
    },
    Finished {
        scheduled_time: std::time::Instant,
        started_time: std::time::Instant,
        finished_time: std::time::Instant,
    },
}

const DIGEST_LEN: usize = 20;
pub struct CommandDefDigest([u8; DIGEST_LEN]);

pub struct ExecDigest([u8; DIGEST_LEN]);

trait Digester: Sized {
    fn get_payload(&self) -> &[u8; DIGEST_LEN];
    fn new(val: [u8; DIGEST_LEN]) -> Self;
    fn to_string(&self) -> String {
        hex::encode(&self.get_payload())
    }
    fn from_str(value: impl AsRef<str>) -> Result<Self, DigestError> {
        let str = value.as_ref();
        let val = hex::decode(str)?;
        let rv =
            val.try_into()
                .map(|val| Self::new(val))
                .map_err(|err| DigestError::WrongPayloadSize {
                    expected: DIGEST_LEN,
                    observed: err.len(),
                });
        rv
    }
}

use thiserror::Error;
#[derive(Error, Debug)]
pub enum DigestError {
    #[error("Could not convert hex string to command digest due to str format")]
    FromHexError(#[from] FromHexError),
    #[error("Digest wasn't the right size")]
    WrongPayloadSize { expected: usize, observed: usize },
}

impl Digester for CommandDefDigest {
    fn new(val: [u8; DIGEST_LEN]) -> Self {
        Self(val)
    }
    fn get_payload(&self) -> &[u8; DIGEST_LEN] {
        &self.0
    }
}

impl Digester for ExecDigest {
    fn new(val: [u8; DIGEST_LEN]) -> Self {
        Self(val)
    }
    fn get_payload(&self) -> &[u8; DIGEST_LEN] {
        &self.0
    }
}

impl Command {
    pub fn def_digest(&self) -> CommandDefDigest {
        let mut hasher = Sha1::new();
        hasher.update(&self.name);
        hasher.update(&self.target_type.to_string());
        for line in self.script.iter() {
            hasher.update(line);
        }
        for dep in self.dependencies.iter() {
            hasher.update(dep);
        }

        let rv: [u8; 20] = hasher.finalize().into();
        CommandDefDigest(rv)
    }

    pub const fn script_file() -> &'static str {
        "command.sh"
    }

    pub const fn stderr_file() -> &'static str {
        "command.err"
    }

    pub const fn stdout_file() -> &'static str {
        "command.out"
    }

    pub fn default_target_root(&self, root: &Path) -> Result<PathBuf, OtlErr> {
        Ok(root.join("otl-out").join(&self.name))
    }

    pub fn script_contents(&self) -> impl Iterator<Item = String> + '_ {
        self.runtime
            .env
            .iter()
            .map(|(env_name, env_val)| format!("export {}={}", env_name, env_val))
            .chain(self.script.iter().cloned())
    }

    pub async fn get_status_from_fs(&self, root: &Path) -> Result<CommandOutput, OtlErr> {
        if let Ok(working_dir) = self.default_target_root(root) {
            let val = working_dir
                .exists()
                .then(|| working_dir.join("command.status"));
            if let Some(ile) = val {
                let val: CommandOutput = tokio::fs::read_to_string(ile)
                    .await
                    .map(|val| serde_json::from_str(val.as_str()))??;
                Ok(val)
            } else {
                Err(OtlErr::CommandCacheMiss)
            }
        } else {
            Err(OtlErr::CommandCacheMiss)
        }
    }
}

#[derive(Serialize, Deserialize, Clone, Dupe, PartialEq, Eq, Hash, Debug, Allocative)]
#[serde(rename_all = "lowercase")]
pub enum TargetType {
    Test,
    Stimulus,
    Build,
}

impl FromStr for TargetType {
    type Err = OtlErr;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "test" => Ok(TargetType::Test),
            "stimulus" => Ok(TargetType::Stimulus),
            "build" => Ok(TargetType::Build),
            _ => Err(OtlErr::BadTargetType(s.to_string())),
        }
    }
}

#[derive(Serialize, Deserialize, Clone, PartialEq, Eq, Hash, Debug, Allocative)]
pub struct Runtime {
    pub num_cpus: u32,
    pub max_memory_mb: u32,
    pub timeout: u32,
    pub env: std::collections::BTreeMap<String, String>,
}

impl fmt::Display for Command {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Command {{ name: {}, target_type: {}, script: {:?}, dependencies: {:?}, outputs: {:?}, runtime: {} }}", 
            self.name, self.target_type, self.script, self.dependencies, self.outputs, self.runtime)
    }
}

impl fmt::Display for TargetType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "{}",
            match self {
                TargetType::Test => "test",
                TargetType::Stimulus => "stimulus",
                TargetType::Build => "build",
            }
        )
    }
}

impl fmt::Display for Runtime {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "Runtime {{ num_cpus: {}, max_memory_mb: {}, timeout: {}, env: {:?} }}",
            self.num_cpus, self.max_memory_mb, self.timeout, self.env
        )
    }
}

#[derive(Clone, Dupe, PartialEq, Eq, Hash, Debug, Allocative)]
pub struct CommandScript(Arc<CommandScriptInner>);

#[derive(Clone, PartialEq, Eq, Hash, Debug, Allocative)]
pub(crate) struct CommandScriptInner {
    script: Vec<String>,
    deps: Vec<CommandScript>,
}

//pub async fn maybe_cache(command: &Command) -> Result<CommandOutput, OtlErr> {
//    if let Ok(command_out) = command.get_status_from_fs().await {
//        if command_out.passed() {
//            return Ok(command_out);
//        }
//    } else {
//        //pass
//    };
//
//    execute_command(command).await
//}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn deser_simple_yaml() {
        let yaml_data = include_str!("../../../examples/tests_only.otl.yaml");
        let script: Result<Vec<Command>, _> = serde_yaml::from_str(yaml_data);

        let _script = script.unwrap();
    }
}
