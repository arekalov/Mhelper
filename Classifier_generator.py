import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import f1_score, accuracy_score
import pickle

dataset = pd.read_csv('spam_ham_dataset.csv')  # Загрузка датасета
x_train, x_test, y_train, y_test = train_test_split(dataset['text'],
                                                    dataset['label_num'], test_size=0.2, random_state=1)
# Разбиение датасета на выборки

vectorizer = CountVectorizer()  # Создание и обучения векторайзера
x_train_new = vectorizer.fit_transform(x_train.values)

classifier = MultinomialNB()  # Создание байесовского классификатора
classifier.fit(x_train_new, y_train)  # Обучение

with open('classifier.pkl', 'wb') as file:  # Сохранение классификатора
    pickle.dump(classifier, file)
with open('vectorizer.pkl', 'wb') as file_2:  # Сохранение векторайзера
    pickle.dump(vectorizer, file_2)
