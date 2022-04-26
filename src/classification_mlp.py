#!/usr/bin/env python3

from utils import read_pickle, save_json
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from random import shuffle
from collections import defaultdict
from argparse import ArgumentParser

args = ArgumentParser()
args.add_argument("-d", "--data", default="data/CoLA_BERT.pkl")
args.add_argument("-n", "--name", default="CoLA_BERT")
args = args.parse_args()

data = read_pickle(args.data)

logdata = defaultdict(lambda: defaultdict(list))

for mode in ["pooler", "cls", "mean", "haddamard", "sum"]:
    print(mode)

    layer_generator = range(12) if mode != "pooler" else [0]

    for layer in layer_generator:
        for rstate in range(8):
            model = MLPClassifier(
                random_state=rstate,
                hidden_layer_sizes=(100,),
                early_stopping=True
            )

            if mode == "pooler":
                data_x = [x[mode] for x in data]
            else:
                data_x = [x[mode][layer] for x in data]

            data_x = StandardScaler().fit_transform(data_x)
            # data_y = [x["amb"] for x in data]
            data_y = [x["class"] for x in data]

            data_x_train, data_x_test, data_y_train, data_y_test = train_test_split(
                data_x, data_y, test_size=100, shuffle=True, random_state=0,
            )

            model.fit(data_x_train, data_y_train)
            score_train = model.score(data_x_train, data_y_train)
            score_test = model.score(data_x_test, data_y_test)

            print(
                f"Layer {layer} accuracy:\ttrain: {score_train:.2%}, test: {score_test:.2%}"
            )

            logdata[mode][layer].append((score_train, score_test))


save_json(f"computed/mpl_{args.name}.json", logdata)
