import sys, random, os, io, json
import jsonIO #custom library


def main():

#Distinguish between OS to generate fullpath of groupstest.json, a database file to be created

    if sys.platform == 'win32' or sys.platform == 'win64':

        localDataBasePath = os.path.dirname(os.path.realpath(__file__)) + "\\" + "groups.json"

    else:

        localDataBasePath = os.path.dirname(os.path.realpath(__file__)) + "/groups.json"


    #commandLineOptions =
    if "--jsonFilePath" in sys.argv:
        localDataBasePath = sys.argv[sys.argv.index("--jsonFilePath") + 1]

    if "--maxIterations" in sys.argv:
        giveUp = int(sys.argv[sys.argv.index("--maxIterations") + 1])
    else:
        giveUp = 10000

    numberOfCycles = 1

    if "--arity" in sys.argv:
        requestedArity = int(sys.argv[sys.argv.index("--arity") + 1])
    else:
        requestedArity = 4

    if "--genA" in sys.argv:
        rawInput = list(sys.argv[sys.argv.index("--genA") + 1])
        #07/03/2021: added logic to parse multi-digit numbers in input list
        #The following is used to parse command-line input
        # to be more accepting of different ways of conveying
        # a list of ints:
        genA = []
        ind = 0
        while ind < len(rawInput):
            if isInt(rawInput[ind]):
                this_num = rawInput[ind]
                ind += 1
                while ind < len(rawInput) and isInt(rawInput[ind]):
                    this_num += rawInput[ind]
                    ind += 1
                genA.append(int(this_num))
            ind += 1
        print("chosen genA:", genA)
    else:
        genA = createShuffledElement(requestedArity)


    if "--genB" in sys.argv:

        rawInput = list(sys.argv[sys.argv.index("--genB") + 1])
        #07/03/2021: added logic to parse multi-digit numbers in input list
        #The following is used to parse command-line input
        # to be more accepting of different ways of conveying
        # a list of ints:
        genB = []
        ind = 0
        while ind < len(rawInput):
            if isInt(rawInput[ind]):
                this_num = rawInput[ind]
                ind += 1
                while ind < len(rawInput) and isInt(rawInput[ind]):
                    this_num += rawInput[ind]
                    ind += 1
                genB.append(int(this_num))
            ind += 1
            print("chosen genB:", genB)
    else:

        genB = createShuffledElement(requestedArity)


    if "--cyclicGroupMode" in sys.argv:

        cyclicGroupModeON = True
    else:
        cyclicGroupModeON = False

    print("localDataBasePath:", localDataBasePath)

    if cyclicGroupModeON == True:
        #Mode for calculating the order of cyclic groups
        #and saving them to a database

        cyclicGroupDatabase = CyclicGroupDatabase(localDataBasePath)

        #Calculate giveUp number of cyclic group orders
        for index in [*range(numberOfCycles)]:
            cyclicGroupDatabase.exponentiateElement(createShuffledElement(requestedArity))
            jsonIO.exportCacheFile(localDataBasePath, cyclicGroupDatabase.cyclicGroupDict)


    else:
        #This next variable is the initial condition hopper set for the
        # recursive class method crossIterate(hopperSet)
        initialHopper = {unnamedIteratorFunction(genA, genB)}
        print("initialHopper", initialHopper)
        print("genA:",genA)
        print("genB:",genB)
        #Instantiate a DynamicGroupDatabase object to load data from json file and store it.
        #The last two parameters of constructor of this object are really just for if
        # you have to end the program before reaching the desired max iterations.
        groupyGroup = DynamicGroupDatabase(localDataBasePath, genA, genB, giveUp, set(), set())

        #Now, actually generate the group (or at least as much of it
        groupyGroup.crossIterate(groupyGroup.hopperSet)
        # as can be done within giveUp number of iterations)
        #Finally, update the dictionary containing

        # all the class variables to contain the generated elements
        # and save the updated dictionary into a json file:
        groupyGroup.updateGroupDict()
        jsonIO.exportCacheFile(localDataBasePath, groupyGroup.groupDictFromJson)

def isInt(x):
    try:
        int(x)
    except:
        return False
    return True


def createShuffledElement(n):



    ourElement = [*range(n)]

    random.shuffle(ourElement)

    return tuple(ourElement)


