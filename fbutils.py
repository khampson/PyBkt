# Utility
#
#	Class containing miscellaneous constants and utility functions used in the accompanying code.
#
#	Note: Most, if not all, of the methods within this function will be class methods as opposed to instance methods,
#		  as this class is meant to serve as more of a collector of the methods as opposed to an instantiatable object.
#
#		Written by Ken Hampson, hampsonk+github@gmail.com

import os, re, pprint, sys, datetime

class FBUtils(object):
    # pseudo-constants
    DEBUG_ALWAYS = 0
    DEBUG_OFF	 = 0		# When using this as the debug setting instead of threshold, it should be 0 for off for the 'if debug' comparison below
    DEBUG_LOW    = 1
    DEBUG_MED    = 2
    DEBUG_HIGH   = 3
    DEBUG_NEVER  = 256

    LOG_ALWAYS   = 0
    LOG_OFF	 	 = 0		# When using this as the log setting instead of threshold, it should be 0 for off for the 'if log' comparison below
    LOG_LOW      = 1
    LOG_MED      = 2
    LOG_HIGH     = 3
    LOG_NEVER    = 256

    DEBUG = 0               # current debug level

    @classmethod
    def get_time_str(cls):
        curr_time = datetime.datetime.now()
        time_str = curr_time.strftime("%m/%d/%Y %H:%M:%S")

        return time_str

    @classmethod
    def print_mux(cls, log, msg, debug = 0, log_debug = 0, debug_threshold = 0, log_debug_threshold = 0):
        if cls.DEBUG >= 1:
            print("debug: " + debug + ", log_debug: " + log_debug)
            print("debug_threshold: " + debug_threshold + ", log_debug_threshold: " + log_debug_threshold)

        time = cls.get_time_str()

        if debug >= debug_threshold:
            print(time + "  " + msg)

        if log and log_debug >= log_debug_threshold:
            log.write(time + "  " + msg)

