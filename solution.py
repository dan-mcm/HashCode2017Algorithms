'''
Created on Apr 7, 2017
@author: Daniel McMahon
'''

from read_input import read_google
from copy import deepcopy
from random import  randint

def createMatrixArray(row,col):
    '''function creates a 2D matrix based on rows and cols inputted'''
    '''creates and populates empty matrix array'''
    
    #sets up initial matrix with 0 values in all caches
    matrix = [[0 for i in range(0,col)] for j in range(0,row)]

    return matrix

def visualiser(matrix):
    '''prints out array in semi-legible format - used for bug-testing'''
    for row in matrix:
        print(row)
    

def fitness(matrix):
    '''returns -1 if cache exceeds max limit, returns scores if solution is viaable'''
    
    #PART 1 - FITNESS CHECK - RETURNS -1 IF UNSUITABLE
    
    #setting default cacheOverflow value to 0
    cacheOverflow = 0
    cacheSize = int(data["cache_size"])
    
    #n^2 complexity - can be improved
    for row in matrix:
        #reset counter for each cache
        fileSizes = 0
        for index in range(0,len(matrix[0])):
            
            #adding total filesize of row contents
            #this assumes each value in the array contains filesize..
            if row[index] == 1:
                #add that filesize to our checker....
                fileSize = data["video_size_desc"][index]
                fileSizes += fileSize
                
        if fileSizes > cacheSize:
            cacheOverflow = -1
            #print("Cache Overflow Detected!")
            return cacheOverflow
    
    
    #PART 2 - SCORE CALCULATION
    
    currentEndpoint = 0
    currentFileID = 0
    currentNumberRequests = 0
    numIndividualRequests = 0
    gains = 0
    
    for key, value in data["video_ed_request"].items():
        #print("=====================")
        currentFileID = int(key[0]) #fileID element from tuple
        #print("Current File:", currentFileID)
        #print()
        currentEndpoint = int(key[1]) #endpointID element from tuple
        #print("Current Endpoint:", currentEndpoint)
        
        currentNumberRequests = int(value) #extracting number of requests value
        #print("Current Number of File Requests:", currentNumberRequests, "\n")
        
        #list to store different potential caches that deal the same file for a set endpoint
        cacheArray = []
        
        #boolean representing if file is actually serve-able from a cache
        cacheChecker = False
        
        #check if file is located in cache [i] and append to our array and flip the boolean to true
        for cache in range(0,len(matrix)):
            
            if matrix[cache][currentFileID] == 1:
                
                #print("File Detected in Cache:", cache)
                
                #unsure of indexing order here...
                cacheLatency = int(data["ep_to_cache_latency"][currentEndpoint][cache])       
                #print("Latency of extracting file from Cache", cacheLatency)
                #print()
                cacheArray.append(int(cache))
                cacheChecker = True
                
        #need two separate values one to represent current value and one for the overall total used in end calculation
        currentRequestValue = int(value)       
        numIndividualRequests += currentRequestValue
        
        latency = 0
        
        #DC Latency
        dcLatency = int(data["ep_to_dc_latency"][currentEndpoint])
        #print("Latency of extracting file from Data Center:", dcLatency)
        #print()
        
        #now assigning if there is no cache value that we will use the data centers latency by default
        if cacheChecker:
            #set to 0 as dont know how many caches but must be minimum of 1 if boolean is true
            latency = int(data["ep_to_cache_latency"][currentEndpoint][cacheArray[0]])
        else:
            latency = int(dcLatency)
        
        #print("Potential Caches include:", cacheArray)
        
        #if video is in multiple caches we need to select the best one for our fitness calculation
        #start at index one as index 0 is already used to set initial latency value.
        for i in cacheArray:
            if data["ep_to_cache_latency"][currentEndpoint][i] < latency:
                latency = data["ep_to_cache_latency"][currentEndpoint][i]
        
        #calculating difference as per formulae
        difference = dcLatency - latency
        
        #test print statement to point out difference values if any
        #if difference > 0:
            #print("Difference between DC and Best Cache Latency is:", difference)
        #elif difference == 0:
            #print("File being extracted from Data Centre directly")
                                
        #calculating gains as per formulae
        gains += difference * currentNumberRequests
        #print("=====================")
        #print()
    
    #overall score calculation * 1000 due to milliseconds
    score = (gains/numIndividualRequests) * 1000
    #print("Total Score =", int(score), "\n")
    return score
        