def unnamedIteratorFunction(mapping, inputTuple):

    outList = []
    print("inputTuple:",inputTuple)
    inputList = list(inputTuple)
    print("inputList",inputList)
    print("mapping",mapping)
    for index in range(len(mapping)):

        outList.append(inputList[mapping[index]])

        print("outlist at index", index,":",outList)

    #Returns a tuple for so that these elements can be hashed,
    #so that we can make sets of them:
    print("tuple returned from unnamedIteratorFuction, line 55:", tuple(outList), ".")
    return tuple(outList)


def iterateTheIterator(originalList):

    gencount = 0

    generations = []

    generations.append(originalList)

    generations.append(originalList)

    appropriateIdentity = tuple([*range(len(originalList))])



    while gencount < giveUp:

        gencount += 1

        nextgen = unnamedIteratorFunction(

            generations[gencount],

            generations[0]

        )

        print("generations list at line 73:", generations)

        print(nextgen)

        generations.append(nextgen)

        if nextgen == appropriateIdentity:

            # success

            generations.remove(generations[0])

            print("Found identity element in", gencount, "steps from", generations[0], "and", generations[1])

            print("generations returned on line 80:", generations)

            return generations



    print("Failed to find identity element within", gencount, "steps from", generations[0], "and", generations[1])




def jsonFileExists(jsonFilePath):
    #This function returns true if a json file exists at the path name
    # specified (the if statement evaluates to true in this case, and false otherwise)
    #  (note that os.path.isfile() and os.access() both return true or false)
    return os.path.isfile(jsonFilePath) and os.access(jsonFilePath, os.R_OK)


def crossIterate(generator1, generator2, hopperSet, mainSet,
        jsonFilePath,iterationCount,maxIterations):

    #recursive function to generate groups from 2 elements
    nextHopperSet = {}
    iterations = interationCount
    for element in hopperSet:
        A = unnamedIteratorFunction(generator1, element)
        B = unnamedIteratorFunction(generator2, element)
        if A not in mainSet:
            nextHopperSet.add(A)
            mainSet.add(B)
        if B not in mainSet:
            nextHopperSet.add(B)
            mainSet.add(B)
        if len(nextHopperSet) != 0 and interations < maxIterations:
            crossIterate(generator1, generator2, nextHopperSet, mainSet,jsonFile)

class DynamicGroupDatabase:
    #This class is used to simplify the in-program storage of
    #group data from a json file, with included variables to store
    #data that needs to be remembered through potentially multiple
    #sessions of reading to and writing from the same json file.
    #Data is stored in the json file as a dictionary to make it easy to
    #store and access multiple variables.

    def __init__(self, jsonFileIn,
            desiredGenA, desiredGenB, maxIterations,
            desiredMainSet, desiredHopperSet):
        #check to see if json file exists, otherwise safely create one
        #in the folder specified by desiredFilePath, with the name
        #specified by desiredFileName
        if jsonFileExists(jsonFileIn):
            #the json file must be formatted as a dictionary with
            #the following keys: generatorA, generatorB, mainSet, hopperSet
            #, currentIterations
            self.groupDictFromJson = jsonIO.importCacheFile(jsonFileIn)
            keyList = self.groupDictFromJson.keys()
            if "generatorA" in keyList:
                self.generatorA = self.groupDictFromJson["generatorA"]
                print("genA from file:", self.generatorA)
            else:
                self.generatorA = desiredGenA
            if "generatorB" in keyList:
                self.generatorB = self.groupDictFromJson["generatorB"]
                print("genB from file:", self.generatorB)
            else:
                self.generatorB = desiredGenB
            if "mainSet" in keyList:
                #Sets do not serialize to json files,
                #so we convert into a set for speedy membership checking
                #We must convert to a tuple first so  it can be hashed for the set
                self.mainSet = set(tuple(tuple(element) for element in self.groupDictFromJson["mainSet"]))
            else:
                self.mainSet = desiredMainSet
            if "hopperSet" in keyList:
                self.hopperSet = set(tuple(tuple(element) for element in self.groupDictFromJson["hopperSet"]))
            else:
                self.hopperSet = {unnamedIteratorFunction(self.generatorA,self.generatorB)}
                print("groupyGroup.hopperSet:", self.hopperSet)
            self.currentIterations = 0

        else:
            with io.open(jsonFileIn,'w') as jsonFile:
                self.currentJsonFile = jsonFile
                #Put the empty set in new json file to prevent a json null error
                json.dump("{}",jsonFile)
            self.generatorA = desiredGenA
            self.generatorB = desiredGenB
            self.mainSet = desiredMainSet
            self.hopperSet = {unnamedIteratorFunction(self.generatorA,self.generatorB)}
            print("groupyGroup.hopperSet:",self.hopperSet)
            self.currentIterations = 0

        self.maxIterations = maxIterations

    def crossIterate(self,hopperSet):
    #Function to do the legwork of generating groups from two elements.
    #A class method is used here to make the persistence of the generators and
    #mainSet cleaner and easier to work with.
        nextHopperSet = hopperSet
        while len(nextHopperSet) != 0 and self.currentIterations < self.maxIterations:
            #Initialize nextHopperSet to the empty set.
            #Note that the set() function is used because {} produces
            #an empty dictionary.
            self.hopperSet = nextHopperSet
            nextHopperSet = set()
            for element in self.hopperSet:
                A = unnamedIteratorFunction(self.generatorA, element)
                print("A:", A)
                B = unnamedIteratorFunction(self.generatorB, element)
                print("B:", B)
                if A not in self.mainSet:
                    nextHopperSet.add(A)
                    print("nextHopperSet:", nextHopperSet)
                    self.mainSet.add(A)
                if B not in self.mainSet:
                    nextHopperSet.add(B)
                    print("nextHopperSet:", nextHopperSet)
                    self.mainSet.add(B)
                self.currentIterations = self.currentIterations + 1
                print("nextHopperSet:", nextHopperSet, "len(nextHopperSet:", len(nextHopperSet))

    def updateGroupDict(self):
        #Setter method to update the dictionary holding object variables,
        # converting sets into lists for json serialization:
        self.groupDictFromJson = {"generatorA" : self.generatorA , "generatorB" : self.generatorB ,
                "mainSet" : list(self.mainSet) , "hopperSet" : list(self.hopperSet) ,
                "currentIterations" : self.currentIterations, "mainSetCardinality" : len(self.mainSet) }

