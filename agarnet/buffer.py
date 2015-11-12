# -*- coding: utf-8 -*-
import struct


class BufferUnderflowError(struct.error):
    def __init__(self, fmt, buf):
        self.fmt = fmt
        self.buf = buf
        self.args = ('Buffer too short: wanted %i %s, got %i %s'
                     % (struct.calcsize(fmt), fmt, len(buf), buf),)


class BufferStruct(object):
    def __init__(self, message=bytes(), opcode=None):
        self.buffer = message
        if opcode is not None:
            self.push_uint8(opcode)

    def __str__(self):
        specials = {
            '\r': '\\r',
            '\n': '\\n',
            ' ': '␣',
        }
        nice_bytes = []
        hex_seen = False
        for b in self.buffer:
            if chr(b) in specials:
                if hex_seen:
                    nice_bytes.append(' ')
                    hex_seen = False
                nice_bytes.append(specials[chr(b)])
            elif 33 <= int(b) <= 126:  # printable
                if hex_seen:
                    nice_bytes.append(' ')
                    hex_seen = False
                nice_bytes.append('%c' % b)
            else:
                if not hex_seen:
                    nice_bytes.append(' 0x')
                    hex_seen = True
                nice_bytes.append('%02x' % b)
        return ''.join(nice_bytes)

    def append(self, buf):
        self.buffer += buf.buffer

    def push_int8(self, value):
        self.buffer += struct.pack('<b', value)

    def push_uint8(self, value):
        self.buffer += struct.pack('<B', value)

    def push_int16(self, value):
        self.buffer += struct.pack('<h', value)

    def push_uint16(self, value):
        self.buffer += struct.pack('<H', value)

    def push_int32(self, value):
        self.buffer += struct.pack('<i', value)

    def push_uint32(self, value):
        self.buffer += struct.pack('<I', value)

    def push_float32(self, value):
        self.buffer += struct.pack('<f', value)

    def push_float64(self, value):
        self.buffer += struct.pack('<d', value)

    def push_end_str16(self, value):
        for c in value:
            self.push_uint16(ord(c))

    def push_end_str8(self, value):
        for c in value:
            self.push_uint8(ord(c))

    def push_null_str16(self, value):
        self.push_end_str16(value)
        self.push_uint16(0)

    def push_null_str8(self, value):
        self.push_end_str8(value)
        self.push_uint8(0)

    def pop_values(self, fmt):
        size = struct.calcsize(fmt)
        if len(self.buffer) < size:
            raise BufferUnderflowError(fmt, self.buffer)
        values = struct.unpack_from(fmt, self.buffer, 0)
        self.buffer = self.buffer[size:]
        return values

    def pop_int8(self):
        return self.pop_values('<b')[0]

    def pop_uint8(self):
        return self.pop_values('<B')[0]

    def pop_int16(self):
        return self.pop_values('<h')[0]

    def pop_uint16(self):
        return self.pop_values('<H')[0]

    def pop_int32(self):
        return self.pop_values('<i')[0]

    def pop_uint32(self):
        return self.pop_values('<I')[0]

    def pop_float32(self):
        return self.pop_values('<f')[0]

    def pop_float64(self):
        return self.pop_values('<d')[0]

    def pop_str16(self):
        l_name = []
        while 1:
            c = self.pop_uint16()
            if c == 0:
                break
            l_name.append(chr(c))
        return ''.join(l_name)

    def pop_str8(self):
        l_name = []
        while 1:
            c = self.pop_uint8()
            if c == 0:
                break
            l_name.append(chr(c))
        return ''.join(l_name)
