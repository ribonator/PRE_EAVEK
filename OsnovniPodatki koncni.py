import os  #Uvozi funkcijo OS da se pojavljajo
from builtins import ValueError

from graphics import *
import pyglet
import traceback
from pyglet.window import key
from pyglet.window import mouse


class OsnovniPodatki:
    def __init__(self): #Funkcija potrebna da lahko ustvarimo 'razrede' CLASS
        self.naziv = ''
        self.type = ''
        self.numberOfStories = -1
        self.numberOfElements = -1
        self.numberOfLoadings = -1
        self.numberOfModes = -1
        self.method = ''
        self.secondOrderTheory = False
        self.constant1 = -1
        self.constant2 = -1
        self.storyHeights = []
        self.masses = []
        self.verticalLoading = []
        self.elements = []
        self.loads = []
        self.factor = -1
        self.tabulateMatrices = False
        self.solve = False
        self.xZamik = 10
        self.yZamik = 10
        self.skala = 10

    def preberi(self, potDoDatoteke): #Z tem ukazom definiramo ukaz za Vhodno datoteko, vrstica 919
        if not os.path.exists(potDoDatoteke):
            raise ValueError('Pot do datoteke napačna!!!')

        file = open(potDoDatoteke, 'r') #'r' pomeni branje lahko bi tudi uporabili 'r+'
        fileString = file.readlines()
        file.close()
        i = 0
        while True:
            if i >= len(fileString):
                break

            razdeljenaVrstica = fileString[i].split(" ")
            if fileString[i].startswith("*") or fileString[i].startswith("PRIN") or fileString[i].startswith("PLOT"):
                i = i + 1 # Ukaz v zgornji vrstici nam določa kaj bo program preskočil v branju
                continue
            elif fileString[i] == "\n": #če je prazna vrstica jo preskoči
                continue
            elif razdeljenaVrstica[0].startswith("STRU"): #Če se začne datoteka z Structure nadaljuje
                if i != 0:
                    raise ValueError('Datoteka se ne začne z STRUCTURE!!!') #Napaka v primeru da se ne začne z Structure
                self.naziv = fileString[i].split(" ", 1)[1]
            elif razdeljenaVrstica[0].startswith("TYPE"):
                if razdeljenaVrstica[1].startswith("PLAN"):
                    self.type = "PLANE"
                elif razdeljenaVrstica[1].startswith("SPAC"):
                    self.type = "SPACE" #V teh ukazih izbere ali se začne z SPACE ali z PLANE
                else:
                    raise ValueError('TYPE ni SPACE ali PLANE!!!') #Napaka če ni SPACE/PLANE
            elif razdeljenaVrstica[0].startswith("NUMB") and razdeljenaVrstica[1] == "OF" and razdeljenaVrstica[2].startswith("STOR"):
                stevilka = int(fileString[i].rsplit(" ", 1)[1]) #Razcepi od desne proti levi prvi ukaz
                if (stevilka > 30):
                    raise ValueError("Več kot 30 nadstropij!!!") #Napaka če je več kot 30 nadstropij
                self.numberOfStories = stevilka
            elif razdeljenaVrstica[0].startswith("NUMB") and razdeljenaVrstica[1] == "OF" and razdeljenaVrstica[2].startswith("ELEM"):
                stevilka = int(fileString[i].rsplit(" ", 1)[1])
                if (stevilka > 50):
                    raise ValueError("Več kot 50 elementov!!!") #Napaka če je več kot 50 elementov
                self.numberOfElements = stevilka
            elif razdeljenaVrstica[0].startswith("NUMB") and razdeljenaVrstica[1] == "OF" and razdeljenaVrstica[2].startswith("LOAD"):
                stevilka = int(fileString[i].rsplit(" ", 1)[1])
                if (stevilka > 20):
                    raise ValueError("Več kot 20 obtežb!!!") #Napaka če je več kot 20 obtežb
                self.numberOfLoadings = stevilka
            elif razdeljenaVrstica[0].startswith("NUMB") and razdeljenaVrstica[1] == "OF" and razdeljenaVrstica[2].startswith("MODE"):
                stevilka = int(fileString[i].rsplit(" ", 1)[1])
                if (stevilka > 18): #V knjihi je številka 9 izbrana je 18 zaradi PRIM3B ki jih ima 16
                    raise ValueError("Več kot 18 načinov!!!") ##
                self.numberOfModes = stevilka
            elif fileString[i].startswith("METH"): #Način izračuna
                if razdeljenaVrstica.__len__() == 3:
                    if razdeljenaVrstica[0].startswith("METH") and razdeljenaVrstica[1].startswith("STAT") and razdeljenaVrstica[2].startswith("DYNA"):
                        self.method = "STATIC DYNAMIC"
                elif razdeljenaVrstica.__len__() == 4:
                    if razdeljenaVrstica[0].startswith("METH") and razdeljenaVrstica[1].startswith("STAT") and razdeljenaVrstica[2].startswith("DYNA") and razdeljenaVrstica[3].startswith("STAB"): #Statika/dinamika/stabilnost
                        self.method = "STATIC DYNAMIC STABILITY"
                else:
                    raise ValueError("Napaka pri methodah!!!")
            elif fileString[i].startswith("SECO"): #Teorija 2. reda v primeru da je ni preskoči
                if razdeljenaVrstica[0].startswith("SECO") and razdeljenaVrstica[1].startswith("ORDE") and razdeljenaVrstica[2].startswith("THEO"):
                    self.secondOrderTheory = True
                else:
                    raise ValueError("napaka pri second order theory " + fileString[i])
            elif fileString[i].startswith("CONS"): #Konstante za Elastični modul in strižni modul
                string = fileString[i].split(" ")
                if len(string) == 2:
                    self.constant1 = convert(string[1])
                    self.constant2 = 0.4 * self.constant1 #V primeru da 2. Const. pomnoži prvo z 0.4
                elif len(string) == 3:
                    self.constant1 = convert(string[1])
                    self.constant2 = convert(string[2])
                else:
                    raise ValueError('Preveč ali premalo konstant!!!') #V primeru da ni nobene konstane oz <2 poda napako
            elif fileString[i].startswith("MASS"):
                j = 1
                if self.type == "PLANE":
                    while (fileString[i + j][0].isdigit()):
                        if ("THRU" not in fileString[i + j]): #če thru ni v vrstici obravnava kot da je po celoti enaka vrednost
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.masses.append(Mass(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1]), -1, -1, -1))
                            j += 1
                        else:
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.masses.append(Mass(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3]), -1, -1, -1))
                            if j != 1:
                                if self.masses[j-1].od != self.masses[j-2].do + 1:
                                    raise ValueError("Napaka pri masah!!!")
                            j += 1
                    if self.masses[0].od != 1:
                        raise ValueError("Napaka pri masah!!!")
                    elif self.masses[len(self.masses)-1].od != self.numberOfStories and self.masses[len(self.masses)-1].do == -1:
                        raise ValueError("Napaka pri masah!!!")
                    elif self.masses[len(self.masses)-1].do != self.numberOfStories and self.masses[len(self.masses)-1].do != -1:
                        raise ValueError("Napaka pri masah!!!") #Napake v primerih kadar niso primerno podane mase
                    i = i + j - 1
                else:
                    while (fileString[i + j][0].isdigit()):
                        if ("THRU" not in fileString[i + j]): #če thru ni v vrstici obravnava kot da je enaka vrednost povsod
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.masses.append(Mass(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), convert(spremenljivkeList[4])))
                            j += 1
                        else:
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.masses.append(Mass(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), convert(spremenljivkeList[6])))
                            if j != 1:
                                if self.masses[j-1].od != self.masses[j-2].do + 1:
                                    raise ValueError("Napaka pri masah!!!")
                            j += 1
                    if self.masses[0].od != 1:
                        raise ValueError("Napaka pri masah!!!")
                    elif self.masses[len(self.masses)-1].od != self.numberOfStories and self.masses[len(self.masses)-1].do == -1:
                        raise ValueError("Napaka pri masah!!!")
                    elif self.masses[len(self.masses)-1].do != self.numberOfStories and self.masses[len(self.masses)-1].do != -1:
                        raise ValueError("Napaka pri masah!!!")
                    i = i + j - 1
            elif fileString[i].startswith("VERT"):
                if not razdeljenaVrstica[0].startswith("VERT") and not razdeljenaVrstica[1].startswith("LOAD"):
                    raise ValueError("napaka pri vertical loadings " + fileString[i])
                j = 1
                if self.type == "PLANE":
                    while (fileString[i + j][0].isdigit()):
                        if ("THRU" not in fileString[i + j]):
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.verticalLoading.append(VerticalLoading(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1]), -1, -1, -1))
                            j += 1
                        else:
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.verticalLoading.append(VerticalLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3]), -1, -1, -1))
                            if j != 1:
                                if self.verticalLoading[j-1].od != self.verticalLoading[j-2].do + 1:
                                    raise ValueError("Napaka pri masah!!!")
                            j += 1
                    if self.verticalLoading[0].od != 1:
                        raise ValueError("Napaka pri obtezbah!!!")
                    elif self.verticalLoading[len(self.verticalLoading)-1].od != self.numberOfStories and self.verticalLoading[len(self.verticalLoading)-1].do == -1:
                        raise ValueError("Napaka pri obtezbah!!!")
                    elif self.verticalLoading[len(self.verticalLoading)-1].do != self.numberOfStories and self.verticalLoading[len(self.verticalLoading)-1].do != -1:
                        raise ValueError("Napaka pri obtezbah!!!")
                    i = i + j - 1
                else:
                    while (fileString[i + j][0].isdigit()):
                        if ("THRU" not in fileString[i + j]):
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.verticalLoading.append(VerticalLoading(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), convert(spremenljivkeList[4])))
                            j += 1
                        else:
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.verticalLoading.append(VerticalLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), convert(spremenljivkeList[6])))
                            if j != 1:
                                if self.verticalLoading[j-1].od != self.verticalLoading[j-2].do + 1:
                                    raise ValueError("Napaka pri obtezbah!!!")
                            j += 1
                    if self.verticalLoading[0].od != 1:
                        raise ValueError("Napaka pri etazah!!!")
                    elif self.verticalLoading[len(self.verticalLoading)-1].od != self.numberOfStories and self.verticalLoading[len(self.verticalLoading)-1].do == -1:
                        raise ValueError("Napaka pri etazah!!!")
                    elif self.verticalLoading[len(self.verticalLoading)-1].do != self.numberOfStories and self.verticalLoading[len(self.verticalLoading)-1].do != -1:
                        raise ValueError("Napaka pri etazah!!!")
                    i = i + j - 1
                if (fileString[i].startswith("FACT")):
                    self.factor = convert(fileString[i].split(" ")[1])
            elif fileString[i].startswith("STOR"):
                if not razdeljenaVrstica[0].startswith("STOR") and not razdeljenaVrstica[1].startswith("HEIG"):
                    raise ValueError("napaka pri story heights " + fileString[i])
                j = 1
                while (fileString[i + j][0].isdigit()):
                    if ("THRU" not in fileString[i + j]):
                        spremenljivkeList = fileString[i + j].split(" ")
                        self.storyHeights.append(StoryHeight(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1])))
                    else:
                        spremenljivkeList = fileString[i + j].split(" ")
                        self.storyHeights.append(StoryHeight(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3])))
                        if j != 1:
                            if self.storyHeights[j-1].od != self.storyHeights[j-2].do + 1:
                                raise ValueError("Napaka pri višinah nadstropij!!!")
                        j += 1
                if self.storyHeights[0].od != 1:
                    raise ValueError("Napaka pri višinah nadstropij!!!")
                elif self.storyHeights[len(self.masses) - 1].od != self.numberOfStories and self.storyHeights[len(self.masses) - 1].do == -1:
                    raise ValueError("Napaka pri višinah nadstropij!!!")
                elif self.storyHeights[len(self.masses) - 1].do != self.numberOfStories and self.storyHeights[len(self.masses) - 1].do != -1:
                    raise ValueError("Napaka pri višinah nadstropij!!!") #Napaka če ni pravilno podana višina ali je sploh ni
                i = i + j - 1
            elif fileString[i].startswith("TABU"):
                if razdeljenaVrstica[0].startswith("TABU") and razdeljenaVrstica[1].startswith("MATR"):
                    self.tabulateMatrices = True
                else:
                    raise ValueError("napaka pri tabulate matrices " + fileString[i])
            elif fileString[i].startswith("ELEM"): #Primeri kadar se začne vrstica z ukazom ' '
                element = Element()
                j = element.preberi(i, fileString, self)
                self.elements.append(element)
                i = j
            elif fileString[i].startswith("LOAD"):
                loading = Loading()
                j = loading.preberi(i, fileString, self.type)
                self.loads.append(loading)
                i = j
            elif fileString[i].startswith("SOLV"):
                self.solve = True
                break
            else:
                raise ValueError("Napaka nepoznan ukaz!!! " + fileString[i]) #če je kateri drugi neznani ukaz javi napako

            i = i + 1

        if self.solve != True:
            raise ValueError("Napaka ni ukaza SOLVE!!!") #Napake v primeru manjkajocih ukazov
        elif self.naziv == '':
            raise ValueError("Napaka ni naziva!!!")
        elif self.type != 'PLANE' and self.type != 'SPACE':
            raise ValueError("Napaka napačen type!!!")
        elif self.numberOfStories == -1:
            raise ValueError("Napaka ni ukaza NUMBER OF STORIES!!!")
        elif self.numberOfElements == -1:
            raise ValueError("Napaka ni ukaza NUMBER OF ELEMENTS!!!")
        elif self.numberOfLoadings == -1:
            raise ValueError("Napaka ni ukaza NUMBER OF LOADINGS!!!")
        elif self.numberOfModes == -1:
            raise ValueError("Napaka ni ukaza NUMBER OF MODES!!!")
        elif self.method == '':
            raise ValueError("Napaka ni ukaza MATHOD!!!")
        elif self.constant1 == -1:
            raise ValueError("Napaka ni ukaza CONSTANT!!!")
        elif len(self.storyHeights) == 0:
            raise ValueError("Napaka ni ukaza STORY HEIGHTS!!!")
        elif len(self.masses) == 0:
            raise ValueError("Napaka ni ukaza MASSES!!!")
        elif len(self.elements) == 0:
            raise ValueError("Napaka ni ukaza ELEMENT!!!")

    def preberiSkrajsano(self, potDoDatoteke):
        if not os.path.exists(potDoDatoteke):
            raise ValueError('Pot do datoteke napačna!!!')

        file = open(potDoDatoteke, 'r') #'r' pomeni branje lahko bi tudi uporabili 'r+'
        fileString = file.readlines()
        file.close()
        i = 0
        while True:
            if i >= len(fileString):
                break
            elif fileString[i].startswith("*") or fileString[i].startswith("PRIN") or fileString[i].startswith("PLOT"):
                i = i + 1 # Ukaz v zgornji vrstici nam določa kaj bo program preskočil v branju
                continue
            elif fileString[i] == "\n": #če je prazna vrstica jo preskoči
                i = i + 1  # Ukaz v zgornji vrstici nam določa kaj bo program preskočil v branju
                continue
            elif fileString[i].startswith("STRU"): #Če se začne datoteka z Structure nadaljuje
                if i != 0:
                    raise ValueError('Datoteka se ne začne z STRUCTURE!!!') #Napaka v primeru da se ne začne z Structure
                self.naziv = fileString[i].split(" ", 1)[1]
            elif fileString[i].startswith("TYPE"):
                if fileString[i] == "TYPE PLAN\n":
                    self.type = "PLANE"
                elif fileString[i] == "TYPE SPAC\n":
                    self.type = "SPACE" #V teh ukazih izbere ali se začne z SPACE ali z PLANE
                else:
                    raise ValueError('TYPE ni SPACE ali PLANE!!!') #Napaka če ni SPACE/PLANE
            elif fileString[i].startswith("NUMB OF STOR"):
                stevilka = int(fileString[i].rsplit(" ", 1)[1]) #Razcepi od desne proti levi prvi ukaz
                if (stevilka > 30):
                    raise ValueError("Več kot 30 nadstropij!!!") #Napaka če je več kot 30 nadstropij
                self.numberOfStories = stevilka
            elif fileString[i].startswith("NUMB OF ELEM"):
                stevilka = int(fileString[i].rsplit(" ", 1)[1])
                if (stevilka > 50):
                    raise ValueError("Več kot 50 elementov!!!") #Napaka če je več kot 50 elementov
                self.numberOfElements = stevilka
            elif fileString[i].startswith("NUMB OF LOAD"):
                stevilka = int(fileString[i].rsplit(" ", 1)[1])
                if (stevilka > 20):
                    raise ValueError("Več kot 20 obtežb!!!") #Napaka če je več kot 20 obtežb
                self.numberOfLoadings = stevilka
            elif fileString[i].startswith("NUMB OF MODE"):
                stevilka = int(fileString[i].rsplit(" ", 1)[1])
                if (stevilka > 18): #V knjihi je številka 9 izbrana je 18 zaradi PRIM3B ki jih ima 16
                    raise ValueError("Več kot 18 načinov!!!") ##
                self.numberOfModes = stevilka
            elif fileString[i].startswith("METH"): #Način izračuna
                if fileString[i].startswith("METH STAT DYNA"): #Statika/dinamika
                    self.method = "STATIC DYNAMIC"
                elif fileString[i].startswith("METH STAT DYNA STAB"): #Statika/dinamika/stabilnost
                    self.method = "STATIC DYNAMIC STABILITY"
                else:
                    raise ValueError("Napaka pri methodah!!!")
            elif fileString[i].startswith("SECO ORDE THEO"): #Teorija 2. reda v primeru da je ni preskoči
                self.secondOrderTheory = True
            elif fileString[i].startswith("CONS"): #Konstante za Elastični modul in strižni modul
                string = fileString[i].split(" ")
                if len(string) == 2:
                    self.constant1 = convert(string[1])
                    self.constant2 = 0.4 * self.constant1 #V primeru da 2. Const. pomnoži prvo z 0.4
                elif len(string) == 3:
                    self.constant1 = convert(string[1])
                    self.constant2 = convert(string[2])
                else:
                    raise ValueError('Preveč ali premalo konstant!!!') #V primeru da ni nobene konstane oz <2 poda napako
            elif fileString[i].startswith("MASS"):
                j = 1
                if self.type == "PLANE":
                    while (fileString[i + j][0].isdigit()):
                        if ("THRU" not in fileString[i + j]): #če thru ni v vrstici obravnava kot da je po celoti enaka vrednost
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.masses.append(Mass(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1]), -1, -1, -1))
                            j += 1
                        else:
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.masses.append(Mass(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3]), -1, -1, -1))
                            if j != 1:
                                if self.masses[j-1].od != self.masses[j-2].do + 1:
                                    raise ValueError("Napaka pri masah!!!")
                            j += 1
                    if self.masses[0].od != 1:
                        raise ValueError("Napaka pri masah!!!")
                    elif self.masses[len(self.masses)-1].od != self.numberOfStories and self.masses[len(self.masses)-1].do == -1:
                        raise ValueError("Napaka pri masah!!!")
                    elif self.masses[len(self.masses)-1].do != self.numberOfStories and self.masses[len(self.masses)-1].do != -1:
                        raise ValueError("Napaka pri masah!!!") #Napake v primerih kadar niso primerno podane mase
                    i = i + j - 1
                else:
                    while (fileString[i + j][0].isdigit()):
                        if ("THRU" not in fileString[i + j]): #če thru ni v vrstici obravnava kot da je enaka vrednost povsod
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.masses.append(Mass(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), convert(spremenljivkeList[4])))
                            j += 1
                        else:
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.masses.append(Mass(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), convert(spremenljivkeList[6])))
                            if j != 1:
                                if self.masses[j-1].od != self.masses[j-2].do + 1:
                                    raise ValueError("Napaka pri masah!!!")
                            j += 1
                    if self.masses[0].od != 1:
                        raise ValueError("Napaka pri masah!!!")
                    elif self.masses[len(self.masses)-1].od != self.numberOfStories and self.masses[len(self.masses)-1].do == -1:
                        raise ValueError("Napaka pri masah!!!")
                    elif self.masses[len(self.masses)-1].do != self.numberOfStories and self.masses[len(self.masses)-1].do != -1:
                        raise ValueError("Napaka pri masah!!!")
                    i = i + j - 1
            elif fileString[i].startswith("VERT LOAD"):
                j = 1
                if self.type == "PLANE":
                    while (fileString[i + j][0].isdigit()):
                        if ("THRU" not in fileString[i + j]):
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.verticalLoading.append(VerticalLoading(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1]), -1, -1, -1))
                            j += 1
                        else:
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.verticalLoading.append(VerticalLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3]), -1, -1, -1))
                            if j != 1:
                                if self.verticalLoading[j-1].od != self.verticalLoading[j-2].do + 1:
                                    raise ValueError("Napaka pri masah!!!")
                            j += 1
                    if self.verticalLoading[0].od != 1:
                        raise ValueError("Napaka pri obtezbah!!!")
                    elif self.verticalLoading[len(self.verticalLoading)-1].od != self.numberOfStories and self.verticalLoading[len(self.verticalLoading)-1].do == -1:
                        raise ValueError("Napaka pri obtezbah!!!")
                    elif self.verticalLoading[len(self.verticalLoading)-1].do != self.numberOfStories and self.verticalLoading[len(self.verticalLoading)-1].do != -1:
                        raise ValueError("Napaka pri obtezbah!!!")
                    i = i + j - 1
                else:
                    while (fileString[i + j][0].isdigit()):
                        if ("THRU" not in fileString[i + j]):
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.verticalLoading.append(VerticalLoading(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), convert(spremenljivkeList[4])))
                            j += 1
                        else:
                            spremenljivkeList = fileString[i + j].split(" ")
                            self.verticalLoading.append(VerticalLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), convert(spremenljivkeList[6])))
                            if j != 1:
                                if self.verticalLoading[j-1].od != self.verticalLoading[j-2].do + 1:
                                    raise ValueError("Napaka pri obtezbah!!!")
                            j += 1
                    if self.verticalLoading[0].od != 1:
                        raise ValueError("Napaka pri etazah!!!")
                    elif self.verticalLoading[len(self.verticalLoading)-1].od != self.numberOfStories and self.verticalLoading[len(self.verticalLoading)-1].do == -1:
                        raise ValueError("Napaka pri etazah!!!")
                    elif self.verticalLoading[len(self.verticalLoading)-1].do != self.numberOfStories and self.verticalLoading[len(self.verticalLoading)-1].do != -1:
                        raise ValueError("Napaka pri etazah!!!")
                    i = i + j - 1
                if (fileString[i].startswith("FACT")):
                    self.factor = convert(fileString[i].split(" ")[1])
            elif fileString[i].startswith("STOR HEIG"):
                j = 1
                while (fileString[i + j][0].isdigit()):
                    if ("THRU" not in fileString[i + j]):
                        spremenljivkeList = fileString[i + j].split(" ")
                        self.storyHeights.append(StoryHeight(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1])))
                    else:
                        spremenljivkeList = fileString[i + j].split(" ")
                        self.storyHeights.append(StoryHeight(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3])))
                        if j != 1:
                            if self.storyHeights[j-1].od != self.storyHeights[j-2].do + 1:
                                raise ValueError("Napaka pri višinah nadstropij!!!")
                        j += 1
                if self.storyHeights[0].od != 1:
                    raise ValueError("Napaka pri višinah nadstropij!!!")
                elif self.storyHeights[len(self.masses) - 1].od != self.numberOfStories and self.storyHeights[len(self.masses) - 1].do == -1:
                    raise ValueError("Napaka pri višinah nadstropij!!!")
                elif self.storyHeights[len(self.masses) - 1].do != self.numberOfStories and self.storyHeights[len(self.masses) - 1].do != -1:
                    raise ValueError("Napaka pri višinah nadstropij!!!") #Napaka če ni pravilno podana višina ali je sploh ni
                i = i + j - 1
            elif fileString[i].startswith("TABU MATR"):
                self.tabulateMatrices = True
            elif fileString[i].startswith("ELEM"): #Primeri kadar se začne vrstica z ukazom ' '
                element = Element()
                j = element.preberiSkrajsano(i, fileString, self)
                self.elements.append(element)
                i = j
            elif fileString[i].startswith("LOAD"):
                loading = Loading()
                j = loading.preberiSkrajsano(i, fileString, self.type)
                self.loads.append(loading)
                i = j
            elif fileString[i].startswith("SOLV"):
                self.solve = True
                break
            else:
                raise ValueError("Napaka nepoznan ukaz!!! " + fileString[i]) #če je kateri drugi neznani ukaz javi napako

            i = i + 1

        if self.solve != True:
            raise ValueError("Napaka ni ukaza SOLVE!!!") #Napake v primeru manjkajocih ukazov
        elif self.naziv == '':
            raise ValueError("Napaka ni naziva!!!")
        elif self.type != 'PLANE' and self.type != 'SPACE':
            raise ValueError("Napaka napačen type!!!")
        elif self.numberOfStories == -1:
            raise ValueError("Napaka ni ukaza NUMBER OF STORIES!!!")
        elif self.numberOfElements == -1:
            raise ValueError("Napaka ni ukaza NUMBER OF ELEMENTS!!!")
        elif self.numberOfLoadings == -1:
            raise ValueError("Napaka ni ukaza NUMBER OF LOADINGS!!!")
        elif self.numberOfModes == -1:
            raise ValueError("Napaka ni ukaza NUMBER OF MODES!!!")
        elif self.method == '':
            raise ValueError("Napaka ni ukaza MATHOD!!!")
        elif self.constant1 == -1:
            raise ValueError("Napaka ni ukaza CONSTANT!!!")
        elif len(self.storyHeights) == 0:
            raise ValueError("Napaka ni ukaza STORY HEIGHTS!!!")
        elif len(self.masses) == 0:
            raise ValueError("Napaka ni ukaza MASSES!!!")
        elif len(self.elements) == 0:
            raise ValueError("Napaka ni ukaza ELEMENT!!!")

    def izpisi(self):
        returnString = "STRU " + self.naziv + "\n" #Izpis ukazov v program oz. datoteko
        returnString += "NUMB OF STOR " + str(self.numberOfStories) + "\n"
        returnString += "NUMB OF ELEM " + str(self.numberOfElements) + "\n"
        returnString += "NUMB OF LOAD " + str(self.numberOfLoadings) + "\n"
        returnString += "NUMB OF MODE " + str(self.numberOfModes) + "\n"
        returnString += "TYPE " + self.type[:4] + "\n"
        returnString += "METH "
        for line in self.method.split(" "):
            returnString += line[:4] + " "
        returnString += "\n"
        returnString += "STOR HEIG\n"
        for line in self.storyHeights:
            if line.do == -1:
                returnString += str(line.od) + " " + str(line.visina) + "\n"
            else:
                returnString += str(line.od) + " " + "THRU " + str(line.do) + " " + str(line.visina) + "\n"
        returnString += "CONS " + str(self.constant1) + " " + str(self.constant2) + "\n"
        returnString += "MASS\n"
        for line in self.masses:
            if self.type == "PLANE":
                if line.do == -1:
                    returnString += str(line.od) + " " + str(line.stevilka1) + "\n"
                else:
                    returnString += str(line.od) + " " + "THRU " + str(line.do) + " " + str(line.stevilka1) + "\n"
            else:
                if line.do == -1:
                    returnString += str(line.od) + " " + str(line.stevilka1) + " " + str(line.stevilka2) + " " + str(line.stevilka3) + " " + str(line.stevilka4) + "\n"
                else:
                    returnString += str(line.od) + " " + "THRU " + str(line.do) + " " + str(line.stevilka1) + " " + str(line.stevilka2) + " " + str(line.stevilka3) + " " + str(line.stevilka4) + "\n"
        if len(self.verticalLoading) != 0:
            returnString += "VERT LOAD\n"
            for line in self.verticalLoading:
                if self.type == "PLANE":
                    if line.do == -1:
                        returnString += str(line.od) + " " + str(line.stevilka1) + "\n"
                    else:
                        returnString += str(line.od) + " " + "THRU " + str(line.do) + " " + str(line.stevilka1) + "\n"
                else:
                    if line.do == -1:
                        returnString += str(line.od) + " " + str(line.stevilka1) + " " + str(line.stevilka2) + " " + str(line.stevilka3) + " " + str(line.stevilka4) + "\n"
                    else:
                        returnString += str(line.od) + " " + "THRU " + str(line.do) + " " + str(line.stevilka1) + " " + str(line.stevilka2) + " " + str(line.stevilka3) + " " + str(line.stevilka4) + "\n"

        for element in self.elements:
            returnString += element.izpisi()
            returnString += "\n"
        for loading in self.loads:
            returnString += loading.izpisi()
            returnString += "\n"
        if self.tabulateMatrices == True:
            returnString += "TABULATE MATRICES\n"

        returnString += "SOLV\n"
        return returnString

    def izrisiNarisRavnina(self, skalaVhod, window, zamikonx, zamikony):
        self.xZamik = zamikonx
        self.yZamik = zamikony
        self.skala = skalaVhod

        try:
            @window.event
            def on_draw():
                window.clear()

                coordinates = []
                steviloNadstropij = []

                # dobi koordinate in stevilo nadstropij
                i = 0
                for element in self.elements:
                    coordinates.append(element.coordinatesX)
                    if element.numberOfStories == -1:
                        steviloNadstropij.append(self.numberOfStories)
                    else:
                        steviloNadstropij.append(element.numberOfStories)

                    i += 1

                visine = []
                visine.append(0.0)
                for i in range(0, self.storyHeights.__len__()):
                    if self.storyHeights[i].do == -1:
                        visine.append(self.storyHeights[i].visina * i)
                    else:
                        for j in range(self.storyHeights[i].od, self.storyHeights[i].do + 1):
                            visine.append(self.storyHeights[i].visina * j)

                # naredi tocke
                tocke = []
                for i in range(0, visine.__len__()):
                    for j in range(0, coordinates.__len__()):
                        if steviloNadstropij[j] == -1:
                            tocke.append(Tocka(coordinates[j], visine[i]))
                            continue
                        elif i <= steviloNadstropij[j]:
                            tocke.append(Tocka(coordinates[j], visine[i]))
                            continue

                pyglet.gl.glPointSize(10)
                # izrisi tocke
                zacetneTocke = []
                koncneTocke = []
                tocke = sortPoX(tocke)
                seznamY = []
                for i in range(0, tocke.__len__()):
                    y = int(tocke[i].y * self.skala)
                    if y not in seznamY:
                        seznamY.append(y)
                for i in range(0, seznamY.__len__()):
                    y = seznamY[i]
                    if Tocka(10000, y) not in zacetneTocke:
                        zacetneTocke.append(Tocka(10000, y))
                for i in range(0, seznamY.__len__()):
                    y = seznamY[i]
                    if Tocka(0, y) not in koncneTocke:
                        koncneTocke.append(Tocka(0, y))

                for i in range(0, tocke.__len__()):
                    x1 = int(tocke[i].x * self.skala)
                    y1 = int(tocke[i].y * self.skala)

                    for j in range(0, seznamY.__len__()):
                        if zacetneTocke[j].y == y1:
                            if zacetneTocke[j].x > x1:
                                zacetneTocke[j].x = x1
                        if koncneTocke[j].y == y1:
                            if koncneTocke[j].x < x1:
                                koncneTocke[j].x = x1

                    pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2f', (x1 + self.xZamik, y1 + self.yZamik)))
                    label = pyglet.text.Label('(' + str(tocke[i].x) + ', ' + str(tocke[i].y) + ')',
                                              font_name='Times New Roman', font_size=8)
                    label.x = x1 + 10 + self.xZamik
                    label.y = y1 + 10 + self.yZamik
                    label.draw()

                # izrisi crte
                pyglet.gl.glLineWidth(2)
                for i in range(0, zacetneTocke.__len__()):
                    pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (
                        zacetneTocke[i].x + self.xZamik, zacetneTocke[i].y + self.yZamik,
                        koncneTocke[i].x + self.xZamik,
                        koncneTocke[i].y + self.yZamik)), ('c3f', (.8, .8, .8) * 2))

                xZadnja = -1
                yZadnja = -1
                yPrva = -1
                for i in range(0, tocke.__len__()):
                    x = int(tocke[i].x * self.skala)
                    y = int(tocke[i].y * self.skala)
                    if (i == 0):
                        xZadnja = x
                        yPrva = y
                    elif (xZadnja != x):
                        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, (
                            'v2f',
                            (xZadnja + self.xZamik, yPrva + self.yZamik, xZadnja + self.xZamik, yZadnja + self.yZamik)),
                                             ('c3f', (.8, .8, .8) * 2))
                        xZadnja = x
                        yPrva = y
                        yZadnja = y
                    elif (i == tocke.__len__() - 1):
                        yZadnja = y
                        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, (
                            'v2f',
                            (xZadnja + self.xZamik, yPrva + self.yZamik, xZadnja + self.xZamik, yZadnja + self.yZamik)),
                                             ('c3f', (.8, .8, .8) * 2))
                    else:
                        yZadnja = y

            @window.event
            def on_text_motion(motion):
                try:
                    if motion == pyglet.window.key.MOTION_LEFT:
                        self.xZamik -= 10
                        self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                    elif motion == pyglet.window.key.MOTION_RIGHT:
                        self.xZamik += 10
                        self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                    elif motion == pyglet.window.key.MOTION_UP:
                        self.yZamik += 10
                        self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                    elif motion == pyglet.window.key.MOTION_DOWN:
                        self.yZamik -= 10
                        self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                except Exception as error:
                    window.clear()
                    window.close()
                    pyglet.app.exit()
                    ctypes.windll.user32.MessageBoxW(0, str(error), "Druga Napaka", 1)

            @window.event
            def on_key_press(symbol, modifiers):
                try:
                    if symbol == key.ENTER:
                        window.clear()
                        window.close()
                        pyglet.app.exit()
                    elif symbol == key.LEFT:
                        self.xZamik -= 10
                        self.izrisiNarisRavnina(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.RIGHT:
                        self.xZamik += 10
                        self.izrisiNarisRavnina(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.UP:
                        self.yZamik += 10
                        self.izrisiNarisRavnina(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.DOWN:
                        self.yZamik -= 10
                        self.izrisiNarisRavnina(self.skala, window, self.xZamik, self.yZamik)
                except Exception as error:
                    window.clear()
                    window.close()
                    pyglet.app.exit()
                    ctypes.windll.user32.MessageBoxW(0, str(error), "Druga Napaka", 1)

            @window.event
            def on_mouse_scroll(x, y, scroll_x, scroll_y):
                if scroll_y < 0:
                    self.skala -= 3
                    self.izrisiNarisRavnina(self.skala, window, self.xZamik, self.yZamik)
                else:
                    self.skala += 3
                    self.izrisiNarisRavnina(self.skala, window, self.xZamik, self.yZamik)

            @window.event
            def on_mouse_release(x, y, button, modifiers):
                if button == mouse.LEFT:
                    window.clear()
                    window.close()
                    pyglet.app.exit()

        except Exception as error:
            window.close()
            ctypes.windll.user32.MessageBoxW(0, str(error), "Druga Napaka", 1)

    def izrisiTloris(self, skalaVhod, window, zamikonx, zamikony):
        if self.type == "PLANE":
            return

        self.xZamik = zamikonx
        self.yZamik = zamikony
        self.skala = skalaVhod

        try:
            @window.event
            def on_draw():
                window.clear()

                directionXCoordinatesY = []
                directionYCoordinatesX = []

                # dobi x in y smer koordinate
                i = 0
                for element in self.elements:
                    if element.direction == "X":
                        directionXCoordinatesY.append(CoordinateStartStop(element.coordinatesY, element.od, element.do, element.length, element.shift, element.type))
                    elif element.direction == "Y":
                        directionYCoordinatesX.append(CoordinateStartStop(element.coordinatesX, element.od, element.do, element.length, element.shift, element.type))

                    i += 1

                # naredi tocke
                tocke = []
                for i in range(0, directionXCoordinatesY.__len__()):
                    for j in range(0, directionYCoordinatesX.__len__()):
                        if directionXCoordinatesY[i].od > directionYCoordinatesX[j].coordinate and directionXCoordinatesY[i].od != -1:
                            continue
                        elif directionYCoordinatesX[j].od > directionXCoordinatesY[i].coordinate and directionYCoordinatesX[j].od != -1:
                            continue
                        elif directionXCoordinatesY[i].do < directionYCoordinatesX[j].coordinate and directionXCoordinatesY[i].do != -1:
                            continue
                        elif directionYCoordinatesX[j].do < directionXCoordinatesY[i].coordinate and directionYCoordinatesX[j].do != -1:
                            continue
                        if directionYCoordinatesX[j].length == -1 and directionXCoordinatesY[i].length == -1:
                            tocke.append(TockaTloris(directionYCoordinatesX[j].coordinate, directionXCoordinatesY[i].coordinate, -1, -1, -1, -1, directionYCoordinatesX[j].type, directionXCoordinatesY[i].type))
                        elif directionYCoordinatesX[j].length == -1 and directionXCoordinatesY[i].length != -1:
                            tocke.append(TockaTloris(directionYCoordinatesX[j].coordinate, directionXCoordinatesY[i].coordinate, directionXCoordinatesY[i].length, directionXCoordinatesY[i].shift, -1, -1, directionYCoordinatesX[j].type, directionXCoordinatesY[i].type))
                        elif directionYCoordinatesX[j].length != -1 and directionXCoordinatesY[i].length == -1:
                            tocke.append(TockaTloris(directionYCoordinatesX[j].coordinate, directionXCoordinatesY[i].coordinate, -1, -1, directionYCoordinatesX[j].length, directionYCoordinatesX[j].shift, directionYCoordinatesX[j].type, directionXCoordinatesY[i].type))
                        else:
                            tocke.append(TockaTloris(directionYCoordinatesX[j].coordinate, directionXCoordinatesY[i].coordinate, directionXCoordinatesY[i].length, directionXCoordinatesY[i].shift, directionYCoordinatesX[j].length, directionYCoordinatesX[j].shift, directionYCoordinatesX[j].type, directionXCoordinatesY[i].type))

                pyglet.gl.glPointSize(10)
                # izrisi tocke
                zacetneTocke = []
                koncneTocke = []
                tocke = sortPoX(tocke)
                seznamY = []
                for i in range(0, tocke.__len__()):
                    y = int(tocke[i].y * self.skala)
                    if y not in seznamY:
                        seznamY.append(y)
                for i in range(0, seznamY.__len__()):
                    y = seznamY[i]
                    if Tocka(10000, y) not in zacetneTocke:
                        zacetneTocke.append(Tocka(10000, y))
                for i in range(0, seznamY.__len__()):
                    y = seznamY[i]
                    if Tocka(0, y) not in koncneTocke:
                        koncneTocke.append(Tocka(0, y))

                for i in range(0, tocke.__len__()):
                    x1 = int(tocke[i].x * self.skala)
                    y1 = int(tocke[i].y * self.skala)
                    if tocke[i].lengthX == -1:
                        dolzinaX = -1
                    else:
                        dolzinaX = int(tocke[i].lengthX * self.skala)
                    if tocke[i].lengthY == -1:
                        dolzinaY = -1
                    else:
                        dolzinaY = int(tocke[i].lengthY * self.skala)
                    if tocke[i].shiftX == -1:
                        zamikX = -1
                    else:
                        zamikX = int(tocke[i].shiftX * self.skala)
                    if tocke[i].shiftY == -1:
                        zamikY = -1
                    else:
                        zamikY = int(tocke[i].shiftX * self.skala)

                    for j in range(0, seznamY.__len__()):
                        if zacetneTocke[j].y == y1:
                            if zacetneTocke[j].x > x1:
                                zacetneTocke[j].x = x1
                        if koncneTocke[j].y == y1:
                            if koncneTocke[j].x < x1:
                                koncneTocke[j].x = x1

                    pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2f', (x1 + self.xZamik, y1 + self.yZamik)))
                    label = pyglet.text.Label('(' + str(tocke[i].x) + ', ' + str(tocke[i].y) + ')',
                                              font_name='Times New Roman', font_size=8)
                    label.x = x1 + 10 + self.xZamik
                    label.y = y1 + 10 + self.yZamik
                    label.draw()

                    pyglet.gl.glLineWidth(5)
                    if dolzinaX == -1 and dolzinaY == -1:
                        pass
                    elif dolzinaX != -1 and dolzinaY == -1:
                        zacetna = x1 + self.xZamik
                        koncna = x1 + dolzinaX + self.xZamik
                        if zamikX != -1:
                            zacetna = x1 + zamikX + self.xZamik
                            koncna = x1 + zamikX + self.xZamik + dolzinaX
                        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (zacetna, y1 + self.yZamik, koncna, y1 + self.yZamik)), ('c3f', (.8, .8, .8) * 2))
                    elif dolzinaX == -1 and dolzinaY != -1:
                        zacetna = y1 + self.yZamik
                        koncna = y1 + dolzinaY + self.yZamik
                        if zamikY != -1:
                            zacetna = y1 - zamikY + self.yZamik
                            koncna = y1 - zamikY + self.yZamik + dolzinaY
                        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (x1 + self.xZamik, zacetna, x1 + self.xZamik, koncna)), ('c3f', (.8, .8, .8) * 2))
                    else:
                        zacetna = x1 + self.xZamik
                        koncna = x1 + dolzinaX + self.xZamik
                        if zamikX != -1:
                            zacetna = x1 + zamikX + self.xZamik
                            koncna = x1 + zamikX + self.xZamik + dolzinaX
                        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (zacetna, y1 + self.yZamik, koncna, y1 + self.yZamik)), ('c3f', (.8, .8, .8) * 2))
                        zacetna = y1 + self.yZamik
                        koncna = y1 + dolzinaY + self.yZamik
                        if zamikY != -1:
                            zacetna = y1 - zamikY + self.yZamik
                            koncna = y1 - zamikY + self.yZamik + dolzinaY
                        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (x1 + self.xZamik, zacetna, x1 + self.xZamik, koncna)), ('c3f', (.8, .8, .8) * 2))

                pyglet.gl.glLineWidth(2)
                # izrisi crte vodoravno
                for i in range(0, zacetneTocke.__len__()):
                    pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (zacetneTocke[i].x + self.xZamik, zacetneTocke[i].y + self.yZamik, koncneTocke[i].x + self.xZamik, koncneTocke[i].y + self.yZamik)), ('c3f', (.8,.8,.8)*2))

                xZadnja = -1
                yZadnja = -1
                yPrva = -1
                # izrisi crte navpicno
                for i in range(0, tocke.__len__()):
                    x = int(tocke[i].x * self.skala)
                    y = int(tocke[i].y * self.skala)
                    if (i == 0):
                        xZadnja = x
                        yPrva = y
                    elif (xZadnja != x):
                        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (xZadnja + self.xZamik, yPrva + self.yZamik, xZadnja + self.xZamik, yZadnja + self.yZamik)), ('c3f', (.8,.8,.8)*2))
                        xZadnja = x
                        yPrva = y
                        yZadnja = y
                    elif (i == tocke.__len__() - 1):
                        yZadnja = y
                        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (xZadnja + self.xZamik, yPrva + self.yZamik, xZadnja + self.xZamik, yZadnja + self.yZamik)), ('c3f', (.8, .8, .8) * 2))
                    else:
                        yZadnja = y

            @window.event
            def on_text_motion(motion):
                try:
                    if motion == pyglet.window.key.MOTION_LEFT:
                        self.xZamik -= 10
                        self.izrisiTloris(self.skala, window, self.xZamik, self.yZamik)
                    elif motion == pyglet.window.key.MOTION_RIGHT:
                        self.xZamik += 10
                        self.izrisiTloris(self.skala, window, self.xZamik, self.yZamik)
                    elif motion == pyglet.window.key.MOTION_UP:
                        self.yZamik += 10
                        self.izrisiTloris(self.skala, window, self.xZamik, self.yZamik)
                    elif motion == pyglet.window.key.MOTION_DOWN:
                        self.yZamik -= 10
                        self.izrisiTloris(self.skala, window, self.xZamik, self.yZamik)
                except Exception as error:
                    window.clear()
                    window.close()
                    pyglet.app.exit()
                    ctypes.windll.user32.MessageBoxW(0, str(error), "Druga Napaka", 1)

            @window.event
            def on_key_press(symbol, modifiers):
                try:
                    if symbol == key.ENTER:
                        window.clear()
                        self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.LEFT:
                        self.xZamik -= 10
                        self.izrisiTloris(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.RIGHT:
                        self.xZamik += 10
                        self.izrisiTloris(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.UP:
                        self.yZamik += 10
                        self.izrisiTloris(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.DOWN:
                        self.yZamik -= 10
                        self.izrisiTloris(self.skala, window, self.xZamik, self.yZamik)
                except Exception as error:
                    window.clear()
                    window.close()
                    pyglet.app.exit()
                    ctypes.windll.user32.MessageBoxW(0, str(error), "Druga Napaka", 1)

            @window.event
            def on_mouse_scroll(x, y, scroll_x, scroll_y):
                if scroll_y < 0:
                    self.skala -= 3
                    self.izrisiTloris(self.skala, window, self.xZamik, self.yZamik)
                else:
                    self.skala += 3
                    self.izrisiTloris(self.skala, window, self.xZamik, self.yZamik)

            @window.event
            def on_mouse_release(x, y, button, modifiers):
                if button == mouse.LEFT:
                    window.clear()
                    self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)

        except Exception as error:
            window.clear()
            window.close()
            pyglet.app.exit()
            ctypes.windll.user32.MessageBoxW(0, str(error), "Druga Napaka", 1)

    def izrisiNarisYZ(self, skalaVhod, window, zamikonx, zamikony):
        self.xZamik = zamikonx
        self.yZamik = zamikony
        self.skala = skalaVhod

        try:
            @window.event
            def on_draw():
                window.clear()

                directionYCoordinatesX = []
                directionYCoordinatesY = []
                steviloNadstropij = []

                # dobi y smer koordinate in stevilo nadstropij
                i = 0
                for element in self.elements:
                    if element.direction == "Y":
                        directionYCoordinatesX.append(element.coordinatesX)
                        directionYCoordinatesY.append(element.coordinatesY)
                        if element.numberOfStories == -1:
                            steviloNadstropij.append(self.numberOfStories)
                        else:
                            steviloNadstropij.append(element.numberOfStories)

                    i += 1

                visine = []
                visine.append(0.0)
                for i in range(0, self.storyHeights.__len__()):
                    if self.storyHeights[i].do == -1:
                        visine.append(self.storyHeights[i].visina * i)
                    else:
                        for j in range(self.storyHeights[i].od, self.storyHeights[i].do+1):
                            visine.append(self.storyHeights[i].visina * j)

                # naredi tocke
                tocke = []
                for i in range(0, visine.__len__()):
                    for j in range(0, directionYCoordinatesX.__len__()):
                        if steviloNadstropij[j] == -1:
                            tocke.append(Tocka(directionYCoordinatesX[j], visine[i]))
                            continue
                        elif i <= steviloNadstropij[j]:
                            tocke.append(Tocka(directionYCoordinatesX[j], visine[i]))
                            continue

                pyglet.gl.glPointSize(10)
                # izrisi tocke
                zacetneTocke = []
                koncneTocke = []
                tocke = sortPoX(tocke)
                seznamY = []
                for i in range(0, tocke.__len__()):
                    y = int(tocke[i].y * self.skala)
                    if y not in seznamY:
                        seznamY.append(y)
                for i in range(0, seznamY.__len__()):
                    y = seznamY[i]
                    if Tocka(10000, y) not in zacetneTocke:
                        zacetneTocke.append(Tocka(10000, y))
                for i in range(0, seznamY.__len__()):
                    y = seznamY[i]
                    if Tocka(0, y) not in koncneTocke:
                        koncneTocke.append(Tocka(0, y))

                for i in range(0, tocke.__len__()):
                    x1 = int(tocke[i].x * self.skala)
                    y1 = int(tocke[i].y * self.skala)

                    for j in range(0, seznamY.__len__()):
                        if zacetneTocke[j].y == y1:
                            if zacetneTocke[j].x > x1:
                                zacetneTocke[j].x = x1
                        if koncneTocke[j].y == y1:
                            if koncneTocke[j].x < x1:
                                koncneTocke[j].x = x1

                    pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2f', (x1 + self.xZamik, y1 + self.yZamik)))
                    label = pyglet.text.Label('(' + str(tocke[i].x) + ', ' + str(tocke[i].y) + ')', font_name='Times New Roman', font_size=8)
                    label.x = x1 + 10 + self.xZamik
                    label.y = y1 + 10 + self.yZamik
                    label.draw()

                # izrisi crte
                pyglet.gl.glLineWidth(2)
                for i in range(0, zacetneTocke.__len__()):
                    pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (
                    zacetneTocke[i].x + self.xZamik, zacetneTocke[i].y + self.yZamik, koncneTocke[i].x + self.xZamik,
                    koncneTocke[i].y + self.yZamik)), ('c3f', (.8, .8, .8) * 2))

                xZadnja = -1
                yZadnja = -1
                yPrva = -1
                for i in range(0, tocke.__len__()):
                    x = int(tocke[i].x * self.skala)
                    y = int(tocke[i].y * self.skala)
                    if (i == 0):
                        xZadnja = x
                        yPrva = y
                    elif (xZadnja != x):
                        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, (
                        'v2f', (xZadnja + self.xZamik, yPrva + self.yZamik, xZadnja + self.xZamik, yZadnja + self.yZamik)),
                                             ('c3f', (.8, .8, .8) * 2))
                        xZadnja = x
                        yPrva = y
                        yZadnja = y
                    elif (i == tocke.__len__() - 1):
                        yZadnja = y
                        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, (
                        'v2f', (xZadnja + self.xZamik, yPrva + self.yZamik, xZadnja + self.xZamik, yZadnja + self.yZamik)),
                                             ('c3f', (.8, .8, .8) * 2))
                    else:
                        yZadnja = y

            @window.event
            def on_text_motion(motion):
                try:
                    if motion == pyglet.window.key.MOTION_LEFT:
                        self.xZamik -= 10
                        self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                    elif motion == pyglet.window.key.MOTION_RIGHT:
                        self.xZamik += 10
                        self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                    elif motion == pyglet.window.key.MOTION_UP:
                        self.yZamik += 10
                        self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                    elif motion == pyglet.window.key.MOTION_DOWN:
                        self.yZamik -= 10
                        self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                except Exception as error:
                    window.clear()
                    window.close()
                    pyglet.app.exit()
                    ctypes.windll.user32.MessageBoxW(0, str(error), "Druga Napaka", 1)

            @window.event
            def on_key_press(symbol, modifiers):
                try:
                    if symbol == key.ENTER:
                        window.clear()
                        self.izrisiNarisXZ(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.LEFT:
                        self.xZamik -= 10
                        self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.RIGHT:
                        self.xZamik += 10
                        self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.UP:
                        self.yZamik += 10
                        self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.DOWN:
                        self.yZamik -= 10
                        self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                except Exception as error:
                    window.clear()
                    window.close()
                    pyglet.app.exit()
                    ctypes.windll.user32.MessageBoxW(0, str(error), "Druga Napaka", 1)

            @window.event
            def on_mouse_scroll(x, y, scroll_x, scroll_y):
                if scroll_y < 0:
                    self.skala -= 3
                    self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)
                else:
                    self.skala += 3
                    self.izrisiNarisYZ(self.skala, window, self.xZamik, self.yZamik)

            @window.event
            def on_mouse_release(x, y, button, modifiers):
                if button == mouse.LEFT:
                    window.clear()
                    self.izrisiNarisXZ(self.skala, window, self.xZamik, self.yZamik)

        except Exception as error:
            window.close()
            ctypes.windll.user32.MessageBoxW(0, str(error), "Druga Napaka", 1)

    def izrisiNarisXZ(self, skalaVhod, window, zamikonx, zamikony):
        self.xZamik = zamikonx
        self.yZamik = zamikony
        self.skala = skalaVhod
        
        try:
            @window.event
            def on_draw():
                window.clear()

                directionXCoordinatesX = []
                directionXCoordinatesY = []
                steviloNadstropij = []

                # dobi x smer koordinate
                i = 0
                for element in self.elements:
                    if element.direction == "X":
                        directionXCoordinatesX.append(element.coordinatesX)
                        directionXCoordinatesY.append(element.coordinatesY)
                        if element.numberOfStories == -1:
                            steviloNadstropij.append(self.numberOfStories)
                        else:
                            steviloNadstropij.append(element.numberOfStories)

                    i += 1

                visine = []
                visine.append(0.0)
                for i in range(0, self.storyHeights.__len__()):
                    if self.storyHeights[i].do == -1:
                        visine.append(self.storyHeights[i].visina * i)
                    else:
                        for j in range(self.storyHeights[i].od, self.storyHeights[i].do+1):
                            visine.append(self.storyHeights[i].visina * j)

                # naredi tocke
                tocke = []
                for i in range(0, visine.__len__()):
                    for j in range(0, directionXCoordinatesX.__len__()):
                        if steviloNadstropij[j] == -1:
                            tocke.append(Tocka(directionXCoordinatesX[j], visine[i]))
                            continue
                        elif i <= steviloNadstropij[j]:
                            tocke.append(Tocka(directionXCoordinatesY[j], visine[i]))
                            continue

                pyglet.gl.glPointSize(10)
                # izrisi tocke
                zacetneTocke = []
                koncneTocke = []
                tocke = sortPoX(tocke)
                seznamY = []
                for i in range(0, tocke.__len__()):
                    y = int(tocke[i].y * self.skala)
                    if y not in seznamY:
                        seznamY.append(y)
                for i in range(0, seznamY.__len__()):
                    y = seznamY[i]
                    if Tocka(10000, y) not in zacetneTocke:
                        zacetneTocke.append(Tocka(10000, y))
                for i in range(0, seznamY.__len__()):
                    y = seznamY[i]
                    if Tocka(0, y) not in koncneTocke:
                        koncneTocke.append(Tocka(0, y))

                for i in range(0, tocke.__len__()):
                    x1 = int(tocke[i].x * self.skala)
                    y1 = int(tocke[i].y * self.skala)

                    for j in range(0, seznamY.__len__()):
                        if zacetneTocke[j].y == y1:
                            if zacetneTocke[j].x > x1:
                                zacetneTocke[j].x = x1
                        if koncneTocke[j].y == y1:
                            if koncneTocke[j].x < x1:
                                koncneTocke[j].x = x1

                    pyglet.graphics.draw(1, pyglet.gl.GL_POINTS, ('v2f', (x1 + self.xZamik, y1 + self.yZamik)))
                    label = pyglet.text.Label('(' + str(tocke[i].x) + ', ' + str(tocke[i].y) + ')', font_name='Times New Roman', font_size=8)
                    label.x = x1 + 10 + self.xZamik
                    label.y = y1 + 10 + self.yZamik
                    label.draw()

                # izrisi crte
                pyglet.gl.glLineWidth(2)
                for i in range(0, zacetneTocke.__len__()):
                    pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (zacetneTocke[i].x + self.xZamik, zacetneTocke[i].y + self.yZamik, koncneTocke[i].x + self.xZamik, koncneTocke[i].y + self.yZamik)), ('c3f', (.8, .8, .8) * 2))

                xZadnja = -1
                yZadnja = -1
                yPrva = -1
                for i in range(0, tocke.__len__()):
                    x = int(tocke[i].x * self.skala)
                    y = int(tocke[i].y * self.skala)
                    if (i == 0):
                        xZadnja = x
                        yPrva = y
                    elif (xZadnja != x):
                        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (xZadnja + self.xZamik, yPrva + self.yZamik, xZadnja + self.xZamik, yZadnja + self.yZamik)), ('c3f', (.8, .8, .8) * 2))
                        xZadnja = x
                        yPrva = y
                        yZadnja = y
                    elif (i == tocke.__len__() - 1):
                        yZadnja = y
                        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', (xZadnja + self.xZamik, yPrva + self.yZamik, xZadnja + self.xZamik, yZadnja + self.yZamik)), ('c3f', (.8, .8, .8) * 2))
                    else:
                        yZadnja = y

            @window.event
            def on_text_motion(motion):
                try:
                    if motion == pyglet.window.key.MOTION_LEFT:
                        self.xZamik -= 10
                        self.izrisiNarisXZ(self.skala, window, self.xZamik, self.yZamik)
                    elif motion == pyglet.window.key.MOTION_RIGHT:
                        self.xZamik += 10
                        self.izrisiNarisXZ(self.skala, window, self.xZamik, self.yZamik)
                    elif motion == pyglet.window.key.MOTION_UP:
                        self.yZamik += 10
                        self.izrisiNarisXZ(self.skala, window, self.xZamik, self.yZamik)
                    elif motion == pyglet.window.key.MOTION_DOWN:
                        self.yZamik -= 10
                        self.izrisiNarisXZ(self.skala, window, self.xZamik, self.yZamik)
                except Exception as error:
                    window.clear()
                    window.close()
                    pyglet.app.exit()
                    ctypes.windll.user32.MessageBoxW(0, str(error), "Druga Napaka", 1)

            @window.event
            def on_key_press(symbol, modifiers):
                try:
                    if symbol == key.ENTER:
                        window.clear()
                        window.close()
                        pyglet.app.exit()
                    elif symbol == key.LEFT:
                        self.xZamik -= 10
                        self.izrisiNarisXZ(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.RIGHT:
                        self.xZamik += 10
                        self.izrisiNarisXZ(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.UP:
                        self.yZamik += 10
                        self.izrisiNarisXZ(self.skala, window, self.xZamik, self.yZamik)
                    elif symbol == key.DOWN:
                        self.yZamik -= 10
                        self.izrisiNarisXZ(self.skala, window, self.xZamik, self.yZamik)
                except Exception as error:
                    window.clear()
                    window.close()
                    pyglet.app.exit()
                    ctypes.windll.user32.MessageBoxW(0, str(error), "Druga Napaka", 1)

            @window.event
            def on_mouse_scroll(x, y, scroll_x, scroll_y):
                if scroll_y < 0:
                    self.skala -= 3
                    self.izrisiNarisXZ(self.skala, window, self.xZamik, self.yZamik)
                else:
                    self.skala += 3
                    self.izrisiNarisXZ(self.skala, window, self.xZamik, self.yZamik)

            @window.event
            def on_mouse_release(x, y, button, modifiers):
                if button == mouse.LEFT:
                    window.clear()
                    window.close()
                    pyglet.app.exit()

        except Exception as error:
            window.close()
            ctypes.windll.user32.MessageBoxW(0, str(error), "Druga Napaka", 1)
            traceback.print_exc()

def sortPoX(array):
    less = []
    equal = []
    greater = []

    if len(array) > 1:
        pivot = array[0].x
        for x in array:
            if x.x < pivot:
                less.append(x)
            if x.x == pivot:
                equal.append(x)
            if x.x > pivot:
                greater.append(x)
        # Don't forget to return something!
        return sortPoX(less) + sortPoY(equal) + sortPoX(greater)  # Just use the + operator to join lists
    # Note that you want equal ^^^^^ not pivot
    else:  # You need to hande the part at the end of the recursion - when you only have one element in your array, just return the array.
        return array

def sortPoY(array):
    less = []
    equal = []
    greater = []

    if len(array) > 1:
        pivot = array[0].y
        for x in array:
            if x.y < pivot:
                less.append(x)
            if x.y == pivot:
                equal.append(x)
            if x.y > pivot:
                greater.append(x)
        # Don't forget to return something!
        return sortPoY(less) + equal + sortPoY(greater)  # Just use the + operator to join lists
    # Note that you want equal ^^^^^ not pivot
    else:  # You need to hande the part at the end of the recursion - when you only have one element in your array, just return the array.
        return array

class TockaTloris:
    def __init__(self, x, y, lengthX, shiftX, lengthY, shiftY, typeX, typeY):
        self.x = x
        self.y = y
        self.lengthX = lengthX
        self.shiftX = shiftX
        self.lengthY = lengthY
        self.shiftY = shiftY
        self.typeX = typeX
        self.typeY = typeY

    def __str__(self):
        return "x: " + str(self.x) + ", y: " + str(self.y) + ": dolzina x: " + self.lengthX + ": zamik x: " + self.shiftX + ": dolzina y: " + self.lengthY + ": zamik y: " + self.shiftY

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class Tocka:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str(self.x) + ", " + str(self.y)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class CoordinateStartStop:
    def __init__(self, coordinate, start, stop, length, shift, type):
        self.coordinate = coordinate
        self.od = start
        self.do = stop
        self.length = length
        self.shift = shift
        self.type = type

class StoryHeight: #razredi vsak CLASS lahko EN __init__
    def __init__(self, od, do, visina):
        self.od = od
        self.do = do
        self.visina = visina

class Mass:
    def __init__(self, od, do, stevilka1, stevilka2, stevilka3, stevilka4):
        self.od = od
        self.do = do
        self.stevilka1 = stevilka1
        self.stevilka2 = stevilka2
        self.stevilka3 = stevilka3
        self.stevilka4 = stevilka4

class VerticalLoading:
    def __init__(self, od, do, stevilka1, stevilka2, stevilka3, stevilka4):
        self.od = od
        self.do = do
        self.stevilka1 = stevilka1
        self.stevilka2 = stevilka2
        self.stevilka3 = stevilka3
        self.stevilka4 = stevilka4

class SectionProperties:
    def __init__(self, od, do, list):
        self.od = od
        self.do = do
        self.list = list

class VerticalLoadings:
    def __init__(self, od, do, stevilke):
        self.od = od
        self.do = do
        self.stevilke = stevilke

class StaticLoading:
    def __init__(self, od, do, stevilka1, stevilka2, stevilka3):
        self.od = od
        self.do = do
        self.stevilka1 = stevilka1
        self.stevilka2 = stevilka2
        self.stevilka3 = stevilka3

class DynamicLoading:
    def __init__(self, od, do, i1, f1, t1, i2, f2, t2, i3, f3, t3):
        self.od = od
        self.do = do
        self.i1 = i1
        self.f1 = f1
        self.t1 = t1
        self.i2 = i2
        self.f2 = f2
        self.t2 = t2
        self.i3 = i3
        self.f3 = f3
        self.t3 = t3

class Element:
    def __init__(self):
        self.naziv = ''                 # STRING
        self.type = ''                  # STRING
        self.typeSwall = -1             # ni nujno potrebno (celo stevlo)
        self.numberOfStories = -1       # ni nujno potrebno (celo stevilo)
        self.direction = ''             # ni potrebno pri ravninski konstrukciji (X, Y, Z, X a (a decimalno stevilo))
        self.angle = -1                 # pri direction x a
        self.coordinatesX = 0          # ce ni ukaza je 0 (realno stevilo)
        self.coordinatesY = 0          # ce ni ukaza je 0 (realno stevilo)
        self.sectionProperties = []
        self.masses = []                # ni nujno potrebno
        self.factorSectionProperties = -1                # realno stevilo (ni nujno potrebno)
        self.factorMasses = -1                           # realno stevilo (ni nujno potrebno)
        self.factorVerticalLoadings = -1                 # realno stevilo (ni nujno potrebno)
        self.verticalLoadings = []      # ni nujno potrebno
        self.tabulateMatrices = False   # ni nujno potrebno
        # nas doprinos
        self.od = -1
        self.do = -1
        self.length = -1
        self.shift = -1

    def preberi(self, zacetekIndex, fileString, referenca):
        i = zacetekIndex
        while True:
            razdeljenaVrstica = fileString[i].split(" ")

            if (fileString[i].startswith("ELEM") or fileString[i].startswith("LOAD") or fileString[i].startswith("SOLV")) and i != zacetekIndex:
                if referenca.type == "SPACE" and self.direction == '' and not self.type.startswith("PELEMENT"):
                    raise ValueError("Elementu manjka ukaz direction!!!")
                return i - 1
            elif fileString[i].startswith("*") or fileString[i].startswith("PRIN"): #Prelom elementov za prvo besedo
                i = i + 1
                continue
            elif fileString[i].startswith("ELEM"):
                self.naziv = fileString[i].split(" ", 1)[1]
                if self.naziv.__contains__(" %% "):
                    temp = self.naziv.split(" %% ")
                    if temp.__len__() == 2:
                        if temp[1].__contains__(" $$ "):
                            stevila = temp[1].split(" ")
                            if stevila.__len__() == 4 or stevila.__len__() == 5:
                                self.od = convert(stevila[0])
                                self.do = convert(stevila[1])
                            else:
                                raise ValueError("Napaka pri %%!!! " + fileString[i])
                        else:
                            stevila = temp[1].split(" ")
                            if stevila.__len__() == 2:
                                self.od = convert(stevila[0])
                                self.do = convert(stevila[1])
                            else:
                                raise ValueError("Napaka pri %%!!! " + fileString[i])
                if self.naziv.__contains__(" $$ "):
                    temp = self.naziv.split(" $$ ")
                    if temp[1].__contains__(" %% "):
                        stevilke = temp[1].split(" ")
                        if len(stevilke) == 5:
                            self.length = convert(stevilke[0])
                            self.shift = convert(stevilke[1])
                        elif len(stevilke) == 4:
                            self.length = convert(stevilke[0])
                            self.shift = (-1) * (self.length / 2)
                        else:
                            raise ValueError("Napaka pri length ni v elementu wall ali swall!!! " + fileString[i])
                    else:
                        stevilke = temp[1].split(" ")
                        if len(stevilke) == 2:
                            self.length = convert(stevilke[0])
                            self.shift = convert(stevilke[1])
                        elif len(stevilke) == 1:
                            self.length = convert(stevilke[0])
                            self.shift = (-1) * (self.length / 2)
                        else:
                            raise ValueError("Napaka pri length ni v elementu wall ali swall!!! " + fileString[i])
            elif fileString[i].startswith("TYPE"):
                if razdeljenaVrstica[1].startswith("CANT"):
                    self.type = "CANTILEVER"
                elif razdeljenaVrstica[1].startswith("SCAN"):
                    self.type = "SCANTILEVER"
                elif razdeljenaVrstica[1].startswith("FRAM"):
                    self.type = "FRAME"
                elif razdeljenaVrstica[1].startswith("WALL"):
                    self.type = "WALL"
                elif razdeljenaVrstica[1].startswith("TUBE"):
                    self.type = "TUBE"
                elif razdeljenaVrstica[1].startswith("FLEX"):
                    self.type = "FLEXIBILITY"
                elif razdeljenaVrstica[1].startswith("STIF"):
                    self.type = "STIFFNESS"
                elif razdeljenaVrstica[1].startswith("PELE") and razdeljenaVrstica.__len__() == 2:
                    elem = referenca.elements.__getitem__(referenca.elements.__len__() - 1)
                    self.copy(elem)
                elif razdeljenaVrstica[1].startswith("PELE") and razdeljenaVrstica.__len__() == 3:
                    str = fileString[i].split(" ")
                    if len(str) == 3:
                        elem = referenca.elements.__getitem__(int(str[2]) - 1)
                        self.copy(elem)
                    else:
                        raise ValueError("Napaka pri pelement v elementu!!!")
                elif razdeljenaVrstica[1].startswith("SWAL"):
                    self.type = "SWALL"
                    str = fileString[i].split(" ")
                    if len(str) == 3:
                        self.element = "SWALL" + int(str[2]).__str__()
                    else:
                        raise ValueError("Napaka pri swall v elementu!!!")
                else:
                    raise ValueError("TYPE ni regularen!!! " + fileString[i])
            elif fileString[i].startswith("NUMB"):
                if not razdeljenaVrstica[0].startswith("NUMB")and not razdeljenaVrstica[1].startswith("OF") and not razdeljenaVrstica[2].startswith("STOR"):
                    raise ValueError("napaka pri number of stories v elementu " + fileString[i])
                stevilka = int(fileString[i].rsplit(" ", 1)[1])
                if (stevilka > 30):
                    raise ValueError("Več kot 30 nadstropij!!!")
                self.numberOfStories = stevilka
            elif fileString[i].startswith("DIRE") and referenca.type != "SPACE":
                raise  ValueError("Napaka direction ni v ravninski konstrukciji!!!")
            elif fileString[i].startswith("DIRE"):
                if razdeljenaVrstica[0].startswith("DIRE") and razdeljenaVrstica[1].startswith("X") and razdeljenaVrstica.__len__() == 2:
                    self.direction = "X"
                elif razdeljenaVrstica[0].startswith("DIRE") and razdeljenaVrstica[1].startswith("Y"):
                    self.direction = "Y"
                elif razdeljenaVrstica[0].startswith("DIRE") and razdeljenaVrstica[1].startswith("Z"):
                    self.direction = "Z"
                elif razdeljenaVrstica[0].startswith("DIRE") and razdeljenaVrstica[1].startswith("X"):
                    str = fileString[i].split(" ")
                    if len(str) == 3:
                        self.angle = convert(str[2])
                    else:
                        raise ValueError("Napaka pri element direction x!!!")
                else:
                    raise ValueError("Napaka pri direction element")
            elif fileString[i].startswith("COOR"):
                str = fileString[i].split(" ")
                if len(str) == 3:
                    self.coordinatesX = convert(str[1])
                    self.coordinatesY = convert(str[2])
                elif len(str) == 2:
                    self.coordinatesX = convert(str[1])
                    self.coordinatesY = float("0")
                else:
                    raise ValueError("Napaka pri element coordinates!!! " + fileString[i])
            elif fileString[i].startswith("SECT"):
                if not razdeljenaVrstica[0].startswith("SECT") and not razdeljenaVrstica[1].startswith("PROP"):
                    raise ValueError("napaka pri section properties v elementu " + fileString[i])
                j = 1
                while (fileString[i + j][0].isdigit()):
                    if ("THRU" not in fileString[i + j]):
                        spremenljivkeList = fileString[i + j].split(" ")
                        stevilke = spremenljivkeList[1:]
                        stevilkeconvert = []
                        for stevilka in stevilke:
                            stevilkeconvert.append(convert(stevilka))
                        self.sectionProperties.append(SectionProperties(int(spremenljivkeList[0]), -1, stevilkeconvert))
                        j += 1
                    else:
                        spremenljivkeList = fileString[i + j].split(" ")
                        stevilke = spremenljivkeList[3:]
                        stevilkeconvert = []
                        for stevilka in stevilke:
                            stevilkeconvert.append(convert(stevilka))
                        self.sectionProperties.append(
                            SectionProperties(int(spremenljivkeList[0]), int(spremenljivkeList[2]), stevilkeconvert))
                        if j != 1:
                            if self.sectionProperties[j-1].od != self.sectionProperties[j - 2].do + 1:
                                raise ValueError("Napaka pri masah!!!")
                        j += 1
                i = i + j - 1
                if (fileString[i].startswith("FACTOR")):
                    self.factorSectionProperties = convert(fileString[i].split(" ")[1])
            elif fileString[i].startswith("MASS"):
                j = 1
                while (fileString[i + j][0].isdigit()):
                    if ("THRU" not in fileString[i + j]): #Če ni THRU potem povsod vzame enako vrednost
                        spremenljivkeList = fileString[i + j].split(" ")
                        self.masses.append(Mass(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1])))
                        j += 1
                    else:
                        spremenljivkeList = fileString[i + j].split(" ")
                        self.masses.append(Mass(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3])))
                        if j != 1:
                            if self.masses[j-1].od != self.masses[j-2].do + 1:
                                raise ValueError("Napaka pri masah!!!")
                        j += 1
                if self.masses[0].od != 1:
                    raise ValueError("Napaka pri masah!!!")
                i = i + j
                if (fileString[i].startswith("FACTOR")):
                    self.factorMasses = convert(fileString[i].split(" ")[1])
            elif fileString[i].startswith("VERT"):
                if not razdeljenaVrstica[0].startswith("VERT") and not razdeljenaVrstica[1].startswith("LOAD"):
                    raise ValueError("napaka pri vertical loadings v elementu " + fileString[i])
                j = 1
                while (fileString[i + j][0].isdigit()):
                    if ("THRU" not in fileString[i + j]):
                        spremenljivkeList = fileString[i + j].split(" ")
                        self.verticalLoadings.append(VerticalLoadings(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1])))
                        j += 1
                    else:
                        spremenljivkeList = fileString[i + j].split(" ")
                        self.verticalLoadings.append(VerticalLoadings(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3])))
                        if j != 1:
                            if self.verticalLoadings[j-1].od != self.verticalLoadings[j-2].do + 1:
                                raise ValueError("Napaka pri masah!!!")
                        j += 1
                if self.verticalLoadings[0].od != 1:
                    raise ValueError("Napaka pri masah!!!")
                i = i + j - 1
                if (fileString[i].startswith("FACT")):
                    self.factorVerticalLoadings = convert(fileString[i].split(" ")[1])
            elif fileString[i].startswith("TABU"):
                if razdeljenaVrstica[0].startswith("TABU") and razdeljenaVrstica[1].startswith("MATR"):
                    self.tabulateMatrices = True
                else:
                    raise ValueError("napaka pri tabulate matrices v elementu " + fileString[i])


            i = i + 1

    def preberiSkrajsano(self, zacetekIndex, fileString, referenca):
        i = zacetekIndex
        while True:
            if (fileString[i].startswith("ELEM") or fileString[i].startswith("LOAD") or fileString[i].startswith("SOLV")) and i != zacetekIndex:
                if referenca.type == "SPACE" and self.direction == '' and not self.type.startswith("PELEMENT"):
                    raise ValueError("Elementu manjka ukaz direction!!!")
                return i - 1
            elif fileString[i].startswith("*") or fileString[i].startswith("PRIN"): #Prelom elementov za prvo besedo
                i = i + 1
                continue
            elif fileString[i].startswith("ELEM"):
                self.naziv = fileString[i].split(" ", 1)[1]
                if self.naziv.__contains__("%% "):
                    temp = self.naziv.split("%% ")
                    if temp.__len__() == 2:
                        stevila = temp[1].split(" ")
                        if stevila.__len__() == 2:
                            self.od = convert(stevila[0])
                            self.do = convert(stevila[1])
            elif fileString[i].startswith("TYPE"):
                if fileString[i] == "TYPE CANT\n":
                    self.type = "CANTILEVER"
                elif fileString[i] == "TYPE SCAN\n":
                    self.type = "SCANTILEVER"
                elif fileString[i] == "TYPE FRAM\n":
                    self.type = "FRAME"
                elif fileString[i] == "TYPE WALL\n":
                    self.type = "WALL"
                elif fileString[i] == "TYPE TUBE\n":
                    self.type = "TUBE"
                elif fileString[i] == "TYPE FLEX\n":
                    self.type = "FLEXIBILITY"
                elif fileString[i] == "TYPE STIF\n":
                    self.type = "STIFFNESS"
                elif fileString[i] == "TYPE PELE\n":
                    elem = referenca.elements.__getitem__(referenca.elements.__len__() - 1)
                    self.copy(elem)
                elif fileString[i].startswith("TYPE PELE"):
                    str = fileString[i].split(" ")
                    if len(str) == 3:
                        elem = referenca.elements.__getitem__(int(str[2]) - 1)
                        self.copy(elem)
                    else:
                        raise ValueError("Napaka pri pelement v elementu!!!")
                elif fileString[i].startswith("TYPE SWAL"):
                    str = fileString[i].split(" ")
                    if len(str) == 3:
                        self.element = "SWALL" + int(str[2]).__str__()
                    else:
                        raise ValueError("Napaka pri swall v elementu!!!")
                else:
                    raise ValueError("TYPE ni regularen!!! " + fileString[i])
            elif fileString[i].startswith("NUMB OF STOR"):
                stevilka = int(fileString[i].rsplit(" ", 1)[1])
                if (stevilka > 30):
                    raise ValueError("Več kot 30 nadstropij!!!")
                self.numberOfStories = stevilka
            elif fileString[i].startswith("DIRE") and referenca.type != "SPACE":
                raise  ValueError("Napaka direction ni v ravninski konstrukciji!!!")
            elif fileString[i].startswith("DIRE"):
                if fileString[i] == "DIRE X\n":
                    self.direction = "X"
                elif fileString[i] == "DIRE Y\n":
                    self.direction = "Y"
                elif fileString[i] == "DIRE Z\n":
                    self.direction = "Z"
                elif fileString[i].startswith("DIRE X"):
                    str = fileString[i].split(" ")
                    if len(str) == 3:
                        self.angle = convert(str[2])
                    else:
                        raise ValueError("Napaka pri element direction x!!!")
                else:
                    raise ValueError("Napaka pri direction element")
            elif fileString[i].startswith("COOR"):
                str = fileString[i].split(" ")
                if len(str) == 3:
                    self.coordinatesX = convert(str[1])
                    self.coordinatesY = convert(str[2])
                elif len(str) == 2:
                    self.coordinatesX = convert(str[1])
                    self.coordinatesY = float("0")
                else:
                    raise ValueError("Napaka pri element coordinates!!! " + fileString[i])
            elif fileString[i].startswith("SECT PROP"):
                j = 1
                while (fileString[i + j][0].isdigit()):
                    if ("THRU" not in fileString[i + j]):
                        spremenljivkeList = fileString[i + j].split(" ")
                        stevilke = spremenljivkeList[1:]
                        stevilkeconvert = []
                        for stevilka in stevilke:
                            stevilkeconvert.append(convert(stevilka))
                        self.sectionProperties.append(SectionProperties(int(spremenljivkeList[0]), -1, stevilkeconvert))
                        j += 1
                    else:
                        spremenljivkeList = fileString[i + j].split(" ")
                        stevilke = spremenljivkeList[3:]
                        stevilkeconvert = []
                        for stevilka in stevilke:
                            stevilkeconvert.append(convert(stevilka))
                        self.sectionProperties.append(
                            SectionProperties(int(spremenljivkeList[0]), int(spremenljivkeList[2]), stevilkeconvert))
                        if j != 1:
                            if self.sectionProperties[j-1].od != self.sectionProperties[j - 2].do + 1:
                                raise ValueError("Napaka pri masah!!!")
                        j += 1
                i = i + j - 1
                if (fileString[i].startswith("FACT")):
                    self.factorSectionProperties = convert(fileString[i].split(" ")[1])
            elif fileString[i].startswith("MASS"):
                j = 1
                while (fileString[i + j][0].isdigit()):
                    if ("THRU" not in fileString[i + j]): #Če ni THRU potem povsod vzame enako vrednost
                        spremenljivkeList = fileString[i + j].split(" ")
                        self.masses.append(Mass(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1])))
                        j += 1
                    else:
                        spremenljivkeList = fileString[i + j].split(" ")
                        self.masses.append(Mass(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3])))
                        if j != 1:
                            if self.masses[j-1].od != self.masses[j-2].do + 1:
                                raise ValueError("Napaka pri masah!!!")
                        j += 1
                if self.masses[0].od != 1:
                    raise ValueError("Napaka pri masah!!!")
                i = i + j
                if (fileString[i].startswith("FACT")):
                    self.factorMasses = convert(fileString[i].split(" ")[1])
            elif fileString[i].startswith("VERT LOAD"):
                j = 1
                while (fileString[i + j][0].isdigit()):
                    if ("THRU" not in fileString[i + j]):
                        spremenljivkeList = fileString[i + j].split(" ")
                        self.verticalLoadings.append(VerticalLoadings(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1])))
                        j += 1
                    else:
                        spremenljivkeList = fileString[i + j].split(" ")
                        self.verticalLoadings.append(VerticalLoadings(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3])))
                        if j != 1:
                            if self.verticalLoadings[j-1].od != self.verticalLoadings[j-2].do + 1:
                                raise ValueError("Napaka pri masah!!!")
                        j += 1
                if self.verticalLoadings[0].od != 1:
                    raise ValueError("Napaka pri masah!!!")
                i = i + j - 1
                if (fileString[i].startswith("FACT")):
                    self.factorVerticalLoadings = convert(fileString[i].split(" ")[1])
            elif fileString[i] == "TABU MATR\n":
                self.tabulateMatrices = True
            elif fileString[i].startswith("LENG"):
                if self.type == "WALL" or self.type == "SWALL":
                    str = fileString[i].split(" ")
                    if len(str) == 3:
                        self.length = convert(str[1])
                        self.shift = convert(str[2])
                    elif len(str) == 2:
                        self.length = convert(str[1])
                        self.shift = -1
                    else:
                        raise ValueError("Napaka pri length elementa wall ali swall!!! " + fileString[i])
                else:
                    raise ValueError("Napaka pri length ni v elementu wall ali swall!!! " + fileString[i])

            i = i + 1

    def copy(self, element):
        self.type = element.type
        self.numberOfStories = element.numberOfStories
        self.direction = element.direction
        self.coordinatesY = element.coordinatesY
        self.coordinatesX = element.coordinatesX
        self.sectionProperties = element.sectionProperties
        self.factorVerticalLoadings = element.factorVerticalLoadings
        self.angle = element.angle
        self.factorMasses = element.factorMasses
        self.sectionProperties = element.sectionProperties
        self.typeSwall = element.typeSwall
        self.masses = element.masses
        self.tabulateMatrices = element.tabulateMatrices
        self.length = element.length
        self.shift = element.shift
        self.od = element.od
        self.do = element.do

    def izpisi(self):
        returnString = "ELEM " + self.naziv
        returnString += "TYPE " + self.type[0:4] + "\n"
        if self.numberOfStories != -1:
            returnString += "NUMB OF STOR " + self.numberOfStories.__str__() + "\n"
        if self.direction != '' and self.angle == -1:
            returnString += "DIRE " + self.direction.__str__() + "\n"
        elif self.direction != '':
            returnString += "DIRE " + self.direction.__str__() + " " + self.angle.__str__() + "\n"
        returnString += "COOR " + self.coordinatesX.__str__() + " " + self.coordinatesY.__str__() + "\n"
        if len(self.sectionProperties) == 0:
            # raise ValueError("Napaka manjka section properties!!!")
            pass
        else:
            returnString += "SECT PROP\n"
            for line in self.sectionProperties:
                if line.do == -1:
                    returnString += str(line.od) + " "
                    for stevilka in line.list:
                        returnString += str(stevilka) + " "
                    returnString += "\n"
                else:
                    returnString += str(line.od) + " " + str(line.do) + " "
                    for stevilka in line.list:
                        returnString += str(stevilka) + " "
                    returnString += "\n"
            if self.factorSectionProperties != -1:
                returnString += "FACT " + str(self.factorSectionProperties) + "\n"
        if len(self.masses) != 0:
            returnString += "MASS\n"
            for line in self.masses:
                if line.do == -1:
                    returnString += str(line.od) + " " + str(line.stevilka1) + "\n"
                else:
                    returnString += str(line.od) + " " + "THRU " + str(line.do) + " " + str(line.stevilka1) + "\n"
            if self.factorMasses != -1:
                returnString += "FACT " + str(self.factorMasses) + "\n"
        if len(self.verticalLoadings) != 0:
            returnString += "VERT LOAD\n"
            for line in self.verticalLoadings:
                if line.do == -1:
                    returnString += str(line.od) + " " + str(line.stevilka1) + "\n"
                else:
                    returnString += str(line.od) + " " + "THRU " + str(line.do) + " " + str(line.stevilka1) + "\n"
            if self.factorVerticalLoadings != -1:
                returnString += "FACT " + str(self.factorVerticalLoadings) + "\n"
        if self.tabulateMatrices == True:
            returnString += "TABU MATR\n" #Okrajšave zapisov določenih ukazov
        if self.length != -1:
            if self.shift == -1:
                returnString += "LENG " + str(self.length) + "\n"
            else:
                returnString += "LENG " + str(self.length) + " " + str(self.shift) + "\n"

        return returnString

