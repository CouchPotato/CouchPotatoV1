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
* Quality options to download best available. Overwrite if better is found.


![preview thumb](http://github.com/RuudBurger/Movie-Manager/raw/master/media/images/screenshot.png)

IMDB UserScript:

![imdb](http://github.com/RuudBurger/Movie-Manager/raw/master/media/images/imdbScriptPreview.png)

If you find a bug or need a feature that you think is awesome! Let me know!

## Todo

[Can be found here](http://github.com/RuudBurger/Movie-Manager/blob/master/todo.md)

## Dependencies

To run MM you will need Python.

## Installation and Setup

Windows:

* Download the latest Windows build "r6": [Can be found here](http://cl.ly/2b7a21de73313725cc32)
* Extract it wherever you like
* Start MovieManager.exe
* Set your username & password in the settings if you want.
* Fill in all the config stuff

OSx
* If you're on Leopard (10.5) install Python 2.6+: [Python 2.6.5](http://www.python.org/download/releases/2.6.5/)
* Git clone/extract MM wherever you like
* Run "MovieManager.app"
* Set your username & password in the settings if you want.
* Fill in all the config stuff

Linux:

* Install Python 2.6 or higher
* Git clone/extract MM wherever you like
* Run "python MovieManager.py -d" to start in deamon mode
* Set your username & password in the settings if you want.
* Fill in all the config stuff

Ubuntu (init.d script):

* Copy "initd" to /etc/init.d/moviemanager - > "sudo cp initd /etc/init.d/moviemanager"
* If you want, change "RUN_AS=root" to another user.
* Make executable "sudo chmod a+x /etc/init.d/moviemanager"
* Start "sudo /etc/init.d/moviemanager start"

Other:

* [QNAP Guide can be found here](http://forums.sabnzbd.org/index.php?topic=4636.msg33541#msg33541)

## Update

To update just overwrite all the files with the new ones. Config.ini and data.db should be untouched.
