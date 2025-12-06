#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simulação IoT - Projeto de Telecomunicações
Tecnologia: IEEE 802.11n (Wi-Fi)
Análise de desempenho com variação de parâmetros
"""

import sys
import os
from ns import ns

def main(argv):
    """
    Função principal da simulação
    """
    
    # ==================== PARÂMETROS CONFIGURÁVEIS ====================
    n_nodes = 30                    # Número de nós sensores
    simulation_time = 30.0          # Tempo de simulação (segundos)
    area_size = 100.0               # Tamanho da área (metros)
    data_rate = "1Mbps"             # Taxa de dados
    packet_size = 64                # Tamanho do pacote (bytes)
    interval = 0.1                  # Intervalo entre pacotes (segundos)
    tx_power = 16.0                 # Potência de transmissão (dBm)
    propagation_model = "LogDistance"  # Modelo de propagação
    
    # Parsing de argumentos
    cmd = ns.CommandLine()
    cmd.AddValue("nNodes", "Número de nós sensores", n_nodes)
    cmd.AddValue("simulationTime", "Tempo de simulação", simulation_time)
    cmd.AddValue("dataRate", "Taxa de dados", data_rate)
    cmd.AddValue("txPower", "Potência de transmissão (dBm)", tx_power)
    cmd.AddValue("interval", "Intervalo entre pacotes", interval)
    cmd.AddValue("propagationModel", "Modelo de propagação", propagation_model)
    cmd.Parse(argv)
    
    # Obter valores atualizados
    n_nodes = cmd.GetValue("nNodes", n_nodes)
    simulation_time = cmd.GetValue("simulationTime", simulation_time)
    tx_power = cmd.GetValue("txPower", tx_power)
    
    # ==================== LOG ====================
    ns.core.Time.SetResolution(ns.core.Time.NS)
    ns.core.LogComponentEnable("UdpEchoClientApplication", ns.core.LOG_LEVEL_INFO)
    ns.core.LogComponentEnable("UdpEchoServerApplication", ns.core.LOG_LEVEL_INFO)
    
    print("\n" + "="*50)
    print("Simulação IoT - Rede Sem Fio")
    print("="*50)
    print(f"Nós sensores: {n_nodes}")
    print(f"Potência TX: {tx_power} dBm")
    print(f"Taxa de dados: {data_rate}")
    print(f"Tempo de simulação: {simulation_time} s")
    print("="*50 + "\n")
    
    # ==================== CRIAÇÃO DOS NÓS ====================
    sensor_nodes = ns.network.NodeContainer()
    sensor_nodes.Create(n_nodes)
    
    sink_node = ns.network.NodeContainer()
    sink_node.Create(1)
    
    all_nodes = ns.network.NodeContainer()
    all_nodes.Add(sensor_nodes)
    all_nodes.Add(sink_node)
    
    # ==================== CONFIGURAÇÃO WI-FI ====================
    wifi = ns.wifi.WifiHelper()
    wifi.SetStandard(ns.wifi.WIFI_STANDARD_80211n)
    
    # Canal Wi-Fi
    wifi_channel = ns.wifi.YansWifiChannelHelper()
    wifi_channel.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel")
    
    if propagation_model == "LogDistance":
        wifi_channel.AddPropagationLoss("ns3::LogDistancePropagationLossModel",
                                       "Exponent", ns.core.DoubleValue(3.0),
                                       "ReferenceDistance", ns.core.DoubleValue(1.0))
    elif propagation_model == "Nakagami":
        wifi_channel.AddPropagationLoss("ns3::NakagamiPropagationLossModel")
    
    # PHY Wi-Fi
    wifi_phy = ns.wifi.YansWifiPhyHelper()
    wifi_phy.SetChannel(wifi_channel.Create())
    wifi_phy.Set("TxPowerStart", ns.core.DoubleValue(tx_power))
    wifi_phy.Set("TxPowerEnd", ns.core.DoubleValue(tx_power))
    
    # MAC Wi-Fi
    wifi_mac = ns.wifi.WifiMacHelper()
    ssid = ns.wifi.Ssid("iot-network")
    
    # Configurar AP (sink)
    wifi_mac.SetType("ns3::ApWifiMac",
                     "Ssid", ns.wifi.SsidValue(ssid))
    ap_device = wifi.Install(wifi_phy, wifi_mac, sink_node)
    
    # Configurar STAs (sensores)
    wifi_mac.SetType("ns3::StaWifiMac",
                     "Ssid", ns.wifi.SsidValue(ssid),
                     "ActiveProbing", ns.core.BooleanValue(False))
    sta_devices = wifi.Install(wifi_phy, wifi_mac, sensor_nodes)
    
    # ==================== MOBILIDADE ====================
    mobility = ns.mobility.MobilityHelper()
    
    # Sink no centro
    sink_position = ns.mobility.ListPositionAllocator()
    sink_position.Add(ns.core.Vector(area_size/2, area_size/2, 1.5))
    mobility.SetPositionAllocator(sink_position)
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
    mobility.Install(sink_node)
    
    # Sensores distribuídos aleatoriamente
    sensor_position = ns.mobility.RandomDiscPositionAllocator()
    sensor_position.SetAttribute("X", ns.core.DoubleValue(area_size/2))
    sensor_position.SetAttribute("Y", ns.core.DoubleValue(area_size/2))
    sensor_position.SetAttribute("Rho", ns.core.StringValue(
        f"ns3::UniformRandomVariable[Min=0|Max={area_size/2}]"))
    
    mobility.SetPositionAllocator(sensor_position)
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
    mobility.Install(sensor_nodes)
    
    # ==================== PILHA DE PROTOCOLOS ====================
    stack = ns.internet.InternetStackHelper()
    stack.Install(all_nodes)
    
    address = ns.internet.Ipv4AddressHelper()
    address.SetBase(ns.network.Ipv4Address("10.1.1.0"), 
                    ns.network.Ipv4Mask("255.255.255.0"))
    interfaces = address.Assign(sta_devices)
    ap_interface = address.Assign(ap_device)
    
    # ==================== APLICAÇÕES ====================
    port = 9
    
    # Servidor UDP no sink
    server = ns.applications.UdpServerHelper(port)
    server_app = server.Install(sink_node.Get(0))
    server_app.Start(ns.core.Seconds(0.0))
    server_app.Stop(ns.core.Seconds(simulation_time))
    
    # Clientes UDP nos sensores
    client = ns.applications.UdpClientHelper(ap_interface.GetAddress(0), port)
    client.SetAttribute("MaxPackets", ns.core.UintegerValue(4294967295))
    client.SetAttribute("Interval", ns.core.TimeValue(ns.core.Seconds(interval)))
    client.SetAttribute("PacketSize", ns.core.UintegerValue(packet_size))
    
    client_apps = ns.network.ApplicationContainer()
    for i in range(sensor_nodes.GetN()):
        client_apps.Add(client.Install(sensor_nodes.Get(i)))
    
    client_apps.Start(ns.core.Seconds(1.0))
    client_apps.Stop(ns.core.Seconds(simulation_time - 1))
    
    # ==================== FLOW MONITOR ====================
    flowmon_helper = ns.flow_monitor.FlowMonitorHelper()
    monitor = flowmon_helper.InstallAll()
    
    # ==================== EXECUÇÃO ====================
    ns.core.Simulator.Stop(ns.core.Seconds(simulation_time))
    
    print("Iniciando simulação...")
    ns.core.Simulator.Run()
    
    # ==================== COLETA DE MÉTRICAS ====================
    monitor.CheckForLostPackets()
    classifier = flowmon_helper.GetClassifier()
    stats = monitor.GetFlowStats()
    
    total_throughput = 0.0
    total_delay = 0.0
    total_rx_packets = 0
    total_tx_packets = 0
    flow_count = 0
    
    print("\n" + "="*50)
    print("RESULTADOS DA SIMULAÇÃO")
    print("="*50 + "\n")
    
    for flow_id, flow_stats in stats:
        total_throughput += flow_stats.rxBytes * 8.0 / simulation_time / 1000.0  # kbps
        
        if flow_stats.rxPackets > 0:
            delay = flow_stats.delaySum.GetSeconds() / flow_stats.rxPackets * 1000.0  # ms
            total_delay += delay
        
        total_rx_packets += flow_stats.rxPackets
        total_tx_packets += flow_stats.txPackets
        flow_count += 1
    
    # Calcular métricas finais
    pdr = (total_rx_packets / total_tx_packets * 100.0) if total_tx_packets > 0 else 0.0
    avg_delay = (total_delay / flow_count) if flow_count > 0 else 0.0
    
    print(f"Pacotes transmitidos: {total_tx_packets}")
    print(f"Pacotes recebidos: {total_rx_packets}")
    print(f"PDR (Packet Delivery Ratio): {pdr:.2f}%")
    print(f"Vazão total (Throughput): {total_throughput:.2f} kbps")
    print(f"Atraso médio: {avg_delay:.2f} ms")
    print("\n" + "="*50 + "\n")
    
    # Salvar resultados em arquivo
    with open("results.txt", "a") as f:
        f.write(f"{tx_power},{pdr:.2f},{avg_delay:.2f},{total_throughput:.2f}\n")
    
    ns.core.Simulator.Destroy()
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
