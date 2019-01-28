import numpy as np
import random
import copy
import sys
import time
# from matplotlib import pyplot as plt

def checkVictor(board): # check if anyone has won
    for pair in [[0,4,8],[2,4,6],[0,3,6],[1,4,7],[2,5,8],[0,1,2],[3,4,5],[6,7,8]]:
        if (board[pair[0]] != 0) and (board[pair[0]] == board[pair[1]]) and (board[pair[1]] == board[pair[2]]):
            return board[pair[0]]
    
    if 0 in board: # board not complete yet and game still going
        return None
    return 0 # if board is full its a tie

def checkWin(board,value): # check if there is a winning or loss preventing move
    indx = None
    for pair in [[0,4,8],[2,4,6],[0,3,6],[1,4,7],[2,5,8],[0,1,2],[3,4,5],[6,7,8]]:
        for perm in {0,1,2}: # loop through and find if two are equal
            if board[pair[perm]] != 0 and board[pair[perm]] == board[pair[(perm+1)%3]] and\
                board[pair[(perm+2)%3]] == 0:
                        if board[pair[perm]] == value:
                            return pair[(perm+2)%3] # if there is a winning move, return it
                        else:
                            indx = pair[(perm+2)%3] # if there is a not lose move, check for win move first
    return indx


def printBoard(board,myMove):
    for i in [0,1,2,3,4,5,6,7,8]:
        if i == myMove:
            print('\033[1m' + '%3i'%board[i] + '\033[0m', end="")
        else:
            print("%3i"%board[i], end="")
        if i % 3 == 2:
            print()
    print()


def computeAIMoves(board,AI):
    # compute AI moves
    moves = np.ndarray.tolist(board * AI)[0]
    board = np.ndarray.tolist(board)[0]
    zeroCount = board.count(0)
    
    # remove spaces that are taken
    for i in [0,1,2,3,4,5,6,7,8]:
        if board[i] != 0:
            moves[i] = 0
    moves = np.asarray(moves)
    # if np.amax(abs(moves)) > 1:
    # print("max and 9-zeroCount=",np.amax(abs(moves)), (9 - zeroCount) ** 0.5)
     
    # # # moves = np.ndarray.tolist(moves / np.linalg.norm(moves)) # list predicted moves
    # # # moves = np.ndarray.tolist(moves / np.amax(abs(moves))) # list of predicted moves
    moves = np.ndarray.tolist(moves / 1.5) # list of predicted moves
    
    # if max(moves) > 1.1:
    #     print(max(moves))
    
    return moves, board


def calcCost(myMove,board,predictedMoves):
    costs = 0
    zeroCount = board.count(0)
    for j in range(9): # calculate errors in predictions for spots it could have chosen from
        # in the case that we are calculating cost of correct weights
        if j == myMove:
            costs += (1-abs(predictedMoves[j]))**2
        elif board[j] == 0:
            costs += predictedMoves[j]**2 / zeroCount
    return costs


def compileChanges(myMove,board,predictedMoves,changes,count,costs,plays,frac1,frac2):
    # multMoves = np.ndarray.tolist(100 * np.asarray(predictedMoves))
    # if plays > 5000: 
        # print(predictedMoves[myMove])
        # printBoard(multMoves,myMove)
    # multMoves[myMove] = 100 - 100 * abs(predictedMoves[myMove])
    
    # costs[plays-1] += 1-abs(predictedMoves[myMove])
    if np.amax(abs(np.asarray(predictedMoves))) == abs(predictedMoves[myMove]):
        costs[plays-1]+=1
    
    zeroCount = board.count(0)
    # compile changes
    for j in range(9): # loop thru cols of Network
        if j != myMove or predictedMoves[j] != 0: # this way, we dont crash
            mv = predictedMoves[j]
        else:
            mv = 0.00001
        
        if j == myMove: # in the case that we are adjusting the correct weights, coefficient to change weight by
            coeff =  - abs(mv) * (1-abs(mv)) / (2 * mv * frac1)
        else:
            coeff = mv / (2 * zeroCount * frac2)
        
        for i in range(9):
            if board[i] != 0 and i != j:
                changes[i][j] -= coeff * board[i]
    