def hillClimbing(matrix,data):
    '''generates solution based on series of neighbour values changing from 1 to 0 and 0 to 1'''
    rows = len(matrix)
    cols = len(matrix[0])
    scores = []
    counter = 0
    #note due to the way lists work need 
    #to explicitly make tempMatrix a copied list so as
    #to avoid changing initial matrixes values prematurely
    testMatrix = deepcopy(matrix)
    baseScore = fitness(matrix)
    #add our starting score - for reference
    scores.append(baseScore)
    coordinates = []
    matrixArray = []
    #need a base matrix
    matrixArray.append(testMatrix)
    
    #set our default validMatrix value (in case we need to reset to it
    safeMatrix = deepcopy(matrix)
    matrix = deepcopy(safeMatrix)
    
    #setting a maxCounter
    maxCounter = rows*cols
    
    while(counter<maxCounter):
        
        #print("Checking Matrix Count: ", counter)
        counter+=1
        
        #print("Matrix view:")
        #print(matrix)
                            
        #handling swaps of 1s to 0s and 0s to 1s
        for cache in range(0,rows):
            for file in range(0,cols):
                                
                #changing value of current item in data...
                if matrix[cache][file]==1:
                    matrix[cache][file] = 0
                else:
                    matrix[cache][file] = 1
                                
                newScore = fitness(matrix)
                    
                #checking if move is feasible
                scores.append(newScore)
                coordinates.append((cache,file))
                                     
                #idea for iterating through all variations of all other variations
                matrixArray.append(deepcopy(matrix))
                                
                #reset our matrix before next update
                matrix = safeMatrix

        #DEBUG STATEMENTS
        #print("Scores are: ", scores)
        #print("Coords are: ", coordinates)
        #print()
        #print("Best result so far is:", max(scores))
        bestScoreIndex = scores.index(max(scores))
        
        #gonna use our best score to modify the matrix and go all over again the next time!
        if(matrix[coordinates[bestScoreIndex][0]][coordinates[bestScoreIndex][1]] == 1):
            matrix[coordinates[bestScoreIndex][0]][coordinates[bestScoreIndex][1]] = 0
        else:
            matrix[coordinates[bestScoreIndex][0]][coordinates[bestScoreIndex][1]] = 1
        
    #INITIAL DEBUG PRINT STATEMENTS
            
    #print("===================================================")
    #print("List of Results (top result initial input fitness):")
    #print("===================================================")
    
    #print("List of Scores:")
    #for score in scores:
    #    print(score)
        
    #print("===================================================")    
    #print()
    
    print("===================================================")

    bestScoreIndex = scores.index(max(scores))
    #print("Best Coordinates: ", coordinates[bestScoreIndex])
    print("Hill Climbing Algorithm Complete.")
    print("Number of Iterations: ", counter)
    print("Best Score: ", int(max(scores)))
    print("Best Matrix Looks as Follows:")
    print(matrixArray[bestScoreIndex])
    print("===================================================")
    print()

    return matrixArray[bestScoreIndex]

