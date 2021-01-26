import os, sys
def filenumber(fname, input_ext, path):
    same = []
    for f in os.listdir(path):
        f, ext = os.path.splitext(f)
        if str(f) == str(fname) and ext == input_ext:
            pass
        flag = 0
        for i in range(len(str(f)) - 1, -1, -1):
            if str(f)[i] == '_':
                flag = i
                break
        if str(f)[:flag] == fname and ext == input_ext:
            same.append(int(str(f)[flag + 1:]))
    if not same:
        return str(fname) + '_' + str(0) + str(input_ext)

    return str(fname) + '_' + str(max(same) + 1) + str(input_ext)
