# Kuwahara Filter STM32 - v2-kuwahara

## Descrição
Este projeto implementa o filtro Kuwahara para imagens 90x90 em um microcontrolador STM32 (F030R8) usando **modo streaming** com buffer otimizado. A imagem é enviada via UART em duas fases, processada pelo STM32, e o resultado filtrado é retornado no formato PGM (P2, texto).

## Estrutura
- **Core/Inc/**: Headers do projeto (configurações, tipos, etc)
- **Core/Src/**: Código fonte principal (main.c com filtro Kuwahara)
- **Core/pgms/**: Exemplos de arquivos PGM gerados
- **python_script/**: Script Python para enviar imagem e receber resultado filtrado

## Configuração do STM32
- **Placa:** STM32F030R8 (ARM Cortex-M0, 48 MHz, 8KB SRAM)
- **UART:** USART2
- **Baudrate:** 38400 bps
- **Tamanho da imagem:** 90×90 pixels
- **Formato:** PGM ASCII (P2)
- **Modo:** STREAMING_MODE (processamento em 2 fases com buffer de 46 linhas)
- **Memória:** Buffer de 4,140 bytes (46×90 pixels = 50.54% da SRAM)

## Algoritmo - Processamento em Duas Fases

O STM32 processa a imagem em **duas fases** para otimizar o uso de memória:

### FASE 1: Linhas 0-44
1. Python envia linhas 0-45 (46 linhas)
2. STM32 armazena no buffer[0-45]
3. STM32 processa linhas 0-44 (45 linhas)
4. STM32 envia 45 linhas filtradas

### FASE 2: Linhas 45-89
1. Python envia linhas 44-89 (46 linhas, linha 44 reenviada para contexto)
2. STM32 sobrescreve buffer[0-45]
3. STM32 processa linhas 45-89 (45 linhas)
4. STM32 envia 45 linhas filtradas

**Resultado:** 90 linhas filtradas (45 + 45) em ~35 segundos

## Como Usar - Passo a Passo

### 1. Preparar o Ambiente Python

```bash
# Navegue até o diretório do script
cd v2-kuwahara/python_script

# Crie um ambiente virtual (opcional, mas recomendado):
# Windows:
python -m venv venv
venv\Scripts\activate

# Linux/macOS:
python3 -m venv venv
source venv/bin/activate

# Instale as dependências:
pip install -r requirements.txt
# ou
pip install pyserial
```

### 2. Gravar o Firmware no STM32 (UMA VEZ)

```bash
# Abra o STM32CubeIDE
# 1. Abra o projeto em v2-kuwahara/
# 2. Compile: Project → Build (Ctrl+B)
#    ✓ Verifique: "Build Finished. 0 errors, 0 warnings"
# 3. Flash: Run → Debug (F11)
#    ✓ Verifique: "Download verified successfully"
# 4. Desconecte o debugger e reinicie a placa
```

### 3. Executar o Script Python

```bash
# Conecte o STM32 via USB
# Execute o script com o caminho da imagem:

python3 writer_reader.py ../../v1-kuwahara/imgs_original/mona_lisa.ascii.pgm

# Ou com pepper:
python3 writer_reader.py ../../v1-kuwahara/imgs_original/pepper.ascii.pgm
```

### 4. Processo de Execução (automático)

```
1. Script lista portas seriais disponíveis
2. Selecione a porta do STM32
3. Script envia FASE 1 (linhas 0-45)
4. STM32 processa e envia resultado FASE 1
5. Script envia FASE 2 (linhas 44-89)
6. STM32 processa e envia resultado FASE 2
7. Script salva resultado: filtered_YYYYMMDD_HHMMSS.pgm

Tempo total: ~35 segundos
```

### 5. Resultado

O arquivo filtrado será salvo no mesmo diretório da imagem original:
```
v1-kuwahara/imgs_original/filtered_20251107_143022.pgm
```

## Formato do Protocolo UART

### Python → STM32 (Entrada)
```
106 99 97 88 93 101 98 96 90 88 91 86 86 83 82 85 88 86 86 85 ... 70\n
(90 pixels separados por espaço, terminado com \n)
```

### STM32 → Python (Saída)
```
P2
90 90
255
104 98 95 87 91 99 97 95 89 87 ... (linha 0)
100 96 93 85 89 97 95 93 87 85 ... (linha 1)
...
(90 linhas filtradas)
```

## Modos de Operação

O código suporta dois modos (configurável em `main.c`):

### Modo STREAMING (Padrão - ATIVO)
```c
#define STREAMING_MODE     // Habilita recepção via UART (modo streaming)
```
- Recebe imagem via UART do script Python
- Processa em 2 fases com buffer de 46 linhas
- Retorna resultado filtrado via UART

### Modo FLASH (Desativado)
```c
// #define STREAMING_MODE     // Comente para modo Flash
```
- Usa imagem pré-carregada na Flash
- Processa em 1 passada (90 linhas)
- Envia resultado a cada 5 segundos
- Requer mais memória (8,100 bytes vs 4,140 bytes)

## Especificações Técnicas

- **Algoritmo:** Filtro Kuwahara 3×3
- **Quadrantes:** 4 sobrepostos (ordem: {1,1}, {0,1}, {1,0}, {0,0})
- **Estatística:** Variância populacional
- **Bordas:** BORDER_REFLECT_101 (reflexão espelhada)
- **Saída:** Truncamento `(int)(best_mean)`
- **Buffer SRAM:** 46 linhas × 90 pixels = 4,140 bytes
- **Uso total SRAM:** ~4,800 bytes (58.6% de 8KB)

## Troubleshooting

### Problema: Timeout na captura
**Solução:** Aumentar timeout em `writer_reader.py` linha 158:
```python
timeout_time = time.time() + 20  # Aumentar se necessário
```

### Problema: Porta serial não encontrada
**Solução:** 
- Verificar cabo USB (dados, não só alimentação)
- Verificar drivers STLink/Virtual COM Port
- Listar portas: `python3 -m serial.tools.list_ports`

### Problema: Valores incorretos
**Solução:**
- Verificar baudrate (38400 em ambos)
- Verificar se STM32 está em modo STREAMING_MODE
- Reiniciar placa após flash

## Comparação v1 vs v2

| Aspecto | v1 (Flash) | v2 (Streaming) |
|---------|------------|----------------|
| Memória | 8,100 bytes (100%) | 4,140 bytes (51%) |
| Processamento | 1 passada (0-89) | 2 fases (0-44, 45-89) |
| Entrada | Flash (pré-carregada) | UART (dinâmica) |
| Saída | UART (loop 5s) | UART (sob demanda) |
| Algoritmo | Kuwahara 3×3 | Kuwahara 3×3 (idêntico) |
| Resultado | Mesmo pixel-a-pixel | Mesmo pixel-a-pixel |

## Arquivos Principais

- **`main.c`**: Firmware STM32 com filtro Kuwahara
- **`writer_reader.py`**: Script Python para envio/recepção
- **`requirements.txt`**: Dependências Python (pyserial)
- **`README.md`**: Este arquivo

## Requisitos

- **Hardware:** STM32F030R8 (ou compatível)
- **Software:**
  - STM32CubeIDE (para compilar/flash)
  - Python 3.x
  - pyserial
- **Imagens:** Arquivos PGM P2 ASCII 90×90

## Autor
Hiel Saraiva