def geneticAlgorithm(matrix,data):
    '''generates 50 parent matrices, generates 50 children matrices, combines both
    sets of matrices and keeps the best scoring ones. Returns the best scoring matrix
    after 50 iterations'''
    
    caches = len(matrix)
    files = len(matrix[0])
    
    parentArray = []
    childArray = []
    parentchildArray = []
    overallscoresArray = []
    #makes empty 2d array
    mainMatrix = [[0]*files for i in range(caches)]
    samplematrix = deepcopy(mainMatrix)
    ultimateScores = []
    ultimateMatrix = []
    
    #bit of a random number of file insertions... 30%
    numOfAddedFiles = int(files*0.3)
    counter = 0
    #GENERATING PARENTS
    
    #generating 50 random matrices and adding valid ones to our matrix array
    while(len(parentArray) <50):
        #modifying a few 0/1 values
        for j in range(0,numOfAddedFiles):
            value = randint(0,1)
            samplematrix[(int)(randint(0,caches-1))][(int)(randint(0,files-1))] = value;
        
        if fitness(samplematrix)!=-1:
            parentArray.append(deepcopy(samplematrix))
           
        samplematrix=mainMatrix
    
    arraySplit = int(files/2)
    
    
    
    #GENERATING CHILDREN [50 children 2 per set of parents]
    stillComputing=True
    
    while(stillComputing):
        counter+=1
        
        condition = True
        
        for matrix in range(0,len(parentArray)):
            
            while(condition):
                reversed = (len(parentArray)-1) - matrix
                
                for file in range(0,25):
                    
                    child1 = parentArray[matrix][:arraySplit] +  parentArray[reversed][arraySplit:]
                    child2 = parentArray[reversed][:arraySplit] +  parentArray[matrix][arraySplit:]
                    
                    if fitness(child1) != -1:
                        childArray.append(child1)
                        
                    if fitness(child2) != -1:
                        childArray.append(child2)
                
                if len(childArray) >= 50:
                    condition = False
        
        #JOINING PARENTS AND CHILDREN TOGETHER
        parentchildArray = parentArray+childArray
        
        #GENERATING OVERALL SCORES FOR ALL MATRICES
        for matrix in parentchildArray:
            overallscoresArray.append(fitness(matrix))
        
        #DEBUG TEST STATEMENT PRINTED
        #print("===================================================")  
        #print("Current Run Update:")
        #print("Best Score: ", max(overallscoresArray))
        #print("Best Matrix: ", max(parentchildArray))
        #print("===================================================")  
        #print()
        
        #adding our best values from this round to our overall values
        ultimateScores.append(max(overallscoresArray))
        ultimateMatrix.append(max(parentchildArray))
        
        #ADD OUR 50 BEST OVERALL MATRICES (PARENTS AND CHILDREN) AS NEW PARENTS AND RE-ITERATE
    
        #resetting our initial parentArray
        parentArray=[]
    
        for i in range(0,50):
            bestIndex = overallscoresArray.index(max(overallscoresArray))
            parentArray.append(parentchildArray[bestIndex])
            overallscoresArray.pop(bestIndex) # removes highest so next iteration is accurate
            parentchildArray.pop(bestIndex) # removes highest so next iteration is accurate
            
        #reset localized scores
        overallscoresArray = []
        
        #calculation to limit our number of attempts
        #we keep going until we stop adding better values to bestMatrices
        #and the difference of 50 iterations has occurred
        
        if counter == 50:
            stillComputing = False
    
    bestScoreIndex = ultimateScores.index(max(ultimateScores))
    print("===================================================")  
    print("Genetic Algorithm Completed.")
    print("Number of Iterations: ", counter)
    print("Best Score: ", max(ultimateScores))
    print("Best Matrix Looks as Follows:")
    print(ultimateMatrix[bestScoreIndex])
    print("===================================================")  
    print()
    
    return ultimateMatrix[bestScoreIndex]

def randomSearch(matrix,data):
    '''takes starting matrix value, adds a random number of files per cache (max num files up to 1/3 cache size)
    runs for a limit of three times the cache size. Returns best scoring matrix'''
    
    caches = len(matrix)
    files = len(matrix[0])
    
    testMatrix = deepcopy(matrix)
    overallMatrix = []
    overallScores = []
    counter = 0
    limit = caches * 3
    
    randomInts = int(files*0.3)
    
    #PLACING LIMIT ON NUMBER OF ITERATIONS DUE TO RANDOMNESS OF FUNCTION
    while(counter<limit):
        counter+=1

        #FOR EVERY CACHE
        for i in range(0,caches):
            
            #RANDOMISE OUR FILE INSERT POSITION
            randomFile = randint(0,files-1)
            
            #RANDOM NUMBER OF INSERTS SET ABOVE - UP TO MAX 1/3 FILES PER CACHESIZE
            for j in range(0,randomInts):
                if testMatrix[i][randomFile] == 0:
                    testMatrix[i][randomFile] = 1
                else:
                    testMatrix[i][randomFile] = 0
                
        if fitness(testMatrix) != -1:
            overallMatrix.append(testMatrix)
            overallScores.append(fitness(testMatrix))

    print("===================================================")  
    print("Random Search Algorithm Completed.")
    print("Number of Iterations:", counter)
    
    bestScoreIndex = overallScores.index(max(overallScores))
    if len(overallScores) > 0: 
        print("Best Score:", max(overallScores))
        print("Best Matrix Looks as follows:")
        print(overallMatrix[bestScoreIndex])
        print("===================================================")
        print()
        return overallMatrix[bestScoreIndex]
    else:
        print("Failed to find score above 0. Try Again.")
        print("===================================================")
        print()
        return"No Valid Solution"
    
