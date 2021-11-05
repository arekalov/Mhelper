import spacy


def ner_predict(text):
    nlp = spacy.load("ru_core_news_sm")
    dict = {}
    doc2 = nlp(text)

    for ent in doc2.ents:
        if ent.label_ in dict.keys():
            dict[ent.label_].append(ent.text)
        else:
            dict[ent.label_] = [ent.text]
    new_dict = {}
    for key in dict.keys():
        if key == 'ORG':
            new_dict['ORGANIZATION'] = dict[key]
        elif key == 'GPE':
            new_dict['LOCATION'] = dict[key]
        elif key == 'DATE':
            new_dict['DATE'] = dict[key]
        elif key == 'MONEY':
            new_dict['MONEY'] = dict[key]
        elif key == 'PERSON':
            new_dict['PERSON'] = dict[key]
    json_final = []
    index = 0
    offset_counter = 0
    for key in new_dict.keys():
        for i in new_dict[key]:
            json_final.append({'text': i, 'tag': key, 'tokens': []})
            for j in i.split():
                json_final[index]['tokens'].append({'text': j, 'ofset': offset_counter})
                offset_counter += len(j)
            index += 1

    return ({'facts': json_final})


print(ner_predict('''Добрый день, Николай Васильевич!
Прошу предоставить информацию о товаре “Компьютер Apple iMac 21.5 MC309” под кодовым наименованием AMC0039281 в вашем прайс-листе. В письме, прошу изложить подробные технические характеристики и конкурентные преимущества в сравнении с аналогичными моделями других производителей.
На основании ответного письма и заключения технического отдела, нашей организацией будет принято решение о закупке партии компьютеров в количестве 50 шт. Будем рады рассмотреть Ваши предложения о скидках или бонусных программах, предоставляемых в рамках нашего дальнейшего сотрудничества.

---
С уважением,
Егоров Андрей Николаевич
начальник службы технической поддержки
ЗАО “Информационные системы”
тел. (423) 89-64-78'''))
