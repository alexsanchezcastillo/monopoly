# Monopoly

Implementació del joc de taula Monopoly amb jugadors automàtics i visualització del taulell amb svg.

## Descripció

Aquest projecte implementa la lògica completa del joc del Monopoly seguint les regles oficials (https://instructions.hasbro.com/api/download/C1009_en-nz_monopoly-classic-game.pdf), amb les simplificacions indicades a l'enunciat de la pràctica:

- **Jugadors**: De 2 a 4 jugadors automàtics, no més. El primer jugador sempre comença.
- **Cases i hotels**: No hi ha límit en el nombre total disponible.
- **Propietats no comprades**: No hi ha subhasta si un jugador no compra.
- **Sense interacció**: Els jugadors no poden negociar ni fer tractes entre ells.
- **Ordre d'accions**: Les accions de gestió (comprar/vendre cases, hipotecar, etc.) es fan després de moure i completar l'acció de la casella.
- **Gestió d'una en una**: Cada operació de compra-venda, hipoteca o deshipoteca es fa individualment.
- **Presó**: El jugador surt de la presó per tirada doble, carta de sortida, o després de 3 torns. No es pot pagar £50.

### Dinàmica habitual d'una partida

En aquesta implementació del Monopoly, si la partida acaba amb un guanyador clar, és perquè algun jugador ha aconseguit un **monopoli** (totes les propietats d'un color), cobrant així llogers alts als altres jugadors. En aquest cas, el joc sol acabar en menys de 400 torns. En cas contrari, degut als lloguers "baixos" que es cobren sense la construcció d'edificis (no hi ha monopolis), les partides s'allargarien molt. Per evitar-ho s'estableix un **límit de 1000 torns** i guanya el jugador que ha acabat amb més diners.

## Arquitectura

El projecte s'organitza en els mòduls següents:

| Mòdul | Descripció |
|---|---|
| `const.py` | Constants del joc: `GO_SALARY` (200), `START_MONEY` (1500), `MAX_PLAYERS` (4) |
| `tile.py` | Jerarquia de caselles: `Tile` (base) → `Property` → `Street`, `Station`, `Utility`; `Tax`, `Chance`, `Community_Chest`, `Special` |
| `card.py` | Jerarquia de targetes: `Card` (base) → `MoneyCard`, `MoveToPositionCard`, `MoveBackSpacesCard`, `GoToJailCard`, `GetOutOfJailCard`, `PropertyRepairsCard`, `PlayerTransactionCard`, `MoveNearestCard` |
| `deck.py` | Classe `Deck`: pila de targetes amb barreja (`shuffle`), robada (`draw`) i devolució (`add_card`) |
| `player.py` | Classe `Player`: estat complet del jugador (posició, diners, propietats, presó, cartes de sortida, creditor) |
| `board.py` | Classe `Board`: tauler de 40 caselles, 2 decks, gestió de torns, daus, regles i pickle |
| `strategy.py` | Classe `Strategy`: estratègia de decissió de compra de propietats i edificis |
| `draw.py` | Renderització del tauler en format SVG (1000×1000px) amb icones, colors, edificis i indicadors |
| `slideshow.py` | Generació de pàgina HTML interactiva per visualitzar la partida torn a torn |
| `main.py` | Punt d'entrada: executa la partida, genera SVGs a `games/` i crea `game.html` |

## Classes i mètodes

### Caselles (`tile.py`)

**`Tile`** — Classe base. Defineix `land_on(player)` (sobreescrit per cada subclasse) i getters comuns (`name()`, `position()`, `get_owner()`, etc.).

| Subclasse | Descripció | Mètodes clau |
|---|---|---|
| `Property(Tile)` | Base abstracta per a caselles comprables | `land_on()` (ofereix compra o cobra lloguer), `get_rent()`, `mortgage()`/`unmortgage()` |
| `Street(Property)` | Carrers amb cases i hotels | `build_house()`/`sell_house()`, `build_hotel()`/`sell_hotel()`, `can_build_*()` (validacions amb regla uniforme) |
| `Station(Property)` | Estacions de tren | Lloguer escalat: 25/50/100/200 segons estacions del propietari |
| `Utility(Property)` | Serveis públics | Lloguer = daus × multiplicador (×4 amb un, ×10 amb dos) |
| `Tax(Tile)` | Impostos | Dedueix quantitat fixa (creditor = banca) |
| `Chance(Tile)` | Casella de Sort | Treu targeta del deck, l'executa i la retorna |
| `Community_Chest(Tile)` | Casella de Comunitat | Treu targeta del deck, l'executa i la retorna |
| `Special(Tile)` | GO, Jail, Free Parking, Go To Jail | Només "Go To Jail" té acció |

**`build_tile(board, data)`** — Funció fàbrica que construeix el subtipus correcte a partir d'un diccionari JSON.

### Targetes (`card.py`)

**`Card`** — Classe base amb `execute(player, board)` abstracte.

| Subclasse | Efecte |
|---|---|
| `MoneyCard` | Transacció amb la banca (cobrar o pagar) |
| `MoveToPositionCard` | Mou a una posició concreta |
| `MoveBackSpacesCard` | Retrocedeix N caselles |
| `GoToJailCard` | Envia a la presó |
| `GetOutOfJailCard` | Guarda la targeta com a carta de sortida lliure (no retorna al deck) |
| `PropertyRepairsCard` | Paga per casa (×X) + per hotel (×Y) |
| `PlayerTransactionCard` | Transacció amb cada jugador |
| `MoveNearestCard` | Mou a l'estació/servei més proper, amb multiplicador de lloguer |

**`build_card(data)`** — Funció fàbrica que construeix el subtipus correcte a partir d'un diccionari JSON.

### Deck (`deck.py`)

**`Deck`** — Pila de targetes carregada des d'un fitxer JSON. Mètodes: `shuffle()`, `draw()` (treu del cim), `add_card()` (retorna al fons), `size()`.

### Jugador (`player.py`)

**`Player`** — Estat complet d'un jugador (posició, diners, propietats, presó, cartes de sortida, creditor).

| Mètode | Descripció |
|---|---|
| `move(steps)` | Avança i cobra salari de GO si passa la casella 0 |
| `move_to(position)` | Mou a posició directa (amb comprovació de GO) |
| `buy_property(prop)` | Compra propietat (dedueix preu, assigna propietari) |
| `transaction(amount)` | Suma o resta diners |
| `go_to_jail(position)` | Envia a la presó, activa flag |
| `use_get_out_of_jail_card()` | Usa carta de sortida lliure |
| `set_creditor(player)` | Estableix creditor del deute (`None` = banca) |
| `broke()` | `True` si diners negatius |

**`build_player(board, data, index)`** — Funció fàbrica que construeix un `Player` a partir d'un diccionari JSON.

### Tauler (`board.py`)

**`Board`** — Motor principal del joc: tauler de 40 caselles, 2 decks, gestió de torns i daus.

| Mètode | Descripció |
|---|---|
| `play_turn()` | Executa un torn complet (veure secció "Flux d'un torn") |
| `roll_dice()` | Tira dos daus (1-6) |
| `has_monopoly(player, color)` | Comprova si el jugador té totes les propietats d'un color |
| `move_to_nearest_station/utility(player, mult)` | Mou a l'estació/servei més proper amb multiplicador |
| `remove_player(player)` | Elimina un jugador (fallida) |

**`save_board(board, path)`** / **`load_board(path)`** — Serialització amb `pickle`.

### Estratègia (`strategy.py`)

**`Strategy`** — Intel·ligència artificial dels jugadors automàtics.
- `buy_property(player, property)`: Retorna `True` si el jugador té prou diners.
- `build(player, board)`: Construeix com a màxim una casa o hotel per torn, prioritzant carrers amb menys cases (ordre ascendent) per aconseguir una construcció uniforme.

### Visualització (`draw.py`)

Renderitza el tauler en SVG. Funció principal: `draw(board, svg_path)`. Dibuixa caselles amb colors, icones, noms (word-wrapped), preus, edificis (🏠/🏢), indicador de propietari, marca "𝓜" per hipotecades, cercles dels jugadors, quadrants centrals amb informació i daus.

### Presentació (`slideshow.py`)

`generate_slideshow(svgs)`: Genera HTML interactiu amb navegació per visualitzar la partida torn a torn. No té tests perquè és codi auxiliar que no forma part de la lògica del joc.

### Funció principal (`main.py`)

- `play_game(board, max_turns, output_prefix, output_dir)`: Bucle principal — juga torns, genera SVGs, detecta fallides, transfereix propietats. Retorna `(torns, guanyador)`.
- `main()`: Crea el tauler, executa `play_game()`, genera `game.html` amb el slideshow.

## Decisions de disseny

### Herència i polimorfisme

S'utilitza una jerarquia de classes tant per a les caselles (`Tile`) com per a les targetes (`Card`). El mètode `land_on()` de `Tile` i `execute()` de `Card` s'implementen de manera diferent a cada subclasse, aprofitant el polimorfisme per evitar condicionals complexos.

Per exemple, quan un jugador cau en una casella, simplement es crida `tile.land_on(player)` i el comportament correcte s'executa automàticament segons el tipus de casella (cobrar lloguer, treure una targeta, pagar impostos, etc.).

### Funcions fàbrica

Les funcions `build_tile()`, `build_card()` i `build_player()` actuen com a fàbriques que construeixen objectes del tipus adequat a partir de les dades JSON, centralitzant tota la lògica de construcció i evitant condicionals dispersos pel codi.

### Construcció uniforme i estratègia

La compra i venda de cases segueix la **regla de construcció uniforme**: no es pot construir una casa addicional en un carrer si qualsevol altre carrer del mateix color té menys cases (i viceversa per a la venda). A més, l'estratègia limita la construcció a **una casa o hotel per torn**, prioritzant els carrers amb menys cases (ordre ascendent). Això produeix una construcció progressiva i visual al slideshow.

### Flux d'un torn (`play_turn`)

1. **Presó**: Si el jugador està empresonat:
   - Prova de fer servir carta de sortida lliure.
   - Si no en té, tira els daus: dobles → surt i mou; 3r torn → surt automàticament; sinó → es queda.
2. **Torn normal**: Bucle de dobles (màxim 3).
   - Tira daus. Si surt doble per tercera vegada → directe a la presó.
   - Mou el jugador, executa `land_on()` de la casella.
   - Si ha sortit doble i no està en fallida → repeteix tirada.
3. **Fase de construcció**: Delega a `strategy.build()`.
4. **Següent jugador**: Avança l'índex de torn.

### Gestió de la fallida i transferència de propietats

Quan un jugador es queda sense diners (fallida), el sistema utilitza un **sistema de creditor** per determinar qui hereta les seves propietats:

- **Fallida contra un jugador** (lloguer, cartes de pagament entre jugadors): El jugador creditor hereta totes les propietats del fallit.
- **Fallida contra la banca** (impostos, cartes de manteniment): Les propietats retornen a la banca (propietari `None`).

Cada vegada que es fa un pagament, s'estableix el creditor mitjançant `player.set_creditor()`:

- `Property.land_on()`: Creditor = propietari de la propietat.
- `board.move_to_nearest()`: Creditor = propietari de l'estació/servei públic.
- `Tax.land_on()`: Creditor = `None` (banca).
- `MoneyCard.execute()`, `PropertyRepairsCard.execute()`, `PlayerTransactionCard.execute()`: Creditor = `None` (banca).

### Rent multiplier de les cartes de Chance

Les cartes "Move to nearest station/utility" apliquen un multiplicador al lloguer (×2 per a estacions, ×10 per a serveis públics). La implementació estableix el creditor correctament per gestionar l'herència de propietats en cas de fallida.

## Joc de proves

Els tests es troben al directori `tests/` i asseguren un alt nivell de cobertura del codi (~94%). Utilitzen `random.seed()` per garantir resultats deterministes en processos aparentmemt aleatoris com els daus.

**Nota sobre cobertura complementària**: Els tests estan dissenyats per complementar-se entre si. Per exemple, `test_tile.py` individualment ja cobreix bona part de `tile.py`, però la combinació amb `test_board.py`, `test_main.py` i d'altres fa que la cobertura global sigui significativament més alta del que seria cada fitxer de test per separat. Això és perquè els tests d'integració (com `test_main.py`, que juga una partida sencera) fan camins de codi que els tests unitaris no arriben a tocar.

**Nota sobre `slideshow.py`**: Aquest mòdul no té tests perquè és codi auxiliar de visualització HTML que no forma part de la lògica del joc.

| Fitxer de test | Què verifica |
|---|---|
| `test_board.py` | Inicialització del tauler (40 caselles, jugadors), tirada de daus, wrapping d'índexs, serialització pickle, accés a propietats, cicle de jugadors, presència de tots els tipus de casella, comptatge d'estacions |
| `test_card.py` | Construcció de tots els tipus de targeta amb `build_card()`, execució de cada tipus (collect, pay, move, jail, etc.) |
| `test_data_importation.py` | Càrrega correcta de les dades JSON dels 4 fitxers de configuració |
| `test_deck.py` | Inicialització dels dos decks, robada (redueix mida), barreja, mètode `size()`, devolució de targetes |
| `test_draw.py` | Posicionament de caselles al tauler |
| `test_main.py` | `play_game()` retorna (torns, guanyador), respecta `max_turns`, elimina jugadors en fallida, `main()` genera `game.html` |
| `test_player.py` | Estat inicial del jugador, moviment bàsic, salari de GO, transaccions i detecció de fallida |
| `test_strategy.py` | Decisió de compra amb prou diners / sense prou diners |
| `test_tile.py` | Compra de carrers/estacions/serveis, lloguer (tots els nivells), construcció/venda de cases i hotels (regla uniforme), hipoteques (50% i 110%), escalat d'estacions (1-4), serveis amb 2 propietats, casella "Go To Jail" |

## Instal·lació

### Requisits

- Python
- Biblioteca `drawsvg`

## Ús

### Executar una partida

```bash
python3 main.py
```

La partida es juga de forma automàtica fins que només queda un jugador o s'assoleix el límit de 1000 torns. Els fitxers SVG de cada torn es guarden a la carpeta `games/` (format `tauler-0000.svg`, `tauler-0001.svg`, etc.), i es crea `game.html` per visualitzar la partida al navegador.

### Executar els tests

```bash
python3 -m pytest tests/ -v            # Tots els tests 
python3 -m pytest tests/test_tile.py   # Un fitxer de tests concret
```

### Cobertura de codi

```bash
python3 -m pytest tests/ --cov --cov-report=term-missing
```

### Verificació de tipus

```bash
mypy *.py
```

## Estructura de fitxers

```
programa/
├── board.py              # Motor principal del joc
├── card.py               # Jerarquia de targetes
├── const.py              # Constants del joc
├── deck.py               # Gestió de la pila de targetes
├── draw.py               # Renderització SVG del tauler
├── drawsvg.pyi           # Stubs de tipus per drawsvg (autocompletat i verificació mypy)
├── main.py               # Punt d'entrada
├── player.py             # Classe jugador
├── slideshow.py          # Generador HTML de presentació
├── strategy.py           # Estratègia dels jugadors automàtics
├── tile.py               # Jerarquia de caselles
├── README.md             # Documentació del projecte
├── data/                 # Fitxers de configuració JSON
│   ├── tiles.json        # Definició de les 40 caselles
│   ├── chance.json       # 16 targetes de Sort
│   ├── community-chest.json  # 16 targetes de Comunitat
│   └── players.json      # Definició dels jugadors (nom, color, peça)
├── games/                # Directori on es guarden els SVGs de cada torn
│   ├── tauler-0000.svg
│   ├── tauler-0001.svg
│   └── ...
└── tests/                # Joc de proves
    ├── __init__.py       # Marca el directori com a paquet Python
    ├── conftest.py       # Configuració pytest: sys.path i directori de treball
    ├── test_board.py     # Tests del tauler
    ├── test_card.py      # Tests de les targetes
    ├── test_data_importation.py  # Test d'importació de dades JSON
    ├── test_deck.py      # Tests de la pila de targetes
    ├── test_draw.py      # Tests de la visualització SVG
    ├── test_main.py      # Tests del programa principal
    ├── test_player.py    # Tests del jugador
    ├── test_strategy.py  # Tests de l'estratègia
    └── test_tile.py      # Tests de les caselles
```

### Fitxers auxiliars del directori `tests/`

- **`__init__.py`**: Fitxer buit que indica a Python que `tests/` és un paquet importable. Necessari perquè pytest detecti els tests correctament.
- **`conftest.py`**: Configuració automàtica de pytest. Afegeix el directori `programa/` al `sys.path` perquè els tests puguin importar els mòduls (`board`, `tile`, `player`, etc.) i canvia el directori de treball perquè les rutes relatives com `"data/tiles.json"` funcionin.