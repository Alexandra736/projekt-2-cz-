# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath



# елементы

class Grzalka:
    def __init__(self):
        self.temperatura = 20.0
        self.max_temp = 100.0
        self.wlaczona = True

    def aktualizuj(self):
        if self.wlaczona and self.temperatura < self.max_temp:
            self.temperatura += 0.2
            if self.temperatura > self.max_temp:
                self.temperatura = self.max_temp


class Zbiornik:
    def __init__(self, x, y, nazwa):
        self.x = x
        self.y = y
        self.w = 80
        self.h = 120
        self.nazwa = nazwa
        self.pojemnosc = 100.0
        self.ilosc = 0.0
        self.poziom = 0.0
        self.grzalka = None

    def aktualizuj(self):
        self.poziom = self.ilosc / self.pojemnosc

    def dodaj(self, v):
        d = min(v, self.pojemnosc - self.ilosc)
        self.ilosc += d
        self.aktualizuj()
        return d

    def usun(self, v):
        d = min(v, self.ilosc)
        self.ilosc -= d
        self.aktualizuj()
        return d

    def pusty(self):
        return self.ilosc < 0.1

    def gora(self):
        return (self.x + self.w /2, self.y)

    def dol(self):
        return (self.x + self.w /2, self.y + self.h)

    def draw(self, p):
        if self.poziom > 0:
            h = int(self.h * self.poziom)
            p.setBrush(QColor(100, 150, 255, 200))
            p.setPen(Qt.NoPen)
            p.drawRect(
                int(self.x + 3),
                int(self.y + self.h - h),
                int(self.w - 6),
                int(h)
            )
        p.setPen(QPen(Qt.black, 3))
        p.setBrush(Qt.NoBrush)
        p.drawRect(self.x, self.y, self.w, self.h)
        p.drawText(self.x + 20, self.y - 5, self.nazwa)

        if self.grzalka:
            p.setPen(QPen(Qt.red, 2))
            p.drawLine(self.x + 5, self.y + self.h - 5,
                       self.x + self.w -5, self.y + self.h -5)
            p.drawText(self.x, self.y + self.h + 15, f"T={self.grzalka.temperatura:.1f} C")



