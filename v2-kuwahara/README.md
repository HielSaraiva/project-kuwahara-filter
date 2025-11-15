# Versão 2 - Filtro Kuwahara STM32

## Sumário
- [Descrição](#descrição)
- [Placa STM32](#placa-stm32)
- [Configuração do STM32](#configuração-do-stm32)
- [Estrutura de Arquivos](#estrutura-de-arquivos)
- [Algoritmo - Processamento em Duas Fases](#algoritmo---processamento-em-duas-fases)
- [Handshake e sincronização](#handshake-e-sincronização)
- [Como Usar - Passo a Passo](#como-usar---passo-a-passo)
- [Formato do Protocolo UART](#formato-do-protocolo-uart)
- [Modos de Operação](#modos-de-operação)
- [Especificações Técnicas](#especificações-técnicas)
- [Problemas](#problemas)
- [Comparação v1 vs v2](#comparação-v1-vs-v2)
- [Arquivos Principais](#arquivos-principais)
- [Requisitos](#requisitos)
- [Próximos Passos](#próximos-passos)

## Descrição
Este projeto implementa o filtro Kuwahara para imagens 90x90 em um microcontrolador STM32 (F030R8) usando **modo streaming** com buffer otimizado. A imagem é enviada via UART em duas fases, processada pelo STM32, e o resultado filtrado é retornado no formato PGM (P2, texto).

## Placa STM32
Imagem ilustrativa da família STM32 (link oficial ST):

![Placa STM32F0](https://www.st.com/bin/ecommerce/api/image.PF259997.en.feature-description-include-personalized-no-cpn-large.jpg)

## Configuração do STM32
- **Placa:** STM32F030R8 (ARM Cortex-M0, 48 MHz, 8KB SRAM)
- **UART:** USART2
- **Baudrate:** 115200 bps
- **Tamanho da imagem:** 90×90 pixels
- **Formato:** PGM ASCII (P2)
- **Modo:** STREAMING_MODE (processamento em 2 fases com buffer de 46 linhas)
- **Memória:** Buffer de 4,140 bytes (46×90 pixels = 50.54% da SRAM)

## Estrutura de Arquivos

```
v2-kuwahara/
│
├── README.md                      
├── stm32.ioc                      # Configuração do CubeMX
├── STM32F030R8TX_FLASH.ld         # Linker script (memória Flash/SRAM)
├── .project / .cproject           # Metadados do STM32CubeIDE
│
├── Core/
│   ├── Inc/
│   │   ├── main.h                 # Declarações principais
│   │   ├── stm32f0xx_hal_conf.h   
│   │   ├── stm32f0xx_it.h         
│   │   ├── image_mona_lisa.h      # Imagem (modo FLASH)
│   │   └── image_pepper.h         # Imagem (modo FLASH)
│   ├── Src/
│   │   ├── main.c                 # Lógica principal
│   │   ├── stm32f0xx_it.c         
│   │   ├── stm32f0xx_hal_msp.c    
│   │   ├── system_stm32f0xx.c     
│   │   ├── syscalls.c / sysmem.c  
│   │   └── startup_stm32f030r8tx.s
│   ├── pgms/                      # Saídas PGM geradas (modo streaming)
│
├── Drivers/
│   
└── python_script/
    ├── writer_reader.py           # Envio de imagem + recepção filtrada
    ├── compare_filtered.py        # Comparação com versão v1
    ├── requirements.txt           # Dependências Python
    └── heatmaps/                  # Imagens de diferenças


```

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

### Handshake e sincronização
- Após concluir o envio das 45 linhas filtradas da FASE 1, o STM32 envia o token `#READY2#` indicando que está pronto para receber a FASE 2.
- O script Python, ao detectar `#READY2#`, limpa o buffer de entrada, responde com `#GO2#` e então transmite as linhas 44–89.
- Proteção (gate) na FASE 2: o firmware só processa e envia a segunda metade se todas as 46 linhas forem recebidas com sucesso; caso contrário, emite uma mensagem `SKIP` e reinicia o ciclo.

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
# Isso instalará: pyserial, numpy, matplotlib
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
5. STM32 envia token de pronto: #READY2#
6. Script responde com #GO2# e envia FASE 2 (linhas 44-89)
7. STM32 processa e envia resultado FASE 2
8. Script salva resultado: filtered_YYYYMMDD_HHMMSS.pgm

Tempo total: ~35 segundos (pode reduzir com 115200 bps, dependendo do host)
```

### 5. Resultado

O arquivo filtrado será salvo na pasta `Core/pgms/`:
```
v2-kuwahara/Core/pgms/filtered_20251108_143022.pgm
```

### 6. Comparar Resultados (Opcional)

Para comparar pixel a pixel a imagem filtrada com outra referência:

```bash
# Comparar saída do v2 com v1
python compare_filtered.py ../Core/pgms/filtered_20251108_143022.pgm \
                            ../../v1-kuwahara/imgs_filtered/mona_lisa.ascii.pgm

# O script irá:
# 1. Calcular métricas de diferença (MAE, RMSE, correlação)
# 2. Gerar heatmap visual mostrando diferenças pixel a pixel
# 3. Salvar em: python_script/heatmaps/heatmap_*.png
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

### Handshake
- Token de pronto do STM32: `#READY2#` (após enviar a primeira metade do resultado)
- Comando do host para iniciar FASE 2: `#GO2#`
- Mensagens de erro/controle possíveis:
  - `ERROR: Failed to receive line <n>`: houve falha na recepção de uma linha.
  - `ERROR: GO2 timeout`: o host não enviou `#GO2#` no tempo esperado.
  - `SKIP: Phase 2 processing skipped due to incomplete reception.`: FASE 2 não foi processada por dados incompletos.

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

## Problemas

### Problema: Timeout na captura
**Solução:** Aumentar timeout em `writer_reader.py` linha 158:
```python
timeout_time = time.time() + 20  # Aumentar se necessário
```

### Problema: FASE 2 não inicia
**Sintoma:** Mensagem `ERROR: GO2 timeout` no log do STM32.
**Solução:** Verifique o cabo/porta serial e se o script está recebendo `#READY2#` e enviando `#GO2#`. Tente reiniciar a placa e rodar o script novamente.

### Problema: Duplicação de linhas ou imagem "metade/metade"
**Causa raiz (antiga):** colisão de dados entre as fases e processamento com buffer parcial.
**Solução (atual):** o handshake READY2/GO2 e o gate na FASE 2 eliminam esse problema. Se aparecer `SKIP`, repita a execução para garantir recepção completa.

### Problema: Porta serial não encontrada
**Solução:** 
- Verificar cabo USB (dados, não só alimentação)
- Verificar drivers STLink/Virtual COM Port
- Listar portas: `python3 -m serial.tools.list_ports`

### Problema: Valores incorretos
**Solução:**
- Verificar baudrate (115200 em ambos)
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
- **`writer_reader.py`**: Script Python para envio/recepção de imagens
- **`compare_filtered.py`**: Script Python para comparação pixel a pixel com heatmap
- **`requirements.txt`**: Dependências Python (pyserial, numpy, matplotlib)
- **`README.md`**: Este arquivo

## Requisitos

- **Hardware:** STM32F030R8 (ou compatível)
- **Software:**
  - STM32CubeIDE (para compilar/flash)
  - Python 3.x
  - pyserial (comunicação UART)
  - numpy (processamento de arrays - opcional, para comparação)
  - matplotlib (geração de heatmaps - opcional, para comparação)
- **Imagens:** Arquivos PGM P2 ASCII 90×90

## Próximos Passos

- **Versão 3**: Otimizações (cache, SIMD, paralelização)