# 🖐️ Controle de Slides por Gestos

Controle apresentações usando gestos da mão detectados pela câmera, sem precisar tocar no teclado.

## Como funciona

| Gesto | Ação |
|-------|------|
| 🤙 Mindinho levantado | Próximo slide (→) |
| 👍 Polegar levantado | Slide anterior (←) |
| `ESC` | Sair |

---

## Requisitos

- Python 3.8+
- Linux com suporte a **Wayland** (usa `python-uinput`)
- Câmera conectada

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/pSangali/Python.git
cd Python
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Baixe o modelo do MediaPipe

Baixe o arquivo `hand_landmarker.task` e coloque na **mesma pasta** do script:

```
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

### 4. Ative o módulo uinput

```bash
sudo modprobe uinput
```

---

## Como rodar

> ⚠️ O script precisa de `sudo` para simular teclas via uinput.

```bash
sudo python hands_presentation.py
```

---

## Arquivos necessários na pasta

```
📁 pasta do projeto
├── hands_presentation.py
├── hand_landmarker.task   ← baixar conforme instrução acima
├── seta dir.PNG           ← opcional (exibe seta na tela)
├── seta esq.PNG           ← opcional (exibe seta na tela)
└── requirements.txt
```

> As imagens das setas são opcionais. Se não estiverem presentes, o script roda normalmente sem exibi-las.

---

## Configurações

No início do script você pode ajustar:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `CAM_INDEX` | `0` | Índice da câmera |
| `COOLDOWN` | `1.0` | Tempo mínimo entre gestos (segundos) |
| `ARROW_SHOW_TIME` | `0.6` | Tempo que a seta fica visível (segundos) |

---

## Dependências

```
mediapipe
opencv-python
numpy
python-uinput
```
