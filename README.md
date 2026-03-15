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
| `strategy.py` | Patró estratègia: `PlayerStrategy` (base) i `SimpleStrategy` |
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

### Patró estratègia

Les decisions dels jugadors automàtics (comprar propietats, construir cases) es deleguen a una classe `PlayerStrategy`. Això permet canviar el comportament d'un jugador sense modificar la lògica del joc. La implementació `SimpleStrategy` proporcionada:

- Compra qualsevol propietat si té prou diners.
- Construeix cases/hotels en carrers on té el monopoli, una construcció per torn.

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

Això juga una partida completa, genera fitxers SVG per a cada torn a la carpeta `games/` i crea un fitxer `game.html` per visualitzar la partida al navegador.

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
├── test_board.py               # Tests del tauler
├── test_board_coverage.py      # Tests addicionals del tauler
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
| `test_board.py` | Inicialització del tauler, tirada de daus, serialització pickle, mecànica de torns amb dobles i presó |
| `test_board_coverage.py` | Cobertura addicional: cicle de jugadors, tipus de caselles, operacions de propietats |
| `test_card_coverage.py` | Construcció de targetes des de diccionaris, execució de cada tipus de targeta |
| `test_deck.py` | Inicialització del deck, robada i devolució de targetes, barreja, mida |
| `test_player.py` | Inicialització del jugador, moviment, pas per GO, transaccions i fallida |
| `test_tile.py` | Compra de propietats, lloguer, construcció/venda de cases i hotels, hipoteques |
| `test_strategy.py` | Estratègia base (NotImplementedError), SimpleStrategy amb diferents nivells de diners |
| `test_draw.py` | Posicionament de caselles, mapa de colors, generació de fitxers SVG |
| `test_main.py` | Funció `play_game` amb límit de torns, integració completa |
| `test_slideshow.py` | Generació HTML de la presentació |

Per executar tots els tests:

```bash
pytest -v
```
