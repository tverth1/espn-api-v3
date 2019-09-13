from player import Player

class Team():
    """
    teamData['teams'][teamId]
    """
    def __init__(self, teamData):
        self.teamId = teamData['id']
        self.teamAbbrev = teamData['abbrev']
        self.teamName = "%s %s" % (teamData['location'], teamData['nickname'])
        self.divisionId = teamData['divisionId']
        self.wins = teamData['record']['overall']['wins']
        self.losses = teamData['record']['overall']['losses']
        self.ties = teamData['record']['overall']['ties']
        self.pointsFor = teamData['record']['overall']['pointsFor']
        self.pointsAgainst = teamData['record']['overall']['pointsAgainst']
        self.owner = "Unknown"
        
        self.schedule = {}              # Constructed by League.buildTeams
        self.scores = {}                # Constructed by League.buildTeams when it calls Team.addMatchup
        self.rosters = {}               # Constructed by League.buildTeams when it calls League.loadWeeklyRosters when it calls Team.fetchWeeklyRoster
                                        # self.startingRosterSlots is constructed by League.buildTeams
        
    
    def __repr__(self):
        """ This is what is displayed when print(team) is entered"""
        return 'Team(%s)' % (self.teamName)     
        
    def nameOwner(self, owner):
        """owner = teams['members'][teamIndex]['firstName']"""
        self.owner = owner
        return
    
    def addMatchup(self, teamData, week):
        ''' Currently only adds a team's score for a given week to its scores{} attribute '''
        self.scores[week] = round(teamData['totalPoints'],1)    
        return

    def fetchWeeklyRoster(self, rosterData, week):
        '''Fetch the roster of a team for a specific week'''
        roster = rosterData['entries']                      # Get the players in roster{}
        self.rosters[week] = []                             # Create an empty list for the team roster for the given week
        for player in roster:
            self.rosters[week].append(Player(player))       # Add each player on the roster to team's roster for the given week
        
    ''' **************************************************
        *      Begin advanced stats team methods         *
        ************************************************** '''
    
    def topPlayers(self, week, slotCategoryId, n):
        ''' Takes a list of players and returns a list of the top n players based on points scored. '''
        # Gather players of the desired position
        unsortedList = []
        for player in self.rosters[week]:
            if slotCategoryId in player.eligibleSlots:
                unsortedList += [player]
                
        # Sort players by points scored
        sortedList = [unsortedList[0]]
        for player in unsortedList[1:]:
            for i in range(len(sortedList)):
                if (player.score >= sortedList[i].score):
                    sortedList = sortedList[:i] + [player] + sortedList[i:]
                    break
            if player not in sortedList:
                sortedList += [player]
        return sortedList[:n]       
    
    def bestLineup(self, week):
        ''' Returns the best possible lineup for team during a given week. '''
        savedRoster = self.rosters[week][:]
        
        # Find Best Lineup
        bestLineup = []
        for slotId in self.startingRosterSlots.keys():
            numPlayers = self.startingRosterSlots[slotId][0]
            bestPlayers = self.topPlayers(week, int(slotId), numPlayers)
            bestLineup += bestPlayers
            for player in bestPlayers:
                self.rosters[week].remove(player)
        self.rosters[week] = savedRoster 
        
        # Sum Scores
        maxScore = 0
        for player in bestLineup:
            maxScore += player.score          
        return round(maxScore, 2)   

    def bestTrio(self, week):
        ''' Returns the the sum of the top QB/RB/Reciever tri0 for a team during a given week. '''
        qb = self.topPlayers(week, 0, 1)[0].score
        rb = self.topPlayers(week, 2, 1)[0].score
        wr = self.topPlayers(week, 4, 1)[0].score
        te = self.topPlayers(week, 6, 1)[0].score
        bestTrio = round(qb + rb + max(wr, te), 2)
        return bestTrio 

    def getTeams(self):
        ''' Takes a team and returns all other teams in the league (in order of schedule, not team ID). ''' 
        opponents = self.schedule
        otherTeams = []
        for opp in opponents.values():
            if opp not in otherTeams:
                otherTeams += [opp]
        return otherTeams

    def weeklyFinish(self, week):
        ''' Returns the rank of a team based on the weekly score of a team for a given week. '''
        otherTeams = self.getTeams()
        weeklyFinish = 1
        for teamId in range(len(otherTeams)):
            if (self.scores[week] != otherTeams[teamId].scores[week]) and (self.scores[week] <= otherTeams[teamId].scores[week]):
                weeklyFinish += 1;
        return weeklyFinish  

    def numOut(self, week):
        ''' Returns the (esimated) number of players who did not play for a team during a given week (excluding IR slot players). '''
        numOut = 0
        # TODO: write new code based on if player was injured
        return numOut

    def avgStartingScore(self, week, slotId):
        count = 0
        sum = 0
        for p in self.rosters[week]:
            if (p.positionId == slotId) and (p.isStarting):
                count += 1
                sum += p.score
        avgScore = round(sum/count,2)
        return avgScore
    
    def totalBenchPoints(self, week):
        sum = 0
        for p in self.rosters[week]:
            if not p.isStarting:
                sum += p.score
        return sum
    
    def printWeeklyStats(self, week):
        ''' Print the weekly stats for the team during a given week. '''
        print( '----------------------------' + '\n' + \
            self.owner[0] + ' Week ' + str(week) + '\n' + \
            '----------------------------' + '\n' + \
            'Week Score: ' + str(self.scores[week]) + '\n' + \
            'Best Possible Lineup: ' + str(self.bestLineup(week)) + '\n' + \
            'Opponent Score: ' + str(self.schedule[week].scores[week]) + '\n' + \
            'Weekly Finish: ' + str(self.weeklyFinish(week)) + '\n' + \
            'Best Trio: ' + str(self.bestTrio(week)) + '\n' + \
            'Number of Injuries: ' + str(self.numOut(week)) + '\n' + \
            'Starting QB pts: ' + str(self.avgStartingScore(week, 0)) + '\n' + \
            'Avg. Starting RB pts: ' + str(self.avgStartingScore(week, 2)) + '\n' + \
            'Avg. Starting WR pts: ' + str(self.avgStartingScore(week, 4)) + '\n' + \
            'Starting TE pts: ' + str(self.avgStartingScore(week, 6)) + '\n' + \
            'Starting Flex pts: ' + str(self.avgStartingScore(week, 23)) + '\n' + \
            'Starting DST pts: ' + str(self.avgStartingScore(week, 16)) + '\n' + \
            'Starting K pts: ' + str(self.avgStartingScore(week, 17)) + '\n' + \
            'Total Bench pts: ' + str(self.totalBenchPoints(week)) + '\n' + \
            '----------------------------')    