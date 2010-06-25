Movie Manager
=====

*This is my first Python app, so it WILL contain lots of bugs and crappy code.*

Movie Manager (MM) is an automatic NZB downloader. You can keep a "movies I want"-list and it will search for NZBs of these movies every X minutes.
Once a movie is found, it will send it to SABnzbd.

![preview thumb](http://github.com/RuudBurger/Movie-Manager/raw/master/moviemanager/public/media/images/screenshot.png)

IMDB UserScript:

![imdb](http://github.com/RuudBurger/Movie-Manager/raw/master/moviemanager/public/media/images/imdbScriptPreview.png)

If you find a bug or need a feature that you think is awesome! Let me know!

## Todo

[Can be found here](http://github.com/RuudBurger/Movie-Manager/blob/master/todo.md)

## Dependencies

To run MM you will need Python, Pylons and SQLAlchemy.

## Installation and Setup

OSx & Linux:

* Install Python 2.6 or higher
* git clone/extract MM wherever you like
* Run "sudo python setup.py install"
* Rename "config.ini_tmpl" to "config.ini"
* Run "paster serve config.ini" to start
* Goto http://localhost:5000 and login using "username" & "password"
* Change username & password
* Fill in all the config stuff

Ubuntu (init.d script):

* Copy "initd" to /etc/init.d/moviemanager - > "sudo cp initd /etc/init.d/moviemanager"
* Make executable "sudo chmod a+x /etc/init.d/moviemanager"
* Start "sudo /etc/init.d/moviemanager start"

Windows (as service):

* Install Python 2.6 or higher (http://www.python.org/download/)
* Install PyWin32 (http://sourceforge.net/projects/pywin32/files/)
* git clone/extract MM wherever you like
* Run "setup.py install"
* Rename "config.ini_tmpl" to "config.ini"
* Run "WindowsService.py install" as admin
* Run "WindowService.py start" as admin
* Goto http://localhost:5000 and login using "username" & "password"
* Change username & password
* Fill in all the config stuff