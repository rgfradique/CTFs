from pwn import *
import time

t = (int(time.time())*10)
print(t)
while(1):
    conn = remote('3-nh01.bootupctf.net',8229,level='error')
    (conn.recvuntil(b":"))
    conn.sendline(str(t))
    (conn.recvline())
    rc = (conn.recvline())
    print(rc)
    print(b'Rejected challenge.\n')
    if rc != b"Rejected challenge.\n":
        print(conn.recvline())
