#!/bin/bash
## Usage : 
## ./osrd_standalone.sh -i infra.json -r res.json -s sim.json
##
## Une fois osrd core buildé


while getopts i:s:r: flag
do
    case "${flag}" in
        i) infra=${OPTARG};;
        s) simulation=${OPTARG};;
        r) results=${OPTARG};;
    esac
done

# Quick fix
lead='^  \"rolling_stocks\": \[$'
tail='^  ]$'
sed -e "/$lead/,/$tail/{ /$lead/{p; r ./fast_rolling_stock.json
        }; /$tail/p; d }"  $simulation > $simulation"_fix"

# Run stand alone simulation
java -jar /home/renan/osrd/core/build/libs/osrd-all.jar standalone-simulation --infra_path $infra --sim_path $simulation"_fix" --res_path $results