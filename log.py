import sys
from datetime import datetime

class Logger:
    log_level: int = None
    def __init__(self, log_level):
        self.log_level = log_level
        self.terminal = sys.stdout
        self.log = open('log.txt', 'a')

    def write(self, message, level):
        if level < self.log_level:
            # self.terminal.write(message)
            current_datetime = datetime.now()
            time = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
            self.log.write(f'{time}: {message}\n')