# have the hard coded AI or me make a move
def makeMove(board,value):
    # myMove = None
    # check2 = checkWin(board,value) # check if there is a move to win or prevent immediate loss
    # if check2 != None:
    #     board[check2] = value
    #     myMove = check2
    # else:
    #     # middle not taken
    #     if board[4] == 0:
    #         board[4] = value
    #         myMove = 4
    #     elif board[4] == -value and value not in {board[1],board[3],board[5],board[7]}:
    #         if board[2] == 0:
    #             board[2] = value
    #             myMove = 2
    #         elif board[0] == 0:
    #             board[0] = value
    #             myMove = 0
    #     else:
    #         for i in [1,4,0,2,5,3,6,8,7]:
    #             if board[i] == 0 and (i%2 == 0 or board[8-i] == 0):
    #                 board[i] = value
    #                 myMove = i
    #                 break
    #     if myMove == None:
    #         for i in [1,4,0,2,5,3,6,8,7]:
    #             if board[i] == 0:
    #                 board[i] = value
    #                 myMove = i
    
    # dont allow for incorrect move
    while True:
        myMove = int(input())
        if abs(myMove-4) > 4:
            print("not a valid move")
            continue
        if board[myMove] != 0:
            print("space occupied")
            continue
        board[myMove] = value
        break
    
    return [board,myMove]


# make random move
def randomMove(board,value):
    temp = []
    for j in range(9):
        if board[j] == 0:
            temp += [j]
    myMove = temp[random.randint(0,len(temp)-1)]
    board[myMove] = value
    return [board,myMove]


# learn from move of smart AI
def learnMove(AI,board,changes,count,value,costs,plays,frac1,frac2):
    # make predictions and then make calculated move and learn, his moves are -1
    predictedMoves,board = computeAIMoves(np.matrix(board),AI) # predict moves and set board to list
    [board,myMove] = makeMove(board,value) # have smart AI make a move
    compileChanges(myMove,board,predictedMoves,changes,count,costs,plays,frac1,frac2) # make adjustments to changes
    victor = checkVictor(board)
    if count >= 8 or victor != None: # make changes every so often or if victory
        AI += np.asarray(changes)
        changes = [[0 for i in range(9)] for i in range(9)]
    return [board,changes,myMove]


# have the AI make a move
def AIMove(AI,bias,board,value):
    # make predictions and then make AI move
    predictedMoves,board = computeAIMoves(np.matrix(board),AI) # predict moves and set board to list
    cpy = np.ndarray.tolist(abs(np.asarray(predictedMoves))) # makes its move here and next line
    myMove = cpy.index(max(cpy))
    board[myMove] = value
    return [board,myMove]


#####
#####


