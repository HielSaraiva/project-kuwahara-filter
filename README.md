# Filtro Kuwahara

Implementação do filtro Kuwahara para processamento de imagens em C. O filtro Kuwahara é uma técnica de suavização não-linear que preserva bordas, sendo muito utilizado para criar efeitos artísticos semelhantes a pinturas.

## Sumário

- [Sobre o Projeto](#sobre-o-projeto)
  - [Contexto Acadêmico](#contexto-acadêmico)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Formato de Imagens](#formato-de-imagens)
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

```
project-kuwahara-filter/
│
├── README.md                           # Este arquivo
├── LICENSE                             # Licença MIT
│
└── v1-kuwahara/                        # Versão 1 - Implementação em PC
```

## Formato de Imagens

O projeto utiliza imagens no formato **PGM (Portable Gray Map)**:
- **Formato P2** (ASCII): Imagens em texto plano
- **Escala de cinza**: 0-255

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
