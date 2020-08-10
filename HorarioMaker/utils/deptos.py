#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Scrap Departamentos from https://ucampus.uchile.cl/m/fcfm_catalogo/
Save to json file
"""

import json
import requests
from bs4 import BeautifulSoup

def rm_ws(string: str) -> str:
    """
    Remove all extra whitespaces characters

    Get rid of space, tab, newline, return, formfeed
    """
    return ' '.join(string.split())

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

deptolist = []
namelist = []
prefixlist = []
diclist = []
dicc = {}

deptos = soup.find_all(name='select', id='depto')
for depto in deptos:
    for option in depto.find_all(name='option'):
        deptolist.append(option.get('value'))
        name = rm_ws(option.find(text=True, recursive=False))
        prefixlist.append(name[:2])
        namelist.append(name[5:])

for i in range(len(deptolist)):
    dic = {
        deptolist[i]:{
            'prefix':prefixlist[i],
            'name':namelist[i]
            }
        }
    diclist.append(dic)

dicc = {'depto':[dic for dic in diclist]}

with open(file='deptos.json', mode='w', encoding='utf8') as file:
    json.dump(obj=dicc, fp=file, ensure_ascii=False, indent=4)