# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent


class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):

        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        minDistToGhost = 9999999999
        minDistToFood = 99999999999
        value = successorGameState.getScore()

        for ghostState in newGhostStates:
            distGhost = manhattanDistance(newPos, ghostState.getPosition())
            if distGhost < minDistToGhost:
                minDistToGhost = distGhost
        value = value + minDistToGhost

        distancesToFood = [manhattanDistance(newPos, x) for x in newFood.asList()]
        if len(distancesToFood):
            minDistToFood = min(distancesToFood)

        ourScore = 0
        """if (minDistToGhost > 0 & minDistToFood > 0):
            ourScore = (10.0 / minDistToFood) - (10.0 / minDistToGhost)"""
        ourScore = minDistToGhost - minDistToFood
        return successorGameState.getScore() + ourScore


def scoreEvaluationFunction(currentGameState):
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    recursiveCount = 0

    def getAction(self, gameState):


        #Function handles minimizing the Ghost actions
        def handleGhost(results):
            return min(results)

        #Function handles maximizing the PacMan actions
        def handlePacMan(results):
            return max(results)

        #Function handles the base case - For PacMan for initial depth
        def baseCase(results):
            bestMove = max(results)
            bestIndices = []
            for index in range(len(results)):
                if results[index] == bestMove:
                    bestIndices.append(index)
            chosenIndex = random.choice(bestIndices)
            return chosenIndex

        #Recurssive function for minimax
        #gameState contains the current game state
        #Current depth is the current recurssion level
        #For pacman, index is 0; For ghosts it reanges from 1 to (len(gameState.getAgents()) - 1)
        def minMaxSearch(gameState, currentDepth, index):
            self.recursiveCount += 1
            #Check if Pacman is dead or has won, or the depth has exceeded the allowed look-ahead depth.
            #Return the evaluation function value for the paths followed by Ghost, Pacman for the action(s) taken
            if gameState.isWin() or currentDepth > self.depth or gameState.isLose():
                return self.evaluationFunction(gameState)

            #allowedActions contains the allowed actions for current state
            allowedActions = []
            actions = gameState.getLegalActions(index)
            for action in actions:
                if action == Directions.STOP or action == 'Stop':
                    continue
                else:
                    allowedActions.append(action)

            #Increment the index - Handle next agent
            nextIndex = index + 1
            nextDepth = currentDepth

            #If All agents at current depth have been handled, increment the depth and re-initiate the index to 0
            if nextIndex >= gameState.getNumAgents():
                nextIndex = 0
                nextDepth += 1

            #Results will contain the actions allowed at current index
            results = []
            for action in allowedActions:
                results.append(minMaxSearch(gameState.generateSuccessor(index, action), nextDepth, nextIndex))

            #Base case - Pacman at depth 1 calls gets max of min(Ghost states)
            if index == 0 and currentDepth == 1:
                return allowedActions[baseCase(results)]

            #Returns max of pacman's legal actions
            if index == 0:
                return handlePacMan(results)

            #Returns min of ghost's legal actions
            else:
                return handleGhost(results)
        print self.recursiveCount
        return minMaxSearch(gameState, 1, 0)


class AlphaBetaAgent(MultiAgentSearchAgent):
    recursiveCount = 0

    def getAction(self, gameState):

        def minMaxSearch(gameState, currentDepth, index, alpha, beta):
            self.recursiveCount += 1
            if gameState.isWin() or currentDepth > self.depth or gameState.isLose():
                return self.evaluationFunction(gameState)

            allowedActions = []
            actions = gameState.getLegalActions(index)
            for action in actions:
                if action == Directions.STOP or action == 'Stop':
                    continue
                else:
                    allowedActions.append(action)

            nextIndex = index + 1
            nextDepth = currentDepth

            if nextIndex >= gameState.getNumAgents():
                nextIndex = 0
                nextDepth += 1

            results = []
            for action in allowedActions:
                value = minMaxSearch(gameState.generateSuccessor(index, action), nextDepth, nextIndex, alpha, beta)
                # print alpha, beta
                if index == 0:
                    bestMove = value
                    if bestMove > beta:
                        # print "Break with best < beta ", bestMove, alpha, beta
                        results.append(value)
                        break
                    alpha = max(alpha, bestMove)
                    results.append(value)
                else:
                    bestMove = value
                    if bestMove < alpha:
                        # print "Break with bestMove < alpha ", bestMove, alpha, beta
                        results.append(value)
                        break
                    beta = min(beta, bestMove)
                    results.append(value)

            if results == []:
                return None

            if index == 0 and currentDepth == 1:
                bestMove = max(results)
                bestIndices = [index for index in range(len(results)) if results[index] == bestMove]
                chosenIndex = random.choice(bestIndices)
                return allowedActions[chosenIndex]

            if index == 0:
                bestMove = max(results)
                return bestMove
            else:
                bestMove = min(results)
                return bestMove
        print self.recursiveCount
        return minMaxSearch(gameState, 1, 0, -999999999, 9999999999)


class ExpectimaxAgent(MultiAgentSearchAgent):
    recursiveCount = 0

    def getAction(self, gameState):

        #Function handles minimizing the Ghost actions
        def handleGhost(results):
            return sum(results)/len(results)

        #Function handles maximizing the PacMan actions
        def handlePacMan(results):
            return max(results)

        #Function handles the base case - For PacMan for initial depth
        def baseCase(results):
            bestMove = max(results)
            bestIndices = []
            for index in range(len(results)):
                if results[index] == bestMove:
                    bestIndices.append(index)
            chosenIndex = random.choice(bestIndices)
            return chosenIndex

        #Recurssive function for minimax
        #gameState contains the current game state
        #Current depth is the current recurssion level
        #For pacman, index is 0; For ghosts it reanges from 1 to (len(gameState.getAgents()) - 1)
        def minMaxSearch(gameState, currentDepth, index):
            self.recursiveCount += 1
            #Check if Pacman is dead or has won, or the depth has exceeded the allowed look-ahead depth.
            #Return the evaluation function value for the paths followed by Ghost, Pacman for the action(s) taken
            if gameState.isWin() or currentDepth > self.depth or gameState.isLose():
                return self.evaluationFunction(gameState)

            #allowedActions contains the allowed actions for current state
            allowedActions = []
            actions = gameState.getLegalActions(index)
            for action in actions:
                if action == Directions.STOP or action == 'Stop':
                    continue
                else:
                    allowedActions.append(action)

            #Increment the index - Handle next agent
            nextIndex = index + 1
            nextDepth = currentDepth

            #If All agents at current depth have been handled, increment the depth and re-initiate the index to 0
            if nextIndex >= gameState.getNumAgents():
                nextIndex = 0
                nextDepth += 1

            #Results will contain the actions allowed at current index
            results = []
            for action in allowedActions:
                results.append(minMaxSearch(gameState.generateSuccessor(index, action), nextDepth, nextIndex))

            #Base case - Pacman at depth 1 calls gets max of min(Ghost states)
            if index == 0 and currentDepth == 1:
                return allowedActions[baseCase(results)]

            #Returns max of pacman's legal actions
            if index == 0:
                return handlePacMan(results)

            #Returns min of ghost's legal actions
            else:
                return handleGhost(results)

        print self.recursiveCount
        return minMaxSearch(gameState, 1, 0)


def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


# Abbreviation
better = betterEvaluationFunction

