import pickle
import googletrans


def get_category(text):
    file = open('classifier.pkl', 'rb')  # Подгружаем модель баесовского классификатора
    model = pickle.load(file)
    file_2 = open('vectorizer.pkl', 'rb')  # Подгружаем векторайзер для преобразования текста в вектор тегов
    vect = pickle.load(file_2)
    file.close()
    file_2.close()

    translator = googletrans.Translator()  # Используем переводчик на английский для корректной работы
    translation = translator.translate(text, dest='en').text
    new_text = vect.transform([translation])  # Предсказыванием категорию текста
    return model.predict(new_text)[0]  # Передаем класс предсказания
