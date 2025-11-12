# 🔧 Simulador de FTL (Flash Translation Layer) com Garbage Collector

Este projeto implementa um simulador completo de **FTL (Flash Translation Layer)** — a camada de tradução responsável por gerenciar a escrita e leitura em memórias **flash NAND**, como as utilizadas em SSDs.  
O objetivo é demonstrar, de forma didática e realista, como o **mapeamento lógico-físico**, a **invalidação de páginas** e o **Garbage Collector (GC)** trabalham juntos para manter o desempenho e a integridade dos dados.

---

## 🧠 Conceito

Memórias flash não permitem **sobrescrita direta** em uma página já escrita.  
Quando um dado é atualizado, o sistema grava a nova versão em outra página livre e marca a antiga como **inválida**.  
Com o tempo, isso gera fragmentação — e é papel do **Garbage Collector**:

- Identificar blocos com muitas páginas inválidas;
- Mover as páginas válidas para outro bloco;
- Apagar o bloco antigo (erase), liberando todas as páginas para reuso.

O FTL gerencia esse processo de forma transparente para o sistema operacional, simulando o comportamento de um SSD real.

---

## ⚙️ Estrutura do Projeto

O simulador é dividido em quatro camadas principais:

| Módulo | Função |
|--------|---------|
| `Page` | Representa uma página de memória (estado: livre, válida ou inválida). |
| `Block` | Agrupa páginas e controla contadores de erase. |
| `Flash` | Controla o conjunto de blocos e fornece páginas livres. |
| `FTL` | Gerencia o mapeamento lógico-físico e chama o GC quando necessário. |
| `GarbageCollector` | Libera espaço movendo páginas válidas e apagando blocos. |

---

## 🧩 Funcionalidades

- Escrita e leitura lógicas (`write()` e `read()`).
- Mapeamento lógico-físico dinâmico.
- Invalidação automática de páginas antigas.
- Garbage Collector funcional com política de menor número de páginas válidas.
- Estatísticas detalhadas de desempenho:
  - Escritas lógicas e físicas;
  - Contagem de apagamentos (erase);
  - Número de páginas válidas, inválidas e livres;
  - Tamanho da tabela de mapeamento.

---

## 📊 Exemplo de Execução

```text
Estado inicial da memória:
Bloco 0: F F F F F F F F | Erases: 0
Bloco 1: F F F F F F F F | Erases: 0
...
=== ESTATÍSTICAS ===
Escritas lógicas: 0
Escritas físicas: 0
Erasures totais: 0
Páginas livres: 48
====================

Estado final da memória:
Bloco 0: V V I V V I V V | Erases: 0
Bloco 1: I V V I I V V I | Erases: 0
Bloco 2: V V I I V I V V | Erases: 1
Bloco 3: I I V V I I I V | Erases: 0
...
=== ESTATÍSTICAS ===
Escritas lógicas: 50
Escritas físicas: 48
Erasures totais: 3
Páginas válidas: 34
Páginas inválidas: 14
====================
