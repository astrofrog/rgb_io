import struct

PNG_SIGNATURE = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'


class Chunk(object):

    @classmethod
    def read(cls, fileobj):

        self = cls()

        # Read in chunk length
        length = struct.unpack('>I', fileobj.read(4))[0]

        # Read in chunk length
        self.type = fileobj.read(4)

        # Read in data
        self.data = fileobj.read(length)

        # Read in CRC
        crc = struct.unpack('>I', fileobj.read(4))[0]

        # Check that the CRC matches the actual one
        if crc != self.crc:
            raise ValueError("CRC ({0}) does not match expected ({1})".format(crc, self.crc))

        if length != self.length:
            raise ValueError("Dynamic length ({0}) does not match original length ({1})".format(self.length, length))

        return self

    def write(self, fileobj):

        # Write length
        fileobj.write(struct.pack('>I', self.length))

        # Write type
        fileobj.write(self.type)

        # Write data
        fileobj.write(self.data)

        # Write CRC
        fileobj.write(struct.pack('>I', self.crc))

    @property
    def crc(self):
        from zlib import crc32
        return crc32(self.type + self.data)

    @property
    def length(self):
        return len(self.data)


class PNGFile(object):

    @classmethod
    def read(cls, filename):

        fileobj = open(filename, 'rb')

        self = cls()

        sig = fileobj.read(8)

        if sig != PNG_SIGNATURE:
            raise ValueError("Signature ({0}) does match expected ({1})".format(sig, PNG_SIGNATURE))

        self.chunks = []

        while True:
            chunk = Chunk.read(fileobj)
            self.chunks.append(chunk)
            print(chunk.type, chunk.length)
            if chunk.type == b'IHDR':
                print(chunk.data)
            if chunk.type == b'IEND':
                break

        return self

    def write(self, filename):

        fileobj = open(filename, 'wb')

        fileobj.write(PNG_SIGNATURE)

        for chunk in self.chunks:
            chunk.write(fileobj)

        fileobj.close()
