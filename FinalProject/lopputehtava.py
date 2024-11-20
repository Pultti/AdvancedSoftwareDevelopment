import tkinter as tk
import random
import time
import threading
import pygame

pygame.init()
pygame.mixer.init()

# Ladataan äänitiedostot
sharkAttack = pygame.mixer.Sound('sharkSound.wav')  # Haihyökkäys-ääni
monkeyLaugh = pygame.mixer.Sound('monkey_laugh_short.wav')  # Apinan nauru -ääni
boulder = pygame.mixer.Sound('boulder.wav')  # Kallioääni
swim = pygame.mixer.Sound('swim.wav')  # Uimisääni

# Apinaäänet saarella 10s välein
chirp0 = pygame.mixer.Sound('chirp.wav')
chirp1 = pygame.mixer.Sound('chirp2.wav')
chirp2 = pygame.mixer.Sound('chirp3.wav')
woo0 = pygame.mixer.Sound('monkeyWoo.wav')
woo1 = pygame.mixer.Sound('monkeyWoo2.wav')

# Lista käytettävissä olevista äänistä
chirpSounds = [chirp0, chirp1, chirp2]
wooSounds = [woo0, woo1]  

monkey = None
monkeyCoord = None
monkeys = []  # Lista apinaolioista
monkeyCanvas = []
awareMonkeys = []
inWater = []
islandCount = 0  # Saarten lukumäärä
stop = False  # Merkkimuuttuja säikeiden pysäyttämiseen

class Monkey:
    def __init__(self, aware, swimming, onIsland, x, y, canvas):
        self.aware = aware  # Onko apina tietoinen laiturista
        self.swimming = swimming  # Onko apina uimassa
        self.onIsland = onIsland  # Millä saarella apina on
        self.x = x  # Apinan x-koordinaatti
        self.y = y  # Apinan y-koordinaatti
        self.canvas = canvas  # Apinan piirto-olio

    def is_aware(self):
        if self.aware is True:
            return True
        else:
            return False

class Island:
    def __init__(self, dock, x, y, canvas, text):
        self.dock = dock  # Onko saarella laituri
        self.name = f'S{islandCount}'  # Saaren nimi, esim. 'S1'
        self.x = x  # Saaren x-koordinaatti
        self.y = y  # Saaren y-koordinaatti
        self.canvas = canvas  # Saaren piirto-olio
        self.text = text  # Saaren teksti (apinoiden määrä)

def createNewIsland():
    """Luo uuden saaren satunnaiseen paikkaan."""
    global islandCount
    global stop
    stop = False  # Lopetusmerkki pois päältä

    while True:
        x = random.randint(50, 650)  # Satunnainen x-koordinaatti
        y = random.randint(50, 350)  # Satunnainen y-koordinaatti
        overlapping = False  # Onko päällekkäisyyttä muiden saarten kanssa
        for island in islands:
            coords = canvas.coords(island.canvas)
            if coords and abs(coords[0] - x) < 100 and abs(coords[1] - y) < 100:
                overlapping = True  # Liian lähellä toista saarta
                break
        if not overlapping:
            boulder.play()  # Soitetaan kallioääni
            break

    islandCount = len(islands) + 1  # Päivitetään saarten lukumäärä
    # Luodaan uusi saari
    island = Island(
        False, x, y,
        canvas.create_rectangle(x, y, x + 100, y + 100, fill="green"),
        canvas.create_text((x + 50, y + 65), text="10", fill="white")
    )
    islands.append(island)  # Lisätään saari saarten listaan
    canvas.create_text((x + 50, y + 50), text=island.name, fill="white")  # Saaren nimi

    if island.name == "S1":
        addDock(island)  # Lisätään laituri ensimmäiselle saarelle
        island.dock = True
        addAwareMonkeys(island)  # Lisätään tietoisia apinoita
    else:
        addMonkeys(island)  # Lisätään tavallisia apinoita

    canvas.tag_raise("monkey")  # Nostetaan apinat muiden objektien päälle

def addMonkeys(island):
    """Lisää apinoita saarelle."""
    if island:
        for _ in range(10):
            addMonkey(island)
            canvas.update()

