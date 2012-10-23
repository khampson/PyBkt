# fbsorter
#
#	Class that implements a bucket-sorting algorithm aimed at sets of files.
#
#		Written by Ken Hampson, hampsonk+github@gmail.com

# built-in imports
import os, re, pprint, sys
import fset, fbutils
import time

class FileBucketSorter(object):
    """A class which handles the bucket sorting of files."""

    pp = pprint.PrettyPrinter(indent=4)
    fbu = fbutils.FBUtils()

    def __init__(self, log=None, debug=0, log_debug=0):
        # pseudo-constants
        self.debug = debug
        self.log_debug = log_debug

		# constructor-specified variables
        self.log = log

		# variables
        self.bucket_int = 100 * 1024 * 1024     # default to 100 MB buckets
        self.sleep_interval = 0.1               # sleep interval in seconds
        self.total_size = 0                     # running total in bytes

        self.data = {}
        self.file_sets = []

    def __str__(self):
        #return self.pp.pformat(self)
        return ("Data:\n" + self.pp.pformat(self.data) + "\nFile sets: " + self.pp.pformat(self.file_sets) + "\nTotal Size: " + str(self.total_size) + "\n")
    # end def __str__

    # Need this so this object is dumped correctly, else it'll just appear as a shallow dump in some cases
    def __repr__(self):
        return self.__str__()
    # end def __repr__

    def add(self, file):
        """Add the specified file (representing the full path) to the bucket sorter object."""
        stat_info = os.stat(file)
        size = stat_info.st_size

		# Calculate the "bucketed size" for this file.

        # Essentially, this calculation determines bucket placement for the file by rounding down the file size to the nearest
        # bucket based on the specified bucket granularity.
        #
        # Thus, if size were, say, ~1439 MB, the parenthetical of this expression would be ~39 MB, and the expression would round
        # the file size down to the 1400 bucket.
        bucketed_size = size - (size % self.bucket_int)

        # Cover the case with small files where the bucketed size can go negative
        if bucketed_size < 0:
            self.fbu.print_mux(self.log, "bucketed_size is negative - resetting to 0\n", self.debug, self.log_debug, self.fbu.DEBUG_LOW, self.fbu.LOG_LOW)
            bucketed_size = 0

        self.fbu.print_mux(self.log, "bucketed_size = " + str(bucketed_size) + "\n", self.debug, self.log_debug, self.fbu.DEBUG_LOW, self.fbu.LOG_LOW)

        # Make sure the slot is initialized with an empty list at least
        if not bucketed_size in self.data:
            self.data[bucketed_size] = []

        self.data[bucketed_size].append(file)

        self.fbu.print_mux(self.log, "Bucket sorter data after adding:\n" + self.pp.pformat(self.data) + "\n", self.debug, self.log_debug, self.fbu.DEBUG_MED, self.fbu.LOG_LOW)
    # end def add

    def dump(self):
        return self.pp.pformat(self)
    # end def dump

    def get_buckets(self):
        """Get the list of buckets, sorted from largest to smallest"""
        sorted_buckets = sorted(self.data.keys())
        sorted_buckets.reverse()

        self.fbu.print_mux(self.log, "get_buckets> sorted_buckets:" + self.pp.pformat(sorted_buckets) + "\n", self.debug, self.log_debug, self.fbu.DEBUG_MED, self.fbu.LOG_LOW)

        return sorted_buckets
    # end def get_buckets

    def fit_files(self, target):
        """Iterate over the buckets to fit a subset of the files into a set of the target size."""
        buckets = self.get_buckets()
        running_size = 0

        file_set = fset.FileSet(target, self.log, self.debug, self.log_debug)

        # Enumerate over each bucket...
        for bucket_num, bucket in enumerate(buckets):      # make a copy of the list so modifying it is safe
            self.fbu.print_mux(self.log, "Processing bucket: " + str(bucket) + ", num " + str(bucket_num) + "\n")

            for file in self.data[bucket][:]:      # make a copy of the list so modifying it is safe
                stat_info = os.stat(file)
                fsize = stat_info.st_size

                self.fbu.print_mux(self.log, "\tsize: " + str(fsize) + "\n", self.debug, self.log_debug, self.fbu.DEBUG_LOW, self.fbu.LOG_LOW)
                self.fbu.print_mux(self.log, "\trunning_size: " + str(running_size) + "\n", self.debug, self.log_debug, self.fbu.DEBUG_LOW, self.fbu.LOG_LOW)
                self.fbu.print_mux(self.log, "\ttarget: " + str(target) + "\n", self.debug, self.log_debug, self.fbu.DEBUG_LOW, self.fbu.LOG_LOW)

                # sanity-check the file size
                if fsize < 0:
                    self.fbu.print_mux(self.log, "WARNING: fsize < 0 - skipping\n", self.debug, self.log_debug, self.fbu.DEBUG_LOW, self.fbu.LOG_LOW)
                    continue

                # Make sure this file won't push us over the limit
                if (fsize + running_size) < target:
                    # take the first file in this bucket

                    # We really shouldn't ever get an exception here since we're checking for the limit beforehand, but check anyway and then re-raise in that case
                    # so we defer to the caller.
                    try:
                        self.fbu.print_mux(self.log, "\t\tAdding file " + file + " and removing from bucket\n")
                        file_set.add(file, fsize)
                    except FilesTooBigError as e:
                        self.fbu.print_mux(self.log, "\t\tCould not add file " + file + " due to exception: " + e + "\n")
                        raise

                    running_size += fsize

                    # Remove the file from the original list
                    self.data[bucket].remove(file)

                    # See if we should remove the bucket, too
                    if len(self.data[bucket]) == 0:
                        buckets.remove(bucket)
                        self.fbu.print_mux(self.log, "\t\tRemoved bucket: " + str(bucket) + ", num: " + str(bucket_num) + "\n")
                else:
                    # Go to the next bucket and look at smaller files
                    self.fbu.print_mux(self.log, "\t\tDropping down to next bucket\n")
                    break

                # Give the CPU a bit of a break in between files
                time.sleep(self.sleep_interval)
            # end file iteration

            # Give the CPU a bit of a break in between buckets
            time.sleep(self.sleep_interval)
        # end bucket iteration

        # Save off the running size in the object
        self.total_size = running_size

        # Save off the file set
        self.file_sets.append(file_set)

        self.fbu.print_mux(self.log, "total_size: " + str(self.total_size) + "\n", self.debug, self.log_debug, self.fbu.DEBUG_LOW, self.fbu.LOG_LOW)
        self.fbu.print_mux(self.log, "\tfile_sets: " + str(self.file_sets) + "\n", self.debug, self.log_debug, self.fbu.DEBUG_LOW, self.fbu.LOG_LOW)

        return file_set
    # end def fit_files

    def is_empty(self):
        """Returns true if the main data hash of the object contains no keys."""
        return (len(self.data.keys()) == 0)
    # end def is_empty
# end class FileBucketSorter
