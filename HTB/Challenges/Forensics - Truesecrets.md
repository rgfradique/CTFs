# Description

Our cybercrime unit has been investigating a well-known APT group for several months. The group has been responsible for several high-profile attacks on corporate organizations. However, what is interesting about that case, is that they have developed a custom command & control server of their own. Fortunately, our unit was able to raid the home of the leader of the APT group and take a memory capture of his computer while it was still powered on. Analyze the capture to try to find the source code of the server.

# Write-up

We get a raw file that we know from the description to be a memory dump from a computer. So we can start with volatility:

```
└─$ vol.py -f TrueSecrets.raw imageinfo
Volatility Foundation Volatility Framework 2.6.1
INFO    : volatility.debug    : Determining profile based on KDBG search...
          Suggested Profile(s) : Win7SP1x86_23418, Win7SP0x86, Win7SP1x86_24000, Win7SP1x86 (Instantiated with Win7SP1x86)
...                                                                   
```

So we have a Win7 memory dump, time to start digging around for useful information. We need to find the source for a C2 server, so that gives us an indication of the type of files to look for. Starting with running processes:

```
└─$ vol.py -f TrueSecrets.raw --profile=Win7SP1x86 pslist                   
Volatility Foundation Volatility Framework 2.6.1
Offset(V)  Name                    PID   PPID   Thds     Hnds   Sess  Wow64 Start                          Exit                          
---------- -------------------- ------ ------ ------ -------- ------ ------ ------------------------------ ------------------------------
0x8378ed28 System                    4      0     87      475 ------      0 2022-12-15 06:08:19 UTC+0000                                 
0x83e7e020 smss.exe                252      4      2       29 ------      0 2022-12-15 06:08:19 UTC+0000                                 
0x843cf980 csrss.exe               320    312      9      375      0      0 2022-12-15 06:08:19 UTC+0000                                 
0x837f6280 wininit.exe             356    312      3       79      0      0 2022-12-15 06:08:19 UTC+0000                                 
0x84402d28 csrss.exe               368    348      7      203      1      0 2022-12-15 06:08:19 UTC+0000                                 
0x84409030 winlogon.exe            396    348      3      110      1      0 2022-12-15 06:08:19 UTC+0000                                 
0x844577a0 services.exe            452    356      9      213      0      0 2022-12-15 06:08:19 UTC+0000                                 
0x8445e030 lsass.exe               468    356      7      591      0      0 2022-12-15 06:08:19 UTC+0000                                 
0x8445f030 lsm.exe                 476    356     10      142      0      0 2022-12-15 06:08:19 UTC+0000                                 
0x84488030 svchost.exe             584    452     10      347      0      0 2022-12-15 06:08:19 UTC+0000                                 
0x844a2030 VBoxService.ex          644    452     11      116      0      0 2022-12-15 06:08:19 UTC+0000                                 
0x844ab478 svchost.exe             696    452      7      243      0      0 2022-12-14 21:08:21 UTC+0000                                 
0x844c3030 svchost.exe             752    452     18      457      0      0 2022-12-14 21:08:21 UTC+0000                                 
0x845f5030 svchost.exe             864    452     16      399      0      0 2022-12-14 21:08:21 UTC+0000                                 
0x845fcd28 svchost.exe             904    452     15      311      0      0 2022-12-14 21:08:21 UTC+0000                                 
0x84484d28 svchost.exe             928    452     23      956      0      0 2022-12-14 21:08:21 UTC+0000                                 
0x8e013488 svchost.exe             992    452      5      114      0      0 2022-12-14 21:08:21 UTC+0000                                 
0x8e030a38 svchost.exe            1116    452     18      398      0      0 2022-12-14 21:08:21 UTC+0000                                 
0x8e0525b0 spoolsv.exe            1228    452     13      275      0      0 2022-12-14 21:08:21 UTC+0000                                 
0x84477d28 svchost.exe            1268    452     19      337      0      0 2022-12-14 21:08:21 UTC+0000                                 
0x8e0a2658 taskhost.exe           1352    452      9      223      1      0 2022-12-14 21:08:22 UTC+0000                                 
0x844d2d28 dwm.exe                1448    864      3       69      1      0 2022-12-14 21:08:22 UTC+0000                                 
0x8e0d3a40 explorer.exe           1464   1436     32     1069      1      0 2022-12-14 21:08:22 UTC+0000                                 
0x8e1023a0 svchost.exe            1636    452     10      183      0      0 2022-12-14 21:08:22 UTC+0000                                 
0x8e10d998 svchost.exe            1680    452     14      224      0      0 2022-12-14 21:08:22 UTC+0000                                 
0x8e07d900 wlms.exe               1776    452      4       45      0      0 2022-12-14 21:08:22 UTC+0000                                 
0x83825540 VBoxTray.exe           1832   1464     12      140      1      0 2022-12-14 21:08:22 UTC+0000                                 
0x8e1cd8d0 sppsvc.exe              352    452      4      144      0      0 2022-12-14 21:08:23 UTC+0000                                 
0x8e1f6a40 svchost.exe            1632    452      5       91      0      0 2022-12-14 21:08:23 UTC+0000                                 
0x8e06f2d0 SearchIndexer.          856    452     13      626      0      0 2022-12-14 21:08:28 UTC+0000                                 
0x91892030 TrueCrypt.exe          2128   1464      4      262      1      0 2022-12-14 21:08:31 UTC+0000                                 
0x91865790 svchost.exe            2760    452     13      362      0      0 2022-12-14 21:10:23 UTC+0000                                 
0x83911848 WmiPrvSE.exe           2332    584      5      112      0      0 2022-12-14 21:12:23 UTC+0000                                 
0x8e1ef208 taskhost.exe           2580    452      5       86      1      0 2022-12-14 21:13:01 UTC+0000                                 
0x8382f198 7zFM.exe               2176   1464      3      135      1      0 2022-12-14 21:22:44 UTC+0000                                 
0x83c1d030 DumpIt.exe             3212   1464      2       38      1      0 2022-12-14 21:33:28 UTC+0000                                 
0x83c0a030 conhost.exe             272    368      2       34      1      0 2022-12-14 21:33:28 UTC+0000     
```

