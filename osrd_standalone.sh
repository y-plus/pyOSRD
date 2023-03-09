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

# Run stand alone simulation
java -jar /home/renan/osrd/core/build/libs/osrd-all.jar standalone-simulation --infra_path $infra --sim_path $simulation --res_path $results