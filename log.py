import sys

class Logger:
    log_level: int = None
    def __init__(self, log_level):
        self.log_level = log_level
        self.terminal = sys.stdout
        self.log = open('log.txt', 'a')

    def write(self, message, level):
        if level < self.log_level:
            self.terminal.write(message)
            self.log.write(message)
