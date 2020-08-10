#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

url = 'https://ucampus.uchile.cl/m/fcfm_catalogo/'

payload = {
    'semestre': '20202', # 2020 Primavera
    'depto': '21' # MA - Departamento de Ingenería Matemática
    }

headers = {
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 RuxitSynthetic/1.0 v5937104183 t38550 ath9b965f92 altpub'
}

response = requests.get(url=url, params=payload, headers=headers)

html_doc = response.content

soup = BeautifulSoup(markup=html_doc, features='html.parser')

with open(file='catalogo.html', mode='wb') as file:
    file.write(soup.prettify(encoding='utf-8', formatter='minimal'))