# Import všech potřebných knihoven
import sys
import requests
import bs4
import csv


# Hlavní funkce, která vše spustí
def main():
    url = sys.argv[1]
    nazev = sys.argv[2]
    try:
        stahovani(url, nazev)
    except:
        print("CHYBA V ARGUMENTECH, UKONČUJI APLIKACI.")
        quit()


# Spuštění jednotlivých funkcí
def stahovani(url, nazev):
    odpoved = requests.get(url)
    print("STAHUJI DATA Z VYBRANÉHO URL: ", url)
    polevka = bs4.BeautifulSoup(odpoved.text, "html.parser")
    kod_obce(polevka)
    obce(polevka)
    nove_url = novy_link(polevka)
    prohledavani_obci(nove_url)
    print("UKLÁDÁM DO SOUBORU: ", nazev)
    vytvor_tabulku(polevka, nove_url, nazev)
    print("HOTOVO, UKONČUJI APLIKACI")


# Získávání dat z celého okresu - kód obce a jméno

def kod_obce(polevka):
    pol_kody = polevka.find_all("td", {"class": "cislo"})
    list_kodu = []
    for kod in pol_kody:
        list_kodu.append(kod.find("a").text)
    return list_kodu


def obce(polevka):
    pol_obce = polevka.find_all("td", {"class": "overflow_name"})
    list_obci = []
    for obec in pol_obce:
        list_obci.append(obec.text)
    return list_obci


# Vyhledávání linků pro jednotlivé obce

def link_obce(polevka):
    vsechny_url = polevka.find_all("a")
    cast_url = []
    for cista_url in vsechny_url:
        cista_url = (cista_url.get("href"))
        if "ps311" in cista_url:
            if cista_url not in cast_url:
                cast_url.append(cista_url)
    return cast_url


def novy_link(polevka):
    start = "https://volby.cz/pls/ps2017nss/"
    list_url = []
    cast_url = link_obce(polevka)
    for nova_url in cast_url:
        nova_url = start + nova_url
        list_url.append(nova_url)
    return list_url


# Vyhledávání informací v jednotlivých obcích
def hlasy(polevka2):
    volici = polevka2.find("td", headers="sa2").text
    vydane_obalky = polevka2.find("td", headers="sa3").text
    platne_hlasy = polevka2.find("td", headers="sa6").text
    hlasy_stran = []
    for h_stran in polevka2.find_all("td", headers="t1sa2 t1sb3"):
        hlasy_stran.append(h_stran.text)
    return volici, vydane_obalky, platne_hlasy, *hlasy_stran


def strany(polevka2):
    jmena_stran = []
    for j_stran in polevka2.find_all("td", headers="t1sa1 t1sb2"):
        jmena_stran.append(j_stran.text)
    return jmena_stran


def prohledavani_obci(nove_url):
    list1 = []
    list2 = []
    for i in nove_url:
        odpoved2 = requests.get(i)
        polevka2 = bs4.BeautifulSoup(odpoved2.text, "html.parser")
        list1.append(hlasy(polevka2))
        list2 = strany(polevka2)
    return list1, list2


def f_text(polevka, nove_url):
    ko = kod_obce(polevka)
    no = obce(polevka)
    po = prohledavani_obci(nove_url)[0]
    radky = []
    for i in range(len(ko)):
        radek = ko[i], no[i], *po[i]
        radky.append(radek)
    return radky


# Vytváření CSV tabulky
def vytvor_tabulku(polevka, nove_url, nazev):
    js = prohledavani_obci(nove_url)[1]
    hlavicka = ["kod_obce", "nazev_obce", "volici", "vydane_obalky", "platne_hlasy", *js]
    text = list(f_text(polevka, nove_url))

    report = open(nazev, "w", newline="")
    report_writer = csv.writer(report)
    report_writer.writerow(hlavicka)
    report_writer.writerows(text)
    report.close()


if __name__ == "__main__":
    main()

    
