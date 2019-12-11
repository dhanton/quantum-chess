# Game modes

You can select the game mode you want to play with
```
python main.py --game-mode game_mode_file
```

where _game\_mode\_file_ is the name of the file with no path or extension. Each game mode has a unique starting position of the board, as well as different rules regarding castling, pawn double step and promotion (although only queen promotion is allowed).

Below you can see the rules of each game mode. Because of the small board but interesting gameplay, Micro Chess is the default and the one I recommend playing. Some of the other game modes require more qubits and might crash if the system becomes too entangled.

You can also create your own game modes by copying any of the existing ones, changing its name and modifying the parameters.

## Chess
Good old [chess](https://en.wikipedia.org/wiki/Chess). I included this game mode for educational purposes, but no classical computer will be able to simulate it.

## King Wars
![](https://github.com/Dhanton/quantum-chess/blob/master/docs/images/king_wars.png)

* Castling is not allowed

## Micro Chess
![](https://github.com/Dhanton/quantum-chess/blob/master/docs/images/micro_chess.png)

* Castling is allowed
* Pawn double step is not allowed
* Promotion is allowed

## Tall chess
![](https://github.com/Dhanton/quantum-chess/blob/master/docs/images/tall_chess.png)

* Castling is allowed
* Pawn double step is allowed
* Promotion is allowed

## Baby chess
![](https://github.com/Dhanton/quantum-chess/blob/master/docs/images/baby_chess.png)

* Castling is not allowed
* Pawn double step is not allowed
* Promotion is allowed

## Minit chess
![](https://github.com/Dhanton/quantum-chess/blob/master/docs/images/minit_chess.png)

* Castling is allowed
* Pawn double step is not allowed
* Promotion is allowed
