QuranTimingFiles
================

This repository contains scripts to generate timing files to enable gapless playback in Quran applications. For this, it needs a gapless mp3 file for each surah and individual mp3 ayah files for each those surahs.
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
config = {
...     "database": {
...         "host": "127.0.0.1",
...         "user": "root",
...         "passwd": <password above>, 
...         "db": <name of the database you created above>,
...     }
... }
```

```bash
$ git clone https://github.com/anassaiyed/QuranTimingFiles.git ./QuranTimingFiles
$ cd QuranTimingFiles
$ python fingerprint.py -s surahs/
$ python generateTimings.py -s surahs/ -a ayahs/
```

These scripts take a while to run if there are a lot of files or large files. fingerprint.py can be killed in the middle of a run and the files already fingerprinted will not be reprocessed again hence saving time.

**Note:** The scripts expect the surah files to be named in the following way 001\*.mp3, 002\*.mp3, 114\*.mp3, etc. (see the surahs/ directory). It expects the ayah files to be named in the following way 001001.mp3, 001002.mp3, 114001.mp3, 114002.mp3, etc. (see the ayahs/ directory).

**Note:** You are likely to get a memory error when processing very large mp3s (depending on your RAM size). This is due to pyDub storing the whole decoded mp3s in memory. A way to mitigate this is to allocate a very large amount of swap space. I used 32GB of swap while processing 3 large surahs in parallel. Not pretty, but it does the job.

**Note:** To enable multiprocessing while fingerprnting (if you have multiple cpu cores), add a parameter to the "djv.fingerprint_directory" line in fingerprint.py specifying the number of processes. Example: djv.fingerprint_directory(surahDirectory, [".mp3"], 3) for running 3 processes in parallel.

## How it works
Dejavu can memorize audio (gapless surahs for this project) by listening to it once and fingerprinting it; storing the fingerprints in MySQL. Then, when generateTimings.py is run, Dejavu attempts to match the ayah against the fingerprints held in the database, returning the surah it belongs to with it's start time. In my experience, Dejavu always correctly identified the location of the ayah (havent seen an error yet as the ayahs are from the same recording as the surah).

This time can be off by a few hundred milliseconds due to some distortions at the start of the ayah files. To get accurate start locations of the ayahs in the gapless surah, generateTimings.py checks the 1500 millisecond segment of audio around the ayah start time provided by Dejavu. Finally, we pick the quietest (lowest decibel) location within the segment and write that to the timing file as the ayah's location.

The end of the surah is written to the timing file as the length of the surah - 10 milliseconds

This has given pretty accurate results at least for the mp3s of Mishary Rashid AlAfasy which were the only ones tested. But it should work for other reciters too.

## Projects Used
- [Dejavu](https://github.com/worldveil/dejavu)
- [pyDub](https://github.com/jiaaro/pydub)
