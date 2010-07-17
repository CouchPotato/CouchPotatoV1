CouchPotato
=====

*This is my first Python app, so it WILL contain lots of bugs and crappy code.*

CouchPotato (CP) is an automatic NZB and torrent downloader. You can keep a "movies I want"-list and it will search for NZBs/torrents of these movies every X hours.
Once a movie is found, it will send it to SABnzbd or download the torrent to a specified directory.

Features:

* Automatic downloading and sending of NZBs to SABnzbd
* Automatic downloading of torrents files to a specified directory
* Easy adding movies via IMDB UserScript
* Movie sorting & renaming
* Trailer downloading
* Quality options to download best available. Overwrite if better is found.


![preview thumb](http://github.com/RuudBurger/CouchPotato/raw/master/media/images/screenshot.png)

IMDB UserScript:

![imdb](http://github.com/RuudBurger/CouchPotato/raw/master/media/images/imdbScriptPreview.png)

If you find a bug or need a feature that you think is awesome! Let me know!

## Todo

[Can be found here](http://github.com/RuudBurger/CouchPotato/blob/master/todo.md)

## Dependencies

To run CP you will need Python.

## Installation and Setup

Windows:

* Download the latest Windows build [Can be found here](http://github.com/RuudBurger/CouchPotato/downloads)
* Extract it wherever you like
* Start CouchPotato.exe
* Set your username & password in the settings if you want.
* Fill in all the config stuff

OSx:

* If you're on Leopard (10.5) install Python 2.6+: [Python 2.6.5](http://www.python.org/download/releases/2.6.5/)
* Git clone/extract CP wherever you like
* Run "CouchPotato.app"
* Set your username & password in the settings if you want.
* Fill in all the config stuff

Linux:

* Install Python 2.6 or higher
* Git clone/extract CP wherever you like
* Run "python CouchPotato.py -d" to start in deamon mode
* Set your username & password in the settings if you want.
* Fill in all the config stuff

Ubuntu (init.d script):

* Copy "initd" to /etc/init.d/couchpotato - > "sudo cp initd /etc/init.d/couchpotato"
* If you want, change "RUN_AS=root" to another user.
* Make executable "sudo chmod a+x /etc/init.d/couchpotato"
* Start "sudo /etc/init.d/couchpotato start"

Other:

* [QNAP Guide can be found here](http://forums.sabnzbd.org/index.php?topic=4636.msg33541#msg33541)

## Update

To update just overwrite all the files with the new ones. Config.ini and data.db should be untouched.
