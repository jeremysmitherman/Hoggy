class GrabberException(Exception):
    pass

class Grabber(object):
    buffer = []

    def stack(self, user, line):
        self.buffer.append((user, line))
        while len(self.buffer) > 100:
            del self.buffer[0]

    def grab(self, user, lines=1):
        quote_lines = []
        for x in reversed(self.buffer):
            if len(quote_lines) == lines:
                break

            if user == x[0]:
                quote_lines.append(x[1])

        if len(quote_lines):
            quote = ""
            quote_lines.reverse()
            quote += " ".join(quote_lines)
            quote += " --" + user
            return quote
        else:
            raise GrabberException('No quotes found for user in last 100 lines.')
