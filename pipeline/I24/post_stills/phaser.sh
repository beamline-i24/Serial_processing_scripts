#!/bin/bash
for i in $( ls dose*/*.mtz); do
	SUBSTRING1=$(echo $i| cut -d'/' -f 1)
	SUBSTRING2=$(echo $i| cut -d'/' -f 2)
	SUBSTRING3=$(echo $SUBSTRING2| cut -d'.' -f 1)
	ROOT="PHASER_$SUBSTRING3"
	LOG="LOG_$i"
	OUTPUTPATH="$SUBSTRING1/$ROOT.pdb"
	OUTPUTPATH_MTZ="$SUBSTRING1/$ROOT.mtz"
	OUTPUTPATH_LOG="$SUBSTRING1/$LOG.log"
	echo $SUBSTRING1, $SUBSTRING2, $ROOT
	phenix.phaser hklin $i pdbfile 5i6k.pdb sequence_file 5i6k.fasta
	mv PHASER.1.pdb $OUTPUTPATH
	mv PHASER.1.mtz $OUTPUTPATH_MTZ
	mv PHASER.1.log $OUTPUTPATH_LOG
done
