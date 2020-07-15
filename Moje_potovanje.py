import datetime
from model import Potovanje, Uporabniki
import os
import random
import hashlib
import bottle


uporabniki = {}
skrivnost = 'UPORABLJAJ MOŽGAN'


for ime_datoteke in os.listdir('uporabniki'):
    uporabnik = Uporabniki.nalozi_evidenco(os.path.join('uporabniki', ime_datoteke))
    uporabniki[uporabnik.uporabnisko_ime] = uporabnik

def poisci_potovanje(polje_od):
    datum_od = bottle.request.forms.getunicode(polje_od)
    potovanje = potovanja_uporabnika()
    return potovanje.poisci_potovanje(datum_od)

def poisci_evidenco(polje_od):
    datum_od = bottle.request.forms.getunicode(polje_od)
    potovanje = potovanja_uporabnika()
    return potovanje.poisci_evidenco(datum_od)

def poisci_najljubso_lokacijo(polje_mesto):
    mesto = bottle.request.forms.getunicode(polje_mesto)
    potovanje = potovanja_uporabnika()
    return potovanje.poisci_najljubso_lokacijo(mesto)

def poisci_zeljo(polje_mesto):
    mesto = bottle.request.forms.getunicode(polje_mesto)
    potovanje = potovanja_uporabnika()
    return potovanje.poisci_zeljo(mesto)

def trenutni_uporabnik():
    uporabnisko_ime = bottle.request.get_cookie('uporabnisko_ime', secret=skrivnost)
    if uporabnisko_ime is None:
        bottle.redirect('/prijava/')
    return uporabniki[uporabnisko_ime]

def potovanja_uporabnika():
    return trenutni_uporabnik().potovanje

def shrani_trenutnega_uporabnika():
    uporabnik = trenutni_uporabnik()
    uporabnik.shrani_evidenco(os.path.join('uporabniki', f'{uporabnik.uporabnisko_ime}.json'))

@bottle.get('/')
def zacetna_stran():
    bottle.redirect('/planiranje/')

@bottle.get('/planiranje/')
def planiranje_potovanja():
    potovanje = potovanja_uporabnika()
    return bottle.template('plan.html', potovanje=potovanje)

@bottle.get('/evidenca/')
def evidenca():
    potovanje = potovanja_uporabnika()
    return bottle.template('evidenca.html', potovanje=potovanje)

@bottle.get('/zelje/')
def evidenca():
    potovanje = potovanja_uporabnika()
    return bottle.template('lista_zelja.html', potovanje=potovanje)

@bottle.get('/pomoc/')
def pomoc():
    return bottle.template('pomoc.html')

@bottle.get('/prijava/')
def prijava_get():
    return bottle.template('prijava.html')

@bottle.post('/prijava/')
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode('uporabnisko_ime')
    geslo = bottle.request.forms.getunicode('geslo')
    h = hashlib.blake2b()
    h.update(geslo.encode(encoding='utf-8'))
    zasifrirano_geslo = h.hexdigest()
    if 'nov_plan' in bottle.request.forms and uporabnisko_ime not in uporabniki:
        mesto = bottle.request.forms.getunicode('mesto')
        drzava = bottle.request.forms.getunicode('drzava')
        datum_od = bottle.request.forms.getunicode('datum_od')
        datum_do = bottle.request.forms.getunicode('datum_do')
        budzet = int(bottle.request.forms.getunicode('budzet'))
        potovanje = Potovanje(mesto, drzava, datum_od, datum_do, budzet)
        uporabnik = Uporabniki(uporabnisko_ime, zasifrirano_geslo, potovanje)
        uporabniki[uporabnisko_ime] = uporabnik
        uporabnik.shrani_evidenco(f'{uporabnik.uporabnisko_ime}.json')
    else:
        uporabnik = uporabniki[uporabnisko_ime]
        uporabnik.preveri_geslo(zasifrirano_geslo)
    bottle.response.set_cookie('uporabnisko_ime', uporabnik.uporabnisko_ime, path='/', secret=skrivnost)
    bottle.redirect('/')