def play(AI,bias,frac1,frac2):
    # start = time.time()
    wins = 0
    plays = 0
    winList = []
    changes = [[0 for i in range(9)] for i in range(9)]
    value = 1
    costs = []
    
    first = 0
    second = 3
    
    moveArray = [lambda: makeMove(board,value * (2 * (count % 2) - 1)),\
                lambda: randomMove(board,value * (2 * (count % 2) - 1)),\
                lambda: learnMove(AI,board,changes,count,value * (2 * (count % 2) - 1),costs,plays,frac1,frac2),\
                lambda: AIMove(AI,bias,board,value * (2 * (count % 2) - 1))]
    names = ["smart hard code","rand","smart hard code","AI"]
    
    while(True):
        np.savetxt("speedTTTAI.txt",AI)
        costs.append(0)
        # print(costs)
        plays += 1
        print("\nNEWGAME %s vs %s\n"%(names[first],names[second]))
        winList += [wins]
        trials = int((frac1 + 50) * 1.2)
        # if plays % (3 * trials + 2) == 0:
            # np.savetxt("speedTTTAI.txt",AI)
            # # print("AI max =", np.amax(abs(AI)))
        
        if plays % (3 * 5 * trials + 10) == 0: # every so often, check how many we're getting right and how much we're winning
            costs.pop()
            for i in range(5 * trials + 3):
                costs[i] += costs.pop(i+2) + costs.pop(i+1)
            s = sum(costs[5 * trials - 196:5 * trials + 4])*100 // 1 # sum a bunch of values to see how often we are predicting all moves correctly
            print("\n",frac1,frac2,s,"\n")
            
            plt.plot(costs)
            plt.title("num correct")
            plt.show()
            plt.plot(winList)
            plt.title("Wins")
            plt.show()
            
            costs = [0]
            plays = 1
            
        
        count = 0
        # myMove = random.randint(0,8)
        board = [0,0,0,0,0,0,0,0,0]
        # board[myMove] = 1
        # printBoard(board,myMove)
        
        while True:
            count += 1
            
            # make some move
            result = moveArray[second - (second - first) * (count % 2)]()
            if len(result) == 2:
                [board,myMove] = result
            else:
                [board,changes,myMove] = result
            
            # if plays > 5000: p
            printBoard(board,myMove)
            
            victor = checkVictor(board)
            if victor != None: # check if anyone won
                wins -= victor
                winList += [wins]
                if victor != 0:
                    print("ASDFASDFASDF")
                    sys.exit()
                # if victor == 1:
                #     return
                break
        
        costs[plays - 1] /= (count // 2)
        


def main():
    bias = np.matrix([0,.5,0,0,0,0,0,0,0])
    AI = np.matrix(np.loadtxt("speedTTTAI.txt"))
    # print(100000 * AI // 1)
    # return
    # print(AI)
    # return
    # AI = [[random.uniform(0,.5) if (i < 2) else 0 for i in range(9)] for j in range(9)]
    # # change 2nd,8th,6th columns
    # for i in range(9): AI[i][2] = AI[i // 3 + 6 - 3 * (i%3)][0]
    # for i in range(9): AI[i][8] = AI[i // 3 + 6 - 3 * (i%3)][2]
    # for i in range(9): AI[i][6] = AI[i // 3 + 6 - 3 * (i%3)][8]
    # # change 5th,7th,3rd columns
    # for i in range(9): AI[i][5] = AI[i // 3 + 6 - 3 * (i%3)][1]
    # for i in range(9): AI[i][7] = AI[i // 3 + 6 - 3 * (i%3)][5]
    # for i in range(9): AI[i][3] = AI[i // 3 + 6 - 3 * (i%3)][7]
    # # set middle
    # for i in range(9): AI[i][4] = .6
    # 
    # for i in range(9):
    #     AI[i][i] = 0
    # AI = np.matrix(AI)
    
    stuff = play(AI,bias,20,90)
    
    # maxIndexes = []
    # maxes = []
    # stuff = []
    # for frac1 in range(40,60,5):
    #     for frac2 in range(10,20,5):
    #         AI = [[random.uniform(0,.5) for i in range(9)] for i in range(9)]
    #         for i in range(9):
    #             AI[i][i] = 0
    #         AI = np.matrix(AI)
    #         stuff += play(AI,bias,frac1,frac2)
    #     
    #     # plot variance due to frac2
    #     maxi = max(stuff)
    #     maxIndexes.append([stuff.index(maxi),maxi])
    #     maxes.append(maxi)
    #     plt.plot(stuff)
    #     plt.show()
    #     stuff = []
    # 
    # for row in maxIndexes:
    #     print(row)
    # plt.plot(maxes)
    # plt.show()
    # print("BEST = (frac1,frac2)", maxes.index(max(maxes)),maxIndexes[maxes.index(max(maxes))])

main()