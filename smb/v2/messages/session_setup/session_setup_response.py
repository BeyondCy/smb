from dataclasses import dataclass
from enum import IntEnum
from struct import unpack as struct_unpack
from typing import ClassVar

from smb.v2.smbv2_message import SMBv2Message
from smb.v2.smbv2_header import SMBv2Header


class SessionFlag(IntEnum):
    _SMB_SESSION_FLAG_NONE = 0x0000
    SMB2_SESSION_FLAG_IS_GUEST = 0x0001
    SMB2_SESSION_FLAG_IS_NULL = 0x0002
    SMB2_SESSION_FLAG_ENCRYPT_DATA = 0x0004


@dataclass
class SessionSetupResponse(SMBv2Message):
    session_flags: SessionFlag
    security_buffer: bytes

    structure_size: ClassVar[int] = 9

    @classmethod
    def from_bytes_and_header(cls, data: bytes, header: SMBv2Header):
        body_data: bytes = data[len(header):]

        cls.check_structure_size(structure_size_to_test=struct_unpack('<H', body_data[:2])[0])

        security_buffer_offset: int = struct_unpack('<H', body_data[4:6])[0]
        security_buffer_length: int = struct_unpack('<H', body_data[6:8])[0]

        return SessionSetupResponse(
            header=header,
            session_flags=SessionFlag(struct_unpack('<H', body_data[2:4])[0]),
            security_buffer=data[security_buffer_offset:security_buffer_offset+security_buffer_length]
        )

    def __bytes__(self) -> bytes:
        ...

    def __len__(self) -> int:
        ...
