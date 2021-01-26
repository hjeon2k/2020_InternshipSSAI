import os, time, sys
def delete_old_files(path, deletion_period = 7 * 24 * 3600):
    now = time.time()
    for f in os.listdir(path):
        f = os.path.join(path, f)
        if now - os.stat(f).st_ctime > deletion_period:
            if os.path.isfile(f):
                os.remove(f)
