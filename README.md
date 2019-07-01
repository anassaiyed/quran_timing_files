QuranTimingFiles
================

This repository contains scripts to generate timing files to enable gapless playback in Quran applications. For this, it needs a gapless mp3 file for each surah and individual mp3 ayah files for each those surahs. Note that the gapless surah files and the individual ayah files MUST be from the same recording. Else these scripts will not work.

See examples of mp3 files required in the surahs/ and ayahs/ directory. Timing files generated for the surahs in these directories are present in the timingFiles/ directory.

Note: The scripts are not capable of generating timings from just gapless mp3s. Both a gapless surah and individual ayahs are needed to detect ayah start positions.

## Dependencies
This project uses [pyDub](https://github.com/jiaaro/pydub) and [Dejavu](https://github.com/worldveil/dejavu). Follow the links to learn more about those projects

Instructions for installing these dependencies are located [here](https://github.com/worldveil/dejavu/blob/master/INSTALLATION.md). Install everything except Dejavu from that page.

Once the dependencies are installed, install Dejavu using the command below to get the latest version:

    pip install https://github.com/worldveil/dejavu/zipball/master

After the above dependencies are installed, you'll need to create a MySQL database where Dejavu can store fingerprints. For example, on your local setup:
    
    $ mysql -u root -p
    Enter password: **********
    mysql> CREATE DATABASE IF NOT EXISTS dejavu;

Now you're ready to start fingerprinting the surahs and generating the timing files!

## Quickstart

Edit the config in fingerprint.py and generateTimings.py with your MySQL instance details:
```python
DATABASE_HOST = "127.0.0.1"
DATABASE_USER = "root"
DATABASE_PASSWORD = ""
```

```bash
$ python fingerprint.py -s surahs/
$ python generateTimings.py -s surahs/ -a ayahs/
```

These scripts take a while to run if there are a lot of files or large files. fingerprint.py can be killed in the middle of a run and the files already fingerprinted will not be reprocessed again hence saving time.

**Note:** The scripts expect the surah files to be named in the following way 001\*.mp3, 002\*.mp3, 114\*.mp3, etc. (see the surahs/ directory). It expects the ayah files to be named in the following way 001001.mp3, 001002.mp3, 114001.mp3, 114002.mp3, etc. (see the ayahs/ directory).

**Note:** You are likely to get a memory error when processing very large mp3s (depending on your RAM size). This is due to pyDub storing the whole decoded mp3s in memory. A way to mitigate this is to allocate a very large amount of swap space. I used 32GB of swap while processing 3 large surahs in parallel. Not pretty, but it does the job.

**Note:** To enable multiprocessing while fingerprnting (if you have multiple cpu cores), add a parameter to the "djv.fingerprint_directory" line in fingerprint.py specifying the number of processes. Example: djv.fingerprint_directory(surahDirectory, [".mp3"], 3) for running 3 processes in parallel.

## Configuration Options
You may want to modify the following parameters found in fingerprint.py and generateTimings.py.
- *NUMBER_OF_PARALLEL_PROCESSES*: This can be set to 1 (or some other value) if there are resource constraints on the computer. Increasing the number (upto the number of CPUs available on the computer) can increase performance but there are higher chances of memory errors with very large audio files.
- *AYAHFILE_SECONDS_TO_FINGERPRINT_TO_GET_TIMING* : This parameter in generateTimings.py can be modified to play with and test the accuracy of the of the timing files generated. In practice, I found a value of around 5-7 to work well.
- *LEFT_SEGMENT_LENGTH and RIGHT_SEGMENT_LENGTH* : These are found in generateTimings.py. Once the ayah location is detected by dejavu, these variables determine the window size (to the left and right of the detected location) to search for the quietest location around the detected ayah location. These values are in milliseconds.The default values work well for these parameters

## How it works
Dejavu can memorize audio (gapless surahs for this project) by listening to it once and fingerprinting it; storing the fingerprints in MySQL. Then, when generateTimings.py is run, Dejavu attempts to match the ayah against the fingerprints held in the database, returning the surah it belongs to with it's start time. In my experience, Dejavu always correctly identified the location of the ayah (havent seen an error yet as the ayahs are from the same recording as the surah).

This time can be off by a few hundred milliseconds due to some distortions at the start of the ayah files. To get accurate start locations of the ayahs in the gapless surah, generateTimings.py checks a segment of audio in the surah around the ayah start time provided by Dejavu. Finally, we pick the quietest (lowest decibel) location within the segment and write that to the timing file as the ayah's location.

The end of the surah is written to the timing file as the length of the surah - 10 milliseconds

Usually this gives prettu accurate results, but the accuracy may vary between different audio files.

## Manually Generating Timing Files
To manually generate timing files (suppose accuracy is really bad for a surah or the ayah files don't match the surah file for a couple of surahs), put the surah audio files in the ./manual directory. Then, run the following commands:

```bash
cd manual
python manual.py
```

The surahs will start playing. Press enter whenever a new ayah starts to mark its location. The timing files will be created in the ./manual folder itself.
Note: This script requires vlc and the python vlc modules to be installed. Run ```pip install python-vlc``` to install the python vlc modules.

## Projects Used
- [Dejavu](https://github.com/worldveil/dejavu)
- [pyDub](https://github.com/jiaaro/pydub)
