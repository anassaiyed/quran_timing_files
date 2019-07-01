import os
import vlc
from pydub import AudioSegment

surahFiles = os.listdir("./")
surahFiles.sort()
j=0
while j<len(surahFiles):
    print "len: " + str(len(surahFiles)) + " j " + str(j)
    surahFile = surahFiles[j]
    print surahFile

    if not surahFile.endswith('.mp3'):
        j = j + 1
        continue;
    #surahFile = "037-as-saffat.mp3"
    surahPath = surahFile
    print "vlc load"
    player = vlc.MediaPlayer(surahPath)
    player.play()

    surah = AudioSegment.from_mp3(surahPath)

    timingFile = "./" + surahFile[:3] + ".txt"

    # Create/open the timing file for the surah in overwrite mode.
    f = open(timingFile, 'w')
    i=0
    #for line in lines:
    while True:
        input = raw_input('Press enter to record location of ayah ' + str(i+1))
        if input == "n":
            player.stop()
            print "exiting"
            break;
        elif input == "ps":
            player.stop()
            j = j - 3
            break;
        elif input == "p":
            i = i - 1
            continue;
        i = i + 1
        ayah_start_millis = int(player.get_time())
        left_segment_length = 500
        right_segment_length = 500
        # start time and end time of the 1500ms segment withing the gapless surah file
        start = ayah_start_millis-left_segment_length if ayah_start_millis-left_segment_length >=0 else 0
        end = ayah_start_millis+right_segment_length if ayah_start_millis+right_segment_length >=0 else len(surah)
        
        print "Ayah start: " + str(start) + " Ayah end: " + str(end)
        around_ayah_segment = surah[start : end]

        window_start = 0
        silence_dbfs = 0
        current_ayah_start = ayah_start_millis
        # Using a 100ms window size for searching the quitest segment
        # or (end-start) / 15 (beginning or end of surah)
        window_size_millis = 200#min((end - start) / 10, 700)
        print "Window size: " + str(window_size_millis)

        window_movement_size = 100

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
            window_start = window_start + window_movement_size
        f.write(str(int(current_ayah_start)) + '\n')
        continue;
    f.write(str(len(surah) - 10) + '\n')
    f.close()
    j = j + 1
    print "incrementing"


player.stop()
