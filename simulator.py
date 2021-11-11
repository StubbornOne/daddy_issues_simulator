from primarchs import *
from combat import *
import os
import sys
import argparse

def crunch(samples, MODE_CHARGE):
    print("Simulating %d duels between each primarch" % samples)
    numPrimarchs = len(primarch_names)
    crunch_results = [[[0,0,0] for i in range(numPrimarchs)] for i in range(numPrimarchs)]
    if not os.path.exists("results"):
        os.mkdir("results")
    stdout = sys.stdout
    for i in range(numPrimarchs - 1):
        for j in range(i+1, numPrimarchs):
            #print(primarch_names[i], primarch_names[j])
            for x in range(1, samples+1):
                primarchA = createPrimarchFromName(primarch_names[i])
                primarchB = createPrimarchFromName(primarch_names[j])
                os.chdir("results")
                #sys.stdout = open("%s_vs_%s_%d.txt" % (type(primarchA).__name__, type(primarchB).__name__,x),"w+")
                sys.stdout = open(os.devnull, 'w')
                result = duel(primarchA, primarchB, MODE_CHARGE)
                sys.stdout.close()
                sys.stdout = stdout
                if result == 2:
                    crunch_results[i][j][result] += 1
                    crunch_results[j][i][result] += 1
                else:
                    crunch_results[i][j][result] += 1
                    crunch_results[j][i][1-result] += 1
                os.chdir("..")
    for i in range(numPrimarchs):
        for j in range(numPrimarchs):
            if i != j:
                wins = crunch_results[i][j][0]
                losses = crunch_results[i][j][1]
                if wins > losses:
                    winner = primarch_names[i]
                    ratio = 100 * wins/(wins+losses)
                elif losses > wins:
                    winner = primarch_names[j]
                    ratio = 100 * losses/(wins+losses)
                else:
                    winner = "Tie"
                    ratio = 100* wins/(wins+losses)
                print("%s vs %s: %s %s (%.1f)" % (primarch_names[i], primarch_names[j], str(crunch_results[i][j]), winner, ratio))
    absolute_score(crunch_results, samples)
    scaled_score(crunch_results, samples)

def absolute_score(crunch_results,samples=1000):
    print("\n1V1 counts (>50% = win):")
    numPrimarchs = len(primarch_names)
    scores = [0 for i in range(numPrimarchs)]
    for i in range(numPrimarchs):
        #for j in range(numPrimarchs):
        for j in range(18):
            if i != j:
                wins, loss, ties = crunch_results[i][j]
                if wins > loss:
                    scores[i] += 1
    results = list(zip(scores,primarch_names))
    results.sort(key=lambda x: x[0],reverse=True)
    for i in range(numPrimarchs):
        print("%s (%d)" % (results[i][1], results[i][0]))

def scaled_score(crunch_results,samples=1000):
    print("\nPercentage win of all battles:")
    numPrimarchs = len(primarch_names)
    scores = [0 for i in range(numPrimarchs)]
    for i in range(numPrimarchs):
        #for j in range(numPrimarchs):
        for j in range(18):
            if i != j:
                wins, loss, ties = crunch_results[i][j]
                ratio = float(wins)/samples
                scores[i] += ratio
        #scores[i] /= (numPrimarchs-1)
        scores[i] /= 17
    results = list(zip(scores,primarch_names))
    results.sort(key=lambda x: x[0],reverse=True)
    for i in range(numPrimarchs):
        print("%s (%.1f)" % (results[i][1], results[i][0]*100))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--crunch', action='store', type=int, nargs=1, help='crunch [num_samples_per_pairing]')
    group.add_argument('--duel', action='store', type=str,nargs=2, help='duel primarch1 primarch2')

    parser.add_argument('-c', '--charge', dest='charge', action='store_true', help='Use charge, H&R, Overwatch, shooting')

    args = parser.parse_args()

    #global VERBOSE
    
    if args.crunch != None:
        crunch(args.crunch[0], args.charge)
    elif args.duel != None:
        if args.duel[0] not in primarch_names:
            print("Please choose from: %s" % str(primarch_names))
        elif args.duel[1] not in primarch_names:
            print("Please choose from: %s" % str(primarch_names))
        else:
            duel(createPrimarchFromName(args.duel[0]),createPrimarchFromName(args.duel[1]), args.charge)
