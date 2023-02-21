import numpy as np
import argparse
from copy import deepcopy
from collections import defaultdict
from ast import literal_eval as make_tuple
import re
class Stack:
     def __init__(self):
         self.items = []

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def peek(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)

     def print_stack(self):
        print(self.items)
class AFD:
    def __init__(self):
        self.initialState = None
        self.states = set()
        self.lang = [] #lenguaje o alfabeto
        self.nfaStates = dict()
        self.finalState = []
        self.transitions = []

    def display(self):
        print ("Estados: ", self.states)
        print ("Estado Inicial: ", self.initialState)
        print ("Lenguaje: ", self.lang)
        print ("Estados AFN: ", self.nfaStates)
        print ("Estado final: ", self.finalState)
        print ("Transiciones: ", self.transitions)
class AFN:
    def __init__(self):
        self.initialState = None
        self.states = set()
        self.lang = []
        self.finalState = None
        self.transitions = []

    def display(self):
        print ("Estados: ", self.states)
        print ("Estado inicial: ", self.initialState)
        print ("Lenguaje: ", self.lang)
        print ("Estado final: ", self.finalState)
        print ("Transiciones: ", self.transitions)

def readInput(path):
    #poner nombre de archivo
    input = open('resultadoAFN.txt', 'r')
    input = input.read().splitlines()
    afn = AFN()
    afn.states = input[0].split(',')
    #agarra lo que esta dentro de las llaves {}
    result = re.search(r"\{(.*?)\}", input[1])
    afn.lang = result.group(1).split(',')
    #print(result.group(1))
    #print(afn.lang)
    afn.initialState = input[2]
    afn.finalState = input[3].split(',')
    transitions = input[4].replace("},{","|").replace("},  {","|").replace("}, {","|")
    # print('alo')
    # print(transitions)
    transitions = transitions.split('|')
    transitions[0] = transitions[0].strip('{')
    transitions[-1] = transitions[-2].strip('}')

    
    for transition in transitions:
        
        transition = transition.split(',')
        
        if(transition[1] != ' '):
            transition[1] = transition[1].strip(' ')
            #print(transition)
        transition[2] = transition[2].strip(' ')
        afn.transitions.append({
            "desde": transition[0].replace("'desde': ",""),
            "=>": transition[1].replace("'=>': ",""),
            "hacia": transition[2].replace("'hacia': ","")
        })

    #print(afn.transitions)
    #print(afn.transitions[1]['hacia'])

    # afn.display()
    
    return afn

#print(readInput())

def createHashMap(path):
    afn = readInput(path)
    hashMap = defaultdict(list)
    for transition in afn.transitions:
        if transition['=>'] == ' ':
            hashMap[transition['desde']] += [transition['hacia']]
    return hashMap,afn


def getEclosure(state,path):
    stack = Stack()
    [hashMap,_] = createHashMap(path)
    closures = list()
    closures.append(state)
    stack.push(state)
    while(not stack.isEmpty()):
        state = stack.pop()
        for eclosure in hashMap[state]:
            stack.push(eclosure)
            closures.append(eclosure)
    return closures

def initializeAFD(path):
    [hashMap, afn] = createHashMap(path)
    nfaStates = set()
    stack = Stack()
    afd = AFD()
    afd.initialState = 'A'
    afd.states.add(afd.initialState)
    stack.push(afn.initialState)
    nfaStates.add(afn.initialState)
    while(not stack.isEmpty()):
        state = stack.pop()
        for state in hashMap[state]:
            stack.push(state)
            nfaStates.add(state)
    afd.nfaStates[afd.initialState] = list(nfaStates)
    # afd.display()
    return afd,afn,hashMap

def writeOutput(afd):
    string = ""
    output = open('resultAFD.txt','w+')
    for state in sorted(afd.states):
        string+= state+', '
    output.write(string[:-2])
    output.write('\n')
    string = ""
    for lang in sorted(afd.lang):
        string += lang+', '
    output.write(string[:-2])
    output.write('\n')
    output.write(afd.initialState)
    output.write('\n')
    string = ""
    for finalstate in sorted(afd.finalState):
        string += finalstate+', '
    output.write(string[:-2])
    output.write('\n')
    string = ""
    for transition in afd.transitions:
        string+= '('+transition['desde']+', '+transition['=>']+', '+transition['hacia']+')'+', '
    output.write(string[:-2])

def toAFD(path):
    stack = Stack()
    counter = 0
    stateCounter = 0
    [afd, afn, _] = initializeAFD(path)
    if " " in afn.lang:
        afn.lang.remove(" ")
    afd.lang = afn.lang
    stack.push(afd.nfaStates[afd.initialState])
    while(not stack.isEmpty()):
        states = stack.pop()
        for lang in afn.lang:
            print("testing",lang)
            newState = list()
            for state in states:
                print(state)
                for transition in afn.transitions:
                    #print("transicion desde  ",transition['desde'])
                    print("flecha  ",transition['=>'])
                    if ( (transition['desde'] == state) and (transition['=>'] == lang) ):
                        hacia = transition['hacia']
                        # newState.append(to)
                        closures = getEclosure(hacia,path)
                        print('alo')
                        print(closures)
                        newState += closures
                        # print("newState",newState)
            if(not newState in afd.nfaStates.values()):
                print("NewState not in stack", newState)
                if(len(newState)>0):
                    afd.nfaStates[chr(ord('A')+counter+1)] = newState
                    # print(afd.nfaStates)
                    stack.push(newState)
                    # print("pushed",newState)
                    afd.states.add(chr(ord('A')+counter+1))
                    afd.transitions.append({
                        "desde": chr(ord('A')+stateCounter),
                        "=>": lang,
                        "hacia": chr(ord('A')+counter+1)
                    })

                    counter += 1
                #SE EJECUTA CUANDO NO ECUENTRA LO QUE NECESITA
                else:
                    if(['ERROR'] in afd.nfaStates.values()):
                        afd.transitions.append({
                            "desde": chr(ord('A')+stateCounter),
                            "=>": lang,
                            "hacia": 'ERROR'
                        })
                    else:
                        afd.nfaStates['ERROR'] = ['ERROR']
                        afd.states.add('ERROR')
                        afd.transitions.append({
                            "desde": chr(ord('A')+stateCounter),
                            "=>": lang,
                            "hacia": 'ERROR'
                        })
            else:
                afd.transitions.append({
                    "desde": chr(ord('A')+stateCounter),
                    "=>": lang,
                    "hacia": afd.nfaStates.keys()[afd.nfaStates.values().index(newState)]
                })
                # ------------------------------------
                # print("transition",afd.transitions)
        stateCounter += 1
    for state in afd.nfaStates.values():
        # print(afn.finalState[0])
        if(afn.finalState[0] in state):
            # print(state)
            afd.finalState.append(afd.nfaStates.keys()[afd.nfaStates.values().index(state)])
    writeOutput(afd)
    afd.display()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')

    parser.add_argument('--file', action="store", help="path of file to take as input", nargs="?",metavar="file")

    args = parser.parse_args()
    toAFD(args.file)