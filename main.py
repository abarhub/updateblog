import argparse
import ast
import json
from pathlib import Path

import requests

argParser = argparse.ArgumentParser()
argParser.add_argument("-u", "--url_gist_root")
argParser.add_argument("-r", "--rep")
argParser.add_argument("-d", "--date_min")
argParser.add_argument("-g", "--gist_a_ignorer")

args = argParser.parse_args()

url_gist_root = args.url_gist_root

rep = args.rep
date_min = args.date_min

appel_web = False
update = False

gist_a_ignorer = args.gist_a_ignorer
file_last_call = 'lastcall.json'


class Gist:
    def __init__(self, url, date_creation, date_modification, filename, url_file, description):
        self.url = url
        self.date_creation = date_creation
        self.date_modification = date_modification
        self.filename = filename
        self.url_file = url_file
        self.description = description


def convertie(gist):
    filename = list(gist['files'].keys())[0]
    file = gist['files'][filename]['raw_url']
    print("tmp:'" + gist['url'] + "',create:" + gist['created_at'] + ",updated:" + gist[
        'updated_at'] + ",file:" + filename)
    tmp2 = Gist(gist['url'], gist['created_at'], gist['updated_at'], filename, file, gist['description'])
    return tmp2


def parse(s):
    # res = json.loads(s)
    res = ast.literal_eval(s)

    # print(f"res={res}")

    liste = []
    for tmp in res:
        tmp2 = convertie(tmp)
        liste.append(tmp2)

    return liste


def analyse(liste, gist_a_ignorer, date_min):
    nb_total = 0
    nb_ignore = 0
    nb_ajoute = 0
    nb_modifie = 0
    liste_gist_a_ignorer = gist_a_ignorer.split(',')
    liste_a_modifier = []
    for tmp in liste:
        nb_total += 1
        d = tmp.date_modification
        f = tmp.filename
        f2 = f
        if not f2.endswith('.md'):
            f2 += '.md'
        if d > date_min and not (f in liste_gist_a_ignorer):
            my_file = Path(f"{rep}/{f2}")
            if my_file.is_file():
                print(f"file '{f2}' exists")
                nb_ignore += 1
                nb_modifie += 1
                liste_a_modifier.append(f)
            else:
                print(f"file '{f2}' doesn't exists")
                nb_ajoute += 1
                if update:
                    # if f=='liste_design_patern':
                    response = requests.get(tmp.url_file, stream=True)
                    # tmp3=response.raw
                    # print(f"raw:{tmp3}")
                    tmp3 = ''
                    for chunk in response.iter_content(chunk_size=128):
                        tmp3 += chunk.decode()
                    print("description=" + tmp.description)
                    print("tmp3=" + tmp3)
                    date = tmp.date_creation[0:10]
                    s = f"""+++
title = "{tmp.description}"
date = "{date}"
description = "{tmp.description}"
tags = []
summary = "{tmp.description}"
+++
{tmp3}
                    """
                    print(f"s={s}")
                    with open(f"{rep}/{f2}", "w") as f:
                        f.write(s)

        else:
            # print(f"file '{f}' ignore (date={d})")
            nb_ignore += 1

    print(f"nb total:{nb_total}")
    print(f"nb ignore:{nb_ignore}")
    print(f"nb ajoute:{nb_ajoute}")
    print(f"nb modifie:{nb_modifie}")
    print(f"a modifie:{liste_a_modifier}")


if appel_web:
    url_gist = f'{url_gist_root}?per_page=100'
    print("url:" + url_gist)
    response = requests.get(url_gist)
    print(response.json())
    liste2 = response.json()
    with open(file_last_call, "w") as f:
        f.write(str(liste2))

    liste = []
    for tmp in liste2:
        tmp2 = convertie(tmp)
        liste.append(tmp2)

else:
    with  open(file_last_call, "r") as f:
        lines = f.readlines()
    contenuFichier = ""
    for x in lines:
        contenuFichier += x

    # print(f"contenu={contenuFichier}")

    liste = parse(contenuFichier)

print(f"liste({len(liste)})={liste}")

analyse(liste, gist_a_ignorer, date_min)


def main():
    pass
