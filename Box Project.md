# Login with RFID screen
show screen and wait for a rfid to be inserted
using apps' client_credentials getToken if not expired

post rfid to api/cc/rfid-token to get clients personal access token for use in subsequent requests
~~response will have include user_id along with the token~~

can now use the user token to get some user info
api/users

permissions can be checked at
api/can
'project.create.self',
'project.view.self',
'project.edit.self',
'project.printLabel.self',

'box.buy.self',
'box.view.self',
'box.edit.self',
'box.printLabel.self',

'rfidTags.view.self',
'rfidTags.edit.self',

'snackspace.transaction.view.self',

'governance.meeting.checkIn', 

and also check the rfidTags.register permission?? or just 'pins.reactivate'??

move on to Actions screen

~~top bar on all screens from here show user name and a logout button?~~
~~also an auto logout countdown watchdog? set to 30 seconds?,~~
monitor card presence and when removed show 5 sec logout countdown 

# Actions screen
big touch buttons
Projects
Boxes
and smaller touch buttons for
register rfid card, if user can 'rfidTags.register', (new permission to add, and needed logic) or just 'pins.reactivate'??
meeting check in, if agm scheduled (api/cc/governance/meetings/next) and user can 'governance.meeting.checkIn'

# Projects index screen
api/projects

display list of projects
show this array be reversed to show latest first
just Name, current state, then buttons resume/complete & print

add project button > add project screen
back button


# Add Project Screen
input for Name and description
back button

# Box index screen
list boxes with id, dates, state and buttons for print if state BoxState::INUSE
mark remove and mark in-use buttons bases on state
text to say that to buy a box you need to go to the full HMS website
back button

# Register new RFID card screen
Scan new card to register
Back button
once card scanned and we check its not in the db already
show member search box, register card to this member button and cancel button




# Client Credentials Grant Tokens

This /oauth/token route will return a JSON response containing `access_token`, `refresh_token`, and `expires_in` attributes. The `expires_in` attribute contains the number of seconds until the access token expires.

### Retrieving Tokens

To retrieve a token using this grant type, make a request to the `oauth/token` endpoint:

    use Illuminate\Support\Facades\Http;

    $response = Http::asForm()->post('http://passport-app.com/oauth/token', [
        'grant_type' => 'client_credentials',
        'client_id' => 'client-id',
        'client_secret' => 'client-secret',
        'scope' => 'your-scope',
    ]);

    return $response->json()['access_token'];

    
### Refreshing Tokens

If your application issues short-lived access tokens, users will need to refresh their access tokens via the refresh token that was provided to them when the access token was issued:

    use Illuminate\Support\Facades\Http;

    $response = Http::asForm()->post('http://passport-app.com/oauth/token', [
        'grant_type' => 'refresh_token',
        'refresh_token' => 'the-refresh-token',
        'client_id' => 'client-id',
        'client_secret' => 'client-secret',
        'scope' => '',
    ]);

    return $response->json();

This `/oauth/token` route will return a JSON response containing `access_token`, `refresh_token`, and `expires_in` attributes. The `expires_in` attribute contains the number of seconds until the access token expires.



## RFID class

currently run in a thread that checks for a card uid in a thread loop
uid is posted to a Queue, same card can only be posted every 10 seconds
Kivy side then has to when it ready check the queue for an rfid

at time we would need to just drain the queue
logout is either by button or timeout

new idea
have the RFID lib dispatch events to the main kivy app

new Card scanned
card no longer present

still need to run in a check loop, say half a sec?

  IDLE -> new card seen (send uid) -> have a card
  have a card -> it went away (send clear) -> IDLE
  have a card -> different card appeared (send clear, then send uid) -> have a card

threading vs multiprocessor?

may still need a damn queue
event dispatcher needs to live kivy side and check the queue if found something dispatch as event

kivy app can then react to the events
assuming idle at login screen, start log in process,
if logged in and card goes away just log out
if logged in and new card then log out and log in with new card? hmm should have seen clear event first

if on register new card screen, and got uid, enable pin pad
once registered transfer fer to logged in?

KioskApp takes care of binding to the events and push screens around as needed

down side of all this is the current UDP fall back is crap
unless, just add a quick packet around the uid and if sendRfid is run sans args it sends a clear packet

