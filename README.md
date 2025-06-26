# Ventilador Seguidor de Rostos - BitDogLab

##  Descrição
Sistema inteligente de embarcados que move um ventilador para seguir rostos detectados por uma IA de visão computacional. [Link](https://youtu.be/tgpLVKnkNZ8) do vídeo de demonstração. 

![image](https://github.com/user-attachments/assets/e49bbb70-7410-43fe-9ff9-5162cc33b6f5)

Composto por:

- **ESP32-CAM**: Módulo em arduino com camera e wifi que captura imagens e envia para o backend
- **Backend em Python**: Processa imagens com OpenCV e mediapipe para detecção facial e informa os IPs com um mock de servidor DNS
- **Placa BitDogLab**: Placa de raspberry pico com upython que controla servomotores e ventilador
- **Comunicação WiFi**: Todos os componentes se comunicam sem fio

##  Componentes do Hardware

### Lista de Materiais
| Componente | Quantidade | Observações |
|------------|-----------|-------------|
| Placa BitDogLab | 1 | Controlador principal |
| Módulo ESP32-CAM | 1 | Câmera |
| Servomotores | 2 | Para movimento pan-tilt |
| Ponte H L293 | 1 | Para Controlar o ventilador |
| Ventilador DC | 1 | 5V ou 12V conforme modelo |
| Fonte de alimentação 5V | 1 | Adequada para todos componentes |
|pan tilt| 1 | Suporte físico para o ventilador controlado pelos servos|


### Conexões Elétricas BitDogLab
1. GPIO4 PWM ventilador na ponte H
2. GPIO8 Servo horizontal
3. GPIO9 Servo vertical

### Conexões Elétricas L293 (pinos)
- 4,5,12 or 13: terra
- 16: VCC1 fonte de alimentação das portas lógicas internas (5V)
- 8: Vcc2 fonte de alimentação do ventilador
- 9: EN enable dos módulos 4 e 3 (se for nível lógico baixo deixa a saída em alta impedância)
- 15: A do módulo 4 (pulso PWM de controle em GPIO4)
- 14: saída conectada na alimentação do ventilador

### Conexões Elétricas Servo
Tower pro micro Servo 9g SG90 pinout
Configuração dos pinos
|Pin Number| 	Cor| 	Descrição|
|------------|-----------|-------------|
|1| 	Marrom| 	Terra (GND)|
|2| 	Vermelho |	Alimentação 5V (VCC)|
|3| 	Laranja| 	Sinal de controle (PWM)|

### Pan tilt
O modelo de pan tilt utilizado foi impresso com uma impressora 3D usando o seguinte [modelo](https://www.thingiverse.com/thing:6008663) com [intruções de montagem](https://www.instructables.com/Pan-and-Tilt-Camera-With-ESP32-CAM-L0Cost-Robot-Co/). Os arquivos da impressora 3D também estão na pasta pantilt3d.

![image](https://github.com/user-attachments/assets/6dc45f54-bd07-45e9-8b9b-6671ea6c9f25)_Figura instructables com câmera ao invés do ventilador._


### Placa
Arquivos da placa PCB no diretorio placa.

##  Instalação do Software

### Firmware para ESP32-CAM
1. Instalar Arduino IDE com suporte ao ESP32-CAM ([ver guia](https://randomnerdtutorials.com/program-upload-code-esp32-cam/
))
2. Instalar o firmware no módulo com programador ou conversor USB serial.

### Backend em Python
```bash
pip install opencv-python numpy mediapipe 
```
### Firmware bitdoglab
Seguir o guia de instalação no [site](https://bitdoglab.webcontent.website/).

##  Configuração

### Arquivo esp32-cam/arduino_esp32/arduino_esp32.ino (ESP32-CAM)
```arduino
// Configurações de rede
const char* ssid = "SUA_REDE_WIFI";
const char* password = "SENHA_WIFI";

```
### Arquivo bitdog/main.py (bitdoglab)
```python
# Setup Wi-Fi (line 129)
ssid = 'SUA_REDE_WIFI'
password = 'SENHA_WIFI'
```


##  Fluxo de Operação
1. ESP32-CAM captura imagem → Envia para backend via UDP
2. Backend detecta rostos → Calcula posição central
3. Envia coordenadas → BitDogLab via WiFi
4. BitDogLab move servos → Mantém ventilador apontado para rosto

##  Como Usar
1. Energizar todos os componentes (não usar a placa bitdoglab para energizar os servos e ponte H, usar fonte de 5V externa)
2. Iniciar servidor mock dns:
   ```bash
   python backend/mock_dns_server.py
   ```
3. Iniciar backend:
     ```bash
   python backend/backend.py
   ```
3. ESP32 conecta automaticamente e inicia streaming
4. Ligar ou resetar BitDogLab se ligada para registrar no script servidor mock dns 

##  Estrutura do Projeto (há alguns arquivos auxiliares da placa e pantilt)
```
├── esp32-cam/
│   └── arduino_esp32/     #
│        └── arduino_esp32.ino   # Camera com streaming wifi          
├── backend/                # Processamento de imagem
│   ├── backend.py              # Servidor com deteção facial opencv
│   └── mock_dns_server.py   # Permite que os componentes tenham IP dinâmicos
└── bitdog/
    └── main.py   # codigo em upython para controlar os servos e o ventilador com as coordenadas do backend
```

##  Observações Importantes
1. O projeto requer boa iluminação para detecção facial adequada
2. Velocidade do ventilador pode ser ajustada no código
3. Distância ideal de operação: alguns centimetros da camera
4. Consumo elétrico total deve ser calculado para seleção da fonte
