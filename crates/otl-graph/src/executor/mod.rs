use std::sync::Arc;

use crate::Command;
use dice::{DiceData, DiceDataBuilder, UserComputationData};

use otl_data::Event;

use tokio::sync::mpsc::Sender;
mod common;
#[cfg(feature = "docker")]
mod docker;
mod local;

use anyhow;
use async_trait::async_trait;
pub use local::LocalExecutorBuilder;

#[async_trait]
pub trait Executor: Send + Sync {
    async fn execute_commands(
        &self,
        command: Arc<Command>,
        tx: Sender<Event>,
        dice_data: &UserComputationData,
    ) -> anyhow::Result<Event>;
}

pub trait SetExecutor {
    fn set_executor(&mut self, exec: Arc<dyn Executor>);
}

pub trait GetExecutor {
    fn get_executor(&self) -> Arc<dyn Executor>;
}

impl SetExecutor for DiceDataBuilder {
    fn set_executor(&mut self, exec: Arc<dyn Executor>) {
        self.set(exec)
    }
}

impl GetExecutor for DiceData {
    fn get_executor(&self) -> Arc<dyn Executor> {
        self.get::<Arc<dyn Executor>>()
            .expect("Channel should be set")
            .clone()
    }
}
