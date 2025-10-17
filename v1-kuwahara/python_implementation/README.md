# Filtro Kuwahara - Implementação Python

Implementação do filtro Kuwahara usando a biblioteca **pykuwahara**.

## Bibliotecas Utilizadas

- **numpy**: Manipulação de arrays
- **opencv-python**: Processamento de imagens
- **pykuwahara**: Implementação pronta do filtro Kuwahara

## Como Usar

### Pré-requisitos
- Python 3.7+
- pip

### Executar manualmente

```powershell
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
.\.venv\Scripts\Activate

# Instalar dependências
pip install -r requirements.txt

# Executar
python main.py
```

## Configuração

Edite o arquivo `main.py` para:

- **Escolher imagem**: descomente a linha da imagem desejada
- **Ajustar tamanho da janela**: modifique a variável `window`

```python
images = [
    "../imgs_original/mona_lisa.ascii.pgm",  # ← imagem atual
    # "../imgs_original/pepper.ascii.pgm",
]

window = 3  # tamanho da janela (ímpar)
```

## Entrada e Saída

- **Entrada**: Imagens PGM formato P2 (ASCII) da pasta `../imgs_original/`
- **Saída**: Imagens PGM formato P2 (ASCII) na pasta `imgs_filtered/`

## Estrutura do Projeto

```
python_implementation/
├── main.py             # Programa principal
├── requirements.txt    # Dependências Python
├── README.md           # Este arquivo
├── .venv/              # Ambiente virtual (criado automaticamente)
└── imgs_filtered/      # Imagens processadas (saída)
```
