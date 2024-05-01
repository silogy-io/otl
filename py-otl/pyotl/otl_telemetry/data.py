# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: data.proto
# plugin: python-betterproto
from dataclasses import dataclass
from datetime import datetime

import betterproto


@dataclass
class Event(betterproto.Message):
    time: datetime = betterproto.message_field(1)
    # A globally-unique ID (UUIDv4) of this trace. Required.
    trace_id: str = betterproto.string_field(2)
    command: "CommandEvent" = betterproto.message_field(15, group="et")
    invoke: "InvokeEvent" = betterproto.message_field(16, group="et")


@dataclass
class CommandEvent(betterproto.Message):
    command_ref: str = betterproto.string_field(1)
    scheduled: "CommandScheduled" = betterproto.message_field(4, group="CommandVariant")
    started: "CommandStarted" = betterproto.message_field(5, group="CommandVariant")
    cancelled: "CommandCancelled" = betterproto.message_field(6, group="CommandVariant")
    finished: "CommandFinished" = betterproto.message_field(7, group="CommandVariant")
    stdout: "CommandStdout" = betterproto.message_field(8, group="CommandVariant")


@dataclass
class CommandScheduled(betterproto.Message):
    pass


@dataclass
class CommandStarted(betterproto.Message):
    pass


@dataclass
class CommandCancelled(betterproto.Message):
    pass


@dataclass
class CommandStdout(betterproto.Message):
    output: str = betterproto.string_field(1)


@dataclass
class CommandFinished(betterproto.Message):
    out: "CommandOutput" = betterproto.message_field(1)


@dataclass
class CommandOutput(betterproto.Message):
    status_code: int = betterproto.int32_field(1)


@dataclass
class InvokeEvent(betterproto.Message):
    start: "ExecutionStart" = betterproto.message_field(5, group="InvokeVariant")
    done: "AllCommandsDone" = betterproto.message_field(6, group="InvokeVariant")


@dataclass
class ExecutionStart(betterproto.Message):
    path: str = betterproto.string_field(1)
    username: str = betterproto.string_field(2)
    hostname: str = betterproto.string_field(3)


@dataclass
class AllCommandsDone(betterproto.Message):
    pass
