# Quantum Chess

A quantum version of chess based on a very interesting [pre-print](https://arxiv.org/abs/1906.05836). You can play any of the multiple [game modes](game_modes/) available, or you can create your own. You can also play the [tutorials](tutorials/) to learn about the rules of the game and quantum physics in general.

## Prerequisites

Python 3.6. Later versions of Python should also work, but if you're running into trouble I recommend using Python 3.6.

If you're on windows a bash shell is recommended. On linux the default terminal of your preferred distro should be enough.

## Installing

You'll need to install the latest version of [qiskit](https://github.com/Qiskit/qiskit-terra) and [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI/).

```
pip install qiskit
pip install pysimplegui
```

## Getting Started

To see all available parameters, run

```
python main.py --help
```

It is recommended that you play the guided tutorials before playing an actual game

```
python main.py --guided-tutorials
```

This will teach you all the rules that you need to know. You can stop at any time, and your progress will be saved. If you'd like to replay a specific tutorial, you can do

```
python main.py --tutorial specific_tutorial_file
```

Once you're ready to play an actual game
```
python main.py --game-mode game_mode_file
```

where _game\_mode\_file_ is the game mode filename with no extension or path. The default game mode is [micro_chess](game_modes/micro_chess.json). Go to [game_modes/README](game_modes/README.md) to read the rules of each game mode.

Note that some game modes (for example, [chess](game_modes/chess.json)) require more qubits than are possible to simulate classically. A warning will be displayed in such cases, and the program might crash when measuring.

## Running the tests

You can simply run
```
python -m unittest discover -s tests --verbose
```

from the main directory. Be aware that running all the tests takes about 7 to 10 minutes on an average computer. Go to [tests/README](tests/README.md) to find out why and to see how to tune the parameters to reduce execution time or increase accuracy.


## License

This project is licensed under the Apache License 2.0 - see [LICENSE](LICENSE.md) for details.

## Acknowledgments

Most of the mathematical framework this project is based on was developed by Christopher Cantwell in this [pre-print](https://arxiv.org/abs/1906.05836). Some modifications were made to most of the circuits and some of the rules, but the core ideas are all his.

I'd also like to thank Eduardo Bernal and Javier Aguay for multiple discussions and their very helpful feedback on the project.
