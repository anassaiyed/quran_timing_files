import os
import vlc

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

    timingFile = "./" + surahFile[:3] + ".txt"
    lines = [line.rstrip('\n') for line in open(timingFile)]
    i=0
    #for line in lines:
    while i<len(lines):
        ayahTime = int(lines[i])
        player.set_time(ayahTime)
        print str(lines[i])
        input = raw_input('Press  enter for next ayah. Press any other key for next surah. ' + str(i+1))
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
        continue;
    j = j + 1
    print "incrementing"

player.stop()
