from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Tuple, Dict, Type
from math import ceil

from smb.smb_message import SMBMessage
from smb.v2.smbv2_header import SMBv2Header, SMBv2Command, SMBv2RequestHeader, SMBv2ResponseHeader
from smb.exceptions import IncorrectStructureSizeError
# from smb.smb_message import SMBResponseMessage


# TODO: Does this make sense?
def calculate_credit_charge(variable_payload_size: int, expected_maximum_response_size: int) -> int:
    return ceil(((max(variable_payload_size, expected_maximum_response_size) - 1) / 65536) + 1)


@dataclass
class SMBv2Message(SMBMessage, ABC):
    header: SMBv2Header

    structure_size: ClassVar[int] = NotImplemented
    _command: ClassVar[SMBv2Command] = NotImplemented
    _command_and_type_to_class: ClassVar[Dict[Tuple[SMBv2Command, bool], Type[SMBv2Message]]] = {}

    @classmethod
    def check_structure_size(cls, structure_size_to_test: int) -> None:
        if structure_size_to_test != cls.structure_size:
            raise IncorrectStructureSizeError(
                observed_structure_size=structure_size_to_test,
                expected_structure_size=cls.structure_size
            )

    @classmethod
    @abstractmethod
    def _from_bytes_and_header(cls, data: bytes, header: SMBv2Header) -> SMBv2Message:
        pass

    @classmethod
    def from_bytes_and_header(cls, data: bytes, header: SMBv2Header) -> SMBv2Message:

        from smb.v2.messages.negotiate.negotiate_request import NegotiateRequest
        from smb.v2.messages.negotiate.negotiate_response import NegotiateResponse
        from smb.v2.messages.session_setup.session_setup_request import SessionSetupRequest
        from smb.v2.messages.session_setup.session_setup_response import SessionSetupResponse
        from smb.v2.messages.tree_connect.tree_connect_request import TreeConnectRequest
        from smb.v2.messages.tree_connect.tree_connect_response import TreeConnectResponse
        from smb.v2.messages.create.create_request import CreateRequest
        from smb.v2.messages.create.create_response import CreateResponse
        from smb.v2.messages.read.read_request import ReadRequest
        from smb.v2.messages.read.read_response import ReadResponse
        from smb.v2.messages.query_directory.query_directory_request import QueryDirectoryRequest
        from smb.v2.messages.query_directory.query_directory_response import QueryDirectoryResponse
        from smb.v2.messages.close.close_request import CloseRequest
        from smb.v2.messages.close.close_response import CloseResponse
        from smb.v2.messages.tree_disconnect.tree_disconnect_request import TreeDisconnectRequest
        from smb.v2.messages.tree_disconnect.tree_disconnect_response import TreeDisconnectResponse
        from smb.v2.messages.logoff.logoff_request import LogoffRequest
        from smb.v2.messages.logoff.logoff_response import LogoffResponse

        lookup_key_tuple: Tuple[SMBv2Command, bool] = (header.command, header.flags.server_to_redir)

        if cls != SMBv2Message:
            if lookup_key_tuple != (cls._command, issubclass(cls, SMBResponseMessage)):
                # TODO: Use proper exception.
                raise ValueError
            return cls._from_bytes_and_header(data=data, header=header)
        else:
            return cls._command_and_type_to_class[lookup_key_tuple]._from_bytes_and_header(data=data, header=header)


@dataclass
class SMBv2RequestMessage(SMBv2Message, ABC):
    header: SMBv2RequestHeader


@dataclass
class SMBv2ResponseMessage(SMBv2Message, ABC):
    header: SMBv2ResponseHeader


def register_smbv2_message(cls: Type[SMBv2Message]):
    cls._command_and_type_to_class[(cls._command, issubclass(cls, SMBv2ResponseMessage))] = cls
    return cls
