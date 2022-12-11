def parse(message):
    counter, value = message.split(":")
    if not counter:
        raise ValueError("Bad formed counter")
    return counter, int(value)
