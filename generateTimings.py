#!/usr/bin/python

import argparse
import datetime
import math
import multiprocessing
import os
import sys
import traceback
import warnings

from argparse import RawTextHelpFormatter
from dejavu import Dejavu
from dejavu.recognize import FileRecognizer
from pydub import AudioSegment

# Don't show warnings from dejavu saying tables already exist
warnings.filterwarnings("ignore")

# MySQL database config
# Dejavu stores fingerprints in MySQL. Provide information for the database where the fingerprints are stored.
config = {
    "database": {
        "host": "127.0.0.1",
        "user": "root",
        "passwd": "", 
        "db": "dejavu",
    }
}

# Convert milliseconds to a human readable format for logging to stdout
def get_formatted_time(millis):
    hours = int(millis / (60 * 60 * 1000))
    millis = millis - (hours * 60 * 60 *1000)
    minutes = int(millis / (60 * 1000))
    millis = millis - (minutes * 60 * 1000)
    seconds = int(millis / 1000)
    millis = int(millis - (seconds * 1000))

    str_hours = str(hours)
    str_minutes = str(minutes)
    str_seconds = str(seconds)
    str_millis = str(millis)
    if len(str_minutes) == 1:
        str_minutes = "0" + str_minutes
    if len(str_seconds) == 1:
        str_seconds = "0" + str_seconds
    if len(str_millis) == 1:
        str_millis = "0" + str_millis
    elif len(str_millis) == 2:
        str_millis = "00" + str_millis

    return str_hours + ":" + str_minutes + ":" + str_seconds + "," + str_millis

# Function to generate timing files given the surahFile and the directory containing mp3s for individual ayahs.
def generateTimingFileForSurah(args):
    # Unpack the arguments
    (surahDirectory, surahFile, ayahDirectory) = args
    print "Surah file: " + surahFile + " ayahDirectory: " + ayahDirectory

    surahFilePath = os.getcwd() + "/" + surahDirectory + "/" + surahFile

    # Get the first part of the timing file name (eg. 001, 002, 114, etc.)
    timingFileNamePrefix = surahFile[:3]
    timingFileName = timingFileNamePrefix + ".txt"

    print "timingFileNamePrefix: " + timingFileNamePrefix + " timingFileName: " + timingFileName

    # Create a pydub audio segment from the whole surah file. (decoded mp3 is loaded in memory, so this is a memory hog)
    surah = AudioSegment.from_mp3(surahFilePath)

    # Create/open the timing file for the surah in overwrite mode.
    f = open('timingFiles/' + timingFileName, 'w')

    # Get the ayah mp3 files for this surah and sort them.
    # Looks for the ayah files using the first 3 characters of the file name
    # For ex. if teh surah file is named 001.mp3 or 001-AlBaqrah.mp3, it will look 
    # for all files in the ayah directory starting with 001
    ayahFiles = os.listdir(ayahDirectory)
    ayahFiles.sort()
    for ayahFile in ayahFiles:
        if ayahFile.endswith('.mp3') and ayahFile[:3] == timingFileNamePrefix:
            ayahPath = ayahDirectory + "/" + ayahFile
            
            print "Getting start time of " + ayahPath + " in the whole(gapless) surah file."
            # Call the dejavu recognize method to get the start time of the ayah
            ayah = djv.recognize(FileRecognizer, ayahPath)

            ayah_start_millis = ayah["offset_seconds"] * 1000
            # float to int
            ayah_start_millis = int(ayah_start_millis)

            """
             The location (timing information) we get above is not very accurate.
             We are going to fine tune it.
             To do this, we are going to take the 1500ms segment around ayah_start_millis (750ms each side)
             and search for the quitest 100ms segment within this 1500ms segment.
            """
            half_segment_length = 750
            # start time and end time of the 1500ms segment withing the gapless surah file
            start = ayah_start_millis-half_segment_length if ayah_start_millis-half_segment_length >=0 else 0
            end = ayah_start_millis+half_segment_length if ayah_start_millis+half_segment_length >=0 else len(surah)
            
            print "Ayah start: " + str(start) + " Ayah end: " + str(end)
            around_ayah_segment = surah[start : end]

            window_start = 0
            silence_dbfs = 0
            current_ayah_start = ayah_start_millis
            # Using a 100ms window size for searching the quitest segment
            # or (end-start) / 15 (beginning or end of surah)
            window_size_millis = min((end - start) / 15, 100)
            print "Window size: " + str(window_size_millis)

            # Loop over the 1500 ms segment with a window size specified above.
            # To find the segment quietness (or loudness), pydub's dBFS property is used
            while window_start < end - start:
                window = around_ayah_segment[window_start : window_start + window_size_millis]
                
                # Update ayah start if quieter segment found
                if window.dBFS < silence_dbfs:
                    silence_dbfs = window.dBFS 
                    current_ayah_start = start + (window_start + (window_size_millis / 2))
                    print "Window start: " + str(window_start) + " Ayah start: " + str(current_ayah_start) + " Segment dBFS: " + str(silence_dbfs) + " Window dBFS: " + str(window.dBFS)
                
                # last thing in the loop
                window_start = window_start + window_size_millis

            split_millis = int(current_ayah_start)
            print "Corrected ayah location: " + get_formatted_time(split_millis)

            f.write(str(split_millis) + '\n')

    # Location of the end of the surah.
    # Set to 10 ms before the end of the surah 
    f.write(str(len(surah) - 10) + '\n')
    f.close()

    return surahFile

if __name__ == '__main__':
    # Command line arguments
    parser = argparse.ArgumentParser(
        description="Dejavu: Audio Fingerprinting library sound recognizer",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('-s', '--surahDirectory', nargs='?',
                        help='Path to directory\n'
                             'Usages: \n'
                             '--surahDirectory /path/to/directory\n')
    parser.add_argument('-a', '--ayahDirectory', nargs='?',
                        help='Path to directory\n'
                             'Usages: \n'
                             '--ayahDirectory /path/to/directory\n')

    args = parser.parse_args()

    if not len(sys.argv) == 5:
        print str(len(vars(args))) + " arguments passed"
        parser.print_help()
        sys.exit(0)

    # Create a Dejavu object by passing the MySQL config to Dejavu
    djv = Dejavu(config)
    
    surahDirectory = args.surahDirectory
    ayahDirectory = args.ayahDirectory

    # Get a sorted list of mp3 files from the given surah directory
    filesInSurahDirectory = os.listdir(surahDirectory)
    filesInSurahDirectory.sort()
    surahFiles = []
    for fileInSurahDirectory in filesInSurahDirectory:
        if fileInSurahDirectory.endswith('.mp3'):
            surahFiles.append(fileInSurahDirectory)
    print surahFiles

    # Multiprocessing for parallel execution
    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    # Prepare input for the generateTimingFileForSurah function
    function_input = zip([surahDirectory] * len(surahFiles), surahFiles, [ayahDirectory] * len(surahFiles))
    
    # Send off our tasks/processes that run the generateTimingFileForSurah function
    iterator = pool.imap_unordered(generateTimingFileForSurah, function_input)

    # Loop till timing files for all surahs are generated
    while True:
        try:
            print "Processing new surah " + str(datetime.datetime.now())
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
        else:
            print "Processing finished for surah: " + surahFile + " on " + str(datetime.datetime.now())

    pool.close()
    pool.join()

    sys.exit(0)
