import urllib2
import simplejson as json
def lookup_team_info(field="name_abbrev", lookupfield="team_code", lookupval=None):
    try:
        response = urllib2.urlopen("http://mlb.com/lookup/json/named.team_all.bam?sport_code=%27mlb%27&active_sw=%27Y%27&all_star_sw=%27N%27")
        teaminfo = json.load(response)
    except Exception as e:
        print e
        return None

    teamlist = teaminfo.get('team_all').get('queryResults').get('row')
    teams = []
    for team in teamlist:
        if team.get(lookupfield,None).lower() == lookupval.lower(): teams.append(team)
    return teams

print "########"
print "This script will look up the TEAM_CODE value you should use in settings.json."
print "You can enter the team name (Phillies, Athletics, Cubs),"
print "team name abbreviation (PHI, OAK, CHC),"
print "or city (Philadelphia, Oakland, Chicago)"
print ""

while True:
    inputval = raw_input("Enter your team's name, abbreviation, or city: ")
    teams = []
    teams = lookup_team_info(field='team_code', lookupfield='name', lookupval=inputval)
    if not teams: teams = lookup_team_info(field='team_code', lookupfield='name_abbrev', lookupval=inputval)
    if not teams: teams = lookup_team_info(field='team_code', lookupfield='city', lookupval=inputval)
    if not teams: teams = lookup_team_info(field='team_code', lookupfield='name_display_short', lookupval=inputval)
    if len(teams):
        for team in teams:
            print "The TEAM_CODE for",team.get('name_display_long'),"is:",team.get('team_code')
    else:
        print "TEAM_CODE not found. Are you sure you entered the team name/abbreviation/city correctly?"
    print ""
