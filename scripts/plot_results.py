1#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para análise e visualização dos resultados da simulação
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def setup_plot_style():
    """
    Configura o estilo dos gráficos
    """
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10

def plot_tx_power_analysis():
    """
    Plota análise de variação de potência de transmissão
    """
    
    if not os.path.exists("./results/results.txt"):
        print("Arquivo results.txt não encontrado!")
        return
    
    # Ler dados
    df = pd.read_csv("./results/results.txt")
    
    # Criar diretório para gráficos
    os.makedirs("graphs", exist_ok=True)
    
    # Criar figura com subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Análise de Desempenho: Variação da Potência de Transmissão', 
                 fontsize=16, fontweight='bold')
    
    # 1. PDR vs TxPower
    axes[0, 0].plot(df['txPower'], df['PDR'], 'bo-', linewidth=2, markersize=8)
    axes[0, 0].set_xlabel('Potência de Transmissão (dBm)')
    axes[0, 0].set_ylabel('PDR (%)')
    axes[0, 0].set_title('Packet Delivery Ratio')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_ylim([0, 105])
    
    # Adicionar valores nos pontos
    for i, row in df.iterrows():
        axes[0, 0].annotate(f'{row["PDR"]:.1f}%', 
                           (row['txPower'], row['PDR']),
                           textcoords="offset points", 
                           xytext=(0,10), 
                           ha='center',
                           fontsize=9)
    
    # 2. Delay vs TxPower
    axes[0, 1].plot(df['txPower'], df['Delay'], 'ro-', linewidth=2, markersize=8)
    axes[0, 1].set_xlabel('Potência de Transmissão (dBm)')
    axes[0, 1].set_ylabel('Atraso Médio (ms)')
    axes[0, 1].set_title('Atraso Ponta a Ponta')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Adicionar valores nos pontos
    for i, row in df.iterrows():
        axes[0, 1].annotate(f'{row["Delay"]:.1f}ms', 
                           (row['txPower'], row['Delay']),
                           textcoords="offset points", 
                           xytext=(0,10), 
                           ha='center',
                           fontsize=9)
    
    # 3. Throughput vs TxPower
    axes[1, 0].plot(df['txPower'], df['Throughput'], 'go-', linewidth=2, markersize=8)
    axes[1, 0].set_xlabel('Potência de Transmissão (dBm)')
    axes[1, 0].set_ylabel('Vazão (kbps)')
    axes[1, 0].set_title('Throughput Total')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Adicionar valores nos pontos
    for i, row in df.iterrows():
        axes[1, 0].annotate(f'{row["Throughput"]:.0f}', 
                           (row['txPower'], row['Throughput']),
                           textcoords="offset points", 
                           xytext=(0,10), 
                           ha='center',
                           fontsize=9)
    
    # 4. Comparação normalizada
    # Normalizar valores para comparação
    pdr_norm = df['PDR'] / df['PDR'].max() * 100
    delay_norm = (1 - df['Delay'] / df['Delay'].max()) * 100  # Invertido: menor é melhor
    throughput_norm = df['Throughput'] / df['Throughput'].max() * 100
    
    x = np.arange(len(df))
    width = 0.25
    
    axes[1, 1].bar(x - width, pdr_norm, width, label='PDR', color='blue', alpha=0.7)
    axes[1, 1].bar(x, throughput_norm, width, label='Throughput', color='green', alpha=0.7)
    axes[1, 1].bar(x + width, delay_norm, width, label='Delay (inv.)', color='red', alpha=0.7)
    
    axes[1, 1].set_xlabel('Potência de Transmissão (dBm)')
    axes[1, 1].set_ylabel('Desempenho Normalizado (%)')
    axes[1, 1].set_title('Comparação de Métricas Normalizadas')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(df['txPower'])
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('graphs/tx_power_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico salvo: graphs/tx_power_analysis.png")
    plt.show()

def generate_summary_table():
    """
    Gera tabela resumo dos resultados
    """
    
    if not os.path.exists("./results/results.txt"):
        print("Arquivo results.txt não encontrado!")
        return
    
    df = pd.read_csv("./results/results.txt")
    
    print("\n" + "="*70)
    print("TABELA RESUMO DOS RESULTADOS")
    print("="*70)
    
    print(f"\n{'TxPower (dBm)':<15} {'PDR (%)':<15} {'Delay (ms)':<15} {'Throughput (kbps)':<20}")
    print("-"*70)
    
    for _, row in df.iterrows():
        print(f"{row['txPower']:<15.1f} {row['PDR']:<15.2f} {row['Delay']:<15.2f} {row['Throughput']:<20.2f}")
    
    print("-"*70)
    print(f"{'Média:':<15} {df['PDR'].mean():<15.2f} {df['Delay'].mean():<15.2f} {df['Throughput'].mean():<20.2f}")
    print(f"{'Desvio Padrão:':<15} {df['PDR'].std():<15.2f} {df['Delay'].std():<15.2f} {df['Throughput'].std():<20.2f}")
    print("="*70 + "\n")

def plot_comparative_analysis():
    """
    Plota análise comparativa de múltiplos experimentos
    """
    
    files = {
        'Potência TX': './results/results.txt',
        'Taxa de Dados': 'results_datarate.txt',
        'Número de Nós': 'results_nodes.txt'
    }
    
    available_files = {k: v for k, v in files.items() if os.path.exists(v)}
    
    if not available_files:
        print("Nenhum arquivo de resultados encontrado!")
        return
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Análise Comparativa de Diferentes Configurações', 
                 fontsize=16, fontweight='bold')
    
    colors = ['blue', 'green', 'red']
    
    for idx, (name, file) in enumerate(available_files.items()):
        df = pd.read_csv(file)
        col_name = df.columns[0]  # Primeira coluna (variável independente)
        
        axes[0].plot(df[col_name], df['PDR'], 'o-', 
                    color=colors[idx], linewidth=2, markersize=6, label=name)
        axes[1].plot(df[col_name], df['Delay'], 'o-', 
                    color=colors[idx], linewidth=2, markersize=6, label=name)
        axes[2].plot(df[col_name], df['Throughput'], 'o-', 
                    color=colors[idx], linewidth=2, markersize=6, label=name)
    
    axes[0].set_title('Packet Delivery Ratio')
    axes[0].set_ylabel('PDR (%)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    axes[1].set_title('Atraso Médio')
    axes[1].set_ylabel('Atraso (ms)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    axes[2].set_title('Throughput')
    axes[2].set_ylabel('Vazão (kbps)')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('graphs/comparative_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico salvo: graphs/comparative_analysis.png")
    plt.show()

def generate_report():
    """
    Gera relatório completo em texto
    """
    
    if not os.path.exists("./results/results.txt"):
        print("Arquivo results.txt não encontrado!")
        return
    
    df = pd.read_csv("./results/results.txt")
    
    report = []
    report.append("\n" + "="*70)
    report.append("RELATÓRIO DE ANÁLISE DE DESEMPENHO - SIMULAÇÃO IoT")
    report.append("="*70 + "\n")
    
    report.append("1. RESUMO EXECUTIVO\n")
    report.append(f"   - Total de experimentos: {len(df)}")
    report.append(f"   - PDR médio: {df['PDR'].mean():.2f}%")
    report.append(f"   - Atraso médio: {df['Delay'].mean():.2f} ms")
    report.append(f"   - Throughput médio: {df['Throughput'].mean():.2f} kbps\n")
    
    report.append("2. ANÁLISE DE POTÊNCIA DE TRANSMISSÃO\n")
    
    best_pdr = df.loc[df['PDR'].idxmax()]
    report.append(f"   - Melhor PDR: {best_pdr['PDR']:.2f}% com TxPower={best_pdr['txPower']} dBm")
    
    best_delay = df.loc[df['Delay'].idxmin()]
    report.append(f"   - Menor atraso: {best_delay['Delay']:.2f} ms com TxPower={best_delay['txPower']} dBm")
    
    best_throughput = df.loc[df['Throughput'].idxmax()]
    report.append(f"   - Maior throughput: {best_throughput['Throughput']:.2f} kbps com TxPower={best_throughput['txPower']} dBm\n")
    
    report.append("3. RECOMENDAÇÕES\n")
    if df['PDR'].mean() > 90:
        report.append("   - A rede apresenta boa taxa de entrega de pacotes")
    else:
        report.append("   - Considerar aumentar potência ou reduzir densidade de nós")
    
    if df['Delay'].mean() < 50:
        report.append("   - O atraso está dentro de limites aceitáveis para IoT")
    else:
        report.append("   - Considerar otimizar parâmetros de MAC ou reduzir tráfego")
    
    report.append("\n" + "="*70 + "\n")
    
    report_text = "\n".join(report)
    print(report_text)
    
    # Salvar relatório
    with open("report_summary.txt", "w") as f:
        f.write(report_text)
    
    print("✓ Relatório salvo: report_summary.txt\n")

def main():
    """
    Função principal
    """
    
    setup_plot_style()
    
    print("\n" + "="*60)
    print("ANÁLISE E VISUALIZAÇÃO DE RESULTADOS")
    print("="*60)
    print("\nOpções:")
    print("1 - Gerar gráficos de Potência TX")
    print("2 - Gerar tabela resumo")
    print("3 - Análise comparativa")
    print("4 - Gerar relatório completo")
    print("5 - Executar tudo")
    print("0 - Sair")
    
    choice = input("\nOpção: ").strip()
    
    if choice == "1":
        plot_tx_power_analysis()
    elif choice == "2":
        generate_summary_table()
    elif choice == "3":
        plot_comparative_analysis()
    elif choice == "4":
        generate_report()
    elif choice == "5":
        plot_tx_power_analysis()
        generate_summary_table()
        plot_comparative_analysis()
        generate_report()
    elif choice == "0":
        print("\nSaindo...")
        return
    else:
        print("\nOpção inválida!")

if __name__ == "__main__":
    main()
