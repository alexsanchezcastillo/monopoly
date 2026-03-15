# Com provar la partida manualment

## Pas 1: Executar una partida completa

```bash
python main.py
```

Això generarà:
- Fitxers SVG: `tauler-0000.svg`, `tauler-0001.svg`, `tauler-0002.svg`, ...
- Un fitxer per cada torn de la partida
- Output al terminal mostrant tots els moviments

## Pas 2: Generar la visualització HTML

```bash
python slideshow.py game.html tauler-*.svg
```

Això crearà `game.html` amb tots els taulers en una presentació interactiva.

## Pas 3: Obrir al navegador

Opció 1 (terminal):
```bash
open game.html
```

Opció 2 (manual):
- Obrir Finder
- Buscar `game.html`
- Fer doble clic per obrir al navegador

## Exemple de sortida al terminal:

```
[TURN] Jordi rolls 4 and 1 (Total: 5).
       Jordi lands on tile 5.
       Jordi draws Chance: Advance to Go
       Jordi passed GO and collected 200!
[TURN] Mireia rolls 2 and 3 (Total: 5).
       Mireia lands on tile 5.
...
*** Jordi WINS THE GAME! ***
*** Final wealth: M2850 ***
```

## Revisió del codi

Revisa els següents fitxers:
- `board.py` - Lògica principal del joc
- `player.py` - Estat del jugador (propietats, diners, presó)
- `tile.py` - Definició de les caselles i accions
- `card.py` - Sistema de targetes
- `strategy.py` - Decisió de compra de propietats
- `main.py` - Punt d'entrada i llop principal

## Tests

Executa els tests per verificar la correctesa:

```bash
pytest -v                    # Tots els tests
pytest test_tile.py -v       # Tests de caselles
pytest test_player.py -v     # Tests de jugadors
pytest test_board.py -v      # Tests del tauler
```

## Type checking

Verifica que no hi hagi errors de tipus:

```bash
mypy *.py
```
