#!/usr/bin/python3.4
from agarnet.buffer import BufferStruct, BufferUnderflowError


class Dispatcher:
    def __init__(self, opcodes, handler):
        self.packet_opcodes = opcodes
        self.handler = handler

    def dispatch(self, buf):
        opcode = buf.pop_uint8()

        try:
            packet_name = self.packet_opcodes[opcode]
        except KeyError:
            self.subscriber.on_message_error('Unknown packet %s' % opcode)
            return False

        parser = getattr(self.handler, 'parse_%s' % packet_name)

        if parser is None:
            return False

        try:
            parser(buf)
        except BufferUnderflowError as e:
            print('Parsing %s packet failed: %s' % (packet_name, e.args[0]))
