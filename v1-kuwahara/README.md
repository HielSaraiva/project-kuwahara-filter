# Versão 1 - Filtro Kuwahara em C

Implementação do filtro Kuwahara em C para execução em PC, com testes de comparação contra implementação Python.

## Sumário

- [Sobre esta Versão](#sobre-esta-versão)
- [Estrutura de Arquivos](#estrutura-de-arquivos)
- [Pré-requisitos](#pré-requisitos)
- [Como Compilar e Executar](#como-compilar-e-executar)
  - [Windows (PowerShell)](#windows-powershell)
  - [Linux/macOS](#linuxmacos)
- [Configuração](#configuração)
- [Testes e Validação](#testes-e-validação)
- [Resultados](#resultados)
- [Detalhes da Implementação](#detalhes-da-implementação)

## Sobre esta Versão

A **Versão 1** é a implementação inicial do filtro Kuwahara para PC, com os seguintes objetivos:

- Implementar o algoritmo corretamente em C
- Processar imagens PGM (Portable Gray Map)
- Validar resultados comparando com implementação Python (pykuwahara)
- Definir complexidades e comportamento do algoritmo

## Estrutura de Arquivos

```
v1-kuwahara/
│
├── README.md                       
│
├── main.c                          # Programa principal
│
├── include/                        # Headers
│   ├── kuwahara.h                  # Interface do filtro Kuwahara
│   └── pgm_io.h                    # Interface para I/O de PGM
│
├── src/                            # Código-fonte
│   ├── kuwahara.c                  # Implementação do filtro
│   └── pgm_io.c                    # Leitura/escrita de arquivos PGM
│
├── imgs_original/                  # Imagens de entrada 
│
├── imgs_filtered/                  # Imagens processadas (saída)
│
└── python_implementation/          # Implementação Python para comparação
    ├── main.py                     # Programa Python
    ├── requirements.txt            # Dependências
    ├── README.md                   # 
    ├── imgs_filtered/              # Saída Python
    └── test/                       # Scripts de validação
        ├── compare_images.py       # Comparação C vs Python
        └── imgs_tests/             # Gráficos de comparação
```

## Pré-requisitos

### Para C:
- **Compilador C**: GCC, Clang, MSVC ou similar
- **Biblioteca math.h**: Para funções matemáticas (sqrt)

### Para Python (opcional, apenas para comparação):
- **Python 3.x**
- **pip** (gerenciador de pacotes)

## Como Compilar e Executar

### Windows (PowerShell)

```powershell
# 1. Navegar até o diretório v1-kuwahara
cd v1-kuwahara

# 2. Compilar o programa
gcc main.c src/kuwahara.c src/pgm_io.c -o kuwahara.exe -lm

# 3. Executar
.\kuwahara.exe
```

### Linux/macOS

```bash
# 1. Navegar até o diretório v1-kuwahara
cd v1-kuwahara

# 2. Compilar o programa
gcc main.c src/kuwahara.c src/pgm_io.c -o kuwahara -lm

# 3. Executar
./kuwahara
```

**Flags de compilação:**
- `-o kuwahara.exe` (ou `kuwahara`): Nome do executável
- `-lm`: Linka a biblioteca matemática (necessária para `sqrt()`)

## Configuração

Edite o arquivo `main.c` para ajustar:

### 1. Escolher a Imagem de Entrada

```c
// Descomente a linha da imagem desejada
const char *inpath = "imgs_original/balloons.ascii.pgm";
// const char *inpath = "imgs_original/body3.ascii.pgm";
// const char *inpath = "imgs_original/Brain1.pgm";
// const char *inpath = "imgs_original/coins.ascii.pgm";
// const char *inpath = "imgs_original/mona_lisa.ascii.pgm";
// const char *inpath = "imgs_original/PengBrew.pgm";
// const char *inpath = "imgs_original/pepper.ascii.pgm";
// const char *inpath = "imgs_original/saturn.ascii.pgm";
```

### 2. Ajustar Tamanho da Janela

```c
int window = 3;  // Valores comuns: 3, 5, 7, 9 (deve ser ímpar)
```

**Efeito do tamanho da janela:**
- `window = 3`: Suavização sutil, preserva detalhes
- `window = 5`: Suavização moderada
- `window = 7+`: Efeito artístico pronunciado

### 3. Definir Caminho de Saída

```c
const char *outpath = "imgs_filtered/nome_da_imagem.pgm";
```

## Testes e Validação

### Executar Implementação Python (Para Comparação)

**Windows (PowerShell):**

```powershell
# 1. Navegar até python_implementation
cd python_implementation

# 2. Criar ambiente virtual
python -m venv .venv

# 3. Ativar ambiente virtual
.\.venv\Scripts\Activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Executar
python main.py
```

**Linux/macOS:**

```bash
# 1. Navegar até python_implementation
cd python_implementation

# 2. Criar ambiente virtual
python3 -m venv .venv

# 3. Ativar ambiente virtual
source .venv/bin/activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Executar
python main.py
```

### Comparar Resultados C vs Python

**Windows (PowerShell):**

```powershell
# 1. Navegar até pasta de testes (a partir de python_implementation)
cd test

# 2. Executar script de comparação
python compare_images.py
```

**Linux/macOS:**

```bash
# 1. Navegar até pasta de testes (a partir de python_implementation)
cd test

# 2. Executar script de comparação
python compare_images.py
```

**O script gera:**
- Métricas estatísticas detalhadas (EMA, correlação, similaridade)
- Heatmaps visuais mostrando diferenças pixel a pixel
- Gráficos salvos em `imgs_tests/`

## Resultados

### Métricas de Validação (Mona Lisa, window=3)

#### Versão com BORDER_REFLECT_101 (Atual - Otimizada)

```
Dimensões: 90x90 pixels (8100 pixels totais)
Pixels diferentes: 346 (4.27%)
Pixels idênticos: 7754 (95.73%)

Correlação normalizada: 0.9998 (99.98% de similaridade estrutural)
EMA (Erro Médio Absoluto): 0.0664 pixels
Pixels com diferença ≤ 1: 98.98% (8017/8100 pixels)
Pixels com diferença ≤ 5: 99.90% (8091/8100 pixels)

Diferença máxima: 12 pixels (posição: linha 62, coluna 3)
Média dos pixels C: 46.93 | Python: 46.91 (diferença: +0.01)
Desvio padrão C: 46.46 | Python: 46.47 (diferença: -0.01)
```

#### Versão com Clamping (Anterior)

```
Dimensões: 90x90 pixels (8100 pixels totais)
Pixels diferentes: 616 (7.60%)
Pixels idênticos: 7484 (92.40%)

Correlação normalizada: 0.9996
EMA (Erro Médio Absoluto): 0.18 pixels
Pixels com diferença ≤ 1: 96.72% (7834/8100 pixels)

Diferença máxima: 25 pixels
Média dos pixels C: 46.86 | Python: 46.91 (diferença: -0.06)
```

**Melhoria com BORDER_REFLECT_101:**
- ✅ Pixels idênticos: 92.40% → **95.73%** (+3.33 pontos percentuais)
- ✅ EMA: 0.18 → **0.0664 pixels** (63% de redução)
- ✅ Diferença máxima: 25 → **12 pixels** (52% de redução)
- ✅ Diferença de médias: -0.06 → **+0.01** (praticamente zero!)
- ✅ Pixels com diff ≤ 1: 96.72% → **98.98%** (+2.26 pontos)
- ✅ Correlação: 0.9996 → **0.9998** (melhoria significativa)

### Análise Visual - Heatmap de Diferenças

![Heatmap de Comparação](python_implementation/test/imgs_tests/diff_heatmap_mona_lisa.ascii.png)

**Legenda do Heatmap:**
- **Preto**: Pixels idênticos (diff = 0)
- **Azul escuro**: Diferença de 1 pixel (imperceptível)
- **Azul claro**: Diferença de 2-3 pixels
- **Verde**: Diferença de 4-5 pixels
- **Laranja**: Diferença de 6-10 pixels
- **Vermelho**: Diferença > 10 pixels (outliers raros)

### Conclusões da Validação

#### ✅ **Implementação C está CORRETA**

As diferenças observadas **NÃO indicam erro** na implementação em C.

1. **Alta Correlação Estrutural (0.9998)**
   - Correlação próxima de 1.0 indica que as imagens são **estruturalmente idênticas**
   - As bordas, formas e padrões são preservados igualmente em ambas implementações

2. **98.98% dos Pixels com Diferença ≤ 1**
   - Diferenças de 1 pixel são **imperceptíveis ao olho humano**
   - Causadas por **diferenças algorítmicas** entre implementações
   - Normal em implementações independentes do mesmo filtro

3. **Diferenças são Mínimas e Consistentes**
   - EMA de 0.0664 pixels = **0.026% da escala** (0-255)
   - Diferença de médias de apenas +0.01 pixel é praticamente **zero**
   - Não há erros sistemáticos ou padrões incorretos

4. **Por que as Diferenças Existem?**
   - **Variância Amostral vs Populacional**: C usa divisão por (n-1), pykuwahara usa divisão por n
   - **Método de Filtragem**: C usa soma direta, pykuwahara usa convolução separável (cv2.sepFilter2D)
   - **Tratamento de Bordas**: C usa BORDER_REFLECT_101 (reflexão espelhada, igual ao OpenCV), mas pequenas diferenças numéricas podem ocorrer
   - **Arredondamento Final**: C trunca `(int)mean`, pykuwahara arredonda com NumPy
   - **Precisão Numérica**: C usa `double` (64 bits), pykuwahara usa `float32` (32 bits)
   - **Ordem de Operações**: A convolução vetorizada do OpenCV pode ter ordem de cálculo diferente da soma direta

5. **Validação por Inspeção Visual**
   - As imagens são **visualmente indistinguíveis**
   - O efeito artístico é **idêntico** em ambas
   - Heatmap mostra que diferenças estão **uniformemente distribuídas** (não há regiões problemáticas)

#### 🎯 **Conclusão Final**

A implementação em C do filtro Kuwahara está **correta e validada**. As diferenças observadas (4.27% dos pixels, média de 0.0664 pixels) são:
- ✅ **Esperadas** devido a variantes algorítmicas (Kuwahara clássico vs otimizado com OpenCV)
- ✅ **Excelentes** para processamento de imagens (95.73% pixels idênticos)
- ✅ **Imperceptíveis** visualmente (98.98% com diferença ≤ 1 pixel)
- ✅ **Não indicam erro** algorítmico (correlação 99.98%)

A correlação de 99.98% e similaridade de 98.98% (≤1 pixel) confirmam que o algoritmo foi implementado corretamente em C seguindo a abordagem clássica do filtro Kuwahara.

**Otimizações Aplicadas:**
- Implementação de BORDER_REFLECT_101 para tratamento de bordas (compatível com OpenCV)
- Melhoria de 3.33 pontos percentuais na similaridade (92.40% → 95.73%)
- Redução de 63% no erro médio absoluto (0.18 → 0.0664 pixels)
- Diferença máxima reduzida pela metade (25 → 12 pixels)

### Imagens Processadas

As imagens filtradas são salvas em `imgs_filtered/` no formato PGM P2 (ASCII).

## Detalhes da Implementação

### Algoritmo

1. **Para cada pixel da imagem:**
   - Define janela centrada (tamanho configurável)
   - Divide em 4 quadrantes sobrepostos
   - Calcula média e desvio padrão (amostral) de cada quadrante
   - Escolhe quadrante com **menor desvio padrão**
   - Atribui média desse quadrante ao pixel de saída

2. **Tratamento de bordas:**
   - Aplica **BORDER_REFLECT_101** (reflexão espelhada, compatível com OpenCV)
   - Reflete pixels para dentro da imagem sem incluir o pixel da borda
   - Exemplo: Para imagem [10, 20, 30, 40, 50]:
     - Índice -1 → reflete para índice 1 (valor 20)
     - Índice -2 → reflete para índice 2 (valor 30)
     - Índice 5 → reflete para índice 3 (valor 40)

### Complexidade

- **Tempo**: O(W × H × K²)
  - W, H: Largura e altura da imagem
  - K: Tamanho da janela
  
- **Espaço**: O(W × H)
  - Armazena imagem original e filtrada

## Próximos Passos

- **Versão 2**: Portabilidade para sistemas embarcados
- **Versão 3**: Otimizações (cache, SIMD, paralelização)
