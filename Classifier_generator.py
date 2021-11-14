import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import f1_score, accuracy_score
import pickle

dataset = pd.read_csv('spam_ham_dataset.csv')
x_train, x_test, y_train, y_test = train_test_split(dataset['text'],
                                                    dataset['label_num'], test_size=0.2, random_state=1)

vectorizer = CountVectorizer()
x_train_new = vectorizer.fit_transform(x_train.values)
text = 'распродажа на алиеэкспресс'


classifier = MultinomialNB()
classifier.fit(x_train_new, y_train)


with open('classifier.pkl', 'wb') as file:
    pickle.dump(classifier, file)
with open('vectorizer.pkl', 'wb') as file_2:
    pickle.dump(vectorizer, file_2)