def simulatedAnnealing(matrix,data):
    '''focuses on immediate neighbouring solutions. Repeats 2/3rds of the overall filesize.
    returns best scoring Matrix'''
    
    caches = len(matrix)
    files = len(matrix[0])
    randomInts = int(files*0.3)
    basicArray = [[0]*files for caches in range(3)]
    basicArrayTest = []
    neighbourArray = []
    bestMatrices = []
    bestScores = []
    condition = True
    counter = 0
    maxIterations = int(files*0.6)
    
    #STAGE 1 - GENERATE RANDOM SOLUTION
    while(condition):
    
        #FOR EVERY CACHE
        for i in range(0,caches):
            #RANDOMISE OUR FILE INSERT POSITION
            randomFile = randint(0,files-1)
            
            #RANDOM NUMBER OF INSERTS SET ABOVE - UP TO MAX 1/3 FILES PER CACHESIZE
            for j in range(0,randomInts):
                basicArrayTest = deepcopy(basicArray)
                if basicArrayTest[i][randomFile] == 0:
                    basicArrayTest[i][randomFile] = 1
                else:
                    basicArrayTest[i][randomFile] = 0
                 
        if fitness(basicArrayTest) != -1:
            basicArray = deepcopy(basicArrayTest)
            condition = False
            
    #STAGE 2 - GENERATE SCORE OF GENERATED SOLUTION
    initialScore = fitness(basicArray)
    #print("Initial Random Array Fitness:",initialScore)
    
    
    #next few sections will keep looping until a max threshold is hit...
    
    while(counter<maxIterations):
        counter+=1
        #STAGE 3 - GENERATE RANDOM NEIGHBOUR SOLUTION
        neighbourArray = deepcopy(basicArray)
        neighbourArrayTest = deepcopy(neighbourArray)
        
        condition=True
        while(condition):
        
            #FOR EVERY CACHE
            for i in range(0,caches):
                #RANDOMISE OUR FILE INSERT POSITION
                randomFile = randint(0,files-1)
                
                #RANDOM NUMBER OF INSERTS SET ABOVE - UP TO MAX 1/3 FILES PER CACHESIZE
                for j in range(0,randomInts):
                    if neighbourArrayTest[i][randomFile] == 0:
                        neighbourArrayTest[i][randomFile] = 1
                    else:
                        neighbourArrayTest[i][randomFile] = 0
                     
            if fitness(neighbourArrayTest) != -1:
                condition = False
                neighbourArray = deepcopy(neighbourArrayTest)
        
        #STAGE 4 - GENERATE SCORE OF NEIGHBOUR SOLUTION
        neighbourScore = fitness(neighbourArray)
        #print("Neighbour Array Fitness:", neighbourScore)
        
        #STAGE 5 - if our new score is higher make that our main array
        #if the new score isn't higher keep it anyway, might be useful
        if neighbourScore > initialScore:
            basicArray = neighbourArray
            bestMatrices.append(basicArray)
            bestScores.append(fitness(basicArray))
        else:
            bestMatrices.append(basicArray)
            bestScores.append(fitness(basicArray))
    
    
    bestScoreIndex = bestScores.index(max(bestScores))
    print("===================================================")  
    print("Simulated Annealing Algorithm Complete.")
    print("Number of Iterations:", counter)
    print("Highest Score:", max(bestScores))
    print("Best Matrix Looks as follows:")
    print(bestMatrices[bestScoreIndex])
    print("===================================================")
    print()
    
    return bestMatrices[bestScoreIndex]
    
if __name__ == "__main__":
        
    data = read_google("input/hashcodesample.in")
    matrixRows = data["number_of_caches"]
    matrixCols = data["number_of_videos"]
    matrix = createMatrixArray(matrixRows,matrixCols)
    emptyTest = matrix
    matrixTest = [[0,0,1,0,0],[0,1,0,1,0],[1,1,0,0,0]] #should be score of 462,500 with fitness function
    brokenTest = [[1,1,1,1,1],[0,1,0,1,0],[1,1,0,0,0]]

    print("Test Matrix Fitness Score:", fitness(matrixTest), "\n")
    hillClimbing(matrixTest,data)
    geneticAlgorithm(matrixTest, data)
    randomSearch(emptyTest,data)
    simulatedAnnealing(matrixTest, data)