import pickle
import googletrans
from sklearn.feature_extraction.text import CountVectorizer


def get_category(text):
    file = open('classifier.pkl', 'rb')
    model = pickle.load(file)
    file_2 = open('vectorizer.pkl', 'rb')
    vect = pickle.load(file_2)
    file.close()
    file_2.close()

    translator = googletrans.Translator()
    translation = translator.translate(text, dest='en').text
    new_text = vect.transform([translation])
    return model.predict(new_text)[0]

print(get_category('Реклама'))
