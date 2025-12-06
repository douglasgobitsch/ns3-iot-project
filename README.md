# Simulação IoT - Análise de Desempenho de Redes Sem Fio

Projeto de simulação e análise de redes IoT usando Network Simulator 3 (NS-3) com Python.

## 📋 Descrição

Este projeto implementa e avalia o desempenho de redes de comunicação sem fio para aplicações de Internet das Coisas (IoT) em ambiente urbano, comparando diferentes configurações e tecnologias.

### Tecnologias Implementadas
- **IEEE 802.11n (Wi-Fi)** - Principal implementação
- **IEEE 802.15.4 (ZigBee)** - Implementação alternativa

## 🎯 Objetivos

- Avaliar impacto de parâmetros físicos na qualidade da comunicação
- Comparar desempenho entre diferentes configurações
- Analisar métricas fundamentais: PDR, Delay, Throughput

## 🚀 Instalação

### Requisitos
- Linux (Ubuntu 20.04+ recomendado)
- Python 3.8+
- NS-3.41 ou superior
- Git

### Passo a Passo

```bash
# 1. Instalar dependências
sudo apt-get update
sudo apt-get install -y g++ python3 python3-dev pkg-config sqlite3 \
    cmake ninja-build git ccache libgtk-3-dev libfl-dev \
    libxml2-dev libboost-all-dev

# 2. Clonar NS-3
cd ~
git clone https://gitlab.com/nsnam/ns-3-dev.git ns-3-dev
cd ns-3-dev

# 3. Configurar com Python
./ns3 configure --enable-examples --enable-tests --enable-python-bindings

# 4. Compilar (pode demorar ~15 minutos)
./ns3 build

# 5. Clonar este projeto
git clone https://github.com/seu-usuario/ns3-iot-project.git
cd ns3-iot-project

# 6. Instalar dependências Python
pip3 install matplotlib pandas numpy
```

## 📁 Estrutura do Projeto

```
ns3-iot-project/
├── README.md
├── src/
│   ├── iot-simulation.cc          # Implementação C++ (Wi-Fi)
│   ├── iot_simulation.py          # Implementação Python (Wi-Fi)
│   └── iot_simulation_zigbee.py   # Implementação Python (ZigBee)
├── scripts/
│   ├── run_experiments.py         # Execução automatizada
│   ├── run_experiments.sh         # Script bash para C++
│   └── plot_results.py            # Análise e gráficos
├── results/
│   ├── results.txt
│   ├── results_zigbee.txt
│   └── graphs/
├── docs/
│   └── relatorio.pdf
└── video/
    └── demonstracao.mp4
```

## 💻 Uso

### Execução com Python

```bash
# Simulação Wi-Fi padrão
python3 iot_simulation.py

# Com parâmetros personalizados
python3 iot_simulation.py --nNodes=40 --txPower=20 --simulationTime=60

# Simulação ZigBee
python3 iot_simulation_zigbee.py --nNodes=25
```

### Execução com C++

```bash
# Copiar arquivo para o NS-3
cp src/iot-simulation.cc ~/ns3-iot-project/ns-3-dev/scratch/

# Compilar
cd ~/ns3-iot-project/ns-3-dev
./ns3 build

# Executar simulação básica
./ns3 run scratch/iot-simulation

# Com parâmetros personalizados
./ns3 run "scratch/iot-simulation --nNodes=40 --txPower=20 --simulationTime=60"
```

### Experimentos Automatizados

#### Com Python
```bash
# Menu interativo
python3 run_experiments.py

# Opções:
# 1 - Variar Potência de Transmissão
# 2 - Variar Taxa de Dados
# 3 - Variar Número de Nós
# 4 - Executar todos
```

#### Com C++
```bash
# Script bash para experimentos
chmod +x scripts/run_experiments.sh
./scripts/run_experiments.sh

# Variar potência de transmissão automaticamente
for power in 10 13 16 19 22; do
    ./ns3 run "scratch/iot-simulation --txPower=$power --nNodes=30"
done
```

### Análise de Resultados

```bash
# Menu de análise
python3 plot_results.py

# Opções:
# 1 - Gráficos de análise
# 2 - Tabela resumo
# 3 - Comparação entre experimentos
# 4 - Relatório completo
```

## 📊 Métricas Avaliadas

1. **PDR (Packet Delivery Ratio)**: Taxa de entrega de pacotes
   - Indica confiabilidade da rede
   - Valores acima de 90% são considerados bons

