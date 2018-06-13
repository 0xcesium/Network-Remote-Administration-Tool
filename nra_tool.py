#!/usr/bin/env python2
#-*- coding: utf-8 -*-

__author__ = '''
cs133
twitter: @133_cesium
'''
__license__='''
<+> Under the terms of the GPL v3 License.
'''
__description__='''
Env : Linux - SMP Debian 3.2.65-1+deb7u2 i686

### FR ###
Programme :   Execution d'une commande de votre choix sur un panel d'equipements
              administrables à partir d'un fichier texte comprenant une IP ou un 
              nom de machine (tant que ce dernier est connu de /etc/hosts) par ligne.

v2.7 : Threads
v3.1 : Regex et Traitement de texte
v3.4 : Retrait de la methode 2
v4.0 : Respect des conventions : Code plus lisible

Ne comporte que des librairies natives à python mise à part PARAMIKO.

### EN ###
Behavior :  This program allows you to execute one or more command in a no limit range of machines
            (originally developped for networking purpose) mentionned in a text file as argument.
            The text file must have one IP or machine name per line, without any other limits.

It only uses natives libs but PARAMIKO.
'''

from inspect import getfile, currentframe
from os import path, sysconf, system
from re import findall, search
from getpass import getpass
from threading import Thread
from paramiko import SSHClient,AutoAddPolicy
from paramiko import util as putil
from socket import timeout as tmo
from string import ascii_letters
from time import sleep
from argparse import ArgumentParser
import sys

ERR             = "\33[91m[-]\33[0m"
SUCC            = "\33[92m[+]\33[0m"
PEND            = "\33[33m[~]\33[0m"
INFO            = "\33[94m[*]\33[0m"

host            = ""
passwd          = ""
log_info        = "/tmp/paramiko.log"
nom_repertoire  = path.dirname(path.abspath(getfile(currentframe()))) + '/'
BUFSIZE         = 4096
fichier_sortie  = False
ip              = True
DEBUG           = False

commandes       = []
equipements     = []

# Nombre de coeurs disponibles en vu d'un traitement par Threads
nb_coeurs        = sysconf("SC_NPROCESSORS_ONLN")


# Impression des resultats (retour commandes envoyees aux equipements)
def impression_res(txt_retour,index):
    # Extraction du nom de l'equipement si ce n'est pas deja fait
    tmp,nom = '',''
    if ip and not passed:
        tmp = search(r'(?<=<)[a-z]|[A-Z]{3}-[0-9]{4}', txt_retour)
        nom = tmp.group(0)
        passed = True
    else: nom = equipements[index]
    # Exculsion des octets parasites
    out = txt_retour.replace('<' + nom + '>','')
    parasite = 1
    while True:
        if out[-parasite] not in ascii_letters:
            parasite += 1
        else:
            break
    fichier_nom = nom_repertoire + nom + '.cfg'
    if fichier_sortie:
        with open(fichier_nom + 'tmp','w+') as f_t:
            f_t.write(out)
        with open(fichier_nom + 'tmp','r') as f_t:
            with open(fichier_nom,'w+') as f_o:
                for lig in f_t:
                    if not lig.isspace():
                        lig = lig.replace('\x1b[16D                \x1b[16D','')
                        lig = lig.replace('  ---- More ----','')
                        f_o.write(lig)
        system('rm ' + fichier_nom + 'tmp')
    else:
        print SUCC,"Retour de l'equipement :",nom
        print out[:-parasite + 1]
    return

# Envoie de plusieurs commandes : Methode 1
# prise en charge les commandes avec interaction utilisateur.
# EXEMPLE : dis current-configuration
def execution_cmd(client_n,index):
    global commandes
    txt_retour,tmp = '',''
    passed = False
    # Invocation du terminal distant
    connx = client_n.invoke_shell()
    for i in range(len(commandes)):
        if commandes[i].lower() in ('entrée','entree'):
            connx.send('\r\n')
        else:
            connx.send(commandes[i])
            connx.send('\r\n')
        sleep(.9)
        while True:
            tmp = connx.recv(BUFSIZE)
            if '---- More ----' in tmp:
                # Capsule de temps allouee pour l'ouverture du flux
                connx.send('\r\n'*50)
                sleep(.4)
                txt_retour += tmp
            else:
                txt_retour += tmp
                break
    if "Ambiguous command found at" in txt_retour:
        sys.stderr.write(INFO + " AMBIGUOUS COMMAND trouvée dans %s\n" % equipements[index])
    if "Unrecognized command found" in txt_retour:
        sys.stderr.write(INFO + " UNRECOGNIZED COMMAND trouvée dans %s\n" % equipements[index])
    impression_res(txt_retour,index)
    return True

# Recuperation des commandes de configuration a envoyer a l'equipement
def get_commandes():
    global ip, commandes, fichier_sortie
    compteur = 0
    while True:
        compteur += 1
        commandes.append(raw_input(INFO +
                        " " + str(compteur) + "* Commande a executer : "))
        if not commandes[-1]:
            break
    if not len(commandes):
        sys.exit(5)
    pattern = raw_input(INFO + " Dans le fichier, " +
             "il y a des IPv4(1) ou des noms d'equipements(2)? [1|2]: ")
    if pattern != "1":
        ip = False
    if raw_input(INFO +
        " Enregistrer les resultats obtenus dans un fichier? [y|n]: ") in ['y','Y']:
        print SUCC,'Impression dans un fichier au nom de chacun des equipements.'
        fichier_sortie = True
    return

# Ouverture d'une socket par equipement
def open_connexion(index):
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(equipements[index],
                   username=host,
                   password=passwd,
                   timeout=10,
                   look_for_keys=False)
    return client

# Thread de traitement par equipement
def traitement(index):
    try:
        client = open_connexion(index)
        if DEBUG:
            print SUCC,"Connexion SSH reussie sur %s." % equipements[index]
        if execution_cmd(client,index):
            if DEBUG:
                print INFO,"Commandes executees avec succes."
        else:
            sys.stderr.write(ERR + " Commandes non executees sur %s.\n" % equipements[index])
        client.close()
        if DEBUG:
            print INFO,equipements[index],": Client SSH deconnecte avec succes."
    # Gestion des erreurs
    except tmo:
        sys.stderr.write(ERR +
            " Tentative de connexion hors delai sur %s : %s.\n" % (equipements[index], str(tmo)))
    except Exception as e:
        sys.stderr.write(ERR + " Une erreur est survenue.(traitement) %s - %s : %s\n" % (equipements[index], e.__class__, str(e)))
        if DEBUG:
            raise
    return


# Point d'entree
def main():
    global commande, commandes, equipements, host, passwd, DEBUG

    parser = ArgumentParser(description="Execution de commandes via SSH sur une multitude d'equipement HP en une seule phase.")
    parser.add_argument("-r","--read",
           metavar="FICHIER",
           action="store",
           help="Fichier contenant les adresses IP ou les noms d'equipements.",
           required=True)
    parser.add_argument("-d","--debug",
           action="store_true",
           default=False,
           help="Verbosité.")
    args = parser.parse_args()

    if args.debug == True:
        DEBUG = True

    # Capture de la/des commande(s) a executer
    try: get_commandes()
    except: sys.exit(1)

    # Recuperation du mot de passe
    host = raw_input(INFO + " Login : ")
    passwd = getpass(INFO + \
        " Mot de passe de {} (ne sera pas imprime) : ".format(host))

    # Recuperation du contenu du fichier
    try:
        with open(args.read,'r') as file:
            for lig in file:
                if ip:
                    equipement_def = findall(r'[0-9]+(?:\.[0-9]+){3}', lig)
                else:
                    equipement_def = findall(r'[a-z]|[A-Z]{3}-[0-9]{4}', lig)
                if equipement_def:
                    equipements.append(equipement_def[0])
        print SUCC,"Contenu du fichier recupere."

    except:
        sys.stderr.write(ERR + " Erreur sur le fichier.\n")
        if DEBUG:
            raise
        sys.exit(1)

    # Enregistrement des logs en fonction des evenements
    putil.log_to_file(log_info)

    # Boucle de connexion en fonction du fichier et des commandes a envoyer
    # Multi-Threading process (2eme script re-ecrit entierement)
    # La programmation parallele est une solution d'optimisation de calcul
    # L'impact sur le CPU est plafonne a un seuil de threads par coeur du processeur
    threads = []
    compteur,next = 0,0
    while True:
        try:
            compteur += 1

            # Le nombre de Threads optimal se base sur des tests personnels:
            # (nb_coeurs * nb_Threads) < 25% du CPU/nb_coeurs = True
            # Un seul coeur est disponible, nombre maximum de Threads: 5
            thread_client = Thread(target=traitement,args=(next,))
            thread_client.start()
            threads.append(thread_client)
            if DEBUG:
                print PEND,'Nouveau Thread n°',compteur,':',threads[compteur-1]
            next += 1
            if nb_coeurs*100 == len(threads):
                # File d'attente + 1
                thread_client.join()
                if DEBUG:
                    print '~~~~~~~~~~~~~~~~~~~~~~ + ~~~~~~~~~~~~~~~~~~~~~~'
                print INFO,len(threads),\
                      "threads en cours d'execution. "\
                      "Le script reprendra dans 7 secondes."
                if DEBUG:
                    print '~~~~~~~~~~~~~~~~~~~~~~ + ~~~~~~~~~~~~~~~~~~~~~~'
                #print threads
                del threads[:]
                compteur = 0
                sleep(7)

        except KeyboardInterrupt:
            sys.stderr.write("\n" + INFO +
                " L'utilisateur a souhaite interrompre la procedure.\n")
            sys.exit(3)
        except:
            sys.stderr.write(ERR + " Une erreur est survenue.(main)\n")
            if DEBUG:
                raise

        if next == len(equipements):
            print INFO,"Fin du traitement."
            break
    return


# Initialisation de la procedure
if __name__ == "__main__":
    sys.exit(main())
