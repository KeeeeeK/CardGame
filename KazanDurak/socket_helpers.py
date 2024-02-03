def unpack_message(full_message: bytes) -> str:
    if full_message == b'':
        raise BrokenPipeError('empty message means no connection')
    return full_message.decode()


def pack_message(code: chr, message: str) -> bytes:
    return (code + message).encode()


CardIndex = int
