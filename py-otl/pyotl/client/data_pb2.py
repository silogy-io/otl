# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: client.data.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11\x63lient.data.proto\x12\x13otl_client.commands\x1a\x1egoogle/protobuf/duration.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"\xb5\x01\n\rClientCommand\x12\x32\n\x06setter\x18\x01 \x01(\x0b\x32 .otl_client.commands.SetCommandsH\x00\x12-\n\x06runone\x18\x02 \x01(\x0b\x32\x1b.otl_client.commands.RunOneH\x00\x12/\n\x07runtype\x18\x03 \x01(\x0b\x32\x1c.otl_client.commands.RunTypeH\x00\x42\x10\n\x0e\x43lientCommands\"&\n\x0bSetCommands\x12\x17\n\x0f\x63ommand_content\x18\x01 \x01(\t\"\x1e\n\x06RunOne\x12\x14\n\x0c\x63ommand_name\x18\x01 \x01(\t\"\x1b\n\x07RunType\x12\x10\n\x08typeinfo\x18\x01 \x01(\tb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'client.data_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CLIENTCOMMAND']._serialized_start=108
  _globals['_CLIENTCOMMAND']._serialized_end=289
  _globals['_SETCOMMANDS']._serialized_start=291
  _globals['_SETCOMMANDS']._serialized_end=329
  _globals['_RUNONE']._serialized_start=331
  _globals['_RUNONE']._serialized_end=361
  _globals['_RUNTYPE']._serialized_start=363
  _globals['_RUNTYPE']._serialized_end=390
# @@protoc_insertion_point(module_scope)
