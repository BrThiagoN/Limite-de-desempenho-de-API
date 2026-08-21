# ⚡ Modelagem Matemática e Análise de Desempenho de APIs (Checkpoint 4)

[![FIAP](https://img.shields.io/badge/FIAP-2026-ED145B?style=for-the-badge&logo=fiap)](https://www.fiap.com.br/)
[![Disciplina](https://img.shields.io/badge/Disciplina-DPS%20Checkpoint%204-blue?style=for-the-badge)](https://www.fiap.com.br/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org/)

> **Projeto Aplicado de Modelagem Matemática: Da observação de desempenho à tomada de decisão técnica**  
> **Docente:** Prof. Jones Egydio — FIAP 2026  
> **Curso:** Engenharia de Software | **Disciplina:** Differentiated Problem Solving (DPS)  

### 👥 Integrantes do Grupo:
- **Thiago Gomes Nascimento** — RM 569436
- **Gabriel Henrique Ongarelli Reis** — RM 572636
- **Vinicius Scalone Ramires** — RM 573783
- **Matheus de Amorim Brito** — RM 572435
- **Eduardo Felix Frois Silva** — RM 574103

---

## 📌 Sumário
1. [Integrantes do Grupo](#-integrantes-do-grupo)
2. [Contexto do Problema & Challenge](#-contexto-do-problema--challenge)
3. [Fundamentação Matemática & Teoria de Limites](#-fundamentação-matemática--teoria-de-limites)
4. [Estrutura do Repositório](#-estrutura-do-repositório)
5. [Instalação e Pré-requisitos](#-instalação-e-pré-requisitos)
6. [Como Executar o Jupyter Notebook](#-como-executar-o-jupyter-notebook)
7. [Como Executar a Aplicação Streamlit](#-como-executar-a-aplicação-streamlit)
8. [Resultados Numéricos & Simulação](#-resultados-numéricos--simulação)
9. [Tomada de Decisão & Arquitetura de Software](#-tomada-de-decisão--arquitetura-de-software)

---

## 🏢 Contexto do Problema & Challenge

A empresa parceira do Challenge (**Jovi / Vivo**) opera ecossistemas digitais de alta concorrência. Uma das peças centrais dessa arquitetura é o **vivoCloud Storage API**, um microsserviço responsável por receber, processar e persistir arquivos e dados na nuvem da empresa.

### O Desafio
Em testes de carga controlados, a equipe de SRE (*Site Reliability Engineering*) observou que o tempo de resposta ($\text{ms}$) cresce de forma desproporcional conforme a taxa de requisições por segundo ($x$) se aproxima do limite de capacidade de processamento do nó, estimado em **$50\text{ req/s}$**.

### Dados Empíricos Coletados
| Carga ($x$ em req/s) | Tempo Médio de Resposta Medido ($y$ em ms) |
| :---: | :---: |
| **10** | 25 |
| **20** | 33 |
| **30** | 50 |
| **35** | 67 |
| **40** | 100 |
| **45** | 200 |
| **48** | 500 |

---

## 🧮 Fundamentação Matemática & Teoria de Limites

Com base na **Teoria de Filas (Modelo $M/M/1$)**, o tempo total de permanência no sistema é modelado por uma função racional assintótica:

$$f(x) = \frac{1000}{50 - x}$$

- **Variável Independente ($x$):** Taxa de requisições recebidas por segundo ($\text{req/s}$).
- **Variável Dependente ($f(x)$):** Tempo médio de resposta / latência ($\text{ms}$).
- **Domínio Matemático:** $\text{Dom}(f) = \{x \in \mathbb{R} \mid x \neq 50\}$.
- **Domínio Operacional Válido:** $x \in [0, 50)\text{ req/s}$.

### Análise de Limites
1. **Latência Base em Repouso ($x \to 0^+$):**
   $$\lim_{x \to 0^+} \frac{1000}{50 - x} = \frac{1000}{50} = 20\text{ ms}$$
   *Tempo puro de processamento e overhead de rede sem fila de espera.*

2. **Colapso Assintótico pela Esquerda ($x \to 50^-$):**
   $$\lim_{x \to 50^-} \frac{1000}{50 - x} = \frac{1000}{0^+} = +\infty$$
   *Conforme a carga se aproxima de 50 req/s, o enfileiramento cresce infinitamente, gerando timeouts e indisponibilidade.*

3. **Assíntota Vertical em $x = 50$:**
   *Demarca a barreira física intransponível de processamento do hardware.*

---

## 📁 Estrutura do Repositório

```text
Limite-de-desempenho-de-API/
├── checkpoint.ipynb     # Notebook Jupyter com relatório completo, códigos SymPy, gráficos e saídas preservadas
├── app.py               # Aplicação web interativa desenvolvida em Streamlit
├── requirements.txt     # Dependências e bibliotecas necessárias
├── README.md            # Documentação técnica completa do projeto
├── roadmap.md           # Planejamento das fases de desenvolvimento
├── build_and_run_notebook.py # Script de geração e execução automatizada do notebook
└── Checkpoint_4_DPS_Limites_Streamlit_GitHub.pdf # Enunciado oficial do Checkpoint 4
```

---

## 🛠️ Instalação e Pré-requisitos

Clone o repositório e instale as dependências com Python 3.10 ou superior:

```bash
# 1. Clonar o repositório
git clone https://github.com/BrThiagoN/Limite-de-desempenho-de-API.git
cd Limite-de-desempenho-de-API

# 2. Criar e ativar ambiente virtual (recomendado)
python -m venv venv
# No Windows:
.\venv\Scripts\activate
# No Linux/MacOS:
source venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt
```

---

## 📓 Como Executar o Jupyter Notebook

O arquivo `checkpoint.ipynb` contém todo o relatório técnico integrado com códigos SymPy, tabelas formatadas e gráficos do Matplotlib:

```bash
# Iniciar o Jupyter Notebook
jupyter notebook checkpoint.ipynb
```
*Observação:* O notebook já se encontra totalmente executado e com todas as saídas preservadas (`Run All`).

---

## 🚀 Como Executar a Aplicação Streamlit

Para iniciar o painel interativo de simulação e apoio à tomada de decisão:

```bash
streamlit run app.py
```

A aplicação será aberta automaticamente em seu navegador padrão no endereço `http://localhost:8501`.

### Recursos do Streamlit:
- **Slider Interativo:** Simulação de carga em tempo real ($0.0$ a $49.9\text{ req/s}$).
- **Monitor de SLA:** Alertas visuais automáticos de conformidade de latência.
- **Gráfico Dinâmico Plotly:** Visualização da curva assintótica, pontos experimentais e zonas operacionais.
- **Painéis de Decisão:** Recomendações técnicas imediatas para arquitetos e equipes de infraestrutura.

---

## 📊 Resultados Numéricos & Simulação

| Carga ($x$ em req/s) | Denominador ($50 - x$) | Latência Prevista $f(x)$ (ms) | Latência Medida (ms) | Taxa de Utilização ($\%$) | Status Operacional |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **10.0** | 40.0 | 25.00 ms | 25 ms | 20.0% | 🟢 Operação Segura |
| **20.0** | 30.0 | 33.33 ms | 33 ms | 40.0% | 🟢 Operação Segura |
| **30.0** | 20.0 | 50.00 ms | 50 ms | 60.0% | 🟢 Operação Segura |
| **35.0** | 15.0 | 66.67 ms | 67 ms | 70.0% | 🟡 Zona de Atenção |
| **40.0** | 10.0 | 100.00 ms | 100 ms | 80.0% | 🟡 Zona de Atenção |
| **45.0** | 5.0 | 200.00 ms | 200 ms | 90.0% | 🔴 Zona Crítica |
| **48.0** | 2.0 | 500.00 ms | 500 ms | 96.0% | 🔴 Zona Crítica |
| **49.0** | 1.0 | 1000.00 ms | N/A | 98.0% | 🔴 Quase Saturação |
| **49.5** | 0.5 | 2000.00 ms | N/A | 99.0% | 🔴 Quase Saturação |
| **49.9** | 0.1 | 10000.00 ms | N/A | 99.8% | 🔴 Colapso Iminente |

---

## 🏗️ Tomada de Decisão & Arquitetura de Software

Com base na investigação matemática, a equipe conclui:
1. **Capacidade Teórica $\neq$ Capacidade Segura:** O limite de $50\text{ req/s}$ é uma assíntota inatingível em produção estável. A capacidade segura de operação é de até **$35\text{ req/s}$** por nó ($70\%$ de utilização).
2. **Recomendações Implementáveis:**
   - **Horizontal Pod Autoscaling (HPA):** Disparar escalonamento horizontal no Kubernetes ao atingir $35\text{ req/s}$ ou $70\%$ de CPU.
   - **Rate Limiting:** Retornar `HTTP 429 Too Many Requests` para tráfego que ultrapasse o limite de segurança do nó via API Gateway.
   - **Cache Distribuído (Redis):** Cachear leituras na nuvem para reduzir a carga sobre a API principal.
   - **Filas Assíncronas (Kafka / RabbitMQ / SQS):** Desacoplar operações pesadas de persistência.
   - **Circuit Breaker:** Abrir o circuito para evitar falhas em cascata caso o tempo de resposta exceda $200\text{ ms}$.

---

## 👥 Equipe & Integrantes

| Nome do Aluno | RM |
| :--- | :---: |
| **Thiago Gomes Nascimento** | 569436 |
| **Gabriel Henrique Ongarelli Reis** | 572636 |
| **Lucas Rodrigues Dos Santos** | 571778 |
| **Matheus de Amorim Brito** | 572435 |
| **Eduardo Felix Frois Silva** | 574103 |

- **Instituição:** FIAP — 2026
- **Curso:** Engenharia de Software
- **Disciplina:** Differentiated Problem Solving (DPS)
- **Docente:** Prof. Jones Egydio
