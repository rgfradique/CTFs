#!/bin/python
import soundfile as sf
from soundfile import SEEK_END
import struct
import base64

def reps(m):
    m = m.replace("111","-")
    m = m.replace("11","")
    m = m.replace("1",".")
    m = m.replace("000000","/")
    m = m.replace("00"," ")
    m = m.replace("0","")
    return m

#Left
def read_morse(ch):
    data, sampler = sf.read('listen_you_fools.wav',start=0,stop=1280)
    data = data[:,ch]
    m = ""
    for i in data:
        if i <= 4e-5:
            m += "0"
        else:
            m += "1"
    print(reps(m))

read_morse(0)
read_morse(1)

#Left
with sf.SoundFile('listen_you_fools.wav', 'r+') as f:
    extractedR = ""
    cext = 0

    endframe = (f.seek(0,SEEK_END))
    curframe = endframe 
    while cext < 178:
        if curframe % 7 == 0 or curframe % 10 == 4:
            f.seek(curframe)
            data = f.read(1, dtype='int16')
            datar = data[0][1]
            extractedR += str(datar & 1)

            cext += 1
        curframe -= 1


#Right
with sf.SoundFile('listen_you_fools.wav', 'r+') as f:
    extractedL = ""
    cext = 0

    endframe = (f.seek(0))
    curframe = endframe 
    while cext < 178:
        if curframe % 5 == 0 or curframe % 10 == 3:
            f.seek(curframe)
            data = f.read(1, dtype='int16')
            datal = data[0][0]
            extractedL += str(datal & 1)

            cext += 1
        curframe += 1

def extract(dataIn):
    str_lsb = (dataIn[i:i+8] for i in range(0,len(dataIn),8))
    decoded = ''.join(chr(int(char,2)) for char in str_lsb)
    return decoded

print(base64.b64decode(extract(extractedL)+extract(extractedR)))