@bottle.post('/odjava/')
def odjava():
    bottle.response.delete_cookie('uporabnisko_ime', path='/')
    bottle.redirect('/')

@bottle.post('/dodaj-potovanje/')
def dodaj_potovanje():
    potovanje = potovanja_uporabnika()
    mesto = bottle.request.forms.getunicode('mesto')
    drzava = bottle.request.forms.getunicode('drzava')
    datum_od = bottle.request.forms.getunicode('datum_od')
    datum_do = bottle.request.forms.getunicode('datum_do')
    budzet = int(bottle.request.forms.getunicode('budzet'))
    potovanje.dodaj_potovanje(mesto, drzava, datum_od, datum_do, budzet)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/')

@bottle.post('/dodaj-v-seznam-zelja/')
def dodaj_zeljo():
    potovanje = potovanja_uporabnika()
    mesto = bottle.request.forms.getunicode('mesto')
    drzava = bottle.request.forms.getunicode('drzava')
    potovanje.dodaj_zeljo(mesto, drzava)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/zelje/')

@bottle.post('/dodaj-v-evidenco/')
def dodaj_evidenco():
    potovanje = potovanja_uporabnika()
    mesto = bottle.request.forms.getunicode('mesto')
    drzava = bottle.request.forms.getunicode('drzava')
    datum_od = bottle.request.forms.getunicode('datum_od')
    datum_do = bottle.request.forms.getunicode('datum_do')
    budzet = int(bottle.request.forms.getunicode('budzet'))
    potovanje.dodaj_evidenco(mesto, drzava, datum_od, datum_do, budzet)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/evidenca/')

@bottle.post('/dodaj-najljubso-lokacijo/')
def dodaj_najljubso_lokacijo():
    potovanje = potovanja_uporabnika()
    mesto = bottle.request.forms.getunicode('mesto_lj')
    drzava = bottle.request.forms.getunicode('drzava_lj')
    potovanje.dodaj_najljubso_lokacijo(mesto, drzava)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/zelje/')

@bottle.post('/obrisi-potovanje/')
def obrisi_potovanje():
    potovanje = potovanja_uporabnika()
    pot = poisci_potovanje('polje_od')
    mesto = pot[0]
    drzava = pot[1]
    datum_od = pot[2]
    datum_do = pot[3]
    budzet = pot[4]
    potovanje.obrisi_potovanje(mesto, drzava, datum_od, datum_do, budzet)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/')

@bottle.post('/obrisi-zeljo/')
def obrisi_zeljo():
    potovanje = potovanja_uporabnika()
    zelja = poisci_zeljo('z_mesto')
    mesto = zelja[0]
    drzava = zelja[1]
    potovanje.obrisi_zeljo(mesto, drzava)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/zelje/')

@bottle.post('/obrisi-najljubso-lokacijo/')
def obrisi_lokacijo():
    potovanje = potovanja_uporabnika()
    lokacija = poisci_najljubso_lokacijo('l_mesto')
    mesto = lokacija[0]
    drzava = lokacija[1]
    potovanje.obrisi_najljubso_lokacijo(mesto, drzava)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/zelje/')

@bottle.post('/obrisi-evidenco/')
def obriisi_evidenco():
    potovanje = potovanja_uporabnika()
    obisk = poisci_evidenco('polje_od')
    mesto = obisk[0]
    drzava = obisk[1]
    datum_od = obisk[2]
    datum_do = obisk[3]
    budzet = obisk[4]
    potovanje.obrisi_evidenco(mesto, drzava, datum_od, datum_do, budzet)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/evidenca/')

@bottle.post('/premakni-potovanje/')
def iz_pot_v_ev():
    potovanje = potovanja_uporabnika()
    datum = bottle.request.forms.get('premakni_od')
    potovanje.iz_potovanja_v_evidenco(datum)
    shrani_trenutnega_uporabnika()
    bottle.redirect('/')


bottle.run(reloader=True, debug=True)