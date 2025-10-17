# Filtro Kuwahara

Implementação do filtro Kuwahara para processamento de imagens em C. O filtro Kuwahara é uma técnica de suavização não-linear que preserva bordas, sendo muito utilizado para criar efeitos artísticos semelhantes a pinturas.

## Sumário

- [Sobre o Projeto](#sobre-o-projeto)
  - [Contexto Acadêmico](#contexto-acadêmico)
- [Estrutura do Projeto](#estrutura-do-projeto)
  - [Versão 1](#versão-1)
- [Como Executar](#como-executar)
  - [Parte 1](#parte-1)
- [Formato de Imagens](#formato-de-imagens)
- [Exemplos de Uso](#exemplos-de-uso)
  - [Efeito do Tamanho da Janela](#efeito-do-tamanho-da-janela)
- [Detalhes Técnicos](#detalhes-técnicos)
  - [Algoritmo Implementado](#algoritmo-implementado)
  - [Diferenças entre as Implementações](#diferenças-entre-as-implementações)
- [Licença](#licença)
- [Autor](#autor)

## Sobre o Projeto

O filtro Kuwahara divide uma janela ao redor de cada pixel em 4 quadrantes sobrepostos, calcula a média e o desvio padrão de cada quadrante, e atribui ao pixel central a média do quadrante com menor desvio padrão (mais homogêneo). Isso resulta em uma imagem suavizada que mantém as bordas nítidas.

### Contexto Acadêmico

Este projeto foi desenvolvido durante a cadeira de **Sistemas Embarcados** e está dividido em **3 partes**:

#### **Versão 1 (v1)** - Implementação em PC
- Projetar o algoritmo de forma correta
- Indicar entrada/saída de dados e complexidades
- Construir e definir testes para execução em PC
- **Objetivo**: Comparar o resultado do algoritmo implementado em C com a implementação já pronta em Python

#### **Versão 2 (v2)** - Portabilidade
- Transportar o algoritmo para um sistema embarcado
- Realizar as devidas alterações de código
- Implementar gestão de memória adequada para sistemas embarcados

#### **Versão 3 (v3)** - Otimização
- Propor e implementar otimizações na aplicação embarcada
- Reduzir tempo de computação ou uso de memória
- Avaliar ganhos de performance

## Estrutura do Projeto 

### Versão 1

```
project-kuwahara-filter/
│
├── README.md                           # Este arquivo
├── LICENSE                             # Licença MIT
│
└── v1-kuwahara/                        # Diretório v1
    │
    ├── main.c                          # Programa principal em C
    │
    ├── include/                        # Headers (.h)
    │   ├── kuwahara.h                  # Interface do filtro Kuwahara
    │   └── pgm_io.h                    # Interface para I/O de arquivos PGM
    │
    ├── src/                            # Código-fonte (.c)
    │   ├── kuwahara.c                  # Implementação do filtro Kuwahara
    │   └── pgm_io.c                    # Implementação de leitura/escrita PGM
    │
    ├── imgs_original/                  # Imagens de entrada (formato PGM)
    │   ├── balloons.ascii.pgm
    │   ├── body3.ascii.pgm
    │   ├── Brain1.pgm
    │   ├── coins.ascii.pgm
    │   ├── mona_lisa.ascii.pgm
    │   ├── PengBrew.pgm
    │   ├── pepper.ascii.pgm
    │   └── saturn.ascii.pgm
    │
    ├── imgs_filtered/                  # Imagens processadas (saída)
    │
    ├── test/                           # Testes e validação
    │   └── compare_images.py           # Comparação C vs Python (métricas)
    │
    └── python_implementation/          # Versão Python Já Implementada (Para comparação)
        ├── main.py                     # Programa principal em Python
        ├── requirements.txt            # Dependências Python
        ├── README.md                   # Documentação específica
        └── imgs_filtered/              # Saída da versão Python
```

## Como Executar

### Parte 1

#### Pré-requisitos
- Compilador C (GCC, Clang, MSVC, etc.)

#### Compilação e Execução

**No Windows (PowerShell):**
```powershell
# Navegar até o diretório
cd v1-kuwahara

# Compilar
gcc main.c src/kuwahara.c src/pgm_io.c -o kuwahara.exe -lm

# Executar
.\kuwahara.exe
```

**No Linux/macOS:**
```bash
# Navegar até o diretório
cd v1-kuwahara

# Compilar
gcc main.c src/kuwahara.c src/pgm_io.c -o kuwahara -lm

# Executar
./kuwahara
```

#### Configuração

Edite o arquivo `main.c` para:

1. **Escolher a imagem**: Descomente a linha da imagem desejada
   ```c
   // const char *inpath = "imgs_original/balloons.ascii.pgm";
   const char *inpath = "imgs_original/mona_lisa.ascii.pgm";  // ← atual
   // const char *inpath = "imgs_original/pepper.ascii.pgm";
   ```

2. **Ajustar o tamanho da janela**: Modifique a variável `window` (deve ser ímpar)
   ```c
   int window = 3;  // valores comuns: 3, 5, 7, 9
   ```

## Formato de Imagens

O projeto utiliza imagens no formato **PGM (Portable Gray Map)**:
- **Formato P2** (ASCII): Imagens em texto plano
- **Escala de cinza**: 0-255

## Exemplos de Uso

As imagens processadas são salvas automaticamente em:
- **Versão C**: `v1-kuwahara/imgs_filtered/`
- **Versão Python**: `v1-kuwahara/python_implementation/imgs_filtered/`

### Efeito do Tamanho da Janela

- **window = 3**: Suavização sutil, preserva mais detalhes
- **window = 5**: Suavização moderada, efeito mais visível
- **window = 7+**: Suavização forte, efeito artístico pronunciado

## Detalhes Técnicos

### Algoritmo Implementado

1. Para cada pixel da imagem:
   - Define uma janela centrada no pixel
   - Divide a janela em 4 quadrantes sobrepostos
   - Calcula média e desvio padrão de cada quadrante
   - Escolhe o quadrante com menor desvio padrão
   - Atribui a média desse quadrante ao pixel de saída

2. **Tratamento de bordas**: Aplica clamping (limita coordenadas aos limites da imagem)

### Diferenças entre as Implementações

- **C**: Implementação manual completa do algoritmo
- **Python**: Utiliza a biblioteca `pykuwahara` (implementação otimizada)

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Autor

Hiel Saraiva

---
