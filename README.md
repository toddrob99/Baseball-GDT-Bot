Baseball Game Thread Bot for Reddit
=====================================
Maintained by Todd Roberts
https://github.com/toddrob99/Baseball-GDT-Bot

Forked from Baseball GDT Bot by Matt Bullock
https://github.com/mattabullock/Baseball-GDT-Bot

### Current Version: 4.5.5
	
This project contains a bot to post off day, pregame, game, and postgame discussion threads on Reddit for a given MLB team, and keep those threads updated with game data while games are in progress. This fork is written in Python 2.7, using PRAW 5 to interface with the Reddit API.

---

### Setup and Configuration

#### OAuth Setup

Go to reddit.com’s app page (https://www.reddit.com/prefs/apps), click on the “are you a developer? create an app” button. Fill out the name, description and about url. Enter whatever you please for name, `http://localhost:8080` for redirect uri, and the rest don't really matter. All of these variables can be changed later.

Next, copy `sample_settings.json` to the `src` folder and rename it to `settings.json`. Open `/src/settings.json` with a text editor, fill in the `CLIENT_ID`, `CLIENT_SECRET` and `REDIRECT_URI` fields from your Reddit app, and run the `setup_oauth.py` script. 

Your browser will open and take you to a Reddit app authorization page. Make sure you are logged in to Reddit as the user you want the bot to run as, and click allow on the displayed web page. 

Copy the code (everything after code=) from the URL in the browser address bar, paste it into the console, and press Enter. Your refresh token will be displayed. Copy the refresh token into `/src/settings.json` and save. 

That's it for the oauth setup! Now configure the rest of your settings (or leave the defaults) and run `/src/main.py` to start your bot.

#### Configuration Settings

The following settings can be configured in `/src/settings.json`:

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
	* `SUGGESTED_SORT` - what do you want the suggested sort to be? set to "" if your bot user does not have mod rights ("confidence", "top", "new", "controversial", "old", "random", "qa", "")
	* `INBOX_REPLIES` - do you want to receive thread replies in the bot's inbox? (true/false)
	* `FLAIR` - flair to set on the thread, if `FLAIR_MODE` is not "none" ("Off Day Thread")
	* `SUPPRESS_OFFSEASON` - do you want to suppress off day threads during the off season? (true/false)
	* `FOOTER` - text to include in the body of the post, below the next game info ("No game today. Feel free to discuss whatever you want in this thread.")

* `PRE_THREAD` - pregame thread settings
	* `ENABLED` - do you want a pre game thread? (true/false)
	* `TAG` - prefix for the thread title ("PREGAME THREAD:")
	* `TIME` - time to post the pregame thread ("8AM" in context of BOT_TIME_ZONE)
	* `SUPPRESS_MINUTES` - pregame thread will be suppressed if game thread will be posted within this number of minutes. A value of 0 will suppress the pregame thread only if it is already time to post the game thread. Set to -1 to disable suppression based on game thread post time. (-1, 0, 60, 120, etc. default: 0)
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
		* `HEADER`, `BOX_SCORE`, `LINE_SCORE`, `SCORING_PLAYS`, `HIGHLIGHTS`, `CURRENT_STATE`, `UPDATE_STAMP` - sections to include in the post (true/false)
		* `FOOTER` - text to include at the end of the post ("Remember to \*\*sort by new\*\* to keep up!")
		* `THEATER_LINK` - include link to the game's highlights on baseball.theater in the Highlights section (true/false)
		* `PREVIEW_BLURB` - include game headline and blurb in the thread header until the game starts (true/false)
		* `PREVIEW_PROBABLES` - include probable pitchers in game thread until the game starts (true/false)
		* `NEXT_GAME` - include next game date/time/opponent in the game thread after the game is final (true/false)

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
		* `FOOTER` - text to include at the end of the post ("Remember to \*\*sort by new\*\* to keep up!")
		* `THEATER_LINK` - include link to the game's highlights on baseball.theater in the Highlights section (true/false)
		* `NEXT_GAME` - include next game date/time/opponent in the postgame thread (true/false)

---

If something doesn't seem right, feel free to message me on reddit or post it as a bug on github.

This was written in Python 2.7, so beware if you are running Python 3 or
	above that it may not work correctly. Also make sure you install
	praw and simplejson before running!

Modules being used:

	praw 5.0.1+ - interfacing reddit
	simplejson - JSON parsing
	urllib2 - pulling data from MLB servers
	ElementTree - XML parsing

---
### Change Log

#### v4.5.5
* Fixed logging around detection of next game
* Adjusted default value for game thread footers (bold only "sort by new" instead of the whole string)
* Fixed #53, bot will now skip games with placeholder opponents (e.g. `AL Div. Winner 3 or WC`)
* When determining next game, bot will now skip games with placeholder opponents unless there are no games with a valid opponent on the same day. This happens when a team clinches a berth prior to their next opponent.

#### v4.5.4
* Fixed #48, missing probable pitcher table if any piece of data is not posted (e.g. one team doesn't post a probable pitcher, or no report posted for one of the probable pitchers)

#### v4.5.3
* Fixed next game lookup skipping a day when the current game ends after midnight, or skipping doubleheader game 2 (#49)
* Updated start time adjustment for straight doubleheader game 2 to use game 1 start time + 3.5 hours instead of 3 hours, and changed from .replace() to the more appropriate timedelta
* Doubleheader game 2 will no longer show 3:33 AM first pitch in pregame thread or game thraed, instead will show game 1 start + 3.5 hours
* Fixed log entry in `generate_description()` exception handler
* Minor logging adjustments

#### v4.5.2
* Fixed matchup image URL not working for teams whose name_abbrev is different than their file_code (e.g. wsh vs was)

#### v4.5.1
* Truncated change log prior to the start of this fork (v4.0.0)
* Updated `setup_oauth.py` to read from /src/settings.json rather than requiring hard-coded values; updated instructions in `README.md`

#### v4.5.0
* Added `SUPPRESS_MINUTES` option under `PRE_THREAD` section. Pregame thread will be suppressed if game thread will be posted within this number of minutes. Default is 0 (suppress if it is already time to post the game thread), use -1 to disable suppression
* Added detection of stale sticky threads when bot is started. It will look for sticky posts submitted by the bot user (requires identity scope), with title beginning with one of the configured off/pre/game/post tags, and with title not ending with today's date. Stale threads will be unstickied when new off/pre/game thread is posted (existing functionality)
* Enhanced detection of existing pregame and game threads. The bot will now be able to identify existing threads even after the game is over and records have changed
* Fixed variable/function name collision by renaming the `str` variable to `threadstr`
* Fixed spacing on mobile between Linescore and Scoring Plays tables, and between Decisions table and Next Game/Footer
* Current state will now say if the game is delayed
* Added 1 minute sleep if all posted (non-Preview/Pre-Game) games are in Delayed status, rather than checking every 5 seconds
* Fixed final score and decisions not showing when a game is completed early
* Added error handling for sticky, unsticky, and suggested sort actions, in case pre thread was deleted when game/post threads are posted, or bot user does not have mod rights

#### v4.4.2
* Added `SUPPRESS_OFFSEASON` setting under `OFF_THREAD` section. Default is true, which will suppress off day threads during the off season (when there are no games in the next 14 days, or when there have been no games in the last 14 days)
* Added `next_game()` and `last_game()` functions to support suppression of off day threads during the off season
* Added check for games before generating game thread titles or entering game thread post/edit loop
* Re-ordered off thread settings validation to match order in sample settings file
* Added info about next game to off thread body
* Added `get_teams_time()` function to pull home/away team names/codes and game time for an arbitrary game URL, to facilitate pulling info about the next game for offday threads
* Renamed `BODY` to `FOOTER` in `OFF_THREAD` settings to match other threads, since it is now optional and will be below info about the next game
* Added info about next game to game thread (when final) and post thread. Turn off with new `NEXT_GAME` setting under `GAME_THREAD` : `CONTENT` and `POST_THREAD` : `CONTENT` sections
* Added `generate_next_game()` function to support next game info in off, game, and post threads

#### v4.4.1
* Tested with PRAW 5.1.0 - no changes required; updated README to indicate praw 5.0.1+ is supported.
* Added `CURRENT_STATE` setting to `GAME_THREAD` : `CONTENT` section. This will output the current state of the game while game is in progress. For example: "Top of the 4th, bases empty, 1 out, and a count of 2-1 with Edwin Encarnacion batting and Matthew Boyd pitching. Carlos Santana is on deck, and Yandy Diaz is in the hole." or at the end/middle of an inning (except end of game), "Middle of the 3rd with JaCoby Jones, Jose Iglesias, and Ian Kinsler coming up for the Tigers."
* Added Last Updated timestamp to end of game thread. Turn off with `GAME_THREAD` : `CONTENT` : `UPDATE_STAMP` = false.
* Moved end-of-game status check before game thread is updated, to ensure the game thread gets updated with the final result in cases where the MLB data changes to final while the bot is sleeping after editing the game thread.
* Added matchup at top of pre/game/post threads with link to matchup image (e.g. "Phillies @ Marlins", except consolidated doubleheader pre threads, in which case the "Game 1" header will be the link). It will be the header while the game is in Preview status, and then it will be in the "Game Info" table header (instead of saying Game Info, it will say Phillies @ Marlins Game Info). This link will set the thumbnail for mobile to an image such as http://mlb.mlb.com/images/2017_ipad/684/phimia_684.jpg.
* Added check for Preview/Pre-Game status to display preview blurb/probables in game thread, rather than overwriting header content when plays.json becomes available
* Game thread will no longer include header row for scoring plays table if there are no scoring plays
* Changed "Game X" headers from h1 to h2 in consolidated pre threads
* Line score table will no longer show in game thread while game is in Preview/Pre-Game status

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
* Updated `generate_probables()` (renamed from `generate_pre_probables()`) to use `gamecenter.xml` for probables data instead of `linescore.json`, because probables data is removed from `linescore.json` after the game exits Preview status
* Split up `PROBABLES` table in pregame thread, into `PROBABLES` and new `BROADCAST` setting; added pitcher blurb to `PROBABLES`
* Added `PREVIEW_PROBABLES` option to `GAME_THREAD` settings. Shows probable pitchers (including blurb) in game thread while game is in Preview status
* Added validation of `FLAIR` before attempting to set flair for off/pre/game/post threads
* Fixed loop resulting from a postponed game by removing `timechecker.ppcheck()` and letting the overall game status check handle it

#### v4.3.0
* Added `BLURB` pregame thread option and `PREVIEW_BLURB` game thread option, to include game headline and blurb in header (same blurb, but only show in game thread until game starts)
* Updated to use `self.SETTINGS` dict for settings, instead of separate variables for each setting. Made SETTINGS dict available in editor module. This reduces the likelihood of breakage later when adding/changing settings, as the order no longer matters (in the code; the order never mattered in the settings file)
* Removed validation of `REDIRECT_URI` since it is not used in the code anywhere (only used in `setup-oauth.py`)
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
