#!/bin/bash
# run-experiments.sh

echo "txPower,PDR,Delay,Throughput" > results.txt

# Variar potência de transmissão
for power in 10 13 16 19 22
do
    echo "Executando simulação com TxPower = $power dBm"
    ./ns3 run "scratch/iot-simulation --txPower=$power --nNodes=30"
done

echo "Experimentos concluídos! Resultados salvos em results.txt"
