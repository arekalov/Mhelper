import spacy


def ner_predict(text):
    nlp = spacy.load("ru_core_news_sm")  # Подгрузка модели для работы с NER на русском
    dict = {}
    doc2 = nlp(text)  # Сегментация и токенизация текста

    for ent in doc2.ents:
        if ent.label_ in dict.keys():
            dict[ent.label_].append(ent.text)
        else:
            dict[ent.label_] = [ent.text]

    new_dict = {}  # Сбор тегов в словарь по методанным
    for key in dict.keys():
        if key == 'ORG':
            new_dict['ORGANIZATION'] = dict[key]
        elif key == 'GPE':
            new_dict['LOCATION'] = dict[key]
        elif key == 'DATE':
            new_dict['DATE'] = dict[key]
        elif key == 'MONEY':
            new_dict['MONEY'] = dict[key]
        elif key == 'PER':
            new_dict['PERSON'] = dict[key]
    return new_dict  # Передача словаря с токенами и тегами

