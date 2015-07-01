def list_chunks_generator(list_, length):
    if len(list_) == 0:
        return
    if length == 0:
        yield list_
        return
    for i in range(0, len(list_), length):
        yield list_[i:i + length]
