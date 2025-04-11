# Berloga Apiary Defence statistics analyzer

The Python script for Berloga Apiary Defence statistics analysis.

The game is available here: https://platform.kruzhok.org/apiary

The code is distributed under the Lesser GNU Public License (version 3), the documentation -- under
the GNU Free Documentation License (version 1.3).

## Requirements

* Python 3.x
* Python binding for the CyberiadaML library - https://github.com/kruzhok-team/libcyberiadamlpp-py

## The list of available scripts:

There are statistical analysers and printing scripts:

* best-programs.py - print best programs statistics for the selected data
* find-program.py - find players who used the provided (or equivalent) program while playing
* inspect-program.py - print the program and its differece with the default one 
* print-players.py - save players' statistics as CSV 
* print-programs.py - print all player's programs
* print-sessions.py - print all player's sessions
* statistics.py - print total statistics based on the selected data and the player filter

Technical utilities:

* split-data.py - script to select all CSV server data dedicated to the particular players  
* update-archive.py - download all required programming artefacts from the online Berloga storage
