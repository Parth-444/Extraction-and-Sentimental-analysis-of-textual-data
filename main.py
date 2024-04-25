import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

df = pd.read_excel('Input.xlsx')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}

for i in range(0, df.shape[0]):
    link = df.iloc[i, 1]
    webpage = requests.get(link,headers=headers).text
    soup = BeautifulSoup(webpage, 'lxml')
    try:
        heading = soup.find('h1', class_='entry-title').text
        content = soup.find('div', class_='td-post-content tagdiv-type').text
    except Exception as e:
        print(e)
    with open(f'{df.iloc[i, 0]}.txt', "w") as f:
        f.writelines(heading)
        f.writelines(content)
        if i > 1:
            break

for i in range(0, df.shape[0]):
    with open(f'{df.iloc[i, 0]}.txt') as f:
        page = f.readlines()
        page = [i.lower() for i in page]
    df1 = pd.DataFrame(page)
    df1.rename(columns={0: 'lines'}, inplace=True)

    df1['lines'] = df1['lines'].str.strip()

    # this is for removing empty lines
    empty_lines = df1[df1['lines'] == '']
    df1 = df1.drop(empty_lines.index).reset_index().drop(columns='index')

    # expanding abbreviations
    import re


    def remove_abb(data):
        data = re.sub(r'\b\d{4}\b', '', data)
        data = re.sub(r',', '', data)
        data = re.sub(r'[:\-–\.]', '', data)

        return data


    df1['lines'] = df1['lines'].apply(remove_abb)

    # removing punctutation
    import string


    def remove_punctuation(text):
        for i in string.punctuation:
            if i in text:
                text.replace(i, '')
        return text


    df1['lines'] = df1['lines'].apply(remove_punctuation)

    # creating tokens

    def tokenize(data):
        data = word_tokenize(data)
        return data


    df1['lines'] = df1['lines'].apply(tokenize)

    # removing stop words
    def remove_stopwords(text):
        L = []
        for word in text:
            if word not in stopwords.words('english'):
                L.append(word)
        return L


    df1['lines'] = df1['lines'].apply(remove_stopwords)

    # sentiment analysis

    with open('negative-words.txt', 'r', encoding='utf-8', errors='ignore') as f:
        l = f.readlines()
        l = [i.strip() for i in l]
        neg = np.array(l)
    with open('positive-words.txt', encoding='utf-8', errors='ignore') as f:
        l = f.readlines()
        l = [i.strip() for i in l]
        pos = np.array(l)
    # positive words and negative words array.

    def check(word_list):
        pos_count = 0
        neg_count = 0
        for word in word_list:
            if word in pos:
                pos_count += 1
            elif word in neg:
                neg_count += 1
        return neg_count, pos_count


    df1['lines'].apply(check)