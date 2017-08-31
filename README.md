Baseball Game Thread Bot for Reddit
=====================================
Maintained by Todd Roberts
https://github.com/toddrob99/Baseball-GDT-Bot

Forked from Baseball GDT Bot by Matt Bullock
https://github.com/mattabullock/Baseball-GDT-Bot

### Current Version: 4.4.0
	
This project contains a bot to post off day, pregame, game, and postgame discussion threads on Reddit for a given MLB team, and keep those threads updated with game data while games are in progress. This fork is written in Python 2.7, using PRAW 5 to interface with the Reddit API.

---

### Setup and Configuration

#### OAuth Setup

Go to reddit.com’s app page (https://www.reddit.com/prefs/apps), click on the “are you a developer? create an app” button. Fill out the name, description and about url. Name must be filled out, but the rest doesn’t matter. Write whatever you please. For redirect uri set it to `http://localhost:8080`. All four variables can be changed later.

Next, open setup.py, fill in the `client_id`, `client_secret` and `redirect_uri` fields from your Reddit app and run the script. Your browser will open. Make sure you are logged in to Reddit as the user you want the bot to run as, and click allow on the displayed web page. 

Enter the code (everything after code=) from the URL in the browser address bar into the console and your refresh token will be displayed. Copy the refresh token for the next step.

Finally, copy `sample_settings.json` to the `src` folder and rename it to `settings.json`. Fill in the `CLIENT_ID`, `CLIENT_SECRET`, `REDIRECT_URI`, and `REFRESH_TOKEN` fields in the settings.json file and save. 

#### Configuration Settings

The following settings can be configured in `src/settings.json`:

* `CLIENT_ID`, `CLIENT_SECRET`, `REDIRECT_URI`, `REFRESH_TOKEN` - these are used to authenticate with the Reddit API. See `OAuth Setup` section above

* `USER_AGENT` - user agent string to identify your bot to the Reddit API - this will be appended to the system-generated user agent (e.g. "implemented for r/Phillies by u/toddrob")

* `SUBREDDIT` - subreddit that you want the threads posted to (do not include "/r/", e.g. "Phillies")

* `TEAM_CODE` - three letter code that represents team - not always what you think (Cubs: CHN, Yankees: NYA)! look this up by running `lookup_team_code.py` and entering the team name (e.g. Phillies, Athletics, Cardinals), name abbreviation (e.g. CHC, STL, CWS), city (e.g. Chicago, Miami, Anaheim)

* `BOT_TIME_ZONE` - time zone of the computer running the bot ("ET", "CT", "MT", "PT")

* `TEAM_TIME_ZONE` - time zone of the team ("ET", "CT", "MT", "PT")

* `STICKY` - do you want the threads stickied? bot must have mod rights. (true/false)

* `FLAIR_MODE` - do you want to set flair on offday/pre/game/post threads using a mod command (bot user must have mod rights), as the thread submitter (sub settings must allow), or none? ("none", "submitter", "mod") **NOTE**: in order to use this, you may have to re-do the OAuth setup process described above to obtain a new refresh token that includes flair permissions.

* `LOG_LEVEL` - controls the amount of logging to the console (0 for none--not recommended, 1 for error only, 2 for normal/info (default), 3 for debug, 4 for verbose debug)

* `OFF_THREAD` - offday thread settings
	* `ENABLED` - do you want an off day thread on days when your team does not play? (true/false)
	* `TAG` - prefix for the thread title ("OFF DAY THREAD:")
	* `TIME` - time to post the offday thread ("8AM" in context of BOT_TIME_ZONE)
	* `BODY` - text to include in the body of the post ("No game today. Feel free to discuss whatever you want in this thread.")
	* `SUGGESTED_SORT` - what do you want the suggested sort to be? set to "" if your bot user does not have mod rights ("confidence", "top", "new", "controversial", "old", "random", "qa", "")
	* `INBOX_REPLIES` - do you want to receive thread replies in the bot's inbox? (true/false)
	* `FLAIR` - flair to set on the thread, if `FLAIR_MODE` is not "none" ("Off Day Thread")

* `PRE_THREAD` - pregame thread settings
	* `ENABLED` - do you want a pre game thread? (true/false)
	* `TAG` - prefix for the thread title ("PREGAME THREAD:")
	* `TIME` - time to post the pregame thread ("8AM" in context of BOT_TIME_ZONE)
	* `SUGGESTED_SORT` - what do you want the suggested sort to be? set to "" if your bot user does not have mod rights ("confidence", "top", "new", "controversial", "old", "random", "qa", "")
	* `INBOX_REPLIES` - do you want to receive thread replies in the bot's inbox? (true/false)
	* `FLAIR` - flair to set on the thread, if `FLAIR_MODE` is not "none" ("Pregame Thread")
	* `CONSOLIDATE_DH` - do you want to consolidate pre game threads for doubleheaders? (true/false)
	* `CONTENT` (`BLURB`, `BROADCAST`, `PROBABLES`, `FIRST_PITCH`, `DESCRIPTION`) - what to include in the body of the post (true/false)

* `GAME_THREAD` - game thread settings
	* `TAG` - prefix for the thread title ("GAME THREAD:")
	* `HOURS_BEFORE` - number of hours prior to game time that the bot posts the game thread (1, 2, 3, etc.)
	* `SUGGESTED_SORT` - what do you want the suggested sort to be? set to "" if your bot user does not have mod rights ("confidence", "top", "new", "controversial", "old", "random", "qa", "")
	* `INBOX_REPLIES` - do you want to receive thread replies in the bot's inbox? (true/false)
	* `FLAIR` - flair to set on the thread, if `FLAIR_MODE` is not "none" ("Game Thread")
	* `MESSAGE` - send submission shortlink to /u/baseballbot to add a link to the game thread on the /r/Baseball sidebar (true/false)
	* `HOLD_DH_GAME2_THREAD` - do you want to hold the game thread for doubleheader game 2 until game 1 is final? (true/false)
	* `EXTRA_SLEEP` - do you want the bot to sleep longer than 5 seconds between game thread edits? set this to the number of seconds (e.g. 25 for a total sleep of 30 seconds; default: 0)
	* `CONTENT` - what to include in the body of the post
		* `HEADER`, `BOX_SCORE`, `LINE_SCORE`, `SCORING_PLAYS`, `HIGHLIGHTS` - sections to include in the post (true/false)
		* `FOOTER` - text to include at the end of the post ("\*\*Remember to sort by new to keep up!\*\*")
		* `THEATER_LINK` - include link to the game's highlights on baseball.theater in the Highlights section (true/false)
		* `PREVIEW_BLURB` - include game headline and blurb in the thread header until the game starts (true/false)
		* `PREVIEW_PROBABLES` - include probable pitchers in game thread until the game starts (true/false)

* `POST_THREAD` - postgame thread settings
	* `ENABLED` - do you want a post game thread? (true/false)
	* `WIN_TAG` - prefix for the thread title when game result is win ("OUR TEAM WON:")
	* `LOSS_TAG` - prefix for the thread title when game result is loss ("OUR TEAM LOST:")
	* `OTHER_TAG` - prefix for the thread title when game result is tie/postponed/suspended/canceled ("POST GAME THREAD:")
	* `SUGGESTED_SORT` - what do you want the suggested sort to be? set to "" if your bot user does not have mod rights ("confidence", "top", "new", "controversial", "old", "random", "qa", "")
	* `INBOX_REPLIES` - do you want to receive thread replies in the bot's inbox? (true/false)
	* `FLAIR` - flair to set on the thread, if `FLAIR_MODE` is not "none" ("Postgame Thread")
	* `CONTENT` - what to include in the body of the post
		* `HEADER`, `BOX_SCORE`, `LINE_SCORE`, `SCORING_PLAYS`, `HIGHLIGHTS` - sections to include in the post (true/false)
		* `FOOTER` - text to include at the end of the post ("\*\*Remember to sort by new to keep up!\*\*")
		* `THEATER_LINK` - include link to the game's highlights on baseball.theater in the Highlights section (true/false)

---

If something doesn't seem right, feel free to message me on reddit or post it as a bug on github.

This was written in Python 2.7, so beware if you are running Python 3 or
	above that it may not work correctly. Also make sure you install
	praw and simplejson before running!

Modules being used:

	praw 5.0.1 - interfacing reddit
	simplejson - JSON parsing
	urllib2 - pulling data from MLB servers
	ElementTree - XML parsing

---
### Change Log

#### v4.4.0
* Significant changes to settings
	* Renamed thread settings sections to `OFF_THREAD`, `PRE_THREAD`, `GAME_THREAD`, and `POST_THREAD`
	* Moved individual `XXXX_THREAD` boolean settings to their respective sections and renamed to `ENABLED` (Note: game thread still cannot be disabled)
	* Moved/split `SUGGESTED_SORT` and `INBOX_REPLIES` (renamed) into off/pre/game/post thread sections - these can now be set differently for each thread type
	* Moved `MESSAGE` setting into `GAME_THREAD` section
	* Shortened names of settings inside off/pre/game/post thread (`TAG`, `TIME`, `BODY` (offday only), and `FLAIR` (change for offday only))
	* Renamed `POST_TIME` to `HOURS_BEFORE` and moved inside `GAME_THREAD` section
	* Renamed thread tag settings in `POST_THREAD` section
	* Moved `LOG_LEVEL` above the thread settings in `sample_settings.json`
	* Deprecated `WINLOSS_POST_THREAD_TAGS` setting (make all 3 the same if you don't want different tags for wins and losses)
	* Included temporary support for deprecated settings. Will remove in a later version
* Updated settings descriptions in `README.md`
* Removed exception handling around settings load. This will result in a more useful message being displayed if the settings file contains invalid json format or the load fails for another reason that's not handled
* Changed when user agent is concatenated
* Updated logic to determine if game is final using `get_status()` instead of checking game thread code
* Added `EXTRA_SLEEP` option to `GAME_THREAD` settings section to allow bot runners to specify additional wait time between game thread edits (in seconds, default 0)
* Added validation of authorized reddit.com API scopes for bot user. A warning will be logged if any recommended scopes are missing (`LOG_LEVEL` 2+)
* Updated `generate_probables()` (renamed from `generate_pre_probables()` to use `gamecenter.xml` for probables data instead of `linescore.json`, because probables data is removed from `linescore.json` after the game exits Preview status
* Split up `PROBABLES` table in pregame thread, into `PROBABLES` and new `BROADCAST` setting; added pitcher blurb to `PROBABLES`
* Added `PREVIEW_PROBABLES` option to `GAME_THREAD` settings. Shows probable pitchers (including blurb) in game thread while game is in Preview status
* Added validation of `FLAIR` before attempting to set flair for off/pre/game/post threads
* Fixed loop resulting from a postponed game by removing `timechecker.ppcheck()` and letting the overall game status check handle it

#### v4.3.0
* Added `BLURB` pregame thread option and `PREVIEW_BLURB` game thread option, to include game headline and blurb in header (same blurb, but only show in game thread until game starts)
* Updated to use `self.SETTINGS` dict for settings, instead of separate variables for each setting. Made SETTINGS dict available in editor module. This reduces the likelihood of breakage later when adding/changing settings, as the order no longer matters (in the code; the order never mattered in the settings file)
* Removed validation of `REFRESH_TOKEN` since it is not used in the code anywhere (only used in `setup-oauth.py`)
* Fixed `DESCRIPTION` setting not being honored in pregame thread settings
* Changed the order files are downloaded from MLB servers, in order to make gamecenter.xml available prior to game start
* Reduced parameters being passed between functions, used `self.SETTINGS` directly instead
* Removed some redundancy and extra file downloads from the function that determines whether your team won
* Updated `edit.generate_pre_code` function to take games parameter with gameid, in order to pull data about the games without needing separate parameters
* Removed extra slashes in URLs in `edit.generate_code` function
* Moved PRAW instantiation to after timezone and team code validations
* Added logging of Reddit authentication scopes for log level 3+

#### v4.2.0
* Renamed `setup.py` to `setup_oauth.py`
* Added github URL to PRAW user agent and added label to refresh token output in `setup_oauth.py`
* Created `lookup_team_code.py` to help users determine what to use for TEAM_CODE
* Added `lookup_team_info` function, used it to display the better-known team abbreviation in scoring plays section (e.g. CWS instead of CHA)
* Added validation of `TEAM_CODE`, with fatal error resulting from invalid code
* Updated `baseball.theater` link format, will now support doubleheaders
* Moved check for "Decisions" to end of list to ensure more specific statuses (tie, postponed, etc.) take precedence
* Added display of Reddit API Calls after each game edit loop, with `LOG_LEVEL` of 3+
* Added 10 second cool-down betwen game thread edits if getting close to Reddit API rate limit (<10% remaining)
* Added logic to not edit game thread if code has not changed, reducing the rate of Reddit API calls
* Reduced sleep between game thread edit checks to 5 seconds
* Bot will no longer edit game thread immediately after posting
* Bot will now sleep for 5 minutes if all posted games are in `Preview`/`Pre-Game` status (instead of editing every 10 seconds)
* Added log level 4 to print game/thread variables between thread updates
* Additional minor logging improvements
* Stress-tested bot with 5 concurrent games to confirm Reddit API rate limit would not be reached. The maximum usage was below 20% of the rate limit.

#### v4.1.3
* Fixed unsticky of stale offday thread the next day
* Minor logging adjustments

#### v4.1.2
* Fixed clearing of offday thread variable the next day
* Bot will now regenerate title for doubleheader game 2 after game 1 is final, if game 2 thread is not yet posted. This will pull in the new team records as long as the MLB data has been updated.
* Minor logging adjustments

#### v4.1.1
* Fixed message to /u/baseballbot, was failing to generate the shortlink (hotfixed in v4.0.0)
* Added "Game Note" to pregame thread via new `PRE_THREAD_SETTINGS`:`CONTENT`:`DESCRIPTION` setting (default true), and to game/post thread at the end of the header table. This comes from the "Description" field which included in the MLB data for makeup games, e.g. "Makeup of 5/10 PPD"
* Added and improved some log entries
* Fixed posting/editing quirks related to doubleheader consolidated pregame threads
* Base user agent string will now be generated programmatically, and the USER_AGENT setting will be appended.
* Added support for MLB not specifying a valid start time for doubleheader game 2. MLB apparently publishes 3:33am for game 2 of a straight doubleheader, so if game 2 start time is before game 1 start time, the bot will use game 1 start time plus 3 hours for game 2 start time. This will only apply to posting time of the game thread for game 2.
* Added `HOLD_DH_GAME2_THREAD` option to override `POST_TIME` and hold game thread for doubleheader game 2 until game 1 is final (default true)

#### v4.0.0
* First official version of this fork
* Updated to support praw 5.0.1
* Rewrote core posting logic to support concurrent games (pre-season split squad)
* Added support for doubleheaders
	* Pregame threads can be posted separately (at the same time) or consolidated with the new `CONSOLIDATE_PRE` setting
	* Game, postgame, and non-consolidated pregame threads will have a "Game #" suffix on the end of the thread titles
	* Consolidated pregame threads will have a "DOUBLEHEADER" suffix on the end of the thread title
* Added support for off day threads
* Added options to include a link to the game's highlights on baseball.theater in game and postgame threads
* Updated pre and post threads to honor suggested sort setting
* Added option to set post flair on offday/pre/game/post threads, either as submitter if the sub allows it, or using mod rights - you may need to generate a new refresh token including updated permissions to use this feature (obtain a new refresh token using setup.py and the instructions above)
* Added support for different postgame thread tags for wins, losses, and exceptions (tie/canceled/postponed)
* Decreased wait between game thread edits to 30 seconds, made other waits consistent
* Added `LOG_LEVEL` setting, increased available console logging to make it more clear what is happening (0-none, 1-error, 2-info, 3-debug)
* Updated `README.md` to include new header, clarified oauth setup instructions, more thorough descriptions of configuration settings, and updated changelog
* Added logic to explicitly unsticky pregame thread when posting game thread, and game thread when posting postgame thread
* Enhanced existing logic to unsticky any stale threads each day
* Adjusted default values in `sample_settings.json` to turn on offday/pre/post threads, set game thread post time to 3 hours, enable baseball.theater link in post threads, and include footer text for game threads.
* Improved loading/validation of settings and error handling on startup. All settings will be validated rather than aborting on the first missing setting. Also added default values for most settings except those related to oauth, subreddit, and team code. Other missing settings will use default values and log a warning.
* Added settings*.json and main-*.py to .gitignore, to make it easier to switch between config files and have a test version of main.py

---
### Change Log Prior to This Fork

#### v3.0.2
* GUI added (but does not include all settings and is not supported in this fork)

#### v3.0.1
* Now uses OAuth!

#### v3.0.0
* Modular - If you want a certain feature, just change a variable at the top!
* Easier to read - Cleaned up some code, started using more OOP.

#### v2.0.4
* Fixed crash caused by game not being aired on TV.
* Fixed another crash related to scoring plays.

#### v2.0.3
* Fixed the Diamondbacks' subreddit not working properly.
* Fixed crash related to scoring plays.

#### v2.0.2

* Fixed random crashing.
* Fixed bug where some teams names were not displayed correctly. (Though Chi White Sox White Sox is a great name...)

#### v2.0.1

* Fixed gamecheck not always working correctly.
* Fixed the TV media showing the same for both home and away.
* Fixed the timestamp on the game/time checks not displaying correctly.
