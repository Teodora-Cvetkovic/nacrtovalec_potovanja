import datetime

class Potovanje:
    def __init__(self, mesto, drzava, datum_od, datum_do, budzet):
        self.mesto = mesto
        self.drzava = drzava
        self.datum_od = datum_od
        self.datum_do = datum_do
        self.budzet = budzet
        self.lokacije = [(self.mesto, self.drzava)]
        self.datumi = [(str(self.datum_od), str(self.datum_do))]
        self.denar = [budzet]
        self.potovanja_po_datumih = {(self.datum_od, self.datum_do): (self.mesto, self.drzava, self.budzet)}

    def __str__(self):
        return f'Planiram potovanje v/na {self.mesto}, {self.drzava}. Potoval/a bom {self.datum_od} in se bom vrnil/a {self.datum_do}. Pričakujem, da bom porabil/a {self.buzet}€'

    def __repr__(self):
        return f'Potovanje({self.mesto}, {self.drzava}, {self.datum_od}, {self.datum_do}, {self.budzet})'

    def dodaj_lokacijo(self, mesto, drzava):
        with open('drzave.txt', 'r', encoding='utf-8') as dat_drzave:
            seznam_drzav = [vrstica.strip() for vrstica in dat_drzave]
        if drzava not in seznam_drzav:
            raise ValueError('Država s tim imenom ne obstaja!')
        self.lokacije.append((mesto, drzava))

    def obrisi_lokacijo(self, mesto, drzava):
        with open('drzave.txt', 'r', encoding='utf-8') as dat_drzave:
            seznam_drzav = [vrstica.strip() for vrstica in dat_drzave]
        if drzava not in seznam_drzav:
            raise ValueError('Država s tim imenom ne obstaja!')
        elif (mesto, drzava) not in self.lokacije:
            raise ValueError('Tista lokacija ni že shranjena!')
        self.lokacije.remove((mesto, drzava))


    def _preveri_datum(self, datum_od, datum_do):
        for i in range(len(self.datumi)):
            if str(datum_od) in self.datumi[i] or str(datum_do) in self.datumi[i]:
                raise ValueError('Takrat že potojete!')

    def _preveri_cas(self, datum_od, datum_do):
        for i in range(len(self.datumi)):
            novi_od = datetime.datetime.strptime(self.datumi[i][0], '%Y-%m-%d')
            novi_do = datetime.datetime.strptime(self.datumi[i][1], '%Y-%m-%d')
            t = novi_do - novi_od
            if str(datum_od) == str(novi_od + t):
                raise ValueError('Takrat ste že na potovanju!')

    def dodaj_cas(self, datum_od, datum_do):
        self._preveri_datum(datum_od, datum_do)
        self._preveri_cas(datum_od, datum_do)
        self.datumi.append((str(datum_od), str(datum_do)))

    def obrisi_cas(self, datum_od, datum_do):
        if (str(datum_od), str(datum_do)) not in self.datumi:
            raise ValueError('Takrat še nimate planiranega potovanje!')
        self.datumi.remove((str(datum_od), str(datum_do)))

    def dodaj_budzet(self, budzet):
        if budzet < 0:
            raise ValueError('Budžet ne sme biti manjši od 0 €!')
        self.denar.append(budzet)

    def obrisi_buzet(self, budzet):
        if budzet not in self.denar:
            raise ValueError('Tisti budžet ni še dodan!')
        self.denar.remove(budzet)