# Monopoly

Implementació en Python del joc de taula Monopoly amb jugadors automàtics i visualització SVG.

Pràctica de l'assignatura d'Algorísmia i Programació 2 (AP2) del grau en Ciència i Enginyeria de Dades de la UPC.

## Descripció

Aquest projecte implementa la lògica completa del joc del Monopoly seguint les [regles oficials](https://instructions.hasbro.com/api/download/C1009_en-nz_monopoly-classic-game.pdf), amb les simplificacions indicades a l'enunciat de la pràctica:

- **Jugadors**: De 2 a 4 jugadors automàtics. El primer jugador sempre comença.
- **Cases i hotels**: No hi ha límit en el nombre total disponible.
- **Propietats no comprades**: No hi ha subhasta si un jugador no compra.
- **Sense interacció**: Els jugadors no poden negociar ni fer tractes entre ells.
- **Ordre d'accions**: Les accions de gestió (comprar/vendre cases, hipotecar, etc.) es fan després de moure i completar l'acció de la casella.
- **Gestió d'una en una**: Cada operació de compra-venda, hipoteca o deshipoteca es fa individualment.
- **Presó**: El jugador surt de la presó per tirada doble, carta de sortida, o després de 3 torns. No es pot pagar M50.

## Arquitectura

El projecte s'organitza en els mòduls següents:

| Mòdul | Descripció |
|---|---|
| `const.py` | Constants del joc (salari de sortida, diners inicials, etc.) |
| `tile.py` | Jerarquia de caselles: `Tile` (base), `Property`, `Street`, `Station`, `Utility`, `Tax`, `Chance`, `Community_Chest`, `Special` |
| `card.py` | Jerarquia de targetes: `Card` (base), `MoneyCard`, `MoveToPositionCard`, `GoToJailCard`, `GetOutOfJailCard`, `PropertyRepairsCard`, `PlayerTransactionCard`, `MoveNearestCard`, etc. |
| `deck.py` | Classe `Deck` per gestionar les piles de targetes amb barreja i robada |
| `player.py` | Classe `Player` amb estat del joc (posició, diners, propietats, presó) |
| `board.py` | Classe `Board` que gestiona tota la partida, daus, torns i regles |
| `strategy.py` | Classe `Strategy` que defineix les decisions del jugador |
| `draw.py` | Renderització del tauler en format SVG |
| `slideshow.py` | Generació de pàgines HTML per visualitzar partides |
| `main.py` | Punt d'entrada del programa |

### Diagrama de dependències

```
main.py
  └── board.py
        ├── tile.py ──── const.py
        ├── player.py ── strategy.py
        ├── deck.py ──── card.py
        └── draw.py
```

## Decisions de disseny

### Herència i polimorfisme

S'utilitza una jerarquia de classes tant per a les caselles (`Tile`) com per a les targetes (`Card`). El mètode `land_on()` de `Tile` i `execute()` de `Card` s'implementen de manera diferent a cada subclasse, aprofitant el polimorfisme per evitar condicionals complexos.

Per exemple, quan un jugador cau en una casella, simplement es crida `tile.land_on(player)` i el comportament correcte s'executa automàticament segons el tipus de casella (cobrar lloguer, treure una targeta, pagar impostos, etc.).

### Estratègia del jugador

Les decisions dels jugadors automàtics (comprar propietats, construir cases) es defineixen a través de la classe `Strategy`. Aquesta classe centralitza la lògica de decisions del jugador:

- Compra qualsevol propietat si té prou diners.
- **Construcció limitada per torn**: Construeix com a màxim una casa o un hotel per torn en carrers on té el monopoli. Aquesta restricció fa que la progressió del joc sigui més lenta i visible, permetent als jugadors observar clarament l'evolució de les propietats.

La restricció de construcció s'implementa a través del mètode `build()` de `Strategy`, que fa `return` després de completar una construcció, impedint múltiples edificacions en el mateix torn.

### Funcions fàbrica

Les funcions `build_tile()` i `build_card()` actuen com a fàbriques per crear objectes del tipus adequat a partir de les dades JSON, centralitzant tota la lògica de construcció.

### Gestió de la presó

El sistema de presó segueix les regles simplificades:

1. Si el jugador té una carta de "Sortir de la presó lliure", la utilitza automàticament.
2. Si no, tira els daus: si surt doble, surt i mou normalment.
3. Si completa 3 torns a la presó, surt automàticament.

### Càlcul de lloguer

- **Carrers**: El lloguer depèn de si el propietari té el monopoli del color, del nombre de cases o de si hi ha un hotel.
- **Estacions**: El lloguer augmenta segons el nombre d'estacions que posseeix el propietari (25, 50, 100 o 200).
- **Serveis públics**: El lloguer es calcula multiplicant la tirada dels daus per un multiplicador (×4 amb un servei, ×10 amb tots dos).
- Les propietats hipotecades no cobren lloguer.

### Construcció uniforme

La compra i venda de cases segueix la regla de construcció uniforme: no es pot construir una casa addicional en un carrer si qualsevol altre carrer del mateix color té menys cases. Igualment, no es pot vendre una casa si qualsevol altre carrer del mateix color en té més.

### Gestió de la fallida i transferència de propietats

Quan un jugador es queda sense diners (fallida), el sistema utilitza un **sistema de creditor** per determinar qui hereta les seves propietats:

- **Fallida contra un jugador** (lloguer, cartes de pagament entre jugadors): El jugador creditor hereta totes les propietats del fallit i les afegeix al seu patrimoni.
- **Fallida contra la banca** (impostos, cartes de manteniment, pagaments col·lectius): Les propietats retornen a la banca (propietari `None`).

**Implementació técnica:**

Cada vegada que es fa un pagament, s'estableix el creditor mitjançant `player.set_creditor()`:

- `Property.land_on()`: Creditor = propietari de la propietat.
- `board.move_to_nearest()`: Creditor = propietari de l'estació/servei públic.
- `Tax.land_on()`: Creditor = `None` (banca).
- `MoneyCard.execute()` (pay_money): Creditor = `None` (banca).
- `PropertyRepairsCard.execute()`: Creditor = `None` (banca).
- `PlayerTransactionCard.execute()` (pagaments col·lectius): Creditor = `None` (banca).

Aquesta decisió de disseny replica les regles oficials del Monopoly i assegura que les propietats no es perdin arbitràriament quan un jugador fa fallida.

### Rent multiplier de les cartes de Chance

Les cartes de Chance "Move to nearest station/utility" apliquen un multiplicador al lloguer (×2 per a estacions, ×10 per a serveis públics). La implementació estableix el creditor correctament perquè, si el jugador fa fallida, l'herència de propietats es gestioni segons les regles oficials.

## Instal·lació

### Requisits

- Python 3.10+
- Biblioteca `drawsvg`

### Configuració

```bash
pip install drawsvg
```

## Ús

### Executar una partida

```bash
python3 main.py
```

La partida es juga de forma automàtica fins que només queda un jugador (o s'assoleix el límit de 500 torns). Els fitxers SVG es generen per a cada torn a la carpeta `games/` (format `tauler-0000.svg`, `tauler-0001.svg`, etc.), i es crea un fitxer `game.html` per visualitzar la partida al navegador web.

**Nota:** Els SVGs sempre es generen de forma automàtica durant la partida, necessaris per a la visualització i anàlisi del joc.

### Executar els tests

```bash
pytest                    # Tots els tests
pytest -v                 # Sortida detallada
pytest test_tile.py -v    # Un fitxer de tests concret
```

### Verificació de tipus

```bash
mypy *.py
```

### Generar una presentació

```bash
python3 slideshow.py partida.html games/tauler-*.svg
```

## Estructura de fitxers

```
programa/
├── board.py                    # Motor principal del joc
├── card.py                     # Jerarquia de targetes
├── const.py                    # Constants del joc
├── deck.py                     # Gestió de la pila de targetes
├── draw.py                     # Renderització SVG del tauler
├── drawsvg.pyi                 # Stubs de tipus per drawsvg
├── main.py                     # Punt d'entrada
├── player.py                   # Classe jugador
├── slideshow.py                # Generador HTML de presentació
├── strategy.py                 # Estratègies dels jugadors automàtics
├── tile.py                     # Jerarquia de caselles
├── test_board.py               # Tests del tauler (inclou cobertura amplia)
├── test_card_coverage.py       # Tests de les targetes
├── test_data_importation.py    # Test d'importació de dades
├── test_deck.py                # Tests de la pila de targetes
├── test_draw.py                # Tests de la visualització
├── test_main.py                # Tests del programa principal
├── test_player.py              # Tests del jugador
├── test_slideshow.py           # Tests de la presentació
├── test_strategy.py            # Tests de l'estratègia
├── test_tile.py                # Tests de les caselles
├── test_visual.py              # Test visual manual
├── README.md                   # Documentació del projecte
└── data/                       # Fitxers de configuració JSON
    ├── tiles.json              # Definició de les 40 caselles
    ├── chance.json             # 16 targetes de Sort
    ├── community-chest.json    # 16 targetes de Comunitat
    └── players.json            # Definició dels jugadors
```

## Joc de proves

El projecte inclou un conjunt de tests organitzats per mòdul:

| Fitxer de test | Què verifica |
|---|---|
| `test_board.py` | Inicialització del tauler, tirada de daus, serialització pickle, mecànica de torns amb dobles i presó, cicle de jugadors, tipus de caselles, operacions de propietats |
| `test_card_coverage.py` | Construcció de targetes des de diccionaris, execució de cada tipus de targeta |
| `test_deck.py` | Inicialització del deck, robada i devolució de targetes, barreja, mida |
| `test_player.py` | Inicialització del jugador, moviment, pas per GO, transaccions, fallida i gestió de creditor |
| `test_tile.py` | Compra de propietats, lloguer, construcció/venda de cases i hotels, hipoteques, propietat mortgagada |
| `test_strategy.py` | Estratègia base (NotImplementedError), SimpleStrategy amb diferents nivells de diners |
| `test_draw.py` | Posicionament de caselles, mapa de colors, generació de fitxers SVG |
| `test_main.py` | Funció `play_game` amb límit de torns, integració completa del joc |
| `test_slideshow.py` | Generació HTML de la presentació |

Per executar tots els tests:

```bash
pytest -v
```