class CyclicGroupDatabase:

#This class is for a database of cyclic groups
# that can be used as generating sets for groups

    def __init__(self, jsonFile):
        #Check to see if named json file exists, if so import
        # its contained list of cyclic groups to cyclicGroupDict
        # if not, initialize cyclicGroupDict to the empty dictionary.
        if jsonFileExists(jsonFile):
            #the json file must be formatted as a dictionary with
            #the following keys: generatorA, generatorB, mainSet, hopperSet
            #, currentIterations
            self.cyclicGroupDict = jsonIO.importCacheFile(jsonFile)
        else:
            with io.open(jsonFile,'w') as jsonFile:
                self.currentJsonFile = jsonFile
                #Put the empty set in new json file to prevent a json null error
                json.dump({},jsonFile)
            self.cyclicGroupDict = {}


    def exponentiateElement(self, elementIn):
        #This function exponentiates an element
        # until reaching the identity element,
        # in order to get the order of the cyclic group
        # associated with that element
        # allowing us to find factors of the order to exponentiate that element by to hopefully form shorter cycles
        completeGroupList = iterateTheIterator(elementIn)
        print("completeGroupList:", completeGroupList)
        fullOrder = len(completeGroupList)
        elementInLengthIdentity = tuple([*range(len(elementIn))])
        cycleDict = {}
        nextGen =  elementIn
        #The order is equal to the number of times we've iterated,
        # i.e. the exponent we've raised elementIn to
        print("Start Exponeniation")
        print(nextGen)
        for element in completeGroupList:
            order = 1
            nextGen = element
            while nextGen !=  elementInLengthIdentity and order < giveUp:
                nextGen = unnamedIteratorFunction(element, nextGen)
                print(nextGen)
                order = order + 1
        #cyclicGroupDict is setup as a dictionary with keys
        # indexing the cardinality of the contained cyclic groups
        # and values that are dictionaries containing element:order
        # key:value pairs
        #The str() function is used because integers get dumped to
        # json files as strings
            cycleDict[str(element)] = order
        print("cycleDict for", elementIn, ":", cycleDict)
        if str(len(elementIn)) not in self.cyclicGroupDict.keys():
            self.cyclicGroupDict[str(len(elementIn))] = {}
        self.cyclicGroupDict[str(len(elementIn))][str(cycleDict)] = str(completeGroupList)


if __name__ == '__main__':
    main()