Some interesting processes right away:
```
0x91892030 TrueCrypt.exe          2128   1464      4      262      1      0 2022-12-14 21:08:31 UTC+0000                                 
0x8382f198 7zFM.exe               2176   1464      3      135      1      0 2022-12-14 21:22:44 UTC+0000                                 
0x83c1d030 DumpIt.exe             3212   1464      2       38      1      0 2022-12-14 21:33:28 UTC+0000                                 
```

DumpIt is the software used for memory dumping, but we get a TrueCrypt and a 7z instances. Starting with TrueCrypt:

```
─$ vol.py -f TrueSecrets.raw --profile=Win7SP1x86 truecryptsummary
Volatility Foundation Volatility Framework 2.6.1
Password             X2Hk2XbEJqWYsh8VdbSYg6WpG9g7 at offset 0x89ebf064
Process              TrueCrypt.exe at 0x91892030 pid 2128
Service              truecrypt state SERVICE_RUNNING
Kernel Module        truecrypt.sys at 0x89e8b000 - 0x89ec2000
Symbolic Link        D: -> \Device\TrueCryptVolumeD mounted 2022-12-14 21:33:00 UTC+0000
Symbolic Link        Volume{d22d7a9d-7b72-11ed-b81d-0800273bf313} -> \Device\TrueCryptVolumeD mounted 2022-12-14 21:10:21 UTC+0000
Symbolic Link        D: -> \Device\TrueCryptVolumeD mounted 2022-12-14 21:33:00 UTC+0000
Driver               \Driver\truecrypt at 0xbe6b780 range 0x89e8b000 - 0x89ec1b80
Device               TrueCryptVolumeD at 0x8391b9b0 type FILE_DEVICE_DISK
Container            Path: \??\C:\Users\IEUser\Documents\development.tc
Device               TrueCrypt at 0x83e6b600 type FILE_DEVICE_UNKNOWN

```

So we just got:
```
Password: X2Hk2XbEJqWYsh8VdbSYg6WpG9g7 
File location/Name: C:\Users\IEUser\Documents\development.tc
```

