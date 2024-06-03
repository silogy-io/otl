use smelt_core::SmeltErr;
use smelt_data::client_commands::ClientCommand;
use smelt_data::{client_commands::ConfigureSmelt, Event};

use prost::Message;
use pyo3::{
    exceptions::PyRuntimeError,
    prelude::*,
    types::{PyBytes, PyType},
};
use smelt_events::{ClientCommandBundle, ClientCommandResp, EventStreams};
use smelt_graph::{spawn_graph_server, SmeltServerHandle};

use std::sync::Arc;
use tokio::sync::mpsc::{error::TryRecvError, Receiver, UnboundedSender};

pub fn arc_err_to_py(smelt_err: Arc<SmeltErr>) -> PyErr {
    let smelt_string = smelt_err.to_string();
    PyRuntimeError::new_err(smelt_string)
}

/// A Python module implemented in Rust.
#[pymodule]
fn pysmelt(_py: Python, m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyController>()?;
    m.add_class::<PyEventStream>()?;
    Ok(())
}

#[pyclass]
pub struct PyController {
    handle: SmeltServerHandle,
}

#[pyclass]
pub struct PyEventStream {
    recv_chan: Receiver<Event>,
    done: bool,
    exhausted: bool,
}

impl PyEventStream {
    pub(crate) fn create_subscriber(recv_chan: Receiver<Event>) -> Self {
        Self {
            recv_chan,
            done: false,
            exhausted: false,
        }
    }
}

fn client_channel_err(_in_err: impl std::error::Error) -> PyErr {
    PyRuntimeError::new_err("Channel error trying to send a command to the client")
}

fn handle_client_resp(resp: Result<ClientCommandResp, impl std::error::Error>) -> PyResult<()> {
    match resp {
        Ok(Ok(())) => Ok(()),
        Ok(Err(str)) => Err(PyRuntimeError::new_err(format!(
            "Client command failed with error {str}"
        ))),
        Err(err) => Err(PyRuntimeError::new_err(err.to_string())),
    }
}

fn submit_message(
    tx_client: &UnboundedSender<ClientCommandBundle>,
    message: ClientCommand,
) -> Result<EventStreams, PyErr> {
    let (bundle, recv) = ClientCommandBundle::from_message(message);

    tx_client.send(bundle).map_err(client_channel_err)?;
    Ok(recv)
}

#[pymethods]
impl PyController {
    #[new]
    #[classmethod]
    pub fn new(_cls: Bound<'_, PyType>, serialized_cfg: Vec<u8>) -> PyResult<Self> {
        let cfg: ConfigureSmelt =
            ConfigureSmelt::decode(serialized_cfg.as_slice()).expect("Malformed cfg message");

        let handle = spawn_graph_server(cfg);
        Ok(PyController { handle })
    }

    pub fn set_graph(&self, graph: String) -> PyResult<()> {
        let EventStreams { sync_chan, .. } =
            submit_message(&self.handle.tx_client, ClientCommand::send_graph(graph))?;

        let resp = sync_chan.blocking_recv();
        handle_client_resp(resp)
    }

    pub fn run_all_tests(&self, tt: String) -> PyResult<PyEventStream> {
        self.run_tests(ClientCommand::execute_type(tt))
    }

    pub fn run_one_test(&self, test: String) -> PyResult<PyEventStream> {
        self.run_tests(ClientCommand::execute_command(test))
    }

    pub fn run_many_tests(&self, tests: Vec<String>) -> PyResult<PyEventStream> {
        self.run_tests(ClientCommand::execute_many(tests))
    }
}

impl PyController {
    fn run_tests(&self, command: ClientCommand) -> PyResult<PyEventStream> {
        let EventStreams { event_stream, .. } =
            submit_message(&self.handle.tx_client, command).map_err(client_channel_err)?;
        Ok(PyEventStream::create_subscriber(event_stream))
    }
}
#[pymethods]
impl PyEventStream {
    pub fn pop_message_blocking<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PyBytes>> {
        let val = self
            .recv_chan
            .blocking_recv()
            .ok_or_else(|| PyRuntimeError::new_err("Event channel closed"))?;
        self.set_done(&val);

        let val = val.encode_to_vec();

        Ok(PyBytes::new_bound(py, &val))
    }
    pub fn nonblocking_pop<'py>(
        &mut self,
        py: Python<'py>,
    ) -> PyResult<Option<Bound<'py, PyBytes>>> {
        let val = self.recv_chan.try_recv();

        match val {
            Ok(val) => {
                self.set_done(&val);
                let val = val.encode_to_vec();

                Ok(Some(PyBytes::new_bound(py, &val)))
            }
            Err(TryRecvError::Empty) => Ok(None),
            Err(_) => Err(PyRuntimeError::new_err("Event channel closed")),
        }
    }

    pub fn is_done<'py>(&mut self, _py: Python<'py>) -> bool {
        self.done
    }
}

impl PyEventStream {
    fn set_done(&mut self, event: &Event) {
        if event.finished_event() {
            self.done = true;
        }
    }
}
