# Chall description

Can you break into the Philanthropy website and get more information on Snake and Otacon?

# Write up

Navigating to the webpage reveals a login form where I could register for a new account. Doing this and looking around revealed a control panel that would let me update the account name. There was also a `member` field. Trying to update this field just like the names are updated allowed to escalate the account to member.

Once a member, I could identify an API call to images with an email in the query, and the response leaked several emails to try. One of these was `solidsnake@protonmail.com`, the account mentioned in the description, and looking it up revealed an image with the flag written.