Let's see if we can dump the file:
```
─$ vol.py -f TrueSecrets.raw --profile=Win7SP1x86 dumpfiles -r development.tc --dump-dir dump
```
Didn't get anything, so it probably was no longer in memory during the dump. Let's check what we get from 7z. Lots of shared dll's, but we found a zip that looks promissing:

```
└─$ vol.py -f TrueSecrets.raw --profile=Win7SP1x86 dumpfiles -D dump/ -p 2176 -S summary.txt
Volatility Foundation Volatility Framework 2.6.1
...
DataSectionObject 0x843f6158   2176   \Device\HarddiskVolume1\Users\IEUser\Documents\backup_development.zip
SharedCacheMap 0x843f6158   2176   \Device\HarddiskVolume1\Users\IEUser\Documents\backup_development.zip
...
```

File was dumped, and unziping it renders us a `development.tc` file. We got the TrueCrypt file.
Unlocking it and mounting:
```
sudo cryptsetup --type tcrypt open ./development.tc tc
sudo mount -o uid=1001 /dev/mapper/tc /mnt
└─$ tree /mnt                      
/mnt
├── $RECYCLE.BIN
│   └── desktop.ini
└── malware_agent
    ├── AgentServer.cs
    └── sessions
        ├── 5818acbe-68f1-4176-a2f2-8c6bcb99f9fa.log.enc
        ├── c65939ad-5d17-43d5-9c3a-29c6a7c31a32.log.enc
        └── de008160-66e4-4d51-8264-21cbc27661fc.log.enc

$ cat /mnt/AgentServer.cs
using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Security.Cryptography;

class AgentServer {
  
    static void Main(String[] args)
    {
        var localPort = 40001;
        IPAddress localAddress = IPAddress.Any;
        TcpListener listener = new TcpListener(localAddress, localPort);
        listener.Start();
        Console.WriteLine("Waiting for remote connection from remote agents (infected machines)...");
    
        TcpClient client = listener.AcceptTcpClient();
        Console.WriteLine("Received remote connection");
        NetworkStream cStream = client.GetStream();
    
        string sessionID = Guid.NewGuid().ToString();
    
        while (true)
        {
            string cmd = Console.ReadLine();
            byte[] cmdBytes = Encoding.UTF8.GetBytes(cmd);
            cStream.Write(cmdBytes, 0, cmdBytes.Length);
            
            byte[] buffer = new byte[client.ReceiveBufferSize];
            int bytesRead = cStream.Read(buffer, 0, client.ReceiveBufferSize);
            string cmdOut = Encoding.ASCII.GetString(buffer, 0, bytesRead);
            
            string sessionFile = sessionID + ".log.enc";
            File.AppendAllText(@"sessions\" + sessionFile, 
                Encrypt(
                    "Cmd: " + cmd + Environment.NewLine + cmdOut
                ) + Environment.NewLine
            );
        }
    }
    
    private static string Encrypt(string pt)
    {
        string key = "AKaPdSgV";
        string iv = "QeThWmYq";
        byte[] keyBytes = Encoding.UTF8.GetBytes(key);
        byte[] ivBytes = Encoding.UTF8.GetBytes(iv);
        byte[] inputBytes = System.Text.Encoding.UTF8.GetBytes(pt);
        
        using (DESCryptoServiceProvider dsp = new DESCryptoServiceProvider())
        {
            var mstr = new MemoryStream();
            var crystr = new CryptoStream(mstr, dsp.CreateEncryptor(keyBytes, ivBytes), CryptoStreamMode.Write);
            crystr.Write(inputBytes, 0, inputBytes.Length);
            crystr.FlushFinalBlock();
            return Convert.ToBase64String(mstr.ToArray());
        }
    }
}
```

