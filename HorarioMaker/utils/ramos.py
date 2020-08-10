#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import requests
import regex as re
from pathlib import Path
from bs4 import BeautifulSoup

# Tiempo total de 
# ejecución, en segundos:
# 7.151595592498779

# TODO: Arreglar ramos cuyos
# códigos no cumplen con el
# formato XX0000-0.
# Corregir ramos con código
# null pues tienen un error 
# causado por retornar None
# al intentar obtener id

def get_cwd():
    """Current working directory."""
    cwd = Path(__file__).parents[0]
    cwd = str(cwd)
    return cwd

def rm_ws(string: str) -> str:
    """
    Remove all extra whitespaces characters.

    Get rid of space, tab, newline, return, formfeed.
    """
    return ' '.join(string.split())

def get_deptocodelist() -> list:
    """Academic department codes avaiable in semester 20202"""
    with open(
        file=get_cwd()+r'\deptos.json',
        mode='r',
        encoding='utf8') as file:
        deptosdic = json.load(fp=file)
    deptocodelist = [list(list(deptosdic.values())[0][i].keys())[0] for i in range(len(list(deptosdic.values())[0]))]
    return deptocodelist

def get_ramos(semester: str = '20202') -> dict:
    """
    Get every available course at FCFM for a given semester

    :param semester: Since 2013, semesters follow the
     regular expression 'year+season'. Year is any integer between
     2013 and 2020. Season is 1 for autumn, 2 for spring and 3 for
     summer when possible.

    :return: TODO
    """

    url = 'https://ucampus.uchile.cl/m/fcfm_catalogo/'

    deptodic = {} # Departamentos
    for depto in get_deptocodelist():

        # Accionar según documentación
        # de módulo requests para
        # web scraping

        payload = {
            'semestre': f'{semester}',
            'depto': f'{depto}'
            }
        headers = {
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 RuxitSynthetic/1.0 v5937104183 t38550 ath9b965f92 altpub'
        }

        response = requests.get(url=url, params=payload, headers=headers)

        # Ver documentación
        # del módulo bs4

        html_doc = response.content

        soup = BeautifulSoup(markup=html_doc, features='html.parser')

        ramos = soup.find_all(name='div', class_='ramo')
        ramosdic = {} # Ramos
        codelist = [] # Códigos
        namelist = [] # Nombres
        proglist = [] # Programas
        credlist = [] # Créditos
        reqlist = [] # Requisitos
        eqlist = [] # Equivalencias
        comlist = [] # Comentarios

        for ramo in ramos:
            for h2 in ramo.find_all(name='h2'):

                # TODO corregir error de h2 sin id, pero sí tiene
                try:
                    codelist.append(rm_ws(h2.get('id')))
                except:
                    codelist.append(None)
                namelist.append(rm_ws(h2.find(text=True, recursive=False))[7:])

                # Un ramo no necesariamente
                # tiene todos los atributos

                try:
                    proglist.append(ramo.find(name='dl').find(name='dd').find(name='a')['href'])
                except:
                    proglist.append(None)
                
                try:
                    credlist.append(ramo.find(name='dt', text='Créditos').find_next(name='dd').text)
                except:
                    credlist.append(None)

                try:
                    reqlist.append(ramo.find(name='dt', text='Requisitos').find_next(name='dd').text)
                except:
                    reqlist.append(None)

                try:
                    eqlist.append(ramo.find(name='dt', text='Equivalencias').find_next(name='dd').text)
                except:
                    eqlist.append(None)

                try:
                    comlist.append(ramo.find(name='dt', text='Comentario').find_next(name='dd').text)
                except:
                    comlist.append(None)
                
                secdic = {} # Secciones
                secnum = '' # Número de sección
                secname = '' # Sección nombre completo
                cupo = '' # Cupo de la sección
                ocupados = '' # Cupos ocupados

                for sec in ramo.find(name='tbody').find_all(name='tr'):

                    secnum = re.findall(r'%s(\d+)' % '-',sec.get('id'))[0]
                    secname = rm_ws(sec.find(name='td').find(name='h1').text)

                    proflist = [] # Profes de la sección

                    for profes in sec.find(name='td').find_all(name='ul', class_='profes'):
                        for profe in profes.find_all(name='img'):

                            proflist.append(rm_ws(profe.find_next(text=True)))

                    cupo = rm_ws(sec.find_all(name='td')[1].text)
                    ocupados = rm_ws(sec.find_all(name='td')[2].text)

                    horario = {} # Horario
                    catdic = {} # Cátedras
                    auxdic = {} # Auxiliares
                    labdic = {} # Laboratorios
                    condic = {} # Controles

                    horario = sec.find_all(name='td')[3]
                    horario = str(horario).replace('<td>','').replace('</td>','').split('<br/>')

                    for tpclase in horario: # Tipo de clase

                        # Hay clases de bloques simples
                        # y clases de bloques dobles.
                        # Los bloques no necesariamente
                        # corresponden a un módulo
                        # (organización de la docencia FCFM).
                        # Simples son de la forma
                        # Día + HoraInicial + '-' + HoraFinal.
                        # Dobles son de la forma anterior
                        # (largo 4) sumado a solamente
                        # HoraInicial + '-' + HoraFinal (3).
                        # Lo anterior es para casos especiales
                        # como una clase de dos módulos
                        # consecutivos pero separados
                        # por el almuerzo

                        if 'Cátedra: ' in tpclase:
                            cats = tpclase.replace('Cátedra: ', '').split(', ')
                            for i in range(len(cats)):
                                if len(cats[i].split(' ')) == 4:
                                    catday,cati,g,catf = cats[i].split(' ')
                                    catdic[catday] = [[cati,catf]]
                                elif len(cats[i].split(' ')) == 3:
                                    cati,g,catf = cats[i].split(' ')
                                    catdic[cats[i-1].split(' ')[0]] = [cats[i-1].split(' ')[0][0], [cati,catf]]
            
                        elif 'Auxiliar: ' in tpclase:
                            auxs = tpclase.replace('Auxiliar: ', '').split(', ')
                            for i in range(len(auxs)):
                                if len(auxs[i].split(' ')) == 4:
                                    auxday,auxi,g,auxf = auxs[i].split(' ')
                                    auxdic[auxday] = [[auxi,auxf]]
                                elif len(auxs[i].split(' ')) == 3:
                                    auxi,g,auxf = auxs[i].split(' ')
                                    auxdic[auxs[i-1].split(' ')[0]] = [auxs[i-1].split(' ')[0][0],[auxi,auxf]]

                        elif 'Laboratorio: ' in tpclase:
                            labs = tpclase.replace('Laboratorio: ', '').split(', ')
                            for i in range(len(labs)):
                                if len(labs[i].split(' ')) == 4:
                                    labday,labi,g,labf = labs[i].split(' ')
                                    labdic[labday] = [[labi,labf]]
                                elif len(labs[i].split(' ')) == 3:
                                    labi,g,labf = labs[i].split(' ')
                                    labdic[labs[i-1].split(' ')[0]] = [labs[i-1].split(' ')[0][0],[labi,labf]]
                        
                        elif 'Control: ' in tpclase:
                            cons = tpclase.replace('Control: ', '').split(', ')
                            for i in range(len(cons)):
                                if len(cons[i].splot(' ')) == 4:
                                    conday,coni,g,conf = cons[i].spit(' ')
                                    condic[conday] = [[coni,conf]]
                                elif len(cons[i].splot(' ')) == 3:
                                    coni,g,conf = cons[i].spit(' ')
                                    condic[cons[i-1].splot(' ')[0]] = [cons[i-1].splot(' ')[0][0], [coni,conf]]

                    horario = {
                        'Cátedra': catdic,
                        'Auxiliar': auxdic,
                        'Laboratorio': labdic,
                        'Control': condic
                    }

                    secdic[secnum] = {
                        'profe':proflist,
                        'cupo':cupo,
                        'ocupado':ocupados,
                        'horario':horario
                    }

                ramosdic[codelist[-1]] = {
                    'nombre':namelist[-1],
                    'programa':proglist[-1],
                    'crédito':credlist[-1],
                    'requisito':reqlist[-1],
                    'equivalencia':eqlist[-1],
                    'comentario':comlist[-1],
                    'sección':secdic
                }
        
        deptodic[depto] = {'ramo':ramosdic}
    
    return {'depto':deptodic}

if __name__ == "__main__":
    with open(file='catalogo.json', mode='w',encoding='utf8') as file:
        json.dump(obj=get_ramos(), fp=file, ensure_ascii=False, indent=4)