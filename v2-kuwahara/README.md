# Kuwahara Filter STM32 - v2-kuwahara

## Descrição
Este projeto implementa o filtro Kuwahara para imagens 90x90 em um microcontrolador STM32 (F030R8). A imagem é processada e enviada via UART (serial) no formato PGM (P2, texto), podendo ser capturada por um script Python para análise ou visualização.

## Estrutura
- **Core/Inc/**: Headers do projeto (inclui imagens em matriz, configurações, etc)
- **Core/Src/**: Código fonte principal (main.c, drivers, etc)
- **Core/pgms/**: Exemplos de arquivos PGM gerados
- **python_script/**: Script Python para captura da imagem via serial

## Configuração do STM32
- Placa: STM32F030R8
- UART utilizada: USART2
- Baudrate: **38400**
- Tamanho da imagem: **90x90** pixels
- Formato de saída: PGM ASCII (P2)
- A cada 5 segundos, uma nova imagem é enviada pela UART

## Como rodar o script Python para capturar a imagem
1. Instale o Python 3.x

2. Crie um ambiente virtual:
   - **Windows:**
     ```powershell
     python -m venv venv
     venv\Scripts\activate
     ```
   - **Linux/macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Instale o pacote pyserial:
   ```bash
   pip install -r requirements.txt
   ```
   ou
   ```bash
   pip install pyserial
   ```

4. Conecte o STM32 na USB e identifique a porta serial (ex: COM3, COM4...)

5. Execute o script:
   ```bash
   python reader.py
   ```

6. Escolha o número da porta serial conforme listado pelo script

7. O script irá salvar cada imagem recebida como `saida_1.pgm`, `saida_2.pgm`, ...

## Formato da saída serial
A cada ciclo, o STM32 envia:
```
P2
90 90
255
<90 linhas, cada uma com 90 valores de pixel separados por espaço>
```

## Observações
- O script Python só salva arquivos que começam com "P2" e têm exatamente 8100 valores de pixel.
- Para alterar a imagem processada, edite o macro em `main.c`:
  ```c
  #define USE_MONA_LISA
  // #define USE_PEPPER
  ```
- O tempo entre imagens pode ser ajustado em `HAL_Delay(5000);` (milissegundos).

## Requisitos
- Python 3.x
- pyserial
- STM32CubeIDE para compilar/flashar o firmware

## Autor
Hiel Saraiva