2. **Atraso Ponta a Ponta**: Tempo médio de transmissão
   - Crítico para aplicações em tempo real
   - Ideal: < 50ms para IoT

3. **Throughput**: Vazão total da rede
   - Mede capacidade de transferência
   - Varia com tecnologia e configuração

## 🔬 Cenários de Teste

### Configuração Base
- 20-40 dispositivos IoT
- Área: 100m x 100m
- Duração: 30 segundos
- Pacotes UDP de 64 bytes

### Parâmetros Variados

**Potência de Transmissão:**
- Valores: 10, 13, 16, 19, 22 dBm
- Impacto: alcance e consumo

**Taxa de Dados:**
- Valores: 500Kbps, 1Mbps, 2Mbps, 5Mbps, 10Mbps
- Impacto: throughput e latência

**Número de Nós:**
- Valores: 10, 20, 30, 40, 50 nós
- Impacto: congestionamento e PDR

## 📈 Resultados Esperados

### Wi-Fi (802.11n)
- **Vantagens:**
  - Alta taxa de dados (até 600 Mbps)
  - Maior alcance (~100m)
  - Infraestrutura estabelecida

- **Desvantagens:**
  - Maior consumo energético
  - Interferência em 2.4 GHz
  - Overhead de protocolo

### ZigBee (802.15.4)
- **Vantagens:**
  - Baixo consumo (~10mW)
  - Ideal para sensores com bateria
  - Topologia mesh nativa

- **Desvantagens:**
  - Taxa de dados limitada (250 kbps)
  - Menor alcance (~10-100m)
  - Menor throughput

## 🛠️ Parâmetros Configuráveis

```python
# Principais parâmetros no código
n_nodes = 30              # Número de sensores
simulation_time = 30.0    # Duração (segundos)
area_size = 100.0         # Tamanho da área (metros)
data_rate = "1Mbps"       # Taxa de transmissão
packet_size = 64          # Tamanho do pacote (bytes)
interval = 0.1            # Intervalo entre pacotes (s)
tx_power = 16.0           # Potência TX (dBm)
```

## 📚 Justificativa da Tecnologia

### Por que Wi-Fi (802.11n)?

1. **Alta capacidade**: Suporta múltiplos sensores simultaneamente
2. **Infraestrutura**: Disponível na maioria dos ambientes urbanos
3. **Flexibilidade**: Permite ajuste fino de parâmetros
4. **Maturidade**: Protocolo bem estabelecido e testado

### Casos de Uso

- **Wi-Fi**: Câmeras, sensores de alta frequência, gateways
- **ZigBee**: Sensores de temperatura, umidade, presença (bateria)

## 🎥 Demonstração

Vídeo disponível em: `video/demonstracao.mp4`

Conteúdo do vídeo (5 minutos):
1. Apresentação do código (2 min)
2. Execução de experimento (1 min)
3. Análise de resultados (1.5 min)
4. Conclusões (0.5 min)

## 📄 Relatório

Documento completo em: `docs/relatorio.pdf`

Seções:
1. Introdução e objetivos
2. Metodologia
3. Implementação
4. Resultados e análise
5. Discussão
6. Conclusões
7. Referências

## 🤝 Contribuições

Melhorias implementadas:
- Interface interativa para experimentos
- Análise automatizada com gráficos
- Comparação entre tecnologias
- Scripts de automação

## 📞 Contato

- GitHub: [seu-usuario]
- Email: seu-email@exemplo.com

## 📖 Referências

1. NS-3 Documentation: https://www.nsnam.org/documentation/
2. NS-3 Tutorial: https://www.nsnam.org/docs/tutorial/html/
3. IEEE 802.11n Standard: IEEE Std 802.11n-2009
4. IEEE 802.15.4 Standard: IEEE Std 802.15.4-2020
5. Network Performance Metrics for IoT Applications
6. NS-3 Python Bindings: https://www.nsnam.org/docs/manual/html/python.html

## 🔗 Links Importantes

- **Código C++ Original**: `src/iot-simulation.cc`
- **Código Python**: `src/iot_simulation.py`
- **GitHub do Projeto**: [seu-usuario/ns3-iot-project]
- **Documentação NS-3**: https://www.nsnam.org/
- **NS-3 API Documentation**: https://www.nsnam.org/doxygen/

## 📝 Licença

Este projeto é desenvolvido para fins acadêmicos.

---

**Desenvolvido como projeto de Telecomunicações**