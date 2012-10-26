CouchPotato
=====

# Please use the new version of CP (v2), which can be found on the main site.

Version 36:

* [See diff for changes](https://github.com/RuudBurger/CouchPotato/compare/fd6cb0b870ff39e70b26aea6cbaeeebf4a07773c...8d652f7044cffd28c88bbcf14897c8fe4a9de5c7)

Version 35:

* I'm lazy ;)
* [See diff](https://github.com/RuudBurger/CouchPotato/compare/6ef1e06b33711bcb122c2520fc8c12b2f4b20df4...fd6cb0b870ff39e70b26aea6cbaeeebf4a07773c)


Version 34:

* New: Synology Media Server support
* New: RottenTomatoes userscript
* New: NZBget support
* New: Transmission support
* New: NotifyMyAndroid notifications
* New: NZBsRus support
* Enhancement: Check for update in diff thread
* Enhancement: Providers in https
* Enhancement: Created own ETA searcher
* [See diff](https://github.com/RuudBurger/CouchPotato/compare/ba91f05a58d29e490368aafc6b6f0c6dcfde0bf9...6ef1e06b33711bcb122c2520fc8c12b2f4b20df4)


Version 33:

* New: Bluray.com automated movie downloading, based on score and year
* Fix: Catch unicode decoding error when walking through download folder
* Fix: Catch provider errors
* Fix: Redirecting issues
* Enhancement: Better score calculation
* [See diff](https://github.com/RuudBurger/CouchPotato/compare/ba91f05a58d29e490368aafc6b6f0c6dcfde0bf9...master)


Version 32:

* [See diff](https://github.com/RuudBurger/CouchPotato/compare/604f2b516bfc6991ab5bece75cc6794b26d18ac4...ba91f05a58d29e490368aafc6b6f0c6dcfde0bf9)

Version 31:

* New: Plex Media Server support
* New: Growl support
* New: Prowl support
* New: Notifo support
* New: Newzbin support
* [More](https://github.com/RuudBurger/CouchPotato/compare/50f84cd6725766b42a5ab3d8e1c4a1af2b2fd018...604f2b516bfc6991ab5bece75cc6794b26d18ac4)

Version 30:

* New: Safari Extension
* New: Popcorn Hour notification support
* New: Newzbin support
* Enhancement: Firefox only - UserScript: allocine.fr
* Enhancement: New icon!
* Enhancement: Log retention messages
* [More](https://github.com/RuudBurger/CouchPotato/compare/e78659c8892619773c64b1249ce40bc4f0f7522a...50f84cd6725766b42a5ab3d8e1c4a1af2b2fd018)

Version 29:

* Fix: Bug in UserScript crashed Chrome
* Fix: Bug in ignored words returned empty list
* [More](https://github.com/RuudBurger/CouchPotato/compare/65ade7a0dc978c23ef44a6bb54e8fea3d6c0ae03...e78659c8892619773c64b1249ce40bc4f0f7522a)

Version 28:

* New: Ignore NZB/Torrent with specific words
* New: Require specific words inside a NZB/Torrent 
* Enhancement: UserScript, Direct to TV movie support for IMDB
* Enhancement: UserScript, MovieMeter.nl support
* Enhancement: UserScript, Whiwa.net support
* Enhancement: UserScript, Trakt.tv support
* Enhancement: Firefox only - UserScript, AppleTrailer support
* Enhancement: Firefox only - UserScript, TMDB support
* Enhancement: English only support for NZBMatrix feed
* Enhancement: Allow dvdr inside screener searches
* Enhancement: Clear all downloaded movies from Wanted page
* Enhancement: IMDB post processing for renamer
* [More](https://github.com/RuudBurger/CouchPotato/compare/59212f6d9b29d7b4db00fe615838f00aa7071264...65ade7a0dc978c23ef44a6bb54e8fea3d6c0ae03)

Version 27:

* Fix: Quality in naming options not working correctly.
* Fix: Config not working in IE.
* Fix: No more "page not found"-errors in log.
* [More](https://github.com/RuudBurger/CouchPotato/compare/9041f8d5ff2998f8b6207311281835872b381d7f...59212f6d9b29d7b4db00fe615838f00aa7071264)

Version 26:

* New: Preferred words for searching in "Settings >> General".
* New: Download meta-data. Poster, fanart, .nfo file.
* New: XBMC Notifications.
* Enhancement: Ability to disable the updater.
* Enhancement: Better movie detection when renaming.
* Enhancement: Settings page instead of popup.
* Enhancement: R5 DVD-R is allowed
* Enhancement: Added <resolution> and <sourcemedia> to renaming filenames.
* Fix: Don't autofill usernames and passwords.
* Fix: Updated updater for new GitHub download page layout.
* Fix: Images from TheMovieDB couldn't be downloaded.
* Fix: OpenSubtitle didn't always stay logged in.
* Fix: Move .idx files along with .sub files.
* [And a lot more fixed here](https://github.com/RuudBurger/CouchPotato/compare/f60d448ad0...9041f8d5ff2998f8b6207311281835872b381d7f)

Version 25:

* New: Subtitles support using SubScene and OpenSubtitles
* Enhancement: Link to Changelog when new Windows Build is available.
* Enhancement: Better logging class.
* Enhancement: SQLAlchemy updated to 0.6.4, removed unused code.
* Enhancement: Optimized PNGs, Movie list and CSS.
* Enhancement: Movie manage page, beginning.
* Enhancement: Mootools 1.3
* Fix: NZBs.org needs API-key for RSS check.
* Fix: Don't bug out the search on invalid RSS feed.

Version 24:

* Enhancement: Use movie object to get extra movie information on startup.
* Fix: Would quit on startup, because of invalid tMDB xml.

Version 23:

* New: Newznab.com support
* Enhancement: "Scroll to top"-button
* Enhancement: Score points for AC3 and DTS
* Enhancement: Ability to re-add nzb/torrent and search for other version to download
* Enhancement: Rename trailer on overwrite with better quality
* Enhancement: Renamer, change word seperator to space, dash or dot
* Enhancement: Ability to disable providers
* Enhancement: Mark existing non-renameable downloads with _EXISTS_ 
* Fix: Better link to wanted, snatched downloaded
* Fix: Changed default BR-Rip maximum size
* Fix: Strip config string values
* Fix: Strip http:// off of host, if necessary
* Fix: Removed duplicate ETA search
* Fix: Ignore empty "ignore words"
* Fix: Use lowercase for better quality guessing
* Fix: Allow 720p in BR-Rip searches
