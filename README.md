Movie Manager
=====

*This is my first Python app, so it WILL contain lots of bugs and crappy code.*

Movie Manager (MM) is an automatic NZB downloader. You can keep a "movies I want"-list and it will search for NZBs of these movies every X minutes.
Once a movie is found, it will send it to SABnzbd.

Features:

* Automatic downloading and sending of NZBs to SABnzbd
* Easy adding movies via IMDB UserScript
* Movie sorting & renaming
* Trailer downloading


![preview thumb](http://github.com/RuudBurger/Movie-Manager/raw/master/media/images/screenshot.png)

IMDB UserScript:

![imdb](http://github.com/RuudBurger/Movie-Manager/raw/master/media/images/imdbScriptPreview.png)

If you find a bug or need a feature that you think is awesome! Let me know!

## Todo

[Can be found here](http://github.com/RuudBurger/Movie-Manager/blob/master/todo.md)

## Dependencies

To run MM you will need Python.

## Installation and Setup

OSx & Linux:

* Install Python 2.6 or higher
* git clone/extract MM wherever you like
* Rename "config.ini_tmpl" to "config.ini"
* Run "python MovieManager.py -d" to start in deamon mode
* Default login is "username" & "password"
* Change username & password
* Fill in all the config stuff

Ubuntu (init.d script):

* Copy "initd" to /etc/init.d/moviemanager - > "sudo cp initd /etc/init.d/moviemanager"
* If you want, change "RUN_AS=root" to another user.
* Make executable "sudo chmod a+x /etc/init.d/moviemanager"
* Start "sudo /etc/init.d/moviemanager start"

Windows:

* Download the latest Windows build: [Can be found here](http://cl.ly/8482178457ef26bfcc88)
* Extract it wherever you like
* Start MovieManager.exe
* Default login is "username" & "password"
* Change username & password
* Fill in all the config stuff

## Update

To update just overwrite all the files with the new ones. Config.ini and data.db should be untouched.
