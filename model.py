import datetime
import json



class Uporabniki:
    def __init__(self, uporabnisko_ime, geslo, potovanje):
        self.uporabnisko_ime = uporabnisko_ime
        self.geslo = geslo
        self.potovanje = potovanje

    def preveri_geslo(self, geslo):
        if self.geslo != geslo:
            raise ValueError('Geslo je napačno!')

    def shrani_evidenco(self, ime_datoteke):
        slovar_evidence = {
            'uporabnisko_ime': self.uporabnisko_ime,
            'geslo': self.geslo,
            'evidenca': self.potovanje.slovar_s_pregledom(),
        }
        with open(ime_datoteke, 'w', encoding='utf-8') as datoteka:
            json.dump(slovar_evidence, datoteka, ensure_ascii=False, indent=4)

    @classmethod
    def nalozi_evidenco(cls, ime_datoteke):
        with open(ime_datoteke, 'r', encoding='utf-8') as datoteka:
            slovar_evidence = json.load(datoteka)
        uporabnisko_ime = slovar_evidence['uporabnisko_ime']
        geslo = slovar_evidence['geslo']
        potovanje = Potovanje.nalozi_iz_slovarja(slovar_evidence['evidenca'])
        return cls(uporabnisko_ime, geslo, potovanje)



class Potovanje:
    def __init__(self, mesto, drzava, datum_od, datum_do, budzet=0):
        self.mesto = mesto
        self.drzava = drzava
        self.datum_od = datum_od
        self.datum_do = datum_do
        self.budzet = budzet
        self.lokacije = [(self.mesto, self.drzava)]
        self.datumi = [(str(self.datum_od), str(self.datum_do))]
        self.denar = [budzet]
        self.potovanja = [(self.mesto, self.drzava, str(self.datum_od), str(self.datum_do), self.budzet)]
        self.potovanja_po_datumih = {(str(self.datum_od), str(self.datum_do)): (self.mesto, self.drzava, self.budzet)}
        self.najljubse_lokacije = []
        self.slo_najljubse_lokacije = {}
        self.ze_obiskano = []
        self.ze_obiskane_lokacije = []
        self.obiskano_po_datumih = {}
        self.seznam_zelja = []
        self._potovanja_po_datumu_od = {self.datum_od: (self.mesto, self.drzava, self.datum_od, self.datum_do, self.budzet)}
        self._evidence_po_datumu_od = {}
        self._lokacije_po_mestih = {}
        self._zelje_po_mestih = {}

    def __str__(self):
        return f'Planiram potovanje v/na {self.mesto}, {self.drzava}. Potoval/a bom {self.datum_od} in se bom vrnil/a {self.datum_do}. Pričakujem, da bom porabil/a {self.buzet}€'

    def __repr__(self):
        return f'Potovanje({self.mesto}, {self.drzava}, {self.datum_od}, {self.datum_do}, {self.budzet})'

    def _preveri_drzavo(self, drzava):
        with open('drzave.txt', 'r', encoding='utf-8') as dat_drzave:
            seznam_drzav = [vrstica.strip() for vrstica in dat_drzave]
        if drzava not in seznam_drzav:
            raise ValueError(f'{drzava} ne obstaja!')

    def dodaj_lokacijo(self, mesto, drzava):
        self._preveri_drzavo(drzava)
        self.lokacije.append((mesto, drzava))

    def obrisi_lokacijo(self, mesto, drzava):
        self._preveri_drzavo(drzava)
        if (mesto, drzava) not in self.lokacije:
            raise ValueError(f'Lokacija {mesto}, {drzava} ni že shranjena!')
        self.lokacije.remove((mesto, drzava))

    def dodaj_najljubso_lokacijo(self, mesto, drzava):
        self._preveri_drzavo(drzava)
        if mesto in self.najljubse_lokacije:
            raise ValueError(f'Lokacija {mesto}, {drzava} je že dodana v najljubše lokacije!')
        self.slo_najljubse_lokacije[mesto] = drzava
        self.najljubse_lokacije.append((mesto, drzava))
        self._lokacije_po_mestih[mesto] = (mesto, drzava)

    def obrisi_najljubso_lokacijo(self, mesto, drzava):
        self._preveri_drzavo(drzava)
        if (mesto, drzava) not in self.najljubse_lokacije:
            raise ValueError(f'Lokacija {mesto}, {drzava} ni še dodana v najljubše lokacije!')
        self.slo_najljubse_lokacije.pop(mesto)
        self.najljubse_lokacije.remove((mesto, drzava))
        self._lokacije_po_mestih.pop(mesto)

    def _preveri_datum(self, datum_od, datum_do):
        for i in range(len(self.datumi)):
            if str(datum_od) in self.datumi[i] or str(datum_do) in self.datumi[i]:
                raise ValueError('Takrat že potojete!')
        if datum_do < datum_od:
            raise ValueError('Pozor! Datum vrnitve je prej datuma odlaska!')

    def dodaj_cas(self, datum_od, datum_do):
        self._preveri_datum(datum_od, datum_do)
        self.datumi.append((str(datum_od), str(datum_do)))

    def obrisi_cas(self, datum_od, datum_do):
        if (str(datum_od), str(datum_do)) not in self.datumi:
            raise ValueError('Takrat še nimate planiranega potovanja!')
        self.datumi.remove((str(datum_od), str(datum_do)))

    def dodaj_budzet(self, budzet):
        if budzet < 0:
            raise ValueError('Budžet ne sme biti manjši od 0 €!')
        self.denar.append(budzet)

    def obrisi_buzet(self, budzet):
        if budzet not in self.denar:
            raise ValueError('Tisti budžet ni še dodan!')
        self.denar.remove(budzet)

    def dodaj_potovanje(self, mesto, drzava, datum_od, datum_do, budzet=0):
        self.dodaj_lokacijo(mesto, drzava)
        self.dodaj_cas(datum_od, datum_do)
        self.dodaj_budzet(budzet)
        self.potovanja.append((mesto, drzava, str(datum_od), str(datum_do), budzet))
        self.potovanja_po_datumih[(str(datum_od), str(datum_do))] = (mesto, drzava, budzet)
        self._potovanja_po_datumu_od[datum_od] = (mesto, drzava, datum_od, datum_do, budzet)

    def obrisi_potovanje(self, mesto, drzava, datum_od, datum_do, budzet=0):
        self.obrisi_lokacijo(mesto, drzava)
        self.obrisi_cas(datum_od, datum_do)
        self.obrisi_buzet(budzet)
        self.potovanja.remove((mesto, drzava, str(datum_od), str(datum_do), budzet))
        self.potovanja_po_datumih.pop((str(datum_od), str(datum_do)))
        self._potovanja_po_datumu_od.pop(datum_od)

    def dodaj_evidenco(self, mesto, drzava, datum_od, datum_do, budzet=0):
        self._preveri_drzavo(drzava)
        self.ze_obiskane_lokacije.append((mesto, drzava))
        self.ze_obiskano.append((mesto, drzava, str(datum_od), str(datum_do), budzet))
        self.obiskano_po_datumih[(str(datum_od), str(datum_do))] = (mesto, drzava, budzet)
        self._evidence_po_datumu_od[datum_od] = (mesto, drzava, datum_od, datum_do, budzet)

    def obrisi_evidenco(self, mesto, drzava, datum_od, datum_do, budzet=0):
        self._preveri_drzavo(drzava)
        if (mesto, drzava) not in self.ze_obiskane_lokacije:
            raise ValueError(f'Lokacija {mesto}, {drzava} še ni obiskana!')
        self.ze_obiskane_lokacije.remove((mesto, drzava))
        self.ze_obiskano.remove((mesto, drzava, str(datum_od), str(datum_do), budzet))
        self.obiskano_po_datumih.pop((str(datum_od), str(datum_do)))
        self._evidence_po_datumu_od.pop(datum_od)
        if (mesto, drzava) in self.najljubse_lokacije:
            self.obrisi_najljubso_lokacijo(mesto, drzava)

    def dodaj_zeljo(self, mesto, drzava):
        self._preveri_drzavo(drzava)
        if (mesto, drzava) in self.seznam_zelja:
            raise ValueError(f'Destinacija {mesto}, {drzava} je že dodana v vaš seznam želja!')
        elif (mesto, drzava) in self.ze_obiskane_lokacije:
            raise ValueError(f'Lokacijo {mesto}, {drzava} ste že obiskali!')
        self.seznam_zelja.append((mesto, drzava))
        self._zelje_po_mestih[mesto] = (mesto, drzava)

    def obrisi_zeljo(self, mesto, drzava):
        self._preveri_drzavo(drzava)
        if (mesto, drzava) not in self.seznam_zelja:
            raise ValueError(f'Željo {mesto}, {drzava} še niste dodali v seznam želja!')
        self.seznam_zelja.remove((mesto, drzava))
        self._zelje_po_mestih.pop(mesto)

    def poisci_potovanje(self, datum_od):
        return self._potovanja_po_datumu_od[datum_od]

    def poisci_evidenco(self, datum_od):
        return self._evidence_po_datumu_od[datum_od]

    def poisci_najljubso_lokacijo(self, mesto):
        return self._lokacije_po_mestih[mesto]

    def poisci_zeljo(self, mesto):
        return self._zelje_po_mestih[mesto]

    def iz_potovanja_v_evidenco(self, datum_pot):
        pot = self.poisci_potovanje(datum_pot)
        mesto = pot[0]
        drzava = pot[1]
        datum_od = pot[2]
        datum_do = pot[3] 
        budzet = pot[4]
        self.obrisi_potovanje(mesto, drzava, datum_od, datum_do, budzet)
        self.dodaj_evidenco(mesto, drzava, datum_od, datum_do, budzet)

    def planiran_budzet_ukupno(self):
        ukupno = 0
        for n in self.denar:
            ukupno += n
        return ukupno

    def ukupno_porabljeno(self):
        ukupno = 0
        for potovanje in self.ze_obiskano:
            ukupno += potovanje[4]
        return ukupno

    def slovar_s_pregledom(self):
        return {
            'planirana potovanja': [{
                'mesto': potovanje[0],
                'drzava': potovanje[1],
                'datum odhoda': potovanje[2],
                'datum vrnitve': potovanje[3],
                'budzet': potovanje[4],
            } for potovanje in self.potovanja],
            'ze obiskano': [{
                'mesto': obiskano[0],
                'drzava': obiskano[1],
                'datum odhoda': obiskano[2],
                'datum vrnitve': obiskano[3],
                'budzet': obiskano[4],
            } for obiskano in self.ze_obiskano],
            'najljubse lokacije': [{
                'mesto': lokacija[0],
                'drzava': lokacija[1],
            } for lokacija in self.najljubse_lokacije],
            'seznam želja':[{
                'mesto': zelja[0],
                'drzava': zelja[1],
            } for zelja in self.seznam_zelja],
            
            'planirani budzet': self.planiran_budzet_ukupno(),
            'porabljen denar': self.ukupno_porabljeno(),
        }

    @classmethod
    def nalozi_iz_slovarja(cls, slovar_s_pregledom):
        mesto = slovar_s_pregledom['planirana potovanja'][0]['mesto']
        drzava = slovar_s_pregledom['planirana potovanja'][0]['drzava']
        datum_od = slovar_s_pregledom['planirana potovanja'][0]['datum odhoda']
        datum_do = slovar_s_pregledom['planirana potovanja'][0]['datum vrnitve']
        budzet = slovar_s_pregledom['planirana potovanja'][0]['budzet']
        potovanje = cls(mesto, drzava, datum_od, datum_do, budzet)
        for plan in slovar_s_pregledom['planirana potovanja'][1:]:
            nov_plan = potovanje.dodaj_potovanje(
                plan['mesto'],
                plan['drzava'],
                plan['datum odhoda'],
                plan['datum vrnitve'],
                plan['budzet']
            )
        for obisk in slovar_s_pregledom['ze obiskano']:
            nova_evidenca = potovanje.dodaj_evidenco(
                obisk['mesto'],
                obisk['drzava'],
                obisk['datum odhoda'],
                obisk['datum vrnitve'],
                obisk['budzet']
            )
        for lokacija in slovar_s_pregledom['najljubse lokacije']:
            nova_lokacija = potovanje.dodaj_najljubso_lokacijo(
                lokacija['mesto'],
                lokacija['drzava']
            )
        for zelja in slovar_s_pregledom['seznam želja']:
            nova_zelja = potovanje.dodaj_zeljo(
                zelja['mesto'],
                zelja['drzava']
            )
        return potovanje

    def shrani_potovanje(self, ime_datoteke):
        with open(ime_datoteke, 'w', encoding='utf-8') as datoteka:
            json.dump(self.slovar_s_pregledom(), datoteka, ensure_ascii=False, indent=4)

    @classmethod
    def nalozi_potovanje(cls, ime_datoteke):
        with open(ime_datoteke, 'r', encoding='utf-8') as datoteka:
            slovar_s_pregledom = json.load(datoteka)
        return cls.nalozi_iz_slovarja(slovar_s_pregledom)