from __future__ import annotations

import base64

UINT32_MASK = 0xFFFFFFFF


def create_table_password(identifier: str, password_length: int = 20) -> bytes:
    length = round((password_length // 4) * 3)
    generator = MersenneTwister(xxhash32(identifier.encode("utf-8")))
    output = bytearray()
    while len(output) < length:
        output.extend(generator.next_int31().to_bytes(4, "little", signed=True))
    return bytes(output[:length])


def create_table_password_base64(identifier: str, password_length: int = 20) -> str:
    return base64.b64encode(create_table_password(identifier, password_length)).decode("ascii")


def create_table_field_key(table_name: str) -> bytes:
    generator = MersenneTwister(xxhash32(table_name.encode("utf-8")))
    output = bytearray()
    while len(output) < 8:
        output.extend(generator.next_int31().to_bytes(4, "little", signed=True))
    return bytes(output[:8])


def xxhash32(data: bytes, seed: int = 0) -> int:
    prime1 = 2654435761
    prime2 = 2246822519
    prime3 = 3266489917
    prime4 = 668265263
    prime5 = 374761393
    length = len(data)
    index = 0

    if length >= 16:
        acc1 = (seed + prime1 + prime2) & UINT32_MASK
        acc2 = (seed + prime2) & UINT32_MASK
        acc3 = seed & UINT32_MASK
        acc4 = (seed - prime1) & UINT32_MASK
        limit = length - 16
        while index <= limit:
            acc1 = _xxhash_round(acc1, int.from_bytes(data[index : index + 4], "little"))
            index += 4
            acc2 = _xxhash_round(acc2, int.from_bytes(data[index : index + 4], "little"))
            index += 4
            acc3 = _xxhash_round(acc3, int.from_bytes(data[index : index + 4], "little"))
            index += 4
            acc4 = _xxhash_round(acc4, int.from_bytes(data[index : index + 4], "little"))
            index += 4
        result = (_rotate_left(acc1, 1) + _rotate_left(acc2, 7) + _rotate_left(acc3, 12) + _rotate_left(acc4, 18)) & UINT32_MASK
    else:
        result = (seed + prime5) & UINT32_MASK

    result = (result + length) & UINT32_MASK
    while index + 4 <= length:
        result = (_rotate_left((result + int.from_bytes(data[index : index + 4], "little") * prime3) & UINT32_MASK, 17) * prime4) & UINT32_MASK
        index += 4
    while index < length:
        result = (_rotate_left((result + data[index] * prime5) & UINT32_MASK, 11) * prime1) & UINT32_MASK
        index += 1

    result = ((result ^ (result >> 15)) * prime2) & UINT32_MASK
    result = ((result ^ (result >> 13)) * prime3) & UINT32_MASK
    return (result ^ (result >> 16)) & UINT32_MASK


class MersenneTwister:
    def __init__(self, seed: int) -> None:
        self._state = [0] * 624
        self._index = 624
        self._state[0] = seed & UINT32_MASK
        for index in range(1, 624):
            self._state[index] = (1812433253 * (self._state[index - 1] ^ (self._state[index - 1] >> 30)) + index) & UINT32_MASK

    def next_int31(self) -> int:
        return self._generate_uint32() >> 1

    def next_bytes(self, length: int) -> bytes:
        output = bytearray()
        while len(output) < length:
            output.extend(self.next_int31().to_bytes(4, "little", signed=True))
        return bytes(output[:length])

    def _generate_uint32(self) -> int:
        if self._index >= 624:
            self._twist()
        value = self._state[self._index]
        self._index += 1
        value ^= value >> 11
        value ^= (value << 7) & 0x9D2C5680
        value ^= (value << 15) & 0xEFC60000
        value ^= value >> 18
        return value & UINT32_MASK

    def _twist(self) -> None:
        for index in range(0, 227):
            self._twist_index(index, index + 397)
        for index in range(227, 623):
            self._twist_index(index, index - 227)
        value = (self._state[623] & 0x80000000) | (self._state[0] & 0x7FFFFFFF)
        self._state[623] = (self._state[396] ^ (value >> 1) ^ (0x9908B0DF if value & 1 else 0)) & UINT32_MASK
        self._index = 0

    def _twist_index(self, index: int, target_index: int) -> None:
        value = (self._state[index] & 0x80000000) | (self._state[index + 1] & 0x7FFFFFFF)
        self._state[index] = (self._state[target_index] ^ (value >> 1) ^ (0x9908B0DF if value & 1 else 0)) & UINT32_MASK


def _xxhash_round(accumulator: int, value: int) -> int:
    return (_rotate_left((accumulator + value * 2246822519) & UINT32_MASK, 13) * 2654435761) & UINT32_MASK


def _rotate_left(value: int, bits: int) -> int:
    return ((value << bits) | (value >> (32 - bits))) & UINT32_MASK


__all__ = [
    "MersenneTwister",
    "create_table_field_key",
    "create_table_password",
    "create_table_password_base64",
    "xxhash32",
]
