import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def main() -> None:
    print("hello")

    data = pd.read_csv(filepath_or_buffer="snack_500_rev_5.csv", header=None, sep=";") #salad_500
    trainSet = []

    # Make the trainset starting from dataset (& data adjustments)
    for index, row in data.iterrows():
        dish = row[5] #ingredients field
        dish = dish.lower()  # lower case

        dish1 = ""
        for elem in dish:
            if elem != " ":
                dish1 += elem  # in order to remove spaces

        dish = ["".join(dish1)]  # put all ingredients into a string containing comma sparated elements(ingredients)
        trainSet += dish  # add string to list train set

    print("Train set \n\n", trainSet)

    vectorizer = TfidfVectorizer()  # transform foods in vectors

    # TF-IDF to detect importance of ingredients in foods (TF = Term frequency, IDF = Inverse Document Frequency)
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    matrix = vectorizer.fit_transform(trainSet)
    print("MATRICE VECTORIZER \n\n\n\n",matrix)
    print("\n\n\nSHAPE:::::::", matrix.shape)

    matrix_dense = matrix.todense()
    print("DENSE \n\n", matrix_dense)
    print(matrix_dense.shape)

    print("INGR NAMES::::::::::::", vectorizer.get_feature_names_out())

    #SAVE TFIDF SCORES MATRIX INTO A CSV FILE
    np.savetxt("tfIdfMenuSnack500.csv", matrix_dense, delimiter=",", fmt="%.5f")
    np.savetxt("tfIdfIngredientsNamesSnack500.txt", vectorizer.get_feature_names_out(), delimiter=" ", fmt="%s")
    np.savetxt("tfIdfDishesNamesSnack500.txt", data.iloc[:,3], delimiter=" ", fmt="%s")

    cosineSim = cosine_similarity(matrix_dense, matrix_dense)
    print(cosineSim)


    #import matplotlib.pyplot as plt

    #labels = data.iloc[:,3]
    #fig, ax = plt.subplots(figsize=(500, 500))
    #cax = ax.matshow(cosineSim, interpolation='nearest')
    #ax.grid(True)
    ## plt.title('Original 20 dishes Cosine Similarity Matrix')
    #print("\n\n\n\n Cosine Similarity matrix of Item profiles + User profile (last row) \n\n")
    #plt.xticks(range(500), labels, rotation=90);
    #plt.yticks(range(500), labels);
    #fig.colorbar(cax, ticks=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, .75, .8, .85, .90, .95, 1])
    #plt.show()
if __name__ == '__main__':
    main()