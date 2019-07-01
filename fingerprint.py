#!/usr/bin/python

import argparse
import sys
import warnings
import MySQLdb as mysql
import multiprocessing
import os
import traceback

from argparse import RawTextHelpFormatter
from dejavu import Dejavu
from MySQLdb.cursors import DictCursor

# Don't show warnings from dejavu saying tables already exist
warnings.filterwarnings("ignore")

DATABASE_HOST = "127.0.0.1"
DATABASE_USER = "root"
DATABASE_PASSWORD = ""

# This can be changed to 1 or 2 or some other value depending on system resources
NUMBER_OF_PARALLEL_PROCESSES = multiprocessing.cpu_count()

# Read a surah mp3 and store it's fingerprints in the "dejavusurahNumber" database (eg. dejavu001, dejavu002, etc.) in sqlite
def fingerprint(args):
  print args
  (surahDirectory, surahFile) = args
  surahFile = surahDirectory + "/" + surahFile
  
  databaseName= "dejavu" + os.path.basename(surahFile)[:3]
  # MySQL database config
  # Dejavu stores fingerprints in MySQL using the config provided below.
  config = {
    "database": {
      "host": DATABASE_HOST,
      "user": DATABASE_USER,
      "passwd": DATABASE_PASSWORD, 
      "db": databaseName,
    }
  }

  print surahFile.split("/")[-1]

  # Create a database for the current surah
  db1 = mysql.connect(host=config["database"]["host"],user=config["database"]["user"],passwd=config["database"]["passwd"])
  cursor = db1.cursor()
  sql = 'CREATE DATABASE IF NOT EXISTS ' + config["database"]["db"]
  cursor.execute(sql)

  # Pass the MySQL config to dejavu to fingerprint the surah
  djv = Dejavu(config)
  djv.fingerprint_file(surahFile)


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

# Get a sorted list of mp3 files from the given surah directory
filesInSurahDirectory = os.listdir(surahDirectory)
filesInSurahDirectory.sort()
surahFiles = []
for fileInSurahDirectory in filesInSurahDirectory:
    if fileInSurahDirectory.endswith('.mp3'):
        surahFiles.append(fileInSurahDirectory)
print surahFiles

print "Fingerprinting files in: " + surahDirectory

# Multiprocessing for parallel execution
pool = multiprocessing.Pool(NUMBER_OF_PARALLEL_PROCESSES)

# Prepare input for the generateTimingFileForSurah function
function_input = zip([surahDirectory] * len(surahFiles), surahFiles)

# Send off our tasks/processes that run the generateTimingFileForSurah function
iterator = pool.imap_unordered(fingerprint, function_input)

# Loop till timing files for all surahs are generated
while True:
    try:
        #print "Processing new surah " + str(datetime.datetime.now())
        # Call the subprocesses with the generateTimingFileForSurah and corresponding arguments
        surahFile = iterator.next()
    except multiprocessing.TimeoutError:
        continue
    except StopIteration:
        break
    except:
        print("Failed generating the timing file!")
        # Print traceback because we can't reraise it here
        traceback.print_exc(file=sys.stdout)

pool.close()
pool.join()
