---
layout: default
---

# Introduction

The implementation of Quantum Chess presented here is based on this [pre-print](https://arxiv.org/abs/1906.05836) by Christopher Cantwell. In his article, Cantwell creates a theoretical framework that describes a family of circuits and logic that can be used to design a quantum version of chess. The paper goes into a lot of detail, and you should definitely check it out if you want to gain deeper insight into this project. 

Basically, there is a qubit for each square of the board. Each of these qubits represents the state of their corresponding square: ground state if the square is empty and excited if it's not. Each square also has associated with it a data structure that holds classical information, such as the type and color of a piece. When you move a piece you're effectively performing a swap gate between their qubits while also changing their classical data.

Combining both quantum and classical schemes you can create a very elegant and robust quantum version of chess that doesn't require a lot of qubits. With this theoretical framework as the foundation of the project, let's now move on to the goals.

# Project goals

The main goal of this project was to show how one would construct and design a quantum version of chess to play on a quantum computer. The device needed to support the game has the following properties:
* 64 fully-connected qubits
* 9 additional qubits (3 that act as ancilla and 6 to perform the multiple-control toffoli operation)
* Ability to keep evolving a qubit after it's collapsed

All the qubits need to be fully connected because we need to be able to move pieces from an arbitrary square to another arbitrary square. And of course, the ability to evolve a qubit again after it's collapsed is very important since after you collapse it you might need to use its corresponding square again later in the game.

There is obviously no such device in the world at the time of writing this. Even if you reduced the number of qubits by playing in small subsets of the board you'd still need a precision and fidelity that modern quantum computers simply don't have yet.

But that's fine! There is still a way to obtain access to a computer with the requirements listed above: classical simulation. At around 20 qubits classical simulations start to require too much memory, so you'd have to keep the board small. And it is obviously not the ideal solution, because it doesn't scale with the number of qubits, but it's the only one possible at this moment. Although at least you won't have to worry about noise or errors.

[Qiskit](https://qiskit.org/) was our choice of library to implement the circuits and perform all the simulations.

We have defined our goal: to create a quantum version of chess in such a way that, if we substitute the simulation for a real quantum device, the rest of the program would run just fine. In other words, the classical part of the program has to be scalable with the number of qubits, while the quantum part of the program doesn't.

# Brief technical detail

## Quantum
Here we will discuss a few differences with the previously mentioned [paper](https://arxiv.org/abs/1906.05836).

The most important change is how measurements are done. In quantum chess, measurements are used to collapse a certain square to see if it's empty or not, and it's a very important operation that is used to perform many of the moves. In the paper all measurements are included within the circuits, which makes a lot of sense for a theoretical framework. 

Nevertheless, we found that, when implementing the circuits, measuring at the start (before the rest of the circuit takes place) was more convenient for how our system was designed. So we decided to do it that way.

Something else worth mentioning: creating multiple-qubit controlled arbitrary gates (figure 1a) is a very complicated task. And it becomes even more complicated when you don't know the number of control qubits in advance. This is precisely the gate needed when a piece slides through a path. Here each square of the path is one of the control qubits and, as you can imagine, because there are many (many) possible paths a piece can take these circuits become impossible to design.

To solve this problem we use a combined cnot (which has a known implementation for any number of qubits) and we apply it before the arbitary gate (that now has an extra qubit of control). This is shown in figure 1b.

![](https://github.com/Dhanton/quantum-chess/blob/master/docs/images/figure_1.png)

_go [here](https://github.com/Dhanton/quantum-chess/blob/master/docs/images/figure_1.png) if you can't see the image_

These two circuits are equivalent with the appropiate choice of U and U'. Notation a) was used throughout the paper, probably because it was more concise. But notation b) is easier to implement and as such is the one we've used.

## Classical

The classical part of the game needs to be able to work if we used a real quantum computer instead of a simulation. That is, it has to be able to scale to any number of qubits. 

Effectively what this means is that the quantum simulation is a black box (like a real quantum computer) and the classical program can't have access to any internal data (like the statevector of the system). Furthermore, the only information the program can access is the result of the measurements.

The following method was devised with these restrictions in mind.

Each piece is assigned a binary string (a qflag) that starts with a single 1 bit in a unique position. So if we had 4 pieces their qflags would be 0001, 0010, 0100 and 1000. Any time we entangle two pieces we perform a binary OR between their flags. So for example entangling the first piece with the last piece would set both of their flags to 1001.

With this simple idea we can know, without any sort of access to the internal state of the simulation, if two pieces are entangled with each other. Of course we can't know their amplitudes, but we don't need to. 

When one of the pieces needs to be collapsed we simply find all other pieces that have 1s in the same positions (by performing a binary AND) and then we collapse them as well. For example if we wanted to collapse the first piece, we'd instantly know that we also have to collapse the last one (since 1001 AND 1001 != 0).

An example of qflags is shown in figure 2. As you can see, the board is 5x5 and there are 4 unique pieces forming three different pairs. Two of the pieces are entangled (1000 and 0001). One of the pieces is in a state of superposition (0100). And the last piece is collapsed.

![](https://github.com/Dhanton/quantum-chess/blob/master/docs/images/figure_2.png)

_go [here](https://github.com/Dhanton/quantum-chess/blob/master/docs/images/figure_2.png) if you can't see the image_

Qflags are used to run most of the internal operations of the classical program and also to display entanglement and superposition to the player (you can access it by right-cliking).

You can dive right into the qiskit engine [source code](https://github.com/Dhanton/quantum-chess/blob/master/qchess/engines/qiskit/qiskit_engine.py) to find out exactly how qflags work and why they're so powerful. One method of particular interest is _does\_slide\_violate\_double\_occupancy_, which uses permutations to discover if a measurement needs to be done.

# Quantum Chess as a didactic tool

Quantum physics is a very, very complicated and counterintuitive field. And chess is a complex game. It comes as no surprise that quantum chess is very complicated as well.

And yet, it presents a unique sandbox (even to people with limited technical background) to interact directly with quantum phenomena. In doing so the player can develop a more intuitive understanding of the underlying physical principles. And most of these principles are represented in Quantum Chess (such as superposition, entanglement, collapse, bell states or interference) and come from real quantum systems. Or, at least for now, from their simulations.

In our opinion (and this is the opinion expressed in the [paper](https://arxiv.org/abs/1906.05836) as well), quantum games should not teach you quantum physics directly, but rather let you interact with the quantum world. We think this is usually much more effective and didactic.

Although a quantum sandbox sounds exciting, we recommend that players complete the [guided-tutorials](https://github.com/Dhanton/quantum-chess#getting-started) first before playing an actual game of quantum chess.

# Conclusion

We hope players can learn as much playing the game as we've learned developing it.

We've tried to keep the project as configurable as possible. You can create your own [game modes](https://github.com/Dhanton/quantum-chess/tree/master/game_modes), [tutorials](https://github.com/Dhanton/quantum-chess/tree/master/tutorials) and even your own quantum engine (to run the underlying quantum systems). To do so, you can inherit from [BaseEngine class](https://github.com/Dhanton/quantum-chess/blob/master/qchess/engines/base_engine.py).

All the source code and further documentation is available at: [https://github.com/Dhanton/quantum-chess](https://github.com/Dhanton/quantum-chess). If you encounter any bugs or issues, or simply want to discuss the game, you can open a new [Issue](https://github.com/Dhanton/quantum-chess/issues).
