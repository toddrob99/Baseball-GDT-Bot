Baseball Game Thread Bot for Reddit
=====================================
Maintained by Todd Roberts
https://github.com/toddrob99/Baseball-GDT-Bot

Forked from Baseball GDT Bot by Matt Bullock
https://github.com/mattabullock/Baseball-GDT-Bot

### Current Version: 5.1.9
	
This project contains a bot to post off day, pregame, game, and postgame discussion threads on Reddit for a given MLB team, and keep those threads updated with game data while games are in progress. This fork is written in Python 2.7, using PRAW 5 to interface with the Reddit API and the MLB Stats API for MLB data.

---

### Setup and Configuration

#### OAuth Setup

Go to reddit.com’s app page (https://www.reddit.com/prefs/apps), click on the “are you a developer? create an app” button. Fill out the name, description and about url. Enter whatever you please for name, `http://localhost:8080` for redirect uri, and the rest don't really matter. All of these variables can be changed later.

Next, copy `sample_settings.json` to the `src` folder and rename it to `settings.json`. Open `/src/settings.json` with a text editor, fill in the `CLIENT_ID`, `CLIENT_SECRET` and `REDIRECT_URI` fields from your Reddit app, and run the `setup_oauth.py` script. If you want to save your settings file somewhere else or have multiple settings files, specify the filename/path on the command line like this: `python setup_oauth.py --settings=settings-phi.json` or `python setup_oauth.py --settings=/path/to/settings.json`. If an absolute path is not provided, the file must be in the `/src/` folder along with `main.py`.

Your browser will open and take you to a Reddit app authorization page. Make sure you are logged in to Reddit as the user you want the bot to run as, and click allow on the displayed web page. 

Copy the code (everything after code=) from the URL in the browser address bar, paste it into the console, and press Enter. Your refresh token will be displayed. Copy the refresh token into `/src/settings.json` and save. 

That's it for the oauth setup! Now configure the rest of your settings (at least `SUBREDDIT` and `TEAM_CODE`; you can leave the defaults for the rest) and run `/src/main.py` to start your bot. If you want to save your settings file somewhere other than the /src/ folder or you have multiple settings files, specify the filename/path on the command line like this: `python src/main.py --settings=settings-phi.json` or `python src/main.py --settings=/path/to/settings.json`. If an absolute path is not provided, the file must be in the `/src/` folder along with `main.py`.

#### Configuration Settings

The following settings can be configured in `/src/settings.json`:

* `CLIENT_ID`, `CLIENT_SECRET`, `REDIRECT_URI`, `REFRESH_TOKEN` - these are used to authenticate with the Reddit API. See `OAuth Setup` section above

* `USER_AGENT` - user agent string to identify your bot to the Reddit API - this will be appended to the system-generated user agent (e.g. "implemented for r/Phillies by u/toddrob")

* `SUBREDDIT` - subreddit that you want the threads posted to (do not include "/r/", e.g. "Phillies")

* `TEAM_CODE` - three letter code that represents team - not always what you think (Cubs: CHN, Yankees: NYA)! look this up by running `lookup_team_code.py` and entering the team name (e.g. Phillies, Athletics, Cardinals), name abbreviation (e.g. CHC, STL, CWS), city (e.g. Chicago, Miami, Anaheim)

* `STICKY` - do you want the threads stickied? bot must have mod rights. (true/false)

* `FLAIR_MODE` - do you want to set flair on offday/pre/game/post threads using a mod command (bot user must have mod rights), as the thread submitter (sub settings must allow), or none? ("none", "submitter", "mod") **NOTE**: in order to use this, you may have to re-do the OAuth setup process described above to obtain a new refresh token that includes flair permissions.

* `ASG` - do you want threads for All-Star games? (true/false)

* `LOGGING` - controls the amount of logging to the console and file (rotated daily with the previous week's log files retained)
	* `FILE` - do you want to log to a file (`TEAM_CODE-bot.log` in the `/logs` directory, e.g. `/logs/phi-bot.log`)? (true/false)
	* `FILE_LOG_LEVEL` - how much detail do you want logged to file? (`CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG` - default/recommended: `DEBUG`)
	* `CONSOLE` - do you want to log to the console? (true/false)
	* `CONSOLE_LOG_LEVEL` - how much detail do you want logged to the console? (`CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG` - default/recommended: `INFO`)

* `NOTIFICATIONS` - settings related to notifications
	* `PROWL` - settings related to Prowl notifications
		* `ENABLED` - do you want to enable Prowl notifications? (true/false)
		* `API_KEY` - your Prowl API key, generate at https://www.prowlapp.com/api_settings.php
		* `PRIORITY` - with what priority should the notifications be sent (-2: Very Low, -1: Moderate, 0: Normal, 1: High, 2: Emergency, default 0)
		* `NOTIFY_WHEN` - enable/disable individual notifications
			* `OFF_THREAD_SUBMITTED` - send a notification when off day thread is posted (true/false)
			* `PRE_THREAD_SUBMITTED` - send a notification when pregame thread is posted (true/false)
			* `GAME_THREAD_SUBMITTED` - send a notification when game thread is posted (true/false)
			* `POST_THREAD_SUBMITTED` - send a notification when postgame thread is posted (true/false)
			* `WEEKLY_THREAD_SUBMITTED` - send a notification when weekly thread is posted (true/false)
			* `END_OF_DAY_EDIT_STATS` - send notifications at the end of each day with stats about edit rate for each game, and averages across all games since last bot restart (true/false)

* `TWITTER` - holds OAuth fields for Twitter API connection
	* `CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCESS_TOKEN`, `ACCESS_SECRET` - all required to use Twitter features - follow the instructions at https://python-twitter.readthedocs.io/en/latest/getting_started.html

* `OFF_THREAD` - offday thread settings
	* `ENABLED` - do you want an off day thread on days when your team does not play? (true/false)
	* `TITLE` - thread title. see `PRE_THREAD` : `TITLE` for info about available parameters. Note: `{oppTeam}`, `{awayTeam}`, and `{homeTeam}` parameters are not supported for off day threads. (Default: "OFF DAY THREAD: The {myTeam:name} ({myTeam:wins}-{myTeam:losses}) are off today - {date:%A, %B %d}")
	* `TIME` - time to post the offday thread in bot's local time zone ("8AM")
	* `SUGGESTED_SORT` - what do you want the suggested sort to be? set to "" if your bot user does not have mod rights ("confidence", "top", "new", "controversial", "old", "random", "qa", "")
	* `INBOX_REPLIES` - do you want to receive thread replies in the bot's inbox? (true/false)
	* `FLAIR` - flair to set on the thread, if `FLAIR_MODE` is not "none" ("Off Day Thread")
	* `SUPPRESS_OFFSEASON` - do you want to suppress off day threads during the off season? (true/false)
	* `CONTENT`
		* `NEXT_GAME` - do you want to include date/time/opponent for your team's next game in the off day thread body? (true/false)
		* `DIV_STANDINGS` - do you want to include standings for your team's division in the off day thread body? (true/false)
		* `FOOTER` - text to include in the body of the post, below the next game info ("No game today. Feel free to discuss whatever you want in this thread.")
	* `TWITTER` - settings for tweeting off day thread link
		* `ENABLED` - do you want to tweet a link to your off day thread? (true/false)
		* `TEXT` - what do you want your tweet to say? Same parameters as `TITLE` are available, plus `{link}` which will be the thread shortlink. Twitter currently limits tweets to 280 characters, so be brief. (suggested: "The {myTeam:name} are off today. Pass the time in our off day thread: {link} #{myTeam:name%stripspaces}")

* `PRE_THREAD` - pregame thread settings
	* `ENABLED` - do you want a pre game thread? (true/false)
	* `TITLE` - thread title (Default: "PREGAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}")
		* Team-related fields available through `lookup_team_info()` can be used in the below formats (e.g. `{myTeam:name}` for `Phillies`, `{myTeam:name_display_full}` for `Philadelphia Phillies`). In addition to `wins`, `losses`, and `runs` (postgame only), list of team fields is located at http://mlb.com/lookup/json/named.team_all.bam?sport_code=%27mlb%27&active_sw=%27Y%27
			* `{myTeam:<field>}` - fields related to team configured in `TEAM_CODE` setting (`myTeam` is the only team parameter available for off day thread)
			* `{oppTeam:<field>}` - fields related to opponent team
			* `{homeTeam:<field>}` - fields related to home team
			* `{awayTeam:<field>}` - fields related to away team
		* `{vsat}` - "@" when your team is away and "vs" when your team is home (not available for off day threads)
		* `{date:%a %b %d @ %I:%M%p %Z}` where `%a %b %d @ %I:%M%p %Z` is the date format using the variables listed on http://strftime.org/ (`{date}` without format speficied will default to `%B %d, %Y`, e.g. `April 29, 2018`)
		* `{gameNum}` which will always be 1 except game 2 of a doubleheader
		* `{series: %D Game %N -}` - `%D` will be replaced with series description (e.g. `NLDS`, `World Series`), and `%N` will be replaced with series game number (e.g. `1`, `3`). be sure to include a space and/or separator on the beginning and end as needed
		* `{dh: - DH Game %N}` - will be included in thread title only if game is a doubleheader. `%N` will be replaced with doubleheader game number, same value as `{gameNum}`
		* Apply a modifier by suffixing `%modifier` to the end of your parameter
			* `%lower` - lower case, e.g. `{myTeam:name%lower}` -> `phillies`
			* `%upper` - upper case, e.g. `{myTeam:name%upper}` -> `PHILLIES`
			* `%stripspaces` - strip all spaces (useful for hashtags), e.g. `{myTeam:name%stripspaces}` -> `WhiteSox`
			* Multiple modifiers supported, e.g. `{myTeam:name%lower%stripspaces}` -> `whitesox`
		* Use `\\{`, `\\}`, `\\:`, or `\\%` if you want to include `{`, `}`, `:`, or `%` in your title (the json decoder will fail if you try with only 1 escape character, e.g. `\{`)
	* `ASG_TITLE` - thread title for All-Star Game pre threads. see `PRE_THREAD` : `TITLE` for info about available parameters. (Default: "PREGAME THREAD:{series: %D -} {awayTeam:name} @ {homeTeam:name} - {date:%a %b %d @ %I:%M%p %Z}")
	* `CONSOLIDATED_DH_TITLE` - thread title for doubleheader when `CONSOLIDATE_DH` is `true`. see `TITLE` for more info about available parameters, and it's probably best not to include game time in this (Default: "PREGAME THREAD:{series: %D -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d}{dh: - DOUBLEHEADER}")
	* `TIME` - time to post the pregame thread in bot's local time zone ("8AM")
	* `SUPPRESS_MINUTES` - pregame thread will be suppressed if game thread will be posted within this number of minutes. A value of 0 will suppress the pregame thread only if it is already time to post the game thread. Set to -1 to disable suppression based on game thread post time. (-1, 0, 60, 120, etc. default: 0)
	* `SUGGESTED_SORT` - what do you want the suggested sort to be? set to "" if your bot user does not have mod rights ("confidence", "top", "new", "controversial", "old", "random", "qa", "")
	* `INBOX_REPLIES` - do you want to receive thread replies in the bot's inbox? (true/false)
	* `FLAIR` - flair to set on the thread, if `FLAIR_MODE` is not "none" ("Pregame Thread")
	* `CONSOLIDATE_DH` - do you want to consolidate pre game threads for doubleheaders? (true/false)
	* `CONTENT`
		* `HEADER` - include game info header in the post (true/false - strongly suggested: true)
		* `BLURB` - include game headline and blurb about the game (true/false)
		* `PROBABLES` - include probable pitchers in the post, along with reports (true/false)
		* `DIV_STANDINGS` - standings for your team's division in the post (true/false)
		* `FOOTER` - text to include at the end of the post (e.g. "Let's go Phillies!" default: "")
	* `TWITTER` - settings for tweeting pregame thread link
		* `ENABLED` - do you want to tweet a link to your off day thread? (true/false)
		* `TEXT` - what do you want your tweet to say? Same parameters as `TITLE` are available, plus `{link}` which will be the thread shortlink. Twitter currently limits tweets to 280 characters, so be brief. (suggested: "Game day! {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%I:%M%p %Z}. Join the discussion in our pregame thread: {link} #{myTeam:name%stripspaces}")
		* `CONSOLIDATED_DH_TEXT` - what do you want your tweet to say for doubleheaders when `CONSOLIDATE_DH` is `true`? see `TEXT` for more info. (suggested: "Doubleheader day!{series: %D -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}). Join the discussion in our pregame thread: {link} #{myTeam:name%stripspaces}{dh: #doubleheader}")
		* `ASG_TEXT` - what do you want your tweet to say for All-Star games? see `TEXT` for more info. (suggested: "All-Star Game day! {awayTeam:name} @ {homeTeam:name} - {date:%I:%M%p %Z}. Join the discussion in our pregame thread: {link} #MLBAllStarGame #ASG{date:%Y}")

* `GAME_THREAD` - game thread settings
	* `TITLE` - thread title. see `PRE_THREAD` : `TITLE` for info about available parameters. (Default: "GAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}")
	* `ASG_TITLE` - thread title for All-Star Game. see `PRE_THREAD` : `TITLE` for info about available parameters. (Default: "GAME THREAD:{series: %D -} {awayTeam:name} @ {homeTeam:name} - {date:%a %b %d @ %I:%M%p %Z}")
	* `HOURS_BEFORE` - number of hours prior to game time that the bot posts the game thread (1, 2, 3, etc.)
	* `POST_BY` - latest hour you want the game thread to be posted (within 10 minutes past the hour). game thread will be posted at the earlier of `POST_BY` of game start minus `HOURS_BEFORE` hours (except doubleheader game 2 with `HOLD_DH_GAME2_THREAD` enabled. use this to post game thread at the same time every day, for example when pregame threads are disabled. (default: "10PM" -- effectively disabled except for games that start at 10pm with `HOURS_BEFORE` set to 0)
	* `SUGGESTED_SORT` - what do you want the suggested sort to be? set to "" if your bot user does not have mod rights ("confidence", "top", "new", "controversial", "old", "random", "qa", "")
	* `INBOX_REPLIES` - do you want to receive thread replies in the bot's inbox? (true/false)
	* `FLAIR` - flair to set on the thread, if `FLAIR_MODE` is not "none" ("Game Thread")
	* `MESSAGE` - send submission shortlink to /u/baseballbot to add a link to the game thread on the /r/Baseball sidebar (true/false)
	* `HOLD_DH_GAME2_THREAD` - do you want to hold the game thread for doubleheader game 2 until game 1 is final? (true/false)
	* `EXTRA_SLEEP` - do you want the bot to sleep longer than 5 seconds between game thread edits? set this to the number of seconds (e.g. 25 for a total sleep of 30 seconds; default: 0)
	* `CONTENT` - what to include in the body of the post
		* `HEADER`, `BOX_SCORE`, EXTENDED_BOX_SCORE, `LINE_SCORE`, `SCORING_PLAYS`, `HIGHLIGHTS`, `CURRENT_STATE`, `UPDATE_STAMP` - sections to include in the post (true/false)
		* `FOOTER` - text to include at the end of the post ("Remember to \*\*sort by new\*\* to keep up!")
		* `THEATER_LINK` - include link to the game's highlights on baseball.theater in the Highlights section (true/false)
		* `PREVIEW_BLURB` - include game headline and blurb in the thread header until the game starts (true/false)
		* `PREVIEW_PROBABLES` - include probable pitchers in game thread until the game starts (true/false)
		* `PREVIEW_STANDINGS` - include division standings in game thread until the game starts (true/false)
		* `NEXT_GAME` - include next game date/time/opponent in the game thread after the game is final (true/false)
	* `NOTABLE_PLAY_COMMENTS` - settings that control whether the bot comments on the game thread when specific game events occur
		* `ENABLED` - do you want the bot to comment on game threads when configured game events occur? (true/false)
		* `MYTEAM_BATTING` - settings that control comments submitted to game thread by bot while configured team is batting
			* `EVENTS` - list of events for which the bot should submit a comment while the configured team is batting, in list format (e.g. `["Home Run", "Balk", "Scoring Play"]`). Default value: `["Home Run", "Pitcher Substitution", "Scoring Play", "Stolen Base Home"]`. All events that have occurred in 2018 as of August 3: `["Balk", "Batter Interference", "Batter Turn", "Bunt Groundout", "Bunt Lineout", "Bunt Pop Out", "Catcher Interference", "Caught Stealing 2B", "Caught Stealing 3B", "Caught Stealing Home", "Defensive Indiff", "Defensive Sub", "Defensive Switch", "Double", "Double Play", "Ejection", "Error", "Fan interference", "Field Error", "Fielders Choice", "Fielders Choice Out", "Flyout", "Forceout", "Game Advisory", "Grounded Into DP", "Groundout", "Hit By Pitch", "Home Run", "Intent Walk", "Left On Base", "Lineout", "Manager Review", "Offensive Sub", "Passed Ball", "Picked off stealing 2B", "Picked off stealing 3B", "Picked off stealing home", "Pickoff 1B", "Pickoff 2B", "Pickoff 3B", "Pickoff Attempt 1B", "Pickoff Attempt 2B", "Pickoff Error 1B", "Pickoff Error 2B", "Pitcher Switch", "Pitching Substitution", "Player Injured", "Pop Out", "Relief with No Outs", "Runner Advance", "Runner Out", "Sac Bunt", "Sac Fly", "Sac Fly DP", "Sacrifice Bunt DP", "Single", "Stolen Base 2B", "Stolen Base 3B", "Stolen Base Home", "Strikeout", "Strikeout - DP", "Triple", "Triple Play", "Umpire Review", "Umpire Substitution", "Walk", "Wild Pitch"]`.
			* `HEADER` - optional text to include at the beginning of the comment (before the event description). Include an item for each event you want a header for. All parameters supported in thread titles/tweets are supported, e.g. `{myTeam:name}`, plus `{halfInning}` (`Top` or `Bottom`) and `{inning}` (`1`, `2`, etc. with no ordinal). A couple examples of the format are below; see `sample_settings.json` for more examples.
				* `"All": "###Notable Play Alert!"` - note the special value `All` which applies to all events. this will be prepended before any event-specific header
				* `"Home Run": "##RING THE BELL!",`
				* `"Double": "###DOUBLE",`
				* `"Scoring Play": "###SCORING PLAY"` - note the special event name for any scoring play. Could be a single, sac fly, home run, walk, stolen base, etc. If this event is enabled, any event that is a scoring play will trigger a comment
			* `FOOTER` - optional text to include at the end of the comment (after the event description). Include an item for each event you want a footer for. All parameters supported in thread titles/tweets are supported, e.g. `{myTeam:name}`, plus `{halfInning}` (`Top` or `Bottom`) and `{inning}` (`1`, `2`, etc. with no ordinal). A couple examples of the format are below; see `sample_settings.json` for more examples.
				* `"All": "{halfInning} {inning} - {awayTeam:name}: {awayTeam:runs}, {homeTeam:name}: {homeTeam:runs}"` - note the special value `All` which applies to all events. this will be appended after any event-specific footer
				* `"Home Run": "That ball's outta here!",`
				* `"Triple": "He made it all the way to third base."`
		* `MYTEAM_PITCHING` - settings that control comments submitted to game thread by bot while configured team is pitching
			* `EVENTS` - list of events for which the bot should submit a comment while the configured team is pitching, in list format (`["Strikeout", "Strikeout_Called", "Triple Play"]`). Default value: `["Pitcher Substitution", "Strikeout", "Strikeout_Called", "Triple Play"]`. A list of events that have occurred in 2018 as of August 3 is in the previous section
			* `HEADER` - optional text to include at the beginning of the comment (before the event description). Include an item for each event you want a header for. All parameters supported in thread titles/tweets are supported, e.g. `{myTeam:name}`, plus `{halfInning}` (`Top` or `Bottom`) and `{inning}` (`1`, `2`, etc. with no ordinal). A couple examples of the format are below; see `sample_settings.json` for more examples.
				* `"All": "###Notable Play Alert!"` - note the special value `All` which applies to all events. this will be prepended before any event-specific header
				* `"Strikeout": "###K"`
				* `"Strikeout_Called": "###BACKWARD K"` - note the special event name for a called strikeout, vs. a swinging strikeout
			* `FOOTER` - optional text to include at the end of the comment (before the event description). Include an item for each event you want a footer for. All parameters supported in thread titles/tweets are supported, e.g. `{myTeam:name}`, plus `{halfInning}` (`Top` or `Bottom`) and `{inning}` (`1`, `2`, etc. with no ordinal). A couple examples of the format are below; see `sample_settings.json` for more examples.
				* `"All": "{halfInning} {inning} - {awayTeam:name}: {awayTeam:runs}, {homeTeam:name}: {homeTeam:runs}"` - note the special value `All` which applies to all events. this will be appended after any event-specific footer
				* `"Strikeout": ""`
				* `"Strikeout_Called": "He was caught looking..."` - note the special event name for a called strikeout, vs. a swinging strikeout
		* `PITCH_STATS` - list of events that you want to have pitch stats in the comment (pitch type, start speed, end speed, nasty factor). Default value: `["Strikeout_Called", "Bunt Groundout", "Bunt Lineout", "Bunt Pop Out", "Double", "Fielders Choice", "Fielders Choice Out", "Flyout", "Forceout", "Grounded Into DP", "Groundout", "Hit By Pitch", "Home Run", "Lineout", "Passed Ball", "Pop Out", "Sac Bunt", "Sac Fly", "Sac Fly DP", "Sacrifice Bunt DP", "Single", "Strikeout", "Strikeout - DP", "Triple", "Triple Play", "Walk", "Wild Pitch"]`
        * `HIT_STATS` list of events that you want to have hit stats int he comment (launch angle, launch speed, total distance). Default value: `["Bunt Groundout", "Bunt Lineout", "Bunt Pop Out", "Double", "Fielders Choice", "Fielders Choice Out", "Flyout", "Forceout", "Grounded Into DP", "Groundout", "Home Run", "Lineout", "Pop Out", "Sac Bunt", "Sac Fly", "Sac Fly DP", "Sacrifice Bunt DP", "Single", "Triple", "Triple Play"]`
	* `TWITTER` - settings for tweeting game thread link
		* `ENABLED` - do you want to tweet a link to your off day thread? (true/false)
		* `TEXT` - what do you want your tweet to say? Same parameters as `TITLE` are available, plus `{link}` which will be the thread shortlink. Twitter currently limits tweets to 280 characters, so be brief. (suggested: "{series:%D Game %N - }{dh:DH Game %N - }{awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%I:%M%p %Z}. Join the discussion in our game thread: {link} #{myTeam:name%stripspaces}{dh: #doubleheader}")
		* `ASG_TEXT` - what do you want your tweet to say for All-Star Games? Same parameters as `TITLE` are available, plus `{link}` which will be the thread shortlink. Twitter currently limits tweets to 280 characters, so be brief. (suggested: "{series:%D}! {awayTeam:name} @ {homeTeam:name} - {date:%I:%M%p %Z}. Join the discussion in our game thread: {link} #MLBAllStarGame #ASG{date:%Y}")

* `POST_THREAD` - postgame thread settings
	* `ENABLED` - do you want a post game thread? (true/false)
	* `WIN_TITLE` - thread title when game result is win. see `PRE_THREAD` : `TITLE` for more info about available parameters. (Default: "WIN THREAD:{series: %D Game %N -} The {myTeam:name} ({myTeam:wins}-{myTeam:losses}) defeated the {oppTeam:name} ({oppTeam:wins}-{oppTeam:losses}) by a score of {myTeam:runs}-{oppTeam:runs} - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}")
	* `LOSS_TITLE` - thread title when game result is loss. see `PRE_THREAD` : `TITLE` for more info about available parameters. (Default: "LOSS THREAD:{series: %D Game %N -} The {myTeam:name} ({myTeam:wins}-{myTeam:losses}) fell to the {oppTeam:name} ({oppTeam:wins}-{oppTeam:losses}) by a score of {oppTeam:runs}-{myTeam:runs} - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}")
	* `OTHER_TITLE` - thread title when game result is tie/postponed/suspended/canceled. see `PRE_THREAD` : `TITLE` for more info about available parameters. (Default: "POST GAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}")
	* `ASG_TITLE` - thread title for All-Star Games. see `PRE_THREAD` : `TITLE` for more info about available parameters. (Default: "POSTGAME THREAD:{series: %D -} {awayTeam:name} @ {homeTeam:name} - {date:%a %b %d @ %I:%M%p %Z}")
	* `SUGGESTED_SORT` - what do you want the suggested sort to be? set to "" if your bot user does not have mod rights ("confidence", "top", "new", "controversial", "old", "random", "qa", "")
	* `INBOX_REPLIES` - do you want to receive thread replies in the bot's inbox? (true/false)
	* `FLAIR` - flair to set on the thread, if `FLAIR_MODE` is not "none" ("Postgame Thread")
	* `CONTENT` - what to include in the body of the post
		* `HEADER`, `BOX_SCORE`, EXTENDED_BOX_SCORE, `LINE_SCORE`, `SCORING_PLAYS`, `HIGHLIGHTS` - sections to include in the post (true/false)
		* `FOOTER` - text to include at the end of the post ("Remember to \*\*sort by new\*\* to keep up!")
		* `THEATER_LINK` - include link to the game's highlights on baseball.theater in the Highlights section (true/false)
		* `NEXT_GAME` - include next game date/time/opponent in the postgame thread (true/false)
	* `TWITTER` - settings for tweeting postgame thread link
		* `ENABLED` - do you want to tweet a link to your off day thread? (true/false)
		* `WIN_TEXT` - what do you want your tweet to say when your team wins? Same parameters as `*_TITLE` are available, plus `{link}` which will be the thread shortlink. Twitter currently limits tweets to 280 characters, so be brief. (suggested: "{series:%D Game %N - }{dh:DH Game %N - }The {myTeam:name} defeated the {oppTeam:name}, {myTeam:runs}-{oppTeam:runs}! Join the discussion in our postgame thread: {link} #{myTeam:name%stripspaces}{dh: #doubleheader}")
		* `LOSS_TEXT` - what do you want your tweet to say when your team loses? Same parameters as `*_TITLE` are available, plus `{link}` which will be the thread shortlink. Twitter currently limits tweets to 280 characters, so be brief. (suggested: "{series:%D Game %N - }{dh:DH Game %N - }The {myTeam:name} fell to the {oppTeam:name}, {oppTeam:runs}-{myTeam:runs}. Join the discussion in our postgame thread: {link} #{myTeam:name%stripspaces}{dh: #doubleheader}")
		* `OTHER_TEXT` - what do you want your tweet to say when the game results in a tie, or is postponed/cancelled/suspended? Same parameters as `*_TITLE` are available, plus `{link}` which will be the thread shortlink. Twitter currently limits tweets to 280 characters, so be brief. (suggested: "{series:%D Game %N - }{dh:DH Game %N - }The discussion continues in our postgame thread: {link} #{myTeam:name%stripspaces}{dh: #doubleheader}")
		* `ASG_TEXT` - what do you want your tweet to say for All-Star Games? Same parameters as `*_TITLE` are available, plus `{link}` which will be the thread shortlink. Twitter currently limits tweets to 280 characters, so be brief. (suggested: "{series:%D - }The discussion continues in our postgame thread: {link} #MLBAllStarGame #ASG{date:%Y}")

* `WEEKLY_THREAD` - weekly thread settings (intended for off season but can be used all year)
	* `ENABLED` - do you want a weekly discussion thread? (true/false)
	* `OFFSEASON_ONLY` - do you want to post weekly threads only during the off season? (true/false)
	* `WEEK_START` - what day of the week do you want the weekly threads to post (around Midnight bot local time)? ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", default is "Monday")
	* `TITLE` - thread title. see `PRE_THREAD` : `TITLE` for info about available parameters. Note: `{oppTeam}`, `{awayTeam}`, and `{homeTeam}` parameters are not supported for weekly threads. (Default: "Weekly {sub} Offseason Discussion Thread - {date:%B %d, %Y}")
	* `SUGGESTED_SORT` - what do you want the suggested sort to be? set to "" if your bot user does not have mod rights ("confidence", "top", "new", "controversial", "old", "random", "qa", "")
	* `INBOX_REPLIES` - do you want to receive thread replies in the bot's inbox? (true/false)
	* `FLAIR` - flair to set on the thread, if `FLAIR_MODE` is not "none" ("Offseason Thread")
	* `CONTENT`
		* `FOOTER` - text to include in the body of the post ("Use this thread to talk about anything you want!")
	* `TWITTER` - settings for tweeting off day thread link
		* `ENABLED` - do you want to tweet a link to your off day thread? (true/false)
		* `TEXT` - what do you want your tweet to say? Same parameters as `TITLE` are available, plus `{link}` which will be the thread shortlink. Twitter currently limits tweets to 280 characters, so be brief. (suggested: "The {myTeam:name} are off today. Pass the time in our off day thread: {link} #{myTeam:name%stripspaces}")

---

If you have any issues or questions, feel free to message me on reddit (/u/toddrob) or post it as a bug on github.

This was written in Python 2.7, so beware if you are running Python 3 or
	above that it may not work correctly. Also make sure you install
	praw, simplejson, pytz, and localtz before running! If you enable Twitter settings, you also need to install python-twitter!

Modules being used:

	praw 5.0.1+ - interfacing reddit
	simplejson - JSON parsing
	urllib2 - pulling data from MLB servers
	ElementTree - XML parsing
	pytz - timezone conversion
	localtz - to determine bot's local timezone
	python-twitter (optional) - interfacing Twitter
	pyprowl (included) - interfacing Prowl

---
### Change Log

#### v5.1.9
* Updated live game API to v1.1 in order to address #77 (v1 not updating with live game data)
* Improved logging when bot crashes
* Updated Cleveland Indians sub to r/ClevelandIndians

#### v5.1.8
* Added support for weekly threads, which can be enabled all year or only for offseason, and which will be posted around Midnight (bot local time) on the configured day. Configure with the new `WEEKLY_THREADS` section. See `README.md` for descriptions of the settings and `sample_settings.json` for examples.
* Added `WEEKLY_THREAD_SUBMITTED` Prowl notification trigger for when weekly threads are submitted
* Updated probable pitcher reports to use Stats API - this was the last piece of data coming from legacy data files
* Added `GAME_THREAD`:`PREVIEW_STANDINGS` setting to include division standings in game threads while in preview status
* Division standings will now be included in pre and game threads only for regular season games
* Deprecated `download_files()` function
* Added `GAME_THREAD`:`POST_BY` setting, which allows you to set the latest hour you want the game thread to be posted (within 10 minutes after the hour). the game thread will be posted at the earlier of `POST_BY` and game start minus `HOURS_BEFORE`. This is useful for subs that do not want to use pregame threads, and want the game thread posted at a specific time each day instead
* Added check for game status of Live or Final when determining if it is time to post the game thread
* Updated stale thread detection/handling

#### v5.1.7
* Fixed bug when next game is a Wild Card game
* Added line number to logs

#### v5.1.6
* Added support for the bot to comment on game threads when specific events occur. This feature is OFF by default. All events that have occurred in 2018 through August 3 are in `README.md` under the description for `GAME_THREAD` : `NOTABLE_PLAY_COMMENTS` : `MYTEAM_BATTING` : `EVENTS`, and any other events you come across can be configured. Configuration allows bot-runner to decide which events will trigger comments when the configured team is batting or pitching, and a header and footer can be configured for each event--with same substitution parameters as thread titles and tweets, plus `{halfInning}` (`Top`/`Bottom`) and `{inning}` (`1`, `2`, etc.). Configure using the new `GAME_THREAD` : `NOTABLE_PLAY_COMMENTS` setting section. See above in readme for explanation of settings, or copy from `sample_settings.json` and modify as needed.
* Enhanced `replace_params()` to support notable play comments, including supporting runs while the game is in progress (previous only worked after the game is final)
* Added functions to support notable play comments: `get_latest_atBatIndex()`, `get_notable_plays()`, and `generate_notable_play_comment()`
* Added comment count to daily and average game thread stats logging and Prowl notifications (not broken down by event type yet)
* Added max utilization of Reddit API to daily game thread stats logging and Prowl notifications. Reddit API allows 600 calls per 10 minute period, so if this regularly gets near 600, you should increase the `GAME_THREAD` : `EXTRA_SLEEP` setting. The bot will also take a break automatically if the limit is approaching. I have never seen it anywhere near 600.
* Added `E#` (elimination number aka magic number) to standings table in pre/off threads
* Fixed failure to validate some ASG-related settings

#### v5.1.5.1
* Fixed two errors related to `POST_THREAD_SUBMITTED` Prowl notification

#### v5.1.5
* Added support for All-Star Game pre/game/post threads. Turn off with new `ASG` setting, and control title and tweet text with new `ASG_TITLE` and `ASG_TEXT` settings in pre/game/post thread settings
* Fixed error due to sport code not being available in MLB data after game has ended
* Fixed consolidated pregame thread not being suppressed for split doubleheader when Game 1 game thread will be posted within the configured `SUPPRESS_MINUTES` threshold

#### v5.1.4
* Added support to `setup_oauth.py` for settings file command line argument, e.g. `python setup_oauth.py --settings=settings-phi.json` or `python setup_oauth.py --settings=/path/to/settings.json`. If absolute path is not provided, the file must be in the /src/ folder along with main.py.
* Updated README instructions to mention support for passing settings filename/path in command line argument
* Added `get_standings()` function to get standings data for a given team, division, league, or all
* Added `generate_standings()` function to generate a table of the configured team's division standings
* Moved `OFF_THREAD`:`FOOTER` setting into new `OFF_THREAD`:`CONTENT` section, and added `NEXT_GAME` and `DIV_STANDINGS` settings to the same section
* Added off thread support to `generate_thread_code()`; now all thread code is generated through this function
* Added `DIV_STANDINGS` option to `PRE_THREAD`:`CONTENT`, between probable pitchers and footer
* Fixed next game lookup when today's game is rescheduled to doubleheader game 2 tomorrow (it was returning DH game 2 instead of game 1)
* Fixed debug logging in `next_game()` not including the list of found games
* Fixed placeholder game handling in `next_game()`, which I don't think even applies to MLB Stats API but I'll find out when we get to the postseason
* Fixed crash when sending game thread edit stats to prowl after a delayed game

#### v5.1.3
* Updated logger to include a startup log (file=debug, console=info) prior to settings being loaded, then reset logger once user settings are loaded
* Updated logic to re-read settings file on a 60 second loop when critical fields cannot be validated. This allows you to fix the settings file without stopping and restarting the bot.
* Added `config.py` module, which contains `Config` class that handles settings validation. The `conf.SETTINGS_CONFIG` dictionary holds metadata about available settings, including default values, allowed values when applicable (e.g. FLAIR_MODE can only be [mod, submitter, none]), and `validate_all()` replaces individual checks for settings that used to be in `main.py`. In addition to simplifying management of default values, this is groundwork for re-reading settings after each daily loop.
* Added support for `--settings=<filename>` command line argument to specify settings file. This allows multiple copies of the same code to be run with different settings after daily reloads of settings is implemented. Absolute path supported; if only filename is provided, file must exist in /src/ folder where main.py is located.
* Added daily reload and validation of settings file, to enable config changes without restarting the bot
* Added error handling for `FLAIR_MODE`=`mod` when user does not have mod rights
* Added support for `{myTeam:wins}` and `{myTeam:losses}` for off day thread titles/tweets, using new `get_record()` function which pulls wins & losses from standings API for a given team or list of teams
* Clear team info cache earlier each day, so if MLB messes up the team info data, it will not take another full day to update
* Only include delayed status in daily game thread edit stats notification if the game was delayed
* Minor logging adjustments

#### v5.1.2
* Added `logger.py` module, which contains the `Logger` class that adds console and file handlers to the root logger. Enable and set log level for console and file in `settings.json` with the new `LOGGING` section (copy from `sample_settings.json`). `LOG_LEVEL` setting is deprecated. Default is file enabled/DEBUG and console enabled/INFO. Log files will be stored in `/logs` and named `TEAM_CODE-bot.log` (e.g. `phi-bot.log`), rotated daily with a week's logs retained.
* Added `self.editStats` dict to hold data about checks and edits for each game thread. At the end of each day, an INFO entry will be logged with the totals and rate (edits/checks)
* Added Prowl notification support. Enable Prowl notifications overall, as well as individual notifications in the new `NOTIFICATIONS` : `PROWL` section in `settings.json`. See `README.md` for details and copy from `sample_settings.json`
* Fixed crash when MLB posts a game highlight using an all-star team code, in this case team_id 159, "American League All-Stars"
* Fixed stale team records in pregame and game thread titles #69
* Fixed bug that occurs when Twitter feature is turned off for all threads (or Twitter settings are missing)

#### v5.1.1
* Fixed bug in `next_game()` that resulted in doubleheader game 1 being listed as the next game after doubleheader game 2
* Added reason to game status at the end of game/post threads when game is postponed/cancelled/suspended
* Added support for `lower`, `upper`, and `stripspaces` modifiers in thread titles and tweet text, see details under `PRE_THREAD` : `TITLE` setting in `README.md`
* Fixed bug in postgame thread title generation, which resulted in records being incorrect (not updated to reflect the result of the game)
* Added `runs` parameter to `myTeam`, `oppTeam`, `awayTeam`, and `homeTeam` parameters for title/tweet replacement (e.g. {myTeam:runs}). Supported for postgame threads/tweets only
* Updated default postgame thread titles and tweet text to be more conversational and include score - see above and `sample_settings.json` for new defaults
* Fixed some table formatting in new reddit ui

#### v5.1.0
* Updated to use new MLB Stats API
* Added flexible thread title support (using **new `TITLE` setting** in each thread section of `settings.json`, `TAG` setting is deprecated). Info about available parameters and examples are listed in `README.md` under the `PRE_THREAD` : `TITLE` setting
* Added Twitter support. Configure Twitter OAuth settings by copying the new `TWITTER` section in `sample_settings.json`, and enable/configure for each thread by copying the `TWITTER` section from each of the `*_THREAD` sections in `sample_settings.json`
* Added `api_download()` function to modularize downloading of data from MLB Stats API, including a cache of api data in the new Games class (flushed daily), to honor wait time included in live game feed metadata and reduce the number of times the live game feed has to be downloaded for each game thread update. Since wait time in API data does not work correctly, also added a 4 second local wait time so the data only has to be downloaded once per game thread update.
* Added `get_schedule()` function to modularize the lookup of a given day's game schedule (filtered by team, game, or all games)
* Created `games.py` module with a Games class, which simply holds the `games` dict. I had to make it a separate module in order to make the games dict accessible from all modules
* Created a variable in the editor to hold info about all teams, rather than downloading the data for each use of `lookup_team_info()`
* Added support for `sport_code` other than `mlb` in `lookup_team_info()`. This is necessary for exhibition games against college teams (`sport_code` = `bbc`)
* Added `lookup_player_info()` to pull player info from Stats API. Sets local cache wait time to 8 hours since this data shouldn't change during the game
* Deprecated several functions since the same data is available in the Games class: `get_homeaway()`, `generate_pre_first_pitch()`, `generate_pre_description()`
* Deprecated `generate_pre_code()` and `generate_code()` (combined into `generate_thread_code()`)
* Deprecated `download_pre_files()` (replaced with `api_download()`) -- `download_files()` is mostly deprecated, but still used for pitcher reports in `generate_probables()` until I can find a Stats API source for that data. Updated `download_files()` to support different file sets, since it will only be used to download gamecenter.xml
* Deprecated `generate_broadcast_info()` and the `PRE_THREAD` : `CONTENT` : `BROADCAST`, `FIRST_PITCH`, and `DESCRIPTION` settings; added `HEADER` and `FOOTER` settings to the same section. Replaced these pre-thread-specific elements with the same header as the game/post threads, excluding Weather and Strikezone Map links. **Be sure to update your `settings.json` file with these changes (and `TAG`->`TITLE` for each thread)**
* Deprecated `decision` class from `player` module, since decision data is straightforward in Stats API
* Deprecated `get_subreddits()`, `get_notes()`, and `get_team()` in favor of `lookup_team_info()`
* Deprecated `SERIES_IN_TITLES` setting; use `{series}` parameter instead, see `PRE_THREAD` : `TITLE` description above for details
* Updated notes links in thread headers from "Home"/"Away" to team names, and added team names in the TV and Radio sections
* Added innings pitched to probable pitcher section
* Added OBP and SLG to box score
* Added `EXTENDED_BOX_SCORE` setting in `CONTENT` settings section for both `GAME_THREAD` and `POST_THREAD`. This will display the extended box score data (triples, homeruns, total bases, GIDP, etc.) Default false for game and true for postgame.
* Added LOB (runners left on base) to linescore
* Added separate SD and HD links to highlights list (previous version had SD only)
* Added check for postponed/cancelled/suspended status while waiting for time to post game thread. If game is postponed/canceled prior to the game thread being posted and postgame thread is enabled, the bot will now skip the game thread and post the postgame thread immediately
* Moved `skipflag` into `games` dict rather than leaving it as a standalone var--used it to skip posting of game thread for canceled/postponed game
* Updated logic for counting active/pending/delayed/final games--the previous logic was flawed when postgame thread is disabled
* Bot will now sticky (if enabled) pre-existing threads on startup, and then unsticky as usual when the next thread is posted
* Added automatic timezone support based on bot's local timezone and team's timezone; added `convert_tz()` function to editor module and removed `BOT_TIME_ZONE` and `TEAM_TIME_ZONE` settings. This requires two new modules, pytz (for timezone conversion) and tzlocal (to determine bot's local timezone). use pip install <module name> or easy_install <module name> to install them
* Added `get_gameDate()` function to look up UTC date/time stamp for a game based on gamePk
* Added `PRE_THREAD` : `CONSOLIDATED_DH_TITLE` setting to be used for consolidated pregame threads when `CONSOLIDATE_DH` is enabled
* Updated default date format in thread titles to `%a %b %d @ %I:%M%p %Z` (e.g. `Sat Apr 28 @ 06:05PM EDT`) for thread titles (`%a %b %d` for consolidated doubleheader pregame threads, e.g. `Sat Apr 28`)
* Added global var to `lookup_team_code.py` to hold team info, rather than downloading it multiple times for each lookup
* Added `replace_params()` to modularize the replacement of parameters for titles and tweets (and more later)
* Logging improvements

#### v5.0.4
* Suppressed series and game number from next game at the end of game/post threads for regular season games
* Tested with praw 5.0.4
* Minor logging adjustments

#### v5.0.3
* Fixed logging of suppressed off day thread on the first game day of the season
* Added error handling for missing plays.json file, to allow the post header to still show despite missing weather info
* Excluded Game # from "next game" at the end of game/post threads for Spring Training games (#60)
* Minor code formatting cleanup

#### v5.0.2
* Fixed error when generating URL for exhibition game
* Fixed error when attempting to remove nonexistent newsroom node from game data
* Added Scheduled to list of pre-game statuses

#### v5.0.1
* Fixed error when looking up games on a given day, due to MLB server throwing an error when the URL has a trailing slash
* Fixed broken game URLs due to MLB data not having game id populated in grid.json
* Fixed error due to gamecenter.xml not existing yet and MLB servers throwing a new error
* Fixed support for exhibition games against non-MLB teams (as long as their league code is bbc)
* Suppressed game number in game/post thread footers for exhibition games ("Exhibition Game Game 0" -> "Exhibition Game")
* Minor logging improvements

#### v5.0.0
* Re-wrote logic for finding games on MLB website. Instead of reading directory names, the bot will now use grid.json to determine if the configured team has any games on the given day (either "today" for purposes of posting offday/pre/game/post threads, or future days for looking up the next game). This was necessary because MLB publishes placeholder games for the entire postseason, and does not take them down when the teams are determined or the series does not need all 5/7 games. Placeholder games are removed from grid.json when they are no longer relevant, so this method is more accurate. (Issue #55)
* Updates to use some fields directly from MLB data rather than determining on my own. For example, use double_header_sw instead of comparing directory names to identify doubleheaders, use game_nbr instead of pulling gamenum from the end of the directory name, use game info from grid.json in generate_next_game() instead of calling a separate function (teams_time())
* Next game will now display "Time TBD" instead of 3:33 AM
* Added series info to next game in game/post threads, when present (e.g. Next Game: Wednesday, October 11, 8:00 PM vs Yankees (ALDS Game 5))
* Added series info to thread titles (e.g. "PREGAME THREAD: NLDS Game 4 - Nationals (1-2) @ Cubs (2-1) - October 10, 2017"). Turn off with `SERIES_IN_TITLES`=false (not thread-specific)
* Removed support for deprecated settings. Default values will still be used for missing settings that do not trigger a fatal error.
* TV station will no longer be duplicated in game/post thread header if it's the same for home and away teams (national games)
* If team-specific game headline or blurb is missing, the generic game headline or blurb will be used instead of having no headline/blurb at all
* Minor logging improvements

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
* Doubleheader game 2 will no longer show 3:33 AM first pitch in pregame thread or game thread, instead will show game 1 start + 3.5 hours
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
