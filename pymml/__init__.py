__all__ = [
    "device_search",
    "play_mml",
]

def exists_file(filename):
    import os
    if os.path.exists(filename) == False:
        print("not found ->", filename)
        exit()

def device_search():
    from .device.device_util import device_search as ds
    ds(True, True)

def play_mml(filename:str, tick_count:bool=True):
    exists_file(filename)
    from .song import SongData
    from .player import Player
    p = Player()
    try:
        sng = SongData(filename)
        sng.print_text()
        p.stop()
        if tick_count:
            p.tick_count(sng)
        p.play(sng)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    # except Exception as e:
    #     print("***ERROR***\n", e)
    p.stop()
