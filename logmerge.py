import sys
import re
from collections import defaultdict
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--dest", dest="destination",
                  help="write log messages to PATTERN", metavar="PATTERN")
parser.add_option("-s", "--src",  dest="source",
                  help="read log messages from PATTERN")

class LogMerger(object):

    def __init__(self, src, dest):
        self.src = src
        self.dest = dest
        self.lines = defaultdict(list)

    def parseline(self, line):
        "Implemented by subclasses to extract a sort key from each line."
        return re.search(r'(?P<day>\d+)/(?P<month>\w+)/(?P<year>\d+):(?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)', line)

    def opendest(self, match, mode='r'):
        d = match.groupdict()
        try:
            return open(self.dest % d, mode)
        except:
            open(self.dest % d, 'w')
            return open(self.dest % d, mode)

    def key(self, line):
        parsed = self.parseline(line)
        key = "%(year)s/%(month)s/%(day)s" % parsed.groupdict()
        return key

    def parse(self):
        for line in self.src:
            m = self.parseline(line)
            key = self.key(line)
            self.lines[key].append((line, m))

    def writeoutall(self):
        for key, lines in self.lines.iteritems():
            self.writeout(key, lines)

    def writeout(self, key, lines):
        out_m = self.parseline(lines[0][0])
        dest = self.opendest(out_m)
        for line in dest:
            lines.append((line, self.parseline(line)))
        keys = lambda d, keys: [d[k] for k in d if k in keys]
        lines.sort(key=lambda (line, m): (
                keys(self.parseline(line).groupdict(),
                     ('year', 'month', 'day', 'hour', 'minute', 'second')),
                line))
        self.opendest(out_m, 'w')
        for (line, m) in lines:
            dest = self.opendest(out_m, 'a')
            dest.write(line)
            if not line.endswith('\n'):
                dest.write('\n')

def main(args):
    (options, args) = parser.parse_args()
    lm = LogMerger(open(options.source), options.destination)
    lm.parse()
    lm.writeoutall()

if __name__ == '__main__':
    main(sys.argv)