def addAwareMonkeys(island):
    """Lisää tietoisia apinoita saarelle."""
    if island:
        for _ in range(10):
            addAwareMonkey(island)
            canvas.update()

def moveToSea():
    """Liikuttaa tietoiset apinat mereen."""
    if monkeys:
        for i in range(len(monkeys)):
            if monkeys[i].aware is True and monkeys[i].swimming is False:
                monkey = monkeys[i]
                for island in islands:
                    if monkey.onIsland == island.name:
                        chosen_island = island
                x, y, _, _ = canvas.coords(chosen_island.canvas)
                monkeys[i].swimming = True
                t = threading.Thread(target=monkeySwim, args=(chosen_island, monkey))
                t.start()
                return

def moveToSeaAuto():
    """Automaattisesti liikuttaa tietoiset apinat mereen."""
    if monkeys:
        for island in islands:
            for i in range(len(monkeys)):
                if monkeys[i].aware is True and monkeys[i].swimming is False:
                    monkey = monkeys[i]
                    if monkey.onIsland == island.name:
                        x, y, _, _ = canvas.coords(island.canvas)
                        monkeys[i].swimming = True
                        t = threading.Thread(target=monkeySwim, args=(island, monkey))
                        t.start()
                        break

def monkeySwim(island, monkey):
    """Liikuttaa apinaa mereen."""
    global stop
    x, y, _, _ = canvas.coords(island.canvas)
    # Valitaan satunnainen suunta apinan uimiselle
    dest_x, dest_y = random.choice([
        (x - 1000, y + 50),
        (x + 1000, y + 50),
        (x + 50, y + 1000),
        (x + 50, y - 1000)
    ])

    coords = []
    coords.append(monkey.x)
    coords.append(monkey.y)

    while coords != (dest_x, dest_y):
        if stop is True:
            return
        if monkey.swimming is False:
            break

        if coords[0] < dest_x:
            monkey.x = coords[0] + 1
        elif coords[0] > dest_x:
            monkey.x = coords[0] - 1
        if coords[1] < dest_y:
            monkey.y = coords[1] + 1
        elif coords[1] > dest_y:
            monkey.y = coords[1] - 1

        canvas.move(monkey.canvas, monkey.x - coords[0], monkey.y - coords[1])
        coords = (monkey.x, monkey.y)
        canvas.update()
        swim.play()  # Soitetaan uimisääni (suositellaan poistettavaksi testauksen helpottamiseksi)
        time.sleep(0.1)

def addDock(island):
    """Lisää laiturin saarelle."""
    x, y, _, _ = canvas.coords(island.canvas)
    # Piirretään laiturit saaren sivuille
    canvas.create_line(x, y + 50, x - 20, y + 50, fill="brown", width=3)
    canvas.create_line(x + 50, y, x + 50, y - 20, fill="brown", width=3)
    canvas.create_line(x + 100, y + 50, x + 120, y + 50, fill="brown", width=3)
    canvas.create_line(x + 50, y + 100, x + 50, y + 120, fill="brown", width=3)

    for monkey in monkeys:
        if monkey.onIsland == island.name:
            monkey.aware = True  # Apinat ovat nyt tietoisia laiturista

def addMonkey(island):
    """Lisää yksittäisen apinan saarelle."""
    x, y, _, _ = canvas.coords(island.canvas)
    monkey_x = random.randint(int(x), int(x + 100))
    monkey_y = random.randint(int(y), int(y + 100))
    monkey_canvas = canvas.create_oval(
        monkey_x, monkey_y, monkey_x + 5, monkey_y + 5, fill="brown", tags="monkey"
    )
    monkeys.append(Monkey(False, False, island.name, monkey_x, monkey_y, monkey_canvas))

def addAwareMonkey(island):
    """Lisää tietoinen apina saarelle."""
    x, y, _, _ = canvas.coords(island.canvas)
    monkey_x = random.randint(int(x), int(x + 100))
    monkey_y = random.randint(int(y), int(y + 100))
    monkey_canvas = canvas.create_oval(
        monkey_x, monkey_y, monkey_x + 5, monkey_y + 5, fill="brown", tags="monkey"
    )
    monkeys.append(Monkey(True, False, island.name, monkey_x, monkey_y, monkey_canvas))

