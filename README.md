#Winst FakeG

the server for replacing google's long-gone google data v2.

--------

##project status

function/API      | working on PC(custom client based on legit) | working on android(legit gapps from that time) | complete
---------------------------------------------------------------------------------------------------------------------------
google login      | yes(tcli, tcli2 and testcli)                | no/untested                                    | no
blogger           | partly(implementation in progress)          | no(google login needed)                        | no
youtube           | no(need official client working first       | no(google login and more needed)               | no

##info
###project goal
The goal of this project is to make servers that work with official google clients from the android 4.0.4 era, not to make client patches.
This project is not built to infringe on copyright and tries to reimplement everything bit by bit.

###project contribution rules
1. Do not make breaking changes, the goal is to make something that works for everyone. if you do, include a migrator for every previous breaking change(from 0.0.1)
2. This is not a "do everything, leave no control" project, this is a user-controlled thing after all.
3. Do not open a server publically and claim it's official.
4. The server will remain open-source
5. This is not a mail software. don't try to make it one. we use fake, server-bound emails to bypass the connecting to google part.
6. Major parts of the code are AI generated. I will not claim otherwise as I'd rather be transparent than hide this.

###usage guidelines
1. any server claiming to be official is not. do not trust it.
2. you manage HTTPS and more, we implement the backend and API, not https.
3. feel free to enjoy!

###dependencies
This project is built SOLELY for linux. Windows users will need WSL and workarounds to use it.
This software depends on the `uv` software. verify availability for your distro before complaining.

##why
I started this project because I am strongly against E-waste and the discontinuation of Google Data API(API V2) has caused a surge in E-waste.
I want to reimplement it so instead of throwing that old phone or tablet, you look at this and think "oh, something cool to do with it instead of throwing it away".
Also, I know you may have spent good money on it so why not keep using it until it's completely dead.
This is mostly part of a fight against E-waste, planned obselecense and a hobby project.
No, this will **not** recreate the 2G/3G network your phone or tablet depended on, they are shutting down, no one can help it.

##project motto
This project is held together by a motto, and a purpose, "keeping dead devices alive".
What do I mean by this? I mean keeping working hardware and rebuilding services it depended on local-first.
This doesn't mean "make a 3G or 2G network all over again", this means "rebuild servers it depended on without the original servers".
