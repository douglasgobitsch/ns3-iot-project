#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para executar múltiplos experimentos e coletar resultados
"""

import os
import subprocess
import time

def run_experiments():
    """
    Executa simulações variando diferentes parâmetros
    """
    
    # Criar diretório de resultados
    os.makedirs("results", exist_ok=True)
    
    # Limpar arquivo de resultados anterior
    if os.path.exists("results.txt"):
        os.remove("results.txt")
    
    with open("results.txt", "w") as f:
        f.write("txPower,PDR,Delay,Throughput\n")
    
    print("\n" + "="*60)
    print("EXECUTANDO EXPERIMENTOS - VARIAÇÃO DE POTÊNCIA DE TRANSMISSÃO")
    print("="*60 + "\n")
    
    # Experimento 1: Variar potência de transmissão
    tx_powers = [10, 13, 16, 19, 22]
    
    for power in tx_powers:
        print(f"\n>>> Executando simulação com TxPower = {power} dBm")
        print("-" * 60)
        
        cmd = [
            "python3", "iot_simulation.py",
            f"--txPower={power}",
            "--nNodes=30",
            "--simulationTime=30"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            time.sleep(2)  # Pequena pausa entre simulações
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar simulação: {e}")
            continue
    
    print("\n" + "="*60)
    print("EXPERIMENTOS CONCLUÍDOS!")
    print("="*60)
    print("\nResultados salvos em: results.txt")
    print("Execute 'python3 plot_results.py' para gerar gráficos\n")

def run_experiments_data_rate():
    """
    Executa simulações variando taxa de dados
    """
    
    if os.path.exists("results_datarate.txt"):
        os.remove("results_datarate.txt")
    
    with open("results_datarate.txt", "w") as f:
        f.write("dataRate,PDR,Delay,Throughput\n")
    
    print("\n" + "="*60)
    print("EXECUTANDO EXPERIMENTOS - VARIAÇÃO DE TAXA DE DADOS")
    print("="*60 + "\n")
    
    data_rates = ["500Kbps", "1Mbps", "2Mbps", "5Mbps", "10Mbps"]
    
    for rate in data_rates:
        print(f"\n>>> Executando simulação com DataRate = {rate}")
        print("-" * 60)
        
        cmd = [
            "python3", "iot_simulation.py",
            f"--dataRate={rate}",
            "--nNodes=30",
            "--txPower=16"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            time.sleep(2)
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar simulação: {e}")
            continue

def run_experiments_nodes():
    """
    Executa simulações variando número de nós
    """
    
    if os.path.exists("results_nodes.txt"):
        os.remove("results_nodes.txt")
    
    with open("results_nodes.txt", "w") as f:
        f.write("nNodes,PDR,Delay,Throughput\n")
    
    print("\n" + "="*60)
    print("EXECUTANDO EXPERIMENTOS - VARIAÇÃO DE NÚMERO DE NÓS")
    print("="*60 + "\n")
    
    node_counts = [10, 20, 30, 40, 50]
    
    for nodes in node_counts:
        print(f"\n>>> Executando simulação com {nodes} nós")
        print("-" * 60)
        
        cmd = [
            "python3", "iot_simulation.py",
            f"--nNodes={nodes}",
            "--txPower=16",
            "--simulationTime=30"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            time.sleep(2)
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar simulação: {e}")
            continue

def main():
    """
    Função principal
    """
    
    print("\n" + "="*60)
    print("SUITE DE EXPERIMENTOS - SIMULAÇÃO IoT")
    print("="*60)
    print("\nEscolha o tipo de experimento:")
    print("1 - Variar Potência de Transmissão")
    print("2 - Variar Taxa de Dados")
    print("3 - Variar Número de Nós")
    print("4 - Executar todos os experimentos")
    print("0 - Sair")
    
    choice = input("\nOpção: ").strip()
    
    if choice == "1":
        run_experiments()
    elif choice == "2":
        run_experiments_data_rate()
    elif choice == "3":
        run_experiments_nodes()
    elif choice == "4":
        run_experiments()
        run_experiments_data_rate()
        run_experiments_nodes()
    elif choice == "0":
        print("\nSaindo...")
        return
    else:
        print("\nOpção inválida!")
        return

if __name__ == "__main__":
    main()