class Loading: #razredi za obtežbe
    def __init__(self):
        self.naziv = ''
        self.type = ''
        self.typeYuspectrum = -1        # samo ce je type youspectrum (celostevilo)
        self.tabulate = ''
        self.staticLoads = []
        self.kc = -1                    # ce je ta ni functiona
        self.factor1 = -1
        self.factor2 = -1
        self.factor3 = -1
        self.functionNaziv = ''         # ce je ta ni kc
        self.function = []              # stevilke naredi class (t in f) (realna stevila)
        self.damping1 = -1
        self.damping2 = -1
        self.damping3 = -1
        self.damping4 = -1
        self.damping5 = -1
        self.damping6 = -1
        self.damping7 = -1
        self.damping8 = -1
        self.damping9 = -1
        self.earthquakeI = []            # stevilke naredi class (i (celo stevilo), f in t (realni stevili))
        self.earthquakeF = []
        self.earthquakeT = []
        self.dynamicLoads = []          # naredi class (od, do (celi stevili), i1,2,3 (cela stevila), f1,2,3 in t1,2,3 (realna stevila))
        self.numberOfTimeStamps = -1    # celo stevilo
        self.lastTime = -1              # realno stevilo
        self.compute = ''               # NFORCES ali FORCES

    def preberiSkrajsano(self, zacetekIndex, fileString, typeBase):
        i = zacetekIndex
        while True:
            if fileString[i].startswith("*") or fileString[i].startswith("PRIN"): #Izbriše te ukaze oz. komentarje
                i = i + 1
                continue
            elif fileString[i].startswith("LOAD") and i == zacetekIndex:
                self.naziv = fileString[i].split(" ", 1)[1]
            elif fileString[i].startswith("TYPE"):
                if fileString[i] == "TYPE STAT\n":
                    self.type = "STATIC" #Statičen način obtežbe
                    i = i + 1
                    while True:
                        if (fileString[i].startswith("LOAD") or fileString[i].startswith("SOLV")) and i != zacetekIndex:
                            return i - 1
                        elif fileString[i].startswith("*") or fileString[i].startswith("PRIN"):
                            i = i + 1
                            continue
                        elif fileString[i].startswith("TABU"):
                            spremenljivke = fileString[i].split(" ", 1)
                            self.tabulate += spremenljivke[1] + " "
                        elif fileString[i].startswith("STAT LOAD"):
                            j = 1
                            while (fileString[i + j][0].isdigit()):
                                if ("THRU" not in fileString[i + j]):
                                    spremenljivkeList = fileString[i + j].split(" ")
                                    self.staticLoads.append(StaticLoading(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3])))
                                    j += 1
                                else:
                                    spremenljivkeList = fileString[i + j].split(" ")
                                    self.staticLoads.append(StaticLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5])))
                                    j += 1
                            i = i + j - 1
                        else:
                            raise ValueError("Napaka pri Loadingih " + fileString[i])
                        i = i + 1
                elif fileString[i].startswith("TYPE YUSP"):
                    self.type = "YUSPECTRUM"
                    try:
                        self.typeYuspectrum = int(fileString[i].split(" ")[2].__str__())
                    except:
                        self.typeYuspectrum = 1
                    i = i + 1
                    while True:
                        if (self.typeYuspectrum > 3 or self.typeYuspectrum < 1):
                            raise ValueError("Napaka yuspectrum številka je večja od 3 ali manjša 1!!!")
                        elif fileString[i].startswith("TABU"):
                            spremenljivke = fileString[i].split(" ", 1)
                            self.tabulate += spremenljivke[1] + " "
                        elif fileString[i].startswith("KC"):
                            self.kc = convert(fileString[i].split(" ")[1])
                        elif fileString[i].startswith("FACT"):
                            spremenljivkeList = fileString[i].split(" ")
                            if len(spremenljivkeList) == 2:
                                self.factor1 = convert(spremenljivkeList[1])
                            elif len(spremenljivkeList) == 3:
                                self.factor1 = convert(spremenljivkeList[1])
                                self.factor2 = convert(spremenljivkeList[2])
                            elif len(spremenljivkeList) == 4:
                                self.factor1 = convert(spremenljivkeList[1])
                                self.factor2 = convert(spremenljivkeList[2])
                                self.factor3 = convert(spremenljivkeList[3])
                        elif fileString[i].startswith("*") or fileString[i].startswith("PRIN"):
                            i = i + 1
                            continue
                        elif fileString[i].startswith("SOLV") or fileString[i].startswith("LOAD"):
                            return i - 1
                        i = i + 1
                elif fileString[i] == "TYPE SPEC\n":
                    self.type = "SPECTRUM"
                    i = i + 1
                    while True:
                        if fileString[i].startswith("TABU"):
                            spremenljivke = fileString[i].split(" ", 1)
                            self.tabulate += spremenljivke[1] + " "
                        elif fileString[i].startswith("FUNC"):
                            self.functionNaziv = fileString[i].split(" ")[1]
                            j = 1
                            while (fileString[i + j][0].isdigit()):
                                spremenljivkeList = fileString[i + j].split(" ")
                                for spremenljivka in spremenljivkeList:
                                    self.function.append()
                                j = j + 1
                        elif fileString[i].startswith("FACT"):
                            spremenljivkeList = fileString[i].split(" ")
                            if len(spremenljivkeList) == 2:
                                self.factor1 = convert(spremenljivkeList[1])
                            elif len(spremenljivkeList) == 3:
                                self.factor1 = convert(spremenljivkeList[1])
                                self.factor2 = convert(spremenljivkeList[2])
                            elif len(spremenljivkeList) == 4:
                                self.factor1 = convert(spremenljivkeList[1])
                                self.factor2 = convert(spremenljivkeList[2])
                                self.factor3 = convert(spremenljivkeList[3])
                        elif fileString[i].startswith("*") or fileString[i].startswith("PRIN"):
                            i = i + 1
                            continue
                        elif fileString[i].startswith("SOLV") or fileString[i].startswith("LOAD"):
                            return i - 1
                        i = i + 1
                elif fileString[i] == "TYPE RESP HIST\n":
                    self.type = "RESPONSE HISTORY"
                    i = i + 1
                    while True:
                        if fileString[i].startswith("TABU"):
                            spremenljivke = fileString[i].split(" ", 1)
                            self.tabulate += spremenljivke[1] + " "
                        elif fileString[i].startswith("DAMP"):
                            spremenljivke = fileString[i].split(" ")
                            j = 0
                            for spremenljivka in spremenljivke: #Definiramo spremenljivke za dusenje ni potrebno da vse obstajajo
                                if j == 0:
                                    continue
                                elif j == 1:
                                    self.damping1 = convert(spremenljivka)
                                elif j == 2:
                                    self.damping2 = convert(spremenljivka)
                                elif j == 3:
                                    self.damping3 = convert(spremenljivka)
                                elif j == 4:
                                    self.damping4 = convert(spremenljivka)
                                elif j == 5:
                                    self.damping5 = convert(spremenljivka)
                                elif j == 6:
                                    self.damping6 = convert(spremenljivka)
                                elif j == 7:
                                    self.damping7 = convert(spremenljivka)
                                elif j == 8:
                                    self.damping8 = convert(spremenljivka)
                                elif j == 9:
                                    self.damping9 = convert(spremenljivka)
                                j = j + 1
                        elif fileString[i].startswith("EART"): # Če se string začne z ''
                            spremenljivke = fileString[i].split(" ")
                            j = 0
                            for spremenljivka in spremenljivke:
                                if j == 0:
                                    continue
                                elif j % 3 == 1:
                                    self.earthquakeI.append(int(spremenljivka))
                                elif j % 3 == 2:
                                    self.earthquakeF.append(convert(spremenljivka))
                                elif j % 3 == 0:
                                    self.earthquakeT.append(convert(spremenljivka))
                        elif fileString[i].startswith("DYNA LOAD"):
                            j = 1
                            while (fileString[i + j][0].isdigit()):
                                if ("THRU" not in fileString[i + j]):
                                    spremenljivkeList = fileString[i + j].split(" ")
                                    if len(spremenljivkeList) == 10:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), -1, int(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), int(spremenljivkeList[4]), convert(spremenljivkeList[5]), convert(spremenljivkeList[6]), int(spremenljivkeList[7]), convert(spremenljivkeList[8]), convert(spremenljivkeList[9])))
                                    elif len(spremenljivkeList) == 9:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), -1, int(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), int(spremenljivkeList[4]), convert(spremenljivkeList[5]), convert(spremenljivkeList[6]), int(spremenljivkeList[7]), convert(spremenljivkeList[8]), -1))
                                    elif len(spremenljivkeList) == 7:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), -1, int(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), int(spremenljivkeList[4]), convert(spremenljivkeList[5]), convert(spremenljivkeList[6]), -1, -1, -1))
                                    elif len(spremenljivkeList) == 6:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), -1, int(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), int(spremenljivkeList[4]), convert(spremenljivkeList[5]), -1, -1, -1, -1))
                                    elif len(spremenljivkeList) == 4:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), -1, int(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), -1, -1, -1, -1, -1, -1))
                                    elif len(spremenljivkeList) == 3:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), -1, int(spremenljivkeList[1]), convert(spremenljivkeList[2]), -1, -1, -1, -1, -1, -1, -1))
                                else:
                                    spremenljivkeList = fileString[i + j].split(" ")
                                    if len(spremenljivkeList) == 12:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), int(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), int(spremenljivkeList[6]), convert(spremenljivkeList[7]), convert(spremenljivkeList[8]), int(spremenljivkeList[9]), convert(spremenljivkeList[10]), convert(spremenljivkeList[11])))
                                    elif len(spremenljivkeList) == 11:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), int(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), int(spremenljivkeList[6]), convert(spremenljivkeList[7]), convert(spremenljivkeList[8]), int(spremenljivkeList[9]), convert(spremenljivkeList[10]), -1))
                                    elif len(spremenljivkeList) == 9:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), int(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), int(spremenljivkeList[6]), convert(spremenljivkeList[7]), convert(spremenljivkeList[8]), -1, -1, -1))
                                    elif len(spremenljivkeList) == 8:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), int(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), int(spremenljivkeList[6]), convert(spremenljivkeList[7]), -1, -1, -1, -1))
                                    elif len(spremenljivkeList) == 6:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), int(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), int(spremenljivkeList[6]), -1, -1, -1, -1, -1))
                                    elif len(spremenljivkeList) == 5:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), int(spremenljivkeList[3]), convert(spremenljivkeList[4]), -1, -1, -1, -1, -1, -1, -1))
                                    j += 1
                            i = i + j
                        elif fileString[i].startswith("NUMB OF TIME"): # število intervalov
                            self.numberOfTimeStamps = int(fileString[i].rsplit(" ", 1)[1])
                        elif fileString[i].startswith("LAST TIME"): #zaden interval
                            self.lastTime = convert(fileString[i].rsplit(" ", 1)[1])
                        elif fileString[i].startswith("COMP"):
                            if fileString[i] == "COMP FORC\n":
                                self.compute = "FORCES"
                            elif fileString[i] == "COMP NFOR\n":
                                self.compute = "NFORCES"
                            else:
                                raise ValueError("Napaka pri Compute!!!")
                        elif fileString[i].startswith("*") or fileString[i].startswith("PRIN") or fileString[i].startswith("PLOT"):
                            i = i + 1
                            continue
                        elif fileString[i].startswith("SOLV") or fileString[i].startswith("LOAD"):
                            return i - 1
                        i = i + 1
                i = i + 1
            else:
                raise ValueError("Napaka pri Loadingu!!! " + fileString[i])
            i = i + 1

    def preberi(self, zacetekIndex, fileString, typeBase):
        i = zacetekIndex
        while True:
            razdeljenaVrstica = fileString[i].split(" ")
            if fileString[i].startswith("*") or fileString[i].startswith("PRIN"): #Izbriše te ukaze oz. komentarje
                i = i + 1
                continue
            elif fileString[i].startswith("LOAD") and i == zacetekIndex:
                self.naziv = fileString[i].split(" ", 1)[1]
            elif fileString[i].startswith("TYPE"):
                if razdeljenaVrstica[0].startswith("TYPE") and razdeljenaVrstica[1].startswith("STAT"):
                    self.type = "STATIC" #Statičen način obtežbe
                    i = i + 1
                    while True:
                        razdeljenaVrstica = fileString[i].split(" ")
                        if (fileString[i].startswith("LOAD") or fileString[i].startswith("SOLV")) and i != zacetekIndex:
                            return i - 1
                        elif fileString[i].startswith("*") or fileString[i].startswith("PRIN"):
                            i = i + 1
                            continue
                        elif fileString[i].startswith("TABU"):
                            spremenljivke = fileString[i].split(" ", 1)
                            self.tabulate += spremenljivke[1] + " "
                        elif fileString[i].startswith("STAT"):
                            if not razdeljenaVrstica[0].startswith("STAT") and not razdeljenaVrstica[1].startswith("LOAD"):
                                raise ValueError("napaka pri loadingu staitc loadings" + fileString[i])
                            j = 1
                            while (fileString[i + j][0].isdigit()):
                                if ("THRU" not in fileString[i + j]):
                                    spremenljivkeList = fileString[i + j].split(" ")
                                    self.staticLoads.append(StaticLoading(int(spremenljivkeList[0]), -1, convert(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3])))
                                    j += 1
                                else:
                                    spremenljivkeList = fileString[i + j].split(" ")
                                    self.staticLoads.append(StaticLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), convert(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5])))
                                    j += 1
                            i = i + j - 1
                        else:
                            raise ValueError("Napaka pri Loadingih " + fileString[i])
                        i = i + 1
                elif razdeljenaVrstica[0].startswith("TYPE") and razdeljenaVrstica[1].startswith("YUSP"):
                    self.type = "YUSPECTRUM"
                    try:
                        self.typeYuspectrum = int(fileString[i].split(" ")[2].__str__())
                    except:
                        self.typeYuspectrum = 1
                    i = i + 1
                    while True:
                        if (self.typeYuspectrum > 3 or self.typeYuspectrum < 1):
                            raise ValueError("Napaka yuspectrum številka je večja od 3 ali manjša 1!!!")
                        elif fileString[i].startswith("TABU"):
                            spremenljivke = fileString[i].split(" ", 1)
                            self.tabulate += spremenljivke[1] + " "
                        elif fileString[i].startswith("KC"):
                            self.kc = convert(fileString[i].split(" ")[1])
                        elif fileString[i].startswith("FACT"):
                            spremenljivkeList = fileString[i].split(" ")
                            if len(spremenljivkeList) == 2:
                                self.factor1 = convert(spremenljivkeList[1])
                            elif len(spremenljivkeList) == 3:
                                self.factor1 = convert(spremenljivkeList[1])
                                self.factor2 = convert(spremenljivkeList[2])
                            elif len(spremenljivkeList) == 4:
                                self.factor1 = convert(spremenljivkeList[1])
                                self.factor2 = convert(spremenljivkeList[2])
                                self.factor3 = convert(spremenljivkeList[3])
                        elif fileString[i].startswith("*") or fileString[i].startswith("PRIN"):
                            i = i + 1
                            continue
                        elif fileString[i].startswith("SOLV") or fileString[i].startswith("LOAD"):
                            return i - 1
                        i = i + 1
                elif razdeljenaVrstica[0].startswith("TYPE") and razdeljenaVrstica[1].startswith("SPEC"):
                    self.type = "SPECTRUM"
                    i = i + 1
                    while True:
                        if fileString[i].startswith("TABU"):
                            spremenljivke = fileString[i].split(" ", 1)
                            self.tabulate += spremenljivke[1] + " "
                        elif fileString[i].startswith("FUNC"):
                            self.functionNaziv = fileString[i].split(" ")[1]
                            j = 1
                            while (fileString[i + j][0].isdigit()):
                                spremenljivkeList = fileString[i + j].split(" ")
                                for spremenljivka in spremenljivkeList:
                                    self.function.append()
                                j = j + 1
                        elif fileString[i].startswith("FACT"):
                            spremenljivkeList = fileString[i].split(" ")
                            if len(spremenljivkeList) == 2:
                                self.factor1 = convert(spremenljivkeList[1])
                            elif len(spremenljivkeList) == 3:
                                self.factor1 = convert(spremenljivkeList[1])
                                self.factor2 = convert(spremenljivkeList[2])
                            elif len(spremenljivkeList) == 4:
                                self.factor1 = convert(spremenljivkeList[1])
                                self.factor2 = convert(spremenljivkeList[2])
                                self.factor3 = convert(spremenljivkeList[3])
                        elif fileString[i].startswith("*") or fileString[i].startswith("PRIN"):
                            i = i + 1
                            continue
                        elif fileString[i].startswith("SOLVE") or fileString[i].startswith("LOAD"):
                            return i - 1
                        i = i + 1
                elif razdeljenaVrstica[0].startswith("TYPE") and razdeljenaVrstica[1].startswith("RESP") and razdeljenaVrstica[2].startswith("HIST"):
                    self.type = "RESPONSE HISTORY"
                    i = i + 1
                    while True:
                        razdeljenaVrstica = fileString[i].split(" ")
                        if fileString[i].startswith("TABU"):
                            spremenljivke = fileString[i].split(" ", 1)
                            self.tabulate += spremenljivke[1] + " "
                        elif fileString[i].startswith("DAMP"):
                            spremenljivke = fileString[i].split(" ")
                            j = 0
                            for spremenljivka in spremenljivke: #Definiramo spremenljivke za dusenje ni potrebno da vse obstajajo
                                if j == 0:
                                    continue
                                elif j == 1:
                                    self.damping1 = convert(spremenljivka)
                                elif j == 2:
                                    self.damping2 = convert(spremenljivka)
                                elif j == 3:
                                    self.damping3 = convert(spremenljivka)
                                elif j == 4:
                                    self.damping4 = convert(spremenljivka)
                                elif j == 5:
                                    self.damping5 = convert(spremenljivka)
                                elif j == 6:
                                    self.damping6 = convert(spremenljivka)
                                elif j == 7:
                                    self.damping7 = convert(spremenljivka)
                                elif j == 8:
                                    self.damping8 = convert(spremenljivka)
                                elif j == 9:
                                    self.damping9 = convert(spremenljivka)
                                j = j + 1
                        elif fileString[i].startswith("EART"): # Če se string začne z ''
                            spremenljivke = fileString[i].split(" ")
                            j = 0
                            for spremenljivka in spremenljivke:
                                if j == 0:
                                    continue
                                elif j % 3 == 1:
                                    self.earthquakeI.append(int(spremenljivka))
                                elif j % 3 == 2:
                                    self.earthquakeF.append(convert(spremenljivka))
                                elif j % 3 == 0:
                                    self.earthquakeT.append(convert(spremenljivka))
                        elif fileString[i].startswith("DYNA"):
                            if not razdeljenaVrstica[0].startswith("DYNA") and not razdeljenaVrstica[1].startswith("LOAD"):
                                raise ValueError("napaka pri loadings dynamic loads " + fileString[i])
                            j = 1
                            while (fileString[i + j][0].isdigit()):
                                if ("THRU" not in fileString[i + j]):
                                    spremenljivkeList = fileString[i + j].split(" ")
                                    if len(spremenljivkeList) == 10:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), -1, int(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), int(spremenljivkeList[4]), convert(spremenljivkeList[5]), convert(spremenljivkeList[6]), int(spremenljivkeList[7]), convert(spremenljivkeList[8]), convert(spremenljivkeList[9])))
                                    elif len(spremenljivkeList) == 9:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), -1, int(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), int(spremenljivkeList[4]), convert(spremenljivkeList[5]), convert(spremenljivkeList[6]), int(spremenljivkeList[7]), convert(spremenljivkeList[8]), -1))
                                    elif len(spremenljivkeList) == 7:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), -1, int(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), int(spremenljivkeList[4]), convert(spremenljivkeList[5]), convert(spremenljivkeList[6]), -1, -1, -1))
                                    elif len(spremenljivkeList) == 6:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), -1, int(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), int(spremenljivkeList[4]), convert(spremenljivkeList[5]), -1, -1, -1, -1))
                                    elif len(spremenljivkeList) == 4:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), -1, int(spremenljivkeList[1]), convert(spremenljivkeList[2]), convert(spremenljivkeList[3]), -1, -1, -1, -1, -1, -1))
                                    elif len(spremenljivkeList) == 3:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), -1, int(spremenljivkeList[1]), convert(spremenljivkeList[2]), -1, -1, -1, -1, -1, -1, -1))
                                else:
                                    spremenljivkeList = fileString[i + j].split(" ")
                                    if len(spremenljivkeList) == 12:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), int(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), int(spremenljivkeList[6]), convert(spremenljivkeList[7]), convert(spremenljivkeList[8]), int(spremenljivkeList[9]), convert(spremenljivkeList[10]), convert(spremenljivkeList[11])))
                                    elif len(spremenljivkeList) == 11:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), int(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), int(spremenljivkeList[6]), convert(spremenljivkeList[7]), convert(spremenljivkeList[8]), int(spremenljivkeList[9]), convert(spremenljivkeList[10]), -1))
                                    elif len(spremenljivkeList) == 9:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), int(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), int(spremenljivkeList[6]), convert(spremenljivkeList[7]), convert(spremenljivkeList[8]), -1, -1, -1))
                                    elif len(spremenljivkeList) == 8:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), int(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), int(spremenljivkeList[6]), convert(spremenljivkeList[7]), -1, -1, -1, -1))
                                    elif len(spremenljivkeList) == 6:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), int(spremenljivkeList[3]), convert(spremenljivkeList[4]), convert(spremenljivkeList[5]), int(spremenljivkeList[6]), -1, -1, -1, -1, -1))
                                    elif len(spremenljivkeList) == 5:
                                        self.dynamicLoads.append(DynamicLoading(int(spremenljivkeList[0]), int(spremenljivkeList[2]), int(spremenljivkeList[3]), convert(spremenljivkeList[4]), -1, -1, -1, -1, -1, -1, -1))
                                    j += 1
                            i = i + j
                        elif fileString[i].startswith("NUMB"): # število intervalov
                            if not razdeljenaVrstica[0].startswith("NUMB") and not razdeljenaVrstica[1].startswith("OF") and not razdeljenaVrstica[2].startswith("TIME"):
                                raise ValueError("napaka pri loadings number of timesteps " + fileString[i])
                            self.numberOfTimeStamps = int(fileString[i].rsplit(" ", 1)[1])
                        elif fileString[i].startswith("LAST"): #zaden interval
                            if not razdeljenaVrstica[0].startswith("LAST") and not razdeljenaVrstica[1].startswith("TIME"):
                                raise ValueError("napaka pri loadings last time " + fileString[i])
                            self.lastTime = convert(fileString[i].rsplit(" ", 1)[1])
                        elif fileString[i].startswith("COMP"):
                            if razdeljenaVrstica[0].startswith("COMP") and razdeljenaVrstica[1].startswith("FORC"):
                                self.compute = "FORCES"
                            elif razdeljenaVrstica[0].startswith("COMP") and razdeljenaVrstica[1].startswith("NFOR"):
                                self.compute = "NFORCES"
                            else:
                                raise ValueError("Napaka pri Compute!!!")
                        elif fileString[i].startswith("*") or fileString[i].startswith("PRIN") or fileString[i].startswith("PLOT"):
                            i = i + 1
                            continue
                        elif fileString[i].startswith("SOLV") or fileString[i].startswith("LOAD"):
                            return i - 1
                        i = i + 1
                i = i + 1
            else:
                raise ValueError("Napaka pri Loadingu!!! " + fileString[i])
            i = i + 1

    def izpisi(self):
        returnString = "LOAD " + self.naziv + "\n"
        if self.type == "STATIC":
            returnString += "TYPE " + self.type[:4] + "\n"
            returnString += "TABU"
            spremenljivke = self.tabulate.split()
            for spremenljivka in spremenljivke:
                returnString += " " + spremenljivka[:4]
            returnString += "\n"
            returnString += "STAT LOAD\n"
            for load in self.staticLoads:
                if load.do == -1:
                    returnString += str(load.od) + " " + str(load.stevilka1) + " " + str(load.stevilka2) + " " + str(load.stevilka3) + "\n"
                else:
                    returnString += str(load.od) + " " + "THRU " + str(load.do)+ " " + str(load.stevilka1) + " " + str(load.stevilka2) + " " + str(load.stevilka3) + "\n"
        elif self.type == "YUSPECTRUM":
            returnString += "TYPE " + self.type[:4] + " " + str(self.typeYuspectrum) + "\n"
            returnString += "TABU"
            spremenljivke = self.tabulate.split()
            for spremenljivka in spremenljivke:
                returnString += " " + spremenljivka[:4]
            returnString += "\n"
            returnString += "KC " + str(self.kc) + "\n"
            if self.factor1 != -1 and self.factor2 == -1 and self.factor3 == -1:
                returnString += "FACT " + str(self.factor1) + "\n"
            elif self.factor1 != -1 and self.factor2 != -1 and self.factor3 == -1:
                returnString += "FACT " + str(self.factor1) + " " + str(self.factor2) + "\n"
            else:
                returnString += "FACT " + str(self.factor1) + " " + str(self.factor2) + " " + str(self.factor3) + "\n"
        elif self.type == "SPECTRUM":
            returnString += "TYPE " + self.type[:4] + "\n"
            returnString += "TABU"
            spremenljivke = self.tabulate.split()
            for spremenljivka in spremenljivke:
                returnString += " " + spremenljivka[:4]
            returnString += "\n"
            returnString += "FUNC " + self.functionNaziv + "\n"
            for stevilka in self.function:
                returnString += str(stevilka) + " "
            returnString += "\n"
            if self.factor1 != -1 and self.factor2 == -1 and self.factor3 == -1:
                returnString += "FACT " + str(self.factor1) + "\n"
            elif self.factor1 != -1 and self.factor2 != -1 and self.factor3 == -1:
                returnString += "FACT " + str(self.factor1) + " " + str(self.factor2) + "\n"
            else:
                returnString += "FACT " + str(self.factor1) + " " + str(self.factor2) + " " + str(self.factor3) + "\n"
        else:
            returnString += "TYPE " + self.type.split(" ")[0][:4] + " " + self.type.split(" ")[1][:4] + "\n"
            returnString += "TABU"
            spremenljivke = self.tabulate.split()
            for spremenljivka in spremenljivke:
                returnString += " " + spremenljivka[:4]
            returnString += "\n"
            if len(self.earthquakeI) != 0:
                returnString += "EART "
                i = 0
                for earthI in self.earthquakeI:
                    returnString += str(earthI) + " " + str(self.earthquakeF[i]) + " "
                    if len(self.earthquakeT) <= i:
                        returnString +=  + str(self.earthquakeT[i]) + " "
                    i = i + 1
                returnString += "\n"
            else:
                returnString += "DYNA \n"
                for load in self.dynamicLoads: #definicija vseh možnih ukazov za dinamične obtežbe
                    if load.do == -1 and load.t1 == 0:
                        returnString += str(load.od) + " " + str(load.i1) + " " + str(load.f1) + "\n"
                    elif load.do == -1 and load.i2 == -1:
                        returnString += str(load.od) + " " + str(load.i1) + " " + str(load.f1) + " " + str(load.t1) + "\n"
                    elif load.do == -1 and load.t2 == 0:
                        returnString += str(load.od) + " " + str(load.i1) + " " + str(load.f1) + " " + str(load.t1) + str(load.i2)+ " " + str(load.f2) + "\n"
                    elif load.do == -1 and load.i2 == -1:
                        returnString += str(load.od) + " " + str(load.i1) + " " + str(load.f1) + " " + str(load.t1) + str(load.i2) + " " + str(load.f2) + " " + str(load.t2) + "\n"
                    elif load.do == -1 and load.t3 == 0:
                        returnString += str(load.od) + " " + str(load.i1) + " " + str(load.f1) + " " + str(load.t1) + str(load.i2) + " " + str(load.f2) + " " + str(load.t2) + " " + str(load.i3) + " " + str(load.f3) + "\n"
                    elif load.do == -1:
                        returnString += str(load.od) + " " + str(load.i1) + " " + str(load.f1) + " " + str(load.t1) + str(load.i2) + " " + str(load.f2) + " " + str(load.t2) + " " + str(load.i3) + " " + str(load.f3) + "\n"
                    elif load.do != -1 and load.t1 == 0:
                        returnString += str(load.od) + " THRU " + str(load.do) + " " + str(load.i1) + " " + str(load.f1) + "\n"
                    elif load.do != -1 and load.i2 == -1:
                        returnString += str(load.od) + " THRU " + str(load.do) + " " + str(load.i1) + " " + str(load.f1) + " " + str(load.t1) + "\n"
                    elif load.do != -1 and load.t2 == 0:
                        returnString += str(load.od) + " THRU " + str(load.do) + " " + str(load.i1) + " " + str(load.f1) + " " + str(load.t1) + " " + str(load.i2) + " " + str(load.f2) + "\n"
                    elif load.do != -1 and load.i2 == -1:
                        returnString += str(load.od) + " THRU " + str(load.do) + " " + str(load.i1) + " " + str(load.f1) + " " + str(load.t1) + " " + str(load.i2) + " " + str(load.f2) + " " + str(load.t2) + "\n"
                    elif load.do != -1 and load.t3 == 0:
                        returnString += str(load.od) + " THRU " + str(load.do) + " " + str(load.i1) + " " + str(load.f1) + " " + str(load.t1) + " " + str(load.i2) + " " + str(load.f2) + " " + str(load.t2) + " " + str(load.i3) + " " + str(load.f3) + "\n"
                    elif load.do != -1:
                        returnString += str(load.od) + " THRU " + str(load.do) + " " + str(load.i1) + " " + str(load.f1) + " " + str(load.t1) + " " + str(load.i2) + " " + str(load.f2) + " " + str(load.t2) + " " + str(load.i3) + " " + str(load.f3) + " " + str(load.t3) + "\n"
            returnString += "NUMB OF TIME " + str(self.numberOfTimeStamps) + "\n"
            returnString += "LAST TIME " + str(self.lastTime) + "\n"
            returnString += "DAMP " #Dušenje podoben ukaz kot load pri dinamični obtežbi
            returnString += str(self.damping1)
            if self.damping2 != -1:
                returnString += " " + str(self.damping2)
            elif self.damping3 != -1:
                returnString += " " + str(self.damping3)
            elif self.damping4 != -1:
                returnString += " " + str(self.damping4)
            elif self.damping5 != -1:
                returnString += " " + str(self.damping5)
            elif self.damping6 != -1:
                returnString += " " + str(self.damping6)
            elif self.damping7 != -1:
                returnString += " " + str(self.damping7)
            elif self.damping8 != -1:
                returnString += " " + str(self.damping8)
            elif self.damping9 != -1:
                returnString += " " + str(self.damping9)
            returnString += "\n"
            if self.compute != "":
                returnString += "COMP " + self.compute[:4]

        return returnString

def convert(string):
    if string.endswith("."):
        string = string + "0"
    elif string.endswith(".\n"):
        string = string[0:len(string)-2]

    return float(string)


import ctypes
import tkinter as tk
from tkinter import filedialog

osnovniPodatki = OsnovniPodatki()
try:
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()

    osnovniPodatki.preberi(file_path)
    print(file_path)
    # file = open(file_path, 'w')
    # file.write(osnovniPodatki.izpisi())
    # file.close()

    window = pyglet.window.Window()
    window.set_fullscreen(True)

    if osnovniPodatki.type == "PLANE":
        osnovniPodatki.izrisiNarisRavnina(50, window, 30, 30)
    elif osnovniPodatki.type == "SPACE":
        osnovniPodatki.izrisiTloris(50, window, 30, 30)
    else:
        raise ValueError("Napaka pri tipu")

    pyglet.app.run()

except ValueError as error:
    ctypes.windll.user32.MessageBoxW(0, str(error), "Value error", 1)
    window.clear()
    window.close()
    pyglet.app.exit()
except Exception as error:
    ctypes.windll.user32.MessageBoxW(0, str(error), "Druga Napaka", 1)
    window.clear()
    window.close()
    pyglet.app.exit()