This seems to be the source code we were looking for, but we still need to understand what it was doing to the target computer, and it seems like it was DES encrypting some strings into the `.enc` files we collected. But we have the key and iv, so we can just reverse the process to decrypt them. 
First, need to install mono. And then we can modify the code slightly to decrypt all files. This was my first time using C# so took a bit longer than it should, but a fun challenge anyway:
```
using System;
using System.IO;
using System.Text;
using System.Security.Cryptography;
using System.Collections.Generic;

class AgentServer {
  
    static void Main()
    {
        string directloc = Directory.GetCurrentDirectory();
        var fyles = Directory.EnumerateFiles(directloc, "*", SearchOption.AllDirectories);
        Console.WriteLine("Current folder and files: ");
        Console.WriteLine(String.Join(Environment.NewLine, fyles));

        foreach (var file in fyles)
        {
                IEnumerable<string> lines = File.ReadLines(file);
                foreach (var line in lines)
                {
                        Console.WriteLine(Decrypt(line));
                        //Console.WriteLine(Encoding.UTF8.GetString(line));
                }
        }
    
    }
    
    private static string Decrypt(string pt)
    {
        Console.WriteLine(pt);
        string key = "AKaPdSgV";
        string iv = "QeThWmYq";
        byte[] keyBytes = Encoding.UTF8.GetBytes(key);
        byte[] ivBytes = Encoding.UTF8.GetBytes(iv);

        byte[] inputBytes = Convert.FromBase64String(pt);
        
        using (DESCryptoServiceProvider dsp = new DESCryptoServiceProvider())
        {
            var mstr = new MemoryStream();
            var crystr = new CryptoStream(mstr, dsp.CreateDecryptor(keyBytes, ivBytes), CryptoStreamMode.Write);
            crystr.Write(inputBytes, 0, inputBytes.Length);
            crystr.FlushFinalBlock();
            byte[] decrpt = new byte[mstr.Length];
            mstr.Position = 0;
            mstr.Read(decrpt, 0, decrpt.Length);
            return Encoding.UTF8.GetString(decrpt);
            //return Convert.ToBase64String(mstr.ToArray());
        }
    }
}
```

