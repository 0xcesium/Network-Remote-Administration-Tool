# Network-Remote-Administration-Tool [![python](https://img.shields.io/badge/Python-2.7-green.svg?style=style=flat-square)](https://www.python.org/downloads/) [![version](https://img.shields.io/badge/Version-Gamma-blue.svg?style=style=flat-square)](https://twitter.com/133_cesium) [![license](https://img.shields.io/badge/License-GPL_3-orange.svg?style=style=flat-square)](https://github.com/0xcesium/HP-Network-Remote-Administration-Tool/blob/master/LICENCE)
Sends multiple commands to a non-limited number of remote machines through the network.


# Laboratory Context
Technical Env : Linux - SMP Debian 3.2.65-1+deb7u2 i686

Targets (Originally design for) : HP / H3C equipements

## FR ##
### Programme :   
Execution d'une ou plusieurs commandes de votre choix sur un panel d'equipements
administrables à partir d'un fichier texte comprenant une IP ou un 
nom de machine (tant que ce dernier est connu de /etc/hosts) par ligne.


### Dépendences : 
Ne comporte que des librairies natives à python mise à part PARAMIKO:

Le plus simple est d'installer le paquet via PIP:

 	pip install paramiko


## EN ##
### Behavior :  
This program allows you to remotely execute one or more commands in a no limit range of machines
(originally developped for networking purpose) mentionned in a text file as argument.
It uses threads to achieve this purpose within a suitable time.
The text file must have one IP or a machine name per line.


### Dependencies :
This only uses natives libs but PARAMIKO:

For most users, the recommended method to install this package is via PIP:

 	pip install paramiko