class Rura:
    def __init__(self, punkty, grubosc=10):
        self.punkty = [QPointF(x, y) for x, y in punkty]
        self.grubosc = grubosc
        self.przeplyw = False

    def ustaw_przeplyw(self, stan):
        self.przeplyw = stan

    def draw(self, p):
        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for pt in self.punkty[1:]:
            path.lineTo(pt)
        p.setPen(QPen(Qt.gray, self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(path)
        if self.przeplyw:
            p.setPen(QPen(QColor(0,180,255), self.grubosc -3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawPath(path)



from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton




class RaportOkno(QWidget):
    def __init__(self, zbiorniki):
        super().__init__()
        self.setWindowTitle("Raport zbiornikow")
        self.setFixedSize(400, 300)
        self.zbiorniki = zbiorniki

        # Layout g??wny
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Nag??wek
        header = QHBoxLayout()
        header.addWidget(QLabel("Zbiornik"))
        header.addWidget(QLabel("Temperatura [C]"))
        header.addWidget(QLabel("Poziom [%]"))
        self.layout.addLayout(header)


        # Lista zbiornik?w
        self.labels = []
        for z in zbiorniki:
            hbox = QHBoxLayout()
            l_nazwa = QLabel(z.nazwa)
            l_temp = QLabel("-")
            l_poziom = QLabel("-")
            hbox.addWidget(l_nazwa)
            hbox.addWidget(l_temp)
            hbox.addWidget(l_poziom)
            self.layout.addLayout(hbox)
            self.labels.append((l_temp, l_poziom))


        # таймер ло активации
        self.timer = QTimer()
        self.timer.timeout.connect(self.aktualizuj)
        self.timer.start(200)


    def aktualizuj(self):
        for i, z in enumerate(self.zbiorniki):
            temp = f"{z.grzalka.temperatura:.1f}" if z.grzalka else "-"
            poziom = f"{z.poziom*100:.0f}"
            self.labels[i][0].setText(temp)
            self.labels[i][1].setText(poziom)






# симул€ци€

class Symulacja(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instalacja z odbiciem lustrzanym")
        self.setFixedSize(1100,600)
        self.setStyleSheet("background:#F5FFFA")


        # сосуды
        self.z1 = Zbiornik(300,50,"Z1")
        self.z2 = Zbiornik(500,50,"Z2")
        self.z3 = Zbiornik(400,250,"Z3")
        self.z4 = Zbiornik(300,450,"Z4")
        self.z5 = Zbiornik(500,450,"Z5")
        self.z4.grzalka = Grzalka()
        self.z5.grzalka = Grzalka()


        self.z1.ilosc = 100
        self.z2.ilosc = 100
        for z in [self.z1, self.z2, self.z3, self.z4, self.z5]:
            z.aktualizuj()


        self.zbiorniki = [self.z1,self.z2,self.z3,self.z4,self.z5]


        # трубы
        self.rury = [
            # верхние трубы вниз 2см
            Rura([self.z1.dol(), (self.z1.dol()[0], self.z1.dol()[1]+20)]),
            Rura([self.z2.dol(), (self.z2.dol()[0], self.z2.dol()[1]+20)]),
            # горизонтальна€ труба от Z1->Z2 (объединение)
            Rura([(self.z1.dol()[0], self.z1.dol()[1]+20), (self.z2.dol()[0], self.z2.dol()[1]+20)]),
            # вертикальные к Z3
            Rura([(self.z1.dol()[0], self.z1.dol()[1]+20), (self.z3.gora()[0], self.z1.dol()[1]+20)]),
            Rura([(self.z2.dol()[0], self.z2.dol()[1]+20), (self.z3.gora()[0], self.z2.dol()[1]+20)]),
            Rura([(self.z3.gora()[0], self.z2.dol()[1]+20), self.z3.gora()]),
            # нижние трубы Ч зеркальное отражение
            # Z3 вниз 2см
            Rura([self.z3.dol(), (self.z3.dol()[0], self.z3.dol()[1]+20)]),
            # горизонтальна€ труба 5 см влево и вправо
            Rura([(self.z3.dol()[0], self.z3.dol()[1]+20), (self.z3.dol()[0]-100, self.z3.dol()[1]+20)]),
            Rura([(self.z3.dol()[0], self.z3.dol()[1]+20), (self.z3.dol()[0]+100, self.z3.dol()[1]+20)]),
            # вниз к Z4 и Z5
            Rura([(self.z3.dol()[0]-100, self.z3.dol()[1]+20), self.z4.gora()]),
            Rura([(self.z3.dol()[0]+100, self.z3.dol()[1]+20), self.z5.gora()]),
        ]


        self.timer = QTimer()
        self.timer.timeout.connect(self.logika)
        self.timer.start(30)
        self.flow = 0.8
        #  нопка открыти€ окна отчета
        self.btn_raport = QPushButton("Pokaz raport", self)
        self.btn_raport.move(900, 20)  # позици€ кнопки
        self.btn_raport.clicked.connect(self.pokaz_raport)
        self.raport_okno = None

    

    def pokaz_raport(self):
       if not self.raport_okno:
          self.raport_okno = RaportOkno(self.zbiorniki)
       self.raport_okno.show()




    def logika(self):
        for r in self.rury:
            r.ustaw_przeplyw(False)

        # Z1 -> Z3
        if not self.z1.pusty():
            v = self.z1.usun(self.flow)
            self.z3.dodaj(v)
            for i in [0,2,3,5]:
                self.rury[i].ustaw_przeplyw(True)



        # Z2 -> Z3
        if not self.z2.pusty():
            v = self.z2.usun(self.flow)
            self.z3.dodaj(v)
            for i in [1,2,4,5]:
                self.rury[i].ustaw_przeplyw(True)


        # Z3 -> Z4 i Z5
        if not self.z3.pusty():
            v = self.z3.usun(self.flow)
            self.z4.dodaj(v/2)
            self.z5.dodaj(v/2)
            for i in [6,7,8,9,10]:
                self.rury[i].ustaw_przeplyw(True)


        # нагреватеоь Z4
        if self.z4.grzalka and self.z4.poziom >= 0.99:  # активаци€ после наполнени€
            self.z4.grzalka.aktualizuj()
         
        # нагреватель Z5
        if self.z5.grzalka and self.z5.poziom >= 0.99:  
            self.z5.grzalka.aktualizuj()

 

        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        for r in self.rury:
            r.draw(p)
        for z in self.zbiorniki:
            z.draw(p)



# вызов всех команд

if __name__ == "__main__":
    app = QApplication(sys.argv)
    okno = Symulacja()
    okno.show()
    sys.exit(app.exec_())