And compiling and running it from the sessions folder:
```
└─$ mcs -out:../agent.exe ../AgentServer.cs; mono ../agent.exe
Current folder and files: 
/home/kali/Desktop/htb challs/mnt/sessions/5818acbe-68f1-4176-a2f2-8c6bcb99f9fa.log.enc
/home/kali/Desktop/htb challs/mnt/sessions/c65939ad-5d17-43d5-9c3a-29c6a7c31a32.log.enc
/home/kali/Desktop/htb challs/mnt/sessions/de008160-66e4-4d51-8264-21cbc27661fc.log.enc
wENDQtzYcL3CKv0lnnJ4hk0JYvJVBMwTj7a4Plq8h68=
Cmd: hostname
DESKTOP-MRL1A9O
M35jHmvkY9WGlWdXo0ByOJrYhHmtC8O0rZ28CviPexkfHCFTfKUQVw==
Cmd: whoami
desktop-mrl1a9o\john
hufGZi+isAzspq9AOs+sIwqijQL53yIJa5EVcXF3QLLwXPS1AejOWfPzJZ/wHQbBAIOxsJJIcFq0+83hkFcz+Jz9HAGl8oDianTHILnUlzl1oEc30scurf41lEg+KSu/6orcZQl3Bws=
Cmd: dir c:\users\john\documents
 Volume in drive C is Windows 7
 Volume Serial Number is 1A9Q-0313
6ySb2CBt+Z1SZ4GlB7/yL4cOS/j1whoSEqkyri0dj0juRpFBc4kqLw==
 Directory of C:\Users\john\Documents
U2ltlIYcyGYnuh0P+ahTMe3t9e+TYxKwU+PGm/UsltpkanmBmWym5mDDqqQ14J/VSSgCRKXn/E+DKaxmNc9PpPOG1vZndmflMUnuTUzbiIdHBUAEOWMO8wVCufhanIdN56BhtczjrJS5HRvl9NwE/FNkLGZt6HQNSgDRzrpY0mseJHjTbkal6nh226f43X3ZihIF4sdLn7l766ZksE9JDASBi7qEotE7f0yxEbStNOZ1QPDchKVFkw==
12/13/2022  08:15 AM    <DIR>          .
12/13/2022  08:15 AM    <DIR>          ..
               0 File(s)              0 bytes
               2 Dir(s)  25,422,577,664 bytes free
wENDQtzYcL3CKv0lnnJ4hk0JYvJVBMwTj7a4Plq8h68=
Cmd: hostname
DESKTOP-MRL1A9O
M35jHmvkY9WGlWdXo0ByOJrYhHmtC8O0eu8xtbA16kKagSu6MIFSWQ==
Cmd: whoami
desktop-mrl1a9o\paul
hufGZi+isAzspq9AOs+sI0VYrJ6o8j3e9a1tNb9m1bVwJZpRxCOxg3Vs0NdU9xNxPku+sBziVYsVaOtgWkbH9691++BUkD1BNVRMc0e69lVs2cJmQIAbnagMaJ6OQEZAAvZ/G6y57CQ=
Cmd: dir c:\users\paul\documents
 Volume in drive C is Windows 7
 Volume Serial Number is 1A9Q-0313
6ySb2CBt+Z1SZ4GlB7/yL8asWs1F/wTUTOLEHO92yuzuTzdsiM5t5w==
 Directory of C:\Users\paul\Documents
U2ltlIYcyGYnuh0P+ahTMe3t9e+TYxKwU+PGm/UsltpkanmBmWym5mDDqqQ14J/VSSgCRKXn/E+DKaxmNc9PpPOG1vZndmflMUnuTUzbiIdHBUAEOWMO8wVCufhanIdN56BhtczjrJS5HRvl9NwE/FNkLGZt6HQNSgDRzrpY0mseJHjTbkal6nh226f43X3ZihIF4sdLn7l766ZksE9JDASBi7qEotE7f0yxEbStNOZ1QPDchKVFkw==
12/13/2022  08:15 AM    <DIR>          .
12/13/2022  08:15 AM    <DIR>          ..
               0 File(s)              0 bytes
               2 Dir(s)  25,422,577,664 bytes free
wENDQtzYcL3CKv0lnnJ4hk0JYvJVBMwTj7a4Plq8h68=
Cmd: hostname
DESKTOP-MRL1A9O
M35jHmvkY9WGlWdXo0ByOJrYhHmtC8O0hn+gLHaClb4QbACeOoSiYA==
Cmd: whoami
desktop-mrl1a9o\greg
hufGZi+isAzspq9AOs+sI/u+AS/aWPrAYd+mctDo7qEt+SpW2sELvSaxx6RRdK3vDavTsziAtb4/iCZ72v3QGh78yhY2KXZFu8qAcYdN7ltOOlg1LSrdkhjgr+CWTlvWh7A8IS7NwwI=
Cmd: dir c:\users\greg\documents
 Volume in drive C is Windows 7
 Volume Serial Number is 1A9Q-0313
6ySb2CBt+Z1SZ4GlB7/yL4rJGeZ0WVaYW7N15aUsDAqzIYJWL/f0yw==
 Directory of C:\Users\greg\Documents
U2ltlIYcyGaSmL5xmAkEop+/f5MGUEWeWjpCTe5eStd/cg9FKp89l/EksGB90Z/hLbT44/Ur/6XL9aI27v0+SzaMFsgAeamjyYTRfLQk2fQlsRPCY/vMDj0FWRCGIZyHXCVoo4AePQB93SgQtOEkTQ2oBOeVU4X5sNQo23OcM1wrFrg8x90UOk2EzOm/IbS5BR+Wms1M2dCvLytaGCTmsUmBsATEF/zkfM2aGLytnu5+72bD99j7AiSvFDCpd1aFsogNiYYSai52YKIttjvao22+uqWMM/7Dx/meQWRCCkKm6s9ag1BFUQ==
12/13/2022  09:07 AM    <DIR>          .
12/13/2022  09:07 AM    <DIR>          ..
12/13/2022  09:15 AM                41 flag.txt
               1 File(s)             41 bytes
               2 Dir(s)  25,326,063,616 bytes free
+iTzBxkIgVWgWm/oyP/Uf6+qW+A+kMTQkouTEammirkz2efek8yfrP5l+mtFS+bWA7TCjJDK2nLAdTKssL7CrHnVW8fMvc6mJR4Ismbs/d/fMDXQeiGXCA==
Cmd: type c:\users\greg\documents\flag.txt
HTB{<redacted flag>}
```

And we get a list of commands and outputs used before, and our flag in displayed from one of the files!