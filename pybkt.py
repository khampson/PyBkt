# PyBucket
#
#	Main driver for the fbsorter code.
#	The purpose of this driver is to approximate a best-fit given a set of files and the space constraints
#	of a single-layer DVD. One or more filesets can be created.
#
#	The target size could be altered by creating and using a new constant in place of SINGLE_LAYER_DVD_BYTES.
#
#	Note: This was originally written on Windows with the intention of running only on Windows, and thus makes some Windows-specific
#		  assumptions about file paths and shell behavior, etc. Were cross-platform support required at the onset, some different implementation
#		  decisions would have been made at these Windows-specific points.
#
#		Written by Ken Hampson, hampsonk+github@gmail.com
#

# built-in imports
import os, re, pprint, sys
import argparse
import fbsorter, fset, fbutils

fbu = fbutils.FBUtils()

# Set the thresholds for console and logfile logging
DEBUG       = fbu.DEBUG_OFF
LOG_DEBUG   = fbu.LOG_LOW

PROG_NAME = 'PyBucket'
PROG_VER  = 'v1.0'

GB_IN_BYTES = 1024 * 1024 * 1024

# Discs say 4.7 GB, but in actuality, it's 4.3 GB and change. Manufacturers treat 1 KB as 1000 bytes instead
# of the true 1024, so the actual capacity is less. We'll round down to 4.3 -- from 4.384 -- to allow for a
# bit of extra room.
SINGLE_LAYER_DVD_BYTES = 4.3 * GB_IN_BYTES

LOGFILE_NAME = 'pybucket.log'

pp = pprint.PrettyPrinter(indent=4)

# Define an options parser and parse the cmdline
parser = argparse.ArgumentParser(description = (PROG_NAME + ' bucket sorter ' + PROG_VER) )

parser.add_argument('--path', action='append', help='List of root PATHs to search for files')
#parser.add_argument('--root', help='The root path to examine.')
parser.add_argument('--r', action='store_true', help='Enables recursive searching.')
parser.add_argument('--sets', type=int, help='Specifies the number of sets to generate.')

args = parser.parse_args()

with open(LOGFILE_NAME, 'w') as log:
    log.write("######################################################################################")
    log.write(PROG_NAME + ' ' + PROG_VER)

    pathsList = []

    if 'path' not in args:
        exitStr = 'Path not specified. Exiting.'
        fbu.print_mux(self.log, exitStr)
        sys.exit(exitStr)

    if args.path:
        fbu.print_mux(log, "The following paths were specified:\n")

        for path in args.path:
            fbu.print_mux(log, path)

        pathsList = args.path[:]
    else:
        cwd = os.getcwd()
        fbu.print_mux(log, "No path specified. Using cwd '" + cwd + "'\n")
        pathsList.append(cwd)

    fbu.print_mux(log, "Creating new fbsorter object\n", DEBUG, LOG_DEBUG, fbu.DEBUG_MED, fbu.LOG_LOW)
    buckets = fbsorter.FileBucketSorter(log, DEBUG, LOG_DEBUG)

    file_list = []

    # Walk each path's subtree
    for path in pathsList:
        for root, dirs, files in os.walk(path):
            for name in files:
                fullPath = os.path.join(root, name)
                fbu.print_mux(log, "\tAdding file '" + fullPath + "' to list\n", DEBUG, LOG_DEBUG, fbu.DEBUG_MED, fbu.LOG_LOW)
                file_list.append(fullPath)
                buckets.add(fullPath)
    # end cwd traversal

    fbu.print_mux(log, "file_list: " + pp.pformat(file_list) + "\n", DEBUG, LOG_DEBUG, fbu.DEBUG_MED, fbu.LOG_LOW)
    fbu.print_mux(log, "buckets: \n" + buckets.dump() + "\n", DEBUG, LOG_DEBUG, fbu.DEBUG_MED, fbu.LOG_LOW)

    fileset_set = []
    set_num = 0

    while not buckets.is_empty():
        set_num += 1
        bkts = buckets.get_buckets()
        fbu.print_mux(log, "bkts: \n" + pp.pformat(bkts) + "\n", DEBUG, LOG_DEBUG, fbu.DEBUG_MED, fbu.LOG_LOW)

        file_set = buckets.fit_files(SINGLE_LAYER_DVD_BYTES)
        fbu.print_mux(log, "file_set: \n" + pp.pformat(file_set) + "\n", DEBUG, LOG_DEBUG, fbu.DEBUG_MED, fbu.LOG_LOW)

        fileset_set.append(file_set)

        fbu.print_mux(log, "Total size: " + str(buckets.total_size) + " bytes\n", DEBUG, LOG_DEBUG, fbu.DEBUG_MED, fbu.LOG_LOW)
        fbu.print_mux(log, "\nBuckets left\n" + buckets.dump() + "\n", DEBUG, LOG_DEBUG, fbu.DEBUG_MED, fbu.LOG_LOW)

        # Bail if we're doing a specific number of sets and have reached that number
        if (args.sets and set_num >= args.sets):
            break
    # end while

    num_file_sets = len(fileset_set)
    fbu.print_mux(log, "File sets (" + str(num_file_sets) + "):\n" + pp.pformat(fileset_set) + "\n")

    fbu.print_mux(log, "FileBucketSorter:\n" + pp.pformat(buckets) + "\n")

