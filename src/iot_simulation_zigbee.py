import sys
from ns import ns

def main(argv):
    """
    Simulação com protocolo 802.15.4
    """
    
    # ==================== PARÂMETROS ====================
    n_nodes = 30
    simulation_time = 30.0
    area_size = 50.0  # Área menor para 802.15.4
    packet_size = 50
    interval = 1.0  # Maior intervalo para baixo consumo
    
    # Parsing
    cmd = ns.CommandLine()
    cmd.AddValue("nNodes", "Número de nós", n_nodes)
    cmd.AddValue("simulationTime", "Tempo de simulação", simulation_time)
    cmd.Parse(argv)
    
    n_nodes = cmd.GetValue("nNodes", n_nodes)
    simulation_time = cmd.GetValue("simulationTime", simulation_time)
    
    print("\n" + "="*50)
    print("Simulação IoT - IEEE 802.15.4 (ZigBee)")
    print("="*50)
    print(f"Nós sensores: {n_nodes}")
    print(f"Tempo de simulação: {simulation_time} s")
    print("="*50 + "\n")
    
    # ==================== CRIAÇÃO DOS NÓS ====================
    sensor_nodes = ns.network.NodeContainer()
    sensor_nodes.Create(n_nodes)
    
    coordinator = ns.network.NodeContainer()
    coordinator.Create(1)
    
    all_nodes = ns.network.NodeContainer()
    all_nodes.Add(sensor_nodes)
    all_nodes.Add(coordinator)
    
    # ==================== CONFIGURAÇÃO LR-WPAN ====================
    lr_wpan = ns.lr_wpan.LrWpanHelper()
    
    # Criar canal
    channel = ns.lr_wpan.SingleModelSpectrumChannel()
    loss_model = ns.spectrum.LogDistancePropagationLossModel()
    channel.AddPropagationLossModel(loss_model)
    
    delay_model = ns.propagation.ConstantSpeedPropagationDelayModel()
    channel.SetPropagationDelayModel(delay_model)
    
    # Instalar dispositivos
    devices = lr_wpan.Install(all_nodes)
    
    # Configurar canal nos dispositivos
    for i in range(all_nodes.GetN()):
        device = devices.Get(i)
        device.SetChannel(channel)
    
    # Associar dispositivos ao PAN
    lr_wpan.AssociateToPan(devices, 0)
    
    # ==================== MOBILIDADE ====================
    mobility = ns.mobility.MobilityHelper()
    
    # Coordenador no centro
    coord_pos = ns.mobility.ListPositionAllocator()
    coord_pos.Add(ns.core.Vector(area_size/2, area_size/2, 1.0))
    mobility.SetPositionAllocator(coord_pos)
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
    mobility.Install(coordinator)
    
    # Sensores distribuídos
    sensor_pos = ns.mobility.RandomDiscPositionAllocator()
    sensor_pos.SetAttribute("X", ns.core.DoubleValue(area_size/2))
    sensor_pos.SetAttribute("Y", ns.core.DoubleValue(area_size/2))
    sensor_pos.SetAttribute("Rho", ns.core.StringValue(
        f"ns3::UniformRandomVariable[Min=0|Max={area_size/2}]"))
    
    mobility.SetPositionAllocator(sensor_pos)
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
    mobility.Install(sensor_nodes)
    
    # ==================== PILHA DE PROTOCOLOS ====================
    internet = ns.internet.InternetStackHelper()
    internet.Install(all_nodes)
    
    sixlowpan = ns.sixlowpan.SixLowPanHelper()
    sixlowpan_devices = sixlowpan.Install(devices)
    
    address = ns.internet.Ipv4AddressHelper()
    address.SetBase(ns.network.Ipv4Address("10.1.1.0"),
                    ns.network.Ipv4Mask("255.255.255.0"))
    interfaces = address.Assign(sixlowpan_devices)
    
    # ==================== APLICAÇÕES ====================
    port = 9
    
    # Servidor
    server = ns.applications.UdpServerHelper(port)
    server_app = server.Install(coordinator.Get(0))
    server_app.Start(ns.core.Seconds(0.0))
    server_app.Stop(ns.core.Seconds(simulation_time))
    
    # Clientes
    client = ns.applications.UdpClientHelper(
        interfaces.GetAddress(n_nodes), port)
    client.SetAttribute("MaxPackets", ns.core.UintegerValue(4294967295))
    client.SetAttribute("Interval", ns.core.TimeValue(ns.core.Seconds(interval)))
    client.SetAttribute("PacketSize", ns.core.UintegerValue(packet_size))
    
    client_apps = ns.network.ApplicationContainer()
    for i in range(sensor_nodes.GetN()):
        client_apps.Add(client.Install(sensor_nodes.Get(i)))
    
    client_apps.Start(ns.core.Seconds(1.0))
    client_apps.Stop(ns.core.Seconds(simulation_time - 1))
    
    # ==================== FLOW MONITOR ====================
    flowmon = ns.flow_monitor.FlowMonitorHelper()
    monitor = flowmon.InstallAll()
    
    # ==================== EXECUÇÃO ====================
    ns.core.Simulator.Stop(ns.core.Seconds(simulation_time))
    
    print("Iniciando simulação 802.15.4...")
    ns.core.Simulator.Run()
    
    # ==================== MÉTRICAS ====================
    monitor.CheckForLostPackets()
    stats = monitor.GetFlowStats()
    
    total_throughput = 0.0
    total_delay = 0.0
    total_rx = 0
    total_tx = 0
    flow_count = 0
    
    print("\n" + "="*50)
    print("RESULTADOS - IEEE 802.15.4")
    print("="*50 + "\n")
    
    for flow_id, flow_stats in stats:
        total_throughput += flow_stats.rxBytes * 8.0 / simulation_time / 1000.0
        
        if flow_stats.rxPackets > 0:
            delay = flow_stats.delaySum.GetSeconds() / flow_stats.rxPackets * 1000.0
            total_delay += delay
        
        total_rx += flow_stats.rxPackets
        total_tx += flow_stats.txPackets
        flow_count += 1
    
    pdr = (total_rx / total_tx * 100.0) if total_tx > 0 else 0.0
    avg_delay = (total_delay / flow_count) if flow_count > 0 else 0.0
    
    print(f"Pacotes transmitidos: {total_tx}")
    print(f"Pacotes recebidos: {total_rx}")
    print(f"PDR: {pdr:.2f}%")
    print(f"Throughput: {total_throughput:.2f} kbps")
    print(f"Atraso médio: {avg_delay:.2f} ms")
    print("\n" + "="*50 + "\n")
    
    # Comparação com Wi-Fi
    print("COMPARAÇÃO 802.15.4 vs 802.11n:")
    print("  ✓ Menor consumo de energia")
    print("  ✓ Melhor para sensores com bateria")
    print("  ✗ Menor taxa de dados")
    print("  ✗ Menor alcance que Wi-Fi\n")
    
    with open("results_zigbee.txt", "a") as f:
        f.write(f"{n_nodes},{pdr:.2f},{avg_delay:.2f},{total_throughput:.2f}\n")
    
    ns.core.Simulator.Destroy()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
