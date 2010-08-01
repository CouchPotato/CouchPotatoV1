* Find providers that don't need login/registration
* Edit movie info

Plugins:
* Create a plugin system to allow for easy extension
* Create plugin that monitors the exception log
	plugin would also provide a Controller for the frontend
	so that a JS query can send a request every now and then
	to inform the user if a module has crashed.

Error handling:
* Catch all Exceptions by plugins unless it throws an "unresumable" error
     --> custom Exception class
* Log these Exceptions to custom log
* Have our own error handling/logging class
* Add listener/observer support for infos, might as well have events

Userscript:

* Check version for easy updating
* TheMovieDB
* Apple Trailers
* Rotten Tomatoes

Quality:

* Do something nicer with the quality column on main page.

Coming Soon Page:

* Nothing

Feeder:

* Rottentomatoes, where rating higher then xx%
* SceneReleases -> IMDB, has rating above X where user_voted > Y
* Ignore by Genre

Later:

* Max downloads per day
* Create .app for OSX