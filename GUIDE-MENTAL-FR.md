# MENTAL — prise en main

Un firmware pour le M-VAVE FM-1, réglé pour la tekno mentale. Il est basé sur
SLOOP (groovebox 4 pistes), avec des sons et des réglages faits pour ce style.

## Installer

FM-1 branché en USB, dans **Chrome ou Edge** :
**https://9robinnn.github.io/mental/**

Ne débranche pas pendant l'écriture. Pour revenir en arrière : la même page
propose le retour au firmware d'origine, et M-UPGRADE de M-VAVE marche aussi.
Installer un firmware non officiel reste à tes risques.

## Ce qui change par rapport à SLOOP

- **Kits MENTAL et MENTAL H** (en fin de liste des kits). Le kick MENTAL est un
  sinus sur la tonique, de 41 à 48 Hz selon la note, avec une queue qui atteint
  le temps suivant à 170 BPM : mesuré à 99,7 % d'énergie sous 80 Hz, queue de
  508 ms (et 1059 ms pour KICK 2). MENTAL H est le même en plus sale, avec des
  charleys métal et un clank industriel.
- **Neuf sons mentale** : MNT SUB, MNT ACID, MNT SCREECH (ANALOG) ;
  MNT ABYSS, MNT RITUAL, MNT VOID (GRAIN, les drones) ; MNT SCREAM, MNT CAVERN,
  MNT GRIND (NOISE, les textures qui grincent).
- **À l'allumage** : 170 BPM, gamme phrygienne, piste 1 MNT SUB, piste 2
  MNT RITUAL, piste 3 MNT ACID, piste 4 sur le kit MENTAL. Tu appuies sur une
  touche blanche de la piste de batterie et le kick sort.
- **UNISON corrigé** : les voix se répartissaient au hasard et pouvaient se
  superposer en phase (jusqu'à +8,7 dB d'un coup). Chacune prend maintenant sa
  part du cycle.

## Jouer

- Les **touches blanches** de la piste de batterie jouent les 16 sons.
  OCT− / OCT+ maintenus donnent les frappes douces ou fortes.
- **Maintiens un bouton** et les touches changent de métier : FX pour les
  effets punch-in, SEQ pour les pas, GLO pour les mutes et les volumes,
  SAVE pour les sections A à D.
- Le **tempo** va de 40 à 240.

## Tes samples

Le zip `MENTAL_samples.zip` contient tes sons MTLOX déjà convertis au format
des slots. Tu les charges dans l'éditeur web :
**https://9robinnn.github.io/mental/webapp/editor/**
Le fichier LISEZ-MOI dedans dit quoi mettre où.

## Crédits

Dérivé de SLOOP (isod89, GPL-3.0), lui-même basé sur Felucca (Leo Kuroshita,
Hügelton Instruments). Ce dépôt reste en GPL-3.0. Aucun sample commercial n'y
est distribué.
