import seaborn as sns
from scipy.stats.mstats import ttest_ind
from path import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MAP = {
    'asdf7023random': 'A',
    'asdf7023movefreq': 'B',
    'asdf7023moveco': 'C',
    'asdf7023pokefreq': 'D',
}

def get_frequencies():
    directory = Path("../")
    freqs = {}
    for folder in directory.listdir():
        if "asdf7023" not in folder:
            continue
        if str(folder.name) not in freqs:
            freqs[str(folder.name)] = {}
        for subfolder in folder.listdir():
            score = 0
            total = 0
            if "ladder" in subfolder:
                continue
            for file in subfolder.listdir():
                if "score" not in file.name:
                    continue
                with open(file, 'r') as fp:
                    scores = fp.read().split("\n")
                    s = float(scores[0])
                    t = float(scores[1])
                    score += s
                    total += t
            freqs[str(folder.name)] = 1 - score / total
    return freqs

def get_ratings():
    directory = Path("../")
    ladders = {}
    for folder in directory.listdir():
        ladder = []
        if "asdf7023" not in folder:
            continue
        for subfolder in folder.listdir():
            if "ladder" not in subfolder:
                continue
            with open(subfolder, 'r') as f:
                ladder = f.read().split("\n")
                if '' in ladder:
                    ladder.remove('')
                ladder = ladder[:201]
            ladders[str(folder.name)] = ladder
    return ladders

def graph_frequencies(freqs):
    plt.figure()
    classifiers = []
    errors = []
    width = 0.43       # the width of the bars
    ind = list(map(lambda x: x+width, xrange(4)))  # the x locations for the groups
    for classifier in sorted(MAP.items(), key=lambda x: x[1]):
        print classifier
        classifiers.append(classifier[0])
        errors.append(freqs[classifier[0]])
    plt.xlabel('Classifiers')
    plt.ylabel('Prediction Error Rate')
    plt.xticks(list(map(lambda x: x+width, ind)), ("A", "B", "C", "D"))
    plt.title('Error Rate of Move Classifiers')
    plt.bar(ind, errors)
    plt.savefig('error.png')

def graph_ratings(rating_dict):
    plt.figure()
    labels = ['A', 'B', 'C', 'D']
    for classifier in sorted(MAP.items(), key=lambda x: x[1]):
        print classifier
        rating_list = rating_dict[classifier[0]]
        rating_list = map(int, rating_list)
        rating_list = [1000] + rating_list
        plt.plot(range(len(rating_list)), rating_list, label="Bot " + MAP[classifier[0]])
    plt.xlabel('Number of Games')
    plt.ylabel('Ladder Ratings')
    plt.title('Ladder Ratings of Move Classifiers')
    plt.legend(loc='best')
    plt.savefig('ratings.png')

def ttest(rating1, rating2):
    return ttest_ind(rating1, rating2)

if __name__ == "__main__":
    freqs = get_frequencies()
    ratings = get_ratings()
    rating1 = map(int, ratings['asdf7023pokefreq'])[1:]
    boxplot(rating1)
    #rating2 = map(int, ratings['asdf7023moveco'])[1:]
    #rating3 = map(int, ratings['asdf7023movefreq'])[1:]
    #rating4 = map(int, ratings['asdf7023random'])[1:]
    graph_frequencies(freqs)
    print freqs
    ##print rating1, rating2
    #_, p = ttest_ind(rating1, rating4)
    #print p
    graph_ratings(ratings)
    #for rating in [rating1, rating2, rating3, rating4]:
        #s = pd.Series(rating)
        #print s.describe()
