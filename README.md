PaStaSPyGe
==========

Paras Staattisien sivujen Pythonistinen generaattori.
Remake of (RaStaSPyGe)

Copyright 2013 Kapsi Internet-käyttäjät ry

Tekijä: Antti Jaakkola

Installation
============

Remote machine (www-server):

Create mysite.git repository

$ mkdir mysite.git
$ cd mysite.git
$ git init --bare
$ cd ..

Then copy hooks/post-receive hook from pastaspyge to mysite.git/hooks
directory and make it executable (chmod +x). Also remember to fix
DOCUMENT\_ROOT, PAGE\_REPO and PASTASPYGE variables to correct values.

Then create copy of mysite.git

$ git clone mysite.git .mysite

Local machine (workstation):

Create site repository using git

$ mkdir mypage
$ cd mypage
$ git init

Copy example directory content to new repository.

$ git add .
$ git commit -m "init"
$ git remote add origin username@myhost:/path/to/mysite.git
$ git push origin master

Now you have very simple git based "cms"

Directories
===========
Templates/-directory contains templates.

Dynamic/-directory contains files that needs generating.

Static/-directory contains static files, those are directly copied to 
docroot.

Output/-directory is used for generated files.

