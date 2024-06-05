tonic::include_proto!("executed_tests");
use allocative::Allocative;
use std::path::PathBuf;
impl ArtifactPointer {
    pub fn file_artifact(artifact_name: String, path: PathBuf) -> Self {
        let abs_path = path.to_string_lossy().to_string();
        let pointer = Some(artifact_pointer::Pointer::Path(abs_path));
        Self {
            artifact_name,
            pointer,
        }
    }
}

#[derive(Allocative)]
pub enum ExecutedTestResult {
    Success(TestResult),
    MissingFiles {
        /// this contains the test result, with all the files that exist
        test_result: TestResult,
        /// artifacts that are missing -- will always point to the filesystem
        missing_artifacts: Vec<ArtifactPointer>,
    },
}

impl ExecutedTestResult {
    pub fn to_test_result(self) -> TestOutputs {
        match self {
            Self::Success(val) => val.outputs.unwrap(),
            Self::MissingFiles { test_result, .. } => test_result.outputs.unwrap(),
        }
    }
    pub fn get_retcode(&self) -> i32 {
        match self {
            Self::Success(val) => val.outputs.as_ref().map(|val| val.exit_code).unwrap(),
            Self::MissingFiles { test_result, .. } => test_result
                .outputs
                .as_ref()
                .map(|val| val.exit_code)
                .unwrap(),
        }
    }
}

impl TestOutputs {
    pub fn passed(&self) -> bool {
        self.exit_code == 0
    }
}
