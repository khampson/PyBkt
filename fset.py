# fset
#
#	Class to hold information about a set of files, such as their size and the total max allowable size of the set.
#	Tracks the running total size and if the set has room to add another file to the set.

#	An exception is raised if there is insufficient room to add another item.
#
#		Written by Ken Hampson, hampsonk+github@gmail.com

import pprint
import fbutils

class FileSet(object):
    pp = pprint.PrettyPrinter(indent=4)

    def __init__(self, max_size, log = None, debug = 0, log_debug = 0):
        # pseudo-constants
        self.DEBUG = debug
        self.LOG_DEBUG = log_debug

        # constructor-specified variables
        self.log = log
        self.files = {}
        self.file_sep = '\\'
        self.max_size = max_size

        self.size = 0
    # end __init__

    def __str__(self):
        size_kb = self.size // 1024			# Integer division here to truncate the fractional KB
        size_mb = size_kb / 1024
        size_gb = size_mb / 1024

        return 'Files ({:d}, {:d} bytes / {:d} KB / {:.2f} MB / {:.2f} GB):\n{:}'.format( len( self.files.keys() ), self.size, size_kb, size_mb, size_gb, self.pp.pformat(self.files) )
    # end __str__

    # Need this so this object is dumped correctly, else it'll just appear as a shallow dump in some cases
    def __repr__(self):
        return self.__str__()
    # end __repr__

    def add(self, file, fsize):
        """Add a file to the set, if there is room, and keep a running size total."""
        if (self.size + fsize) > self.max_size:
            raise FilesTooBigError()

        self.files[file] = fsize
        self.size += fsize
    # end add

    def get_file_names(self):
        """Return the list of file names."""
        return self.files.keys()
    # end get_file_names

    def get_num_files(self):
        return ( len( self.files ) )
    # end get_num_files

    def pop(self):
        """Since this is a hash-based data structure, this isn't a 'pop' method in the strictest sense.
            Rather, we'll take the list of keys, and pop the last one of those, returning the resulting
            key/value tuple."""

        lastkey = self.files.keys().pop()
        lastval = self.files.pop(lastkey)

        self.size -= lastval
        return (lastkey, lastval)


# end class FileSet


class FilesTooBigError(Exception):
    def __init__(self, size, max_size):
        self.size = size
        self.max_size = max_size

    def __str__(self):
        return "Current size of " + repr(self.size) + " is bigger than the max size of " + repr(self.max_size)

# end class FilesTooBigError

