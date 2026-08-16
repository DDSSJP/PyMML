import sys
import subprocess
import pymml

if len(sys.argv) <= 1:
    print("Usage:")
    print("python play.py filename")
    print("    filenameに指定されたMMLファイルを演奏します")
    exit()

filename = sys.argv[1]

if len(sys.argv) >= 3:
    if sys.argv[2].upper() == "HIGH":
        try:
            subprocess.run(["python", __file__, filename], creationflags=subprocess.ABOVE_NORMAL_PRIORITY_CLASS)
        except KeyboardInterrupt:
            print("KeyboardInterrupt(subprocess)")
        exit()

pymml.play_mml(filename)
