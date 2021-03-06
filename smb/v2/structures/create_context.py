from __future__ import annotations
from dataclasses import dataclass
from struct import unpack as struct_unpack, pack as struct_pack
from math import ceil
from typing import List


# TODO: In future, make this an abstract class.
@dataclass
class CreateContext:
    name: bytes
    data: bytes
    next: int

    @classmethod
    def from_bytes(cls, data: bytes) -> CreateContext:
        # TODO: Make additional checks?

        name_offset: int = struct_unpack('<H', data[4:6])[0]
        name_length: int = struct_unpack('<H', data[6:8])[0]

        data_offset: int = struct_unpack('<H', data[10:12])[0]
        data_length: int = struct_unpack('<H', data[12:14])[0]

        return cls(
            name=data[name_offset:name_offset+name_length],
            data=data[data_offset:data_offset+data_length],
            next=struct_unpack('<I', data[:4])[0]
        )

    def __bytes__(self) -> bytes:
        current_buffer_offset = 16

        name_len: int = len(self.name)
        name_offset = current_buffer_offset
        num_name_padding = int(ceil(name_len / 8.0)) * 8 - name_len
        current_buffer_offset += name_len + num_name_padding

        return b''.join([
            struct_pack('<I', self.next),
            struct_pack('<H', name_offset),
            struct_pack('<H', name_len),
            b'\x00\x00',
            struct_pack('<H', current_buffer_offset),
            struct_pack('<I', len(self.data)),
            self.name,
            num_name_padding * b'\x00',
            self.data
        ])

    def __len__(self) -> int:
        name_len: int = len(self.name)
        num_name_padding = int(ceil(name_len / 8)) * 8 - name_len
        return 16 + len(self.name) + num_name_padding + len(self.data)


class CreateContextList(list):
    def __init__(self, iterable=()):
        super().__init__(iterable)

    @classmethod
    def from_bytes(cls, data: bytes) -> CreateContextList:
        if not data:
            return cls()

        create_contexts: List[CreateContext] = []

        while True:
            create_context = CreateContext.from_bytes(data=data)
            create_contexts.append(create_context)

            if create_context.next == 0:
                break

            data = data[create_context.next:]

        return cls(create_contexts)

    def __bytes__(self) -> bytes:
        data = b''
        for create_context in self[:-1]:
            create_context_bytes = bytes(create_context)
            create_context_len = len(create_context_bytes)
            num_padding = int(ceil(create_context_len / 8)) * 8 - create_context_len

            data += create_context_bytes + (num_padding * b'\x00')

        try:
            last_create_context_bytes = bytes(self[-1])
        except IndexError:
            last_create_context_bytes = b''

        return data + last_create_context_bytes

    def bytes_len(self) -> int:
        return (sum(int(ceil(len(create_context) / 8)) * 8 for create_context in self[:-1]) + len(self[-1])) \
            if len(self) > 0 else 0

