#!/bin/bash
dir="9000-10000"
inp=${dir}/${dir}dhp-5bromo.hkl
inp1=${dir}/${dir}dhp-5bromo.hkl1
inp2=${dir}/${dir}dhp-5bromo.hkl2
basename=DHP-5bromo_partialator_${dir}
fom="R1I R2 Rsplit CC CCstar"
pdb="DHP.refined.cell"
pg="mmm"
highres="1.90"

module load CrystFEL

if [ ! -d "stat" ]; then
	mkdir stat
fi

for mode in $fom
do
    compare_hkl $inp1 $inp2 -y $pg -p $pdb --fom=$mode --highres=$highres --nshells=20 --shell-file="stat/${basename}-$mode".dat 2>>stat/${basename}.log
done
check_hkl -p $pdb --nshells=20 --highres=$highres -y $pg  --shell-file="stat/${basename}-shells".dat $inp 2>>stat/${basename}.log
