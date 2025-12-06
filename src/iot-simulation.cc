/*
 * Simulação IoT - Projeto de Telecomunicações
 * Tecnologia: IEEE 802.11n (Wi-Fi)
 * Análise de desempenho com variação de parâmetros
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/wifi-module.h"
#include "ns3/mobility-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("IoTSimulation");

// Variáveis globais para métricas
uint32_t g_totalPacketsSent = 0;
uint32_t g_totalPacketsReceived = 0;
double g_totalDelay = 0.0;
uint32_t g_totalBytes = 0;

// Callback para pacotes enviados
void PacketSentCallback(Ptr<const Packet> packet) {
    g_totalPacketsSent++;
}

// Callback para pacotes recebidos
void PacketReceivedCallback(Ptr<const Packet> packet, const Address &address) {
    g_totalPacketsReceived++;
    g_totalBytes += packet->GetSize();
}

int main(int argc, char *argv[]) {
    
    // ==================== PARÂMETROS CONFIGURÁVEIS ====================
    uint32_t nNodes = 30;              // Número de nós sensores
    double simulationTime = 30.0;      // Tempo de simulação (segundos)
    double areaSize = 100.0;           // Tamanho da área (metros)
    std::string dataRate = "1Mbps";    // Taxa de dados
    uint32_t packetSize = 64;          // Tamanho do pacote (bytes)
    double interval = 0.1;             // Intervalo entre pacotes (segundos)
    double txPower = 16.0;             // Potência de transmissão (dBm)
    std::string propagationModel = "LogDistance"; // Modelo de propagação
    
    // Parsing de argumentos da linha de comando
    CommandLine cmd;
    cmd.AddValue("nNodes", "Número de nós sensores", nNodes);
    cmd.AddValue("simulationTime", "Tempo de simulação", simulationTime);
    cmd.AddValue("dataRate", "Taxa de dados", dataRate);
    cmd.AddValue("txPower", "Potência de transmissão (dBm)", txPower);
    cmd.AddValue("interval", "Intervalo entre pacotes", interval);
    cmd.AddValue("propagationModel", "Modelo de propagação", propagationModel);
    cmd.Parse(argc, argv);
    
    // ==================== LOG ====================
    Time::SetResolution(Time::NS);
    LogComponentEnable("UdpEchoClientApplication", LOG_LEVEL_INFO);
    LogComponentEnable("UdpEchoServerApplication", LOG_LEVEL_INFO);
    
    std::cout << "\n========================================" << std::endl;
    std::cout << "Simulação IoT - Rede Sem Fio" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "Nós sensores: " << nNodes << std::endl;
    std::cout << "Potência TX: " << txPower << " dBm" << std::endl;
    std::cout << "Taxa de dados: " << dataRate << std::endl;
    std::cout << "Tempo de simulação: " << simulationTime << " s" << std::endl;
    std::cout << "========================================\n" << std::endl;
    
    // ==================== CRIAÇÃO DOS NÓS ====================
    NodeContainer sensorNodes;
    sensorNodes.Create(nNodes);
    
    NodeContainer sinkNode;
    sinkNode.Create(1);
    
    NodeContainer allNodes;
    allNodes.Add(sensorNodes);
    allNodes.Add(sinkNode);
    
    // ==================== CONFIGURAÇÃO WI-FI ====================
    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211n);
    
    YansWifiChannelHelper wifiChannel;
    wifiChannel.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel");
    
    if (propagationModel == "LogDistance") {
        wifiChannel.AddPropagationLoss("ns3::LogDistancePropagationLossModel",
                                       "Exponent", DoubleValue(3.0),
                                       "ReferenceDistance", DoubleValue(1.0));
    } else if (propagationModel == "Nakagami") {
        wifiChannel.AddPropagationLoss("ns3::NakagamiPropagationLossModel");
    }
    
    YansWifiPhyHelper wifiPhy;
    wifiPhy.SetChannel(wifiChannel.Create());
    wifiPhy.Set("TxPowerStart", DoubleValue(txPower));
    wifiPhy.Set("TxPowerEnd", DoubleValue(txPower));
    
    WifiMacHelper wifiMac;
    Ssid ssid = Ssid("iot-network");
    
    // Configurar AP (sink)
    wifiMac.SetType("ns3::ApWifiMac",
                    "Ssid", SsidValue(ssid));
    NetDeviceContainer apDevice = wifi.Install(wifiPhy, wifiMac, sinkNode);
    
    // Configurar STAs (sensores)
    wifiMac.SetType("ns3::StaWifiMac",
                    "Ssid", SsidValue(ssid),
                    "ActiveProbing", BooleanValue(false));
    NetDeviceContainer staDevices = wifi.Install(wifiPhy, wifiMac, sensorNodes);
    
    // ==================== MOBILIDADE ====================
    MobilityHelper mobility;
    
    // Sink no centro
    Ptr<ListPositionAllocator> sinkPosition = CreateObject<ListPositionAllocator>();
    sinkPosition->Add(Vector(areaSize/2, areaSize/2, 1.5));
    mobility.SetPositionAllocator(sinkPosition);
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(sinkNode);
    
    // Sensores distribuídos aleatoriamente
    mobility.SetPositionAllocator("ns3::RandomDiscPositionAllocator",
                                  "X", DoubleValue(areaSize/2),
                                  "Y", DoubleValue(areaSize/2),
                                  "Rho", StringValue("ns3::UniformRandomVariable[Min=0|Max=" + 
                                                     std::to_string(areaSize/2) + "]"));
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(sensorNodes);
    
    // ==================== PILHA DE PROTOCOLOS ====================
    InternetStackHelper stack;
    stack.Install(allNodes);
    
    Ipv4AddressHelper address;
    address.SetBase("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer interfaces = address.Assign(staDevices);
    Ipv4InterfaceContainer apInterface = address.Assign(apDevice);
    
    // ==================== APLICAÇÕES ====================
    uint16_t port = 9;
    
    // Servidor UDP no sink
    UdpServerHelper server(port);
    ApplicationContainer serverApp = server.Install(sinkNode.Get(0));
    serverApp.Start(Seconds(0.0));
    serverApp.Stop(Seconds(simulationTime));
    
    // Clientes UDP nos sensores
    UdpClientHelper client(apInterface.GetAddress(0), port);
    client.SetAttribute("MaxPackets", UintegerValue(4294967295u));
    client.SetAttribute("Interval", TimeValue(Seconds(interval)));
    client.SetAttribute("PacketSize", UintegerValue(packetSize));
    
    ApplicationContainer clientApps;
    for (uint32_t i = 0; i < sensorNodes.GetN(); i++) {
        clientApps.Add(client.Install(sensorNodes.Get(i)));
    }
    clientApps.Start(Seconds(1.0));
    clientApps.Stop(Seconds(simulationTime - 1));
    
    // ==================== FLOW MONITOR ====================
    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll();
    
    // ==================== EXECUÇÃO ====================
    Simulator::Stop(Seconds(simulationTime));
    
    std::cout << "Iniciando simulação..." << std::endl;
    Simulator::Run();
    
    // ==================== COLETA DE MÉTRICAS ====================
    monitor->CheckForLostPackets();
    Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier>(flowmon.GetClassifier());
    std::map<FlowId, FlowMonitor::FlowStats> stats = monitor->GetFlowStats();
    
    double totalThroughput = 0.0;
    double totalDelay = 0.0;
    uint32_t totalRxPackets = 0;
    uint32_t totalTxPackets = 0;
    uint32_t flowCount = 0;
    
    std::cout << "\n========================================" << std::endl;
    std::cout << "RESULTADOS DA SIMULAÇÃO" << std::endl;
    std::cout << "========================================\n" << std::endl;
    
    for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator i = stats.begin(); 
         i != stats.end(); ++i) {
        
        Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow(i->first);
        
        double throughput = i->second.rxBytes * 8.0 / simulationTime / 1000.0; // kbps
        double delay = 0.0;
        if (i->second.rxPackets > 0) {
            delay = i->second.delaySum.GetSeconds() / i->second.rxPackets * 1000.0; // ms
        }
        
        totalThroughput += throughput;
        totalDelay += delay;
        totalRxPackets += i->second.rxPackets;
        totalTxPackets += i->second.txPackets;
        flowCount++;
    }
    
    double pdr = (totalTxPackets > 0) ? 
                 (static_cast<double>(totalRxPackets) / totalTxPackets * 100.0) : 0.0;
    double avgDelay = (flowCount > 0) ? (totalDelay / flowCount) : 0.0;
    
    std::cout << "Pacotes transmitidos: " << totalTxPackets << std::endl;
    std::cout << "Pacotes recebidos: " << totalRxPackets << std::endl;
    std::cout << "PDR (Packet Delivery Ratio): " << pdr << "%" << std::endl;
    std::cout << "Vazão total (Throughput): " << totalThroughput << " kbps" << std::endl;
    std::cout << "Atraso médio: " << avgDelay << " ms" << std::endl;
    std::cout << "\n========================================\n" << std::endl;
    
    // Salvar resultados em arquivo
    std::ofstream outFile;
    outFile.open("./results/results.txt", std::ios::app);
    outFile << txPower << "," << pdr << "," << avgDelay << "," << totalThroughput << std::endl;
    outFile.close();
    
    Simulator::Destroy();
    
    return 0;
}
