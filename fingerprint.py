#!/usr/bin/python

import argparse
import sys
import warnings

from argparse import RawTextHelpFormatter
from dejavu import Dejavu

# Don't show warnings from dejavu saying tables already exist
warnings.filterwarnings("ignore")

# MySQL database config
# Dejavu stores fingerprints in MySQL using the config provided below.
config = {
	"database": {
		"host": "127.0.0.1",
		"user": "root",
		"passwd": "", 
		"db": "dejavu",
	}
}

# Pass the MySQL config to dejavu
djv = Dejavu(config)

# command line arguments
parser = argparse.ArgumentParser(
        description="Dejavu: Audio Fingerprinting library sound recognizer",
        formatter_class=RawTextHelpFormatter)
parser.add_argument('-s', '--surahDirectory', nargs='?',
                    help='Path to directory\n'
                         'Usages: \n'
                         '--surahDirectory /path/to/directory\n')

args = parser.parse_args()

if not len(sys.argv) == 3:
  print str(len(vars(args))) + " arguments passed"
  parser.print_help()
  sys.exit(0)

# Directory where the audio files that need to be fingerprinted are present
surahDirectory = args.surahDirectory

print "Fingerprinting files in: " + surahDirectory
# This line can be modified for parallel processing as below:
# djv.fingerprint_directory(surahDirectory, [".mp3"], number_of_processes_for_multiprocessing)
djv.fingerprint_directory(surahDirectory, [".mp3"])

print djv.db.get_num_fingerprints()