# client token
{
    "token_type": "Bearer",
    "expires_in": 1292400,
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5IiwianRpIjoiNTJiNGZmMGUwZGJmYjRiNTgzYmM0NGQyNzVlODhkNWRmNjg5YTg4ZGJhZTJlYmU1MDVmMDExMWYzZmQyNmQ2MGRkMjQyZDMzMjM4ZjBjNGYiLCJpYXQiOiIxNjE2NDY5MzQ2Ljg2NjgxNSIsIm5iZiI6IjE2MTY0NjkzNDYuODY2ODIzIiwiZXhwIjoiMTYxNzc2MTc0Ni43MDU3NzUiLCJzdWIiOiIiLCJzY29wZXMiOltdfQ.KGg4NNIBa2fqwgEZrS30eCzVYUuZaB7U9zPCnxaeSr89hD6cFxnSwrM89Bg36vDKOBBTe9fZ-p7CyAW1VWhRADNGwNOUv9t29ufAgWnCX4dkWwMUsG-GGQlKThH6pi8aEEk_xKO_ZB0WoNAE7_2F5wGjzJrEdP-j_Lv0f8fQVe1DJLJ6-LWD9Roniylcjp09hd_-WGpc-MWDsDZZ2uYN6un6enH2idTbQ6FCDpGLLcOvdlxnOiCBuMaFM7Yq3Y7Y8PSiXfhwzHlMPUprC5p4iwjrhpmXtLvg3vxtybqPFkRXVkc8uuts6B9H8der036SXW5U3RU48Il7aa9L8MbM43a0FlbAKR17u__0GKmI1juo9ddOmUAsFeEuOcJHAmNs3dP7NKXHaJ1aeMIqSld8JKO_bJtoRCLcf0UA0vI8M1Hb9sxO8VqchOSBQRersY5X-TM2RF3X6xbI3rbwnPSp9r6P651SPVVSUfsHaEJyBRS27MAQIEINHRkwpiRIpmnfOiOoqKCuo0baoCAtRM7Phm_6VhBR-GfAsrzinE2si2BDFTEz_0tejuL_6c3EseW9XiiizPr6t1bPnzwRD0v1wrl_jPo-5Xq5o_tQk17nJOqEiV6F__krYkTFfsmCm8CdCs7aGqWngcXxcnWEImkqS8eWUzvy5Ge6pC26arXv1AY"
}

# rfid token

{
    "token_type": "Bearer",
    "expires_in": 1295999,
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxMCIsImp0aSI6IjBmMDUxNmZhMDg0NDRkNmI5NGIwNTIwMzAyZGE4ZmNlMzE0N2MwNzM4OWYzMTRjZTc0OWRiMjkyYzMzN2MwZjIwYzc3MTNkYTA1MjFiOTYwIiwiaWF0IjoiMTYxNjQ2ODc3OS40MzU2MzYiLCJuYmYiOiIxNjE2NDY4Nzc5LjQzNTY0MyIsImV4cCI6IjE2MTc3NjExNzkuMTY2MzA5Iiwic3ViIjoiOTUzIiwic2NvcGVzIjpbXX0.Ol0dydyadgcKXWhi0_Jl4eoyLgMqWiIiq8pXGL1-mQ1yfyk6doS0LoaKa7Vf8B_tv1MAXQF0bjPyRXz-CDKMWH8WLA7G96UOCV_PnxbLWfN4lswmDIBdWiRB9X0KakaRtFukU47LXVj1c6k4F95uCXRKw6yQXRITwZWjb-a-OpLFQfIZPFk_1XGlA42Ob_86wNCMcmNmAXHapnpEnCFDNKPOsm72lQTZAo_ENjuSB5-_mpiRr1eB6if0mKuu10VJtKlnjR2F19AthN5b9z6KslP34yp1lIiLii-76rcgQcwocf5IGzsPDCPuPop__SBvVZN0i60nm-mlgkKiKfyPTs5uBMj191i4PPfX4se--GVVN0mPKzqpQt9GXC5Rnm-tO0prFVXAqair0iHFxltRWIJ_Su23KJRtGcgVGoPOsoucw1xqYEbhhp4xWIy-wpkfABiKaeIWjdXxrTr_xzhWkQhZ_UrbNk89OIeOYrdll9IVxKO-hqIUOdEhOMsPmss3cFFOP0mkhi4hiJmdad1XyOXBEepQRrRi0KpfQTNCb5GHCupstxpxOeGhJpF0rjGNBLK9kKJAL70v99jtFeoP7Fjoj_8XS4m18VtSDU4HzD3LzbiyaITpwBhq5bQ4Ok5oDa12fynl0jabR4t9ngtofZP02hN8u9Lp69VkJf5Xg7E"
}
