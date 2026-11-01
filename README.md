# O ÚLTIMO SINAL — edição 3D

Uma pequena experiência de terror em primeira pessoa feita em Python com Ursina Engine.
Esta versão usa uma cena 3D real: é possível olhar para cima, para baixo e para todos os lados com o mouse.

## Requisitos

- Python 3.10 ou mais recente
- Windows, Linux ou macOS com suporte a OpenGL
- Conexão com a internet apenas para instalar as dependências

## Instalação

Abra um terminal dentro desta pasta e execute:

```bash
python -m pip install -r requirements.txt
python main.py
```

Se `python` não funcionar no Windows, tente `py`:

```powershell
py -m pip install -r requirements.txt
py main.py
```

## Controles

- **W A S D** — andar
- **Mouse** — olhar livremente em 360°, inclusive para cima e para baixo
- **E** — ler lembranças / interagir com a saída
- **Shift** — correr
- **Esc** — soltar/travar o mouse e pausar

## Sobre o jogo

Explore três locais conectados pela história. Em cada fase, encontre as três lembranças antes de usar a saída.
As lembranças revelam o que aconteceu com Daniel e por que a voz do telefone conhece seus pensamentos.

## Estrutura

- `main.py` — inicialização, controles, HUD, interações e progressão
- `world.py` — construção dos cenários 3D
- `story.py` — textos, pistas e dados das três fases

## Notas

Os cenários e objetos são criados por código, então não é necessário baixar modelos ou texturas à parte.
A atmosfera vem da iluminação, neblina, cores, geometria e narrativa. É uma base jogável que pode ser expandida com áudio, modelos 3D, animações e mais puzzles.