def diedOnLaughing():
    """Apinat voivat kuolla nauruun."""
    while True:
        for monkey in monkeys:
            if monkey.swimming is False:
                if random.random() < 0.01:
                    monkeys.remove(monkey)
                    canvas.delete(monkey.canvas)
                    monkeyLaugh.play()  # Soitetaan apinan nauru (saatetaan haluta poistaa)
                    print("Monkey died of laughter")  # Tulostetaan viesti
        moveToSeaAuto()
        time.sleep(10)

# Funktion tarkoitus on soittaa apinaääniä
def monkeySound():
    """Soittaa apinaääniä."""
    while True:
        for monkey in monkeys:
            # Satunnaisesti valitaan chirp tai woo -ääni jokaiselle apinalle
            if random.choice([True, False]):
                random.choice(chirpSounds).play()
            else:
                random.choice(wooSounds).play()

            # Satunnainen viive äänien välillä
            time.sleep(random.uniform(0.009, 0.01))
        # Viive ennen seuraavaa kierrosta
        time.sleep(10)


def SharkAttack():
    """Haihyökkäykset uimassa oleviin apinoihin."""
    while True:
        for monkey in monkeys:
            if monkey.swimming is True:
                if random.random() < 0.01:
                    monkeys.remove(monkey)
                    canvas.delete(monkey.canvas)
                    sharkAttack.play()  # Soitetaan haihyökkäys-ääni
                    print("Monkey was eaten by shark")
        time.sleep(1)

def clearSea():
    """Tyhjentää meren ja alustaa muuttujat."""
    global islandCount
    global stop
    canvas.delete("all")
    islands.clear()
    monkeys.clear()
    islandCount = 0
    stop = True  # Asetetaan lopetusmerkki

def islandCollision():
    """Tarkistaa apinoiden törmäykset saariin."""
    while True:
        if monkeys:
            for monkey in monkeys:
                if monkey.swimming is True:
                    for island in islands:
                        x, y, x2, y2 = canvas.coords(island.canvas)
                        if monkey.x >= x and monkey.x <= x2:
                            if monkey.y >= y and monkey.y <= y2:
                                if island.dock is False:
                                    island.dock = True
                                    monkey.onIsland = island.name
                                    monkey.swimming = False
                                    addDock(island)
                                else:
                                    if monkey.onIsland != island.name:
                                        monkey.onIsland = island.name
                                        monkey.swimming = False
        time.sleep(0.5)

def amountCounter():
    """Laskee apinoiden määrän saarella ja päivittää näytön."""
    while True:
        try:
            for island in islands:
                counter = 0
                for monkey in monkeys:
                    if monkey.swimming is False and monkey.onIsland == island.name:
                        counter += 1
                canvas.itemconfig(island.text, text=counter)
            time.sleep(0.5)
        except:
            time.sleep(0.5)

def start_threads():
    """Käynnistää tarvittavat säikeet."""
    t1 = threading.Thread(target=diedOnLaughing)
    t2 = threading.Thread(target=SharkAttack)
    t3 = threading.Thread(target=islandCollision)
    t4 = threading.Thread(target=amountCounter)
    t5 = threading.Thread(target=monkeySound)
    t3.start()
    t1.start()
    t2.start()
    t4.start()
    t5.start()

# Luodaan pääikkuna
root = tk.Tk()
root.title("Monkey island adventure")

canvas = tk.Canvas(root, width=800, height=500, bg="lightblue")
canvas.pack()

newIslandButton = tk.Button(root, text="Tulivuorenpurkaus", command=createNewIsland)
newIslandButton.pack()

clearSeaButton = tk.Button(root, text="Puhdista meri", command=clearSea)
clearSeaButton.pack()

moveToSeaButton = tk.Button(root, text="Lähtekää merelle", command=moveToSea)
moveToSeaButton.pack()

start_threads()  # Käynnistetään säikeet

islands = []

root.mainloop()  # Käynnistetään pääsilmukka