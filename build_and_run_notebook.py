import json
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor
import os
import sys

def create_and_execute_notebook():
    nb = nbf.v4.new_notebook()
    nb['cells'] = []
    
    # -------------------------------------------------------------
    # Célula 1: Título e Apresentação do Trabalho
    # -------------------------------------------------------------
    nb['cells'].append(nbf.v4.new_markdown_cell(r"""# ⚡ Checkpoint 4 — Limites, Desempenho de APIs e Streamlit
**Disciplina:** Differentiated Problem Solving (DPS)  
**Instituição:** FIAP — 2026  
**Docente:** Prof. Jones Egydio  
**Curso:** Engenharia de Software  
**Tema:** Projeto Aplicado de Modelagem Matemática — *Da observação de desempenho à tomada de decisão técnica*  
**Pontuação Total:** 10,0 pontos  

### 👥 Integrantes do Grupo:
- **Thiago Gomes Nascimento** — RM: 569436
- **Gabriel Henrique Ongarelli Reis** — RM: 572636
- **Vinicius Scalone Ramires** — RM: 573783
- **Matheus de Amorim Brito** — RM: 572435
- **Eduardo Felix Frois Silva** — RM: 574103

---

## 🏢 1. Contexto do Problema e Dados Empíricos

### 1.1. Contexto do Challenge
A empresa parceira do Challenge (**Jovi / Vivo**) utiliza ecossistemas digitais em nuvem de alta concorrência para atender milhões de clientes simultâneos. Um dos componentes mais críticos dessa infraestrutura é o **vivoCloud Storage API**, um microsserviço responsável por receber requisições de upload, sincronização e persistência de dados.

### 1.2. Problema de Desempenho Observado
Durante a realização de testes de carga controlados, a equipe de Engenharia de Software e *Site Reliability Engineering* (SRE) constatou que o **tempo médio de resposta (latência)** da API aumenta conforme cresce a taxa de requisições recebidas por segundo ($x$).
- Em regimes de baixa e média carga, o tempo de resposta permanece baixo, estável e previsível.
- Contudo, à medida que a carga se aproxima da capacidade máxima de processamento do nó de infraestrutura ($\approx 50\text{ req/s}$), o tempo de resposta **cresce de forma desproporcional e explosiva**, comprometendo a experiência do usuário, violando os Acordos de Nível de Serviço (**SLA**) e colocando em risco a disponibilidade de todo o ecossistema.

### 1.3. Resultados Observados no Teste de Carga
| Carga ($x$ em req/s) | Tempo Médio de Resposta Medido ($y$ em ms) |
| :---: | :---: |
| **10** | 25 |
| **20** | 33 |
| **30** | 50 |
| **35** | 67 |
| **40** | 100 |
| **45** | 200 |
| **48** | 500 |

O objetivo deste projeto é modelar matematicamente esse comportamento com o auxílio do **Conceito de Limites**, implementar a solução computacional em Python/SymPy, validar o ajuste empírico por regressão não linear e disponibilizar uma **aplicação interativa em Streamlit** para apoiar decisões estratégicas de arquitetura e infraestrutura de software.
"""))

    # -------------------------------------------------------------
    # Célula 2: Critério 3.1 - Construção do Modelo Matemático
    # -------------------------------------------------------------
    nb['cells'].append(nbf.v4.new_markdown_cell(r"""---

## 🧮 2. Construção do Modelo Matemático (Critério 3.1 — 2,0 pontos)

### a) Definição das Variáveis e Domínios
- **Variável Independente ($x$):** Taxa de requisições por segundo recebidas pelo endpoint da API ($\text{req/s}$).
- **Variável Dependente ($f(x)$ ou $T(x)$):** Tempo médio de resposta / latência da API em milissegundos ($\text{ms}$).
- **Domínio Matemático:**  
  $$\text{Dom}(f) = \{x \in \mathbb{R} \mid x \neq 50\}$$  
  Algebricamente, a função é contínua e definida em toda a reta real exceto em $x = 50$, onde ocorre anulação do denominador (divisão por zero).
- **Domínio Válido no Contexto do Sistema (Domínio Operacional):**  
  $$\text{Dom}_{\text{operacional}} = [0, 50) \text{ req/s}$$
  *Fundamentação Física e Computacional:*
  1. $x < 0$ é fisicamente impossível no mundo real (não existe taxa negativa de requisições).
  2. $x = 50$ causa indeterminação matemática e colapso operacional (fila infinita de espera).
  3. $x > 50$ geraria tempos de resposta negativos pelo modelo algébrico, o que não possui significado no processamento de software.

### b) Construção da Função Matemática
Fundamentada na **Teoria de Filas (Modelo $M/M/1$ de Kleinrock)**, o tempo médio de permanência no sistema sob taxa de chegada $\lambda = x$ e taxa de atendimento $\mu = 50\text{ req/s}$ é expresso por $W = \frac{1}{\mu - \lambda}$ (em segundos). Aplicando o fator de conversão de escala para milissegundos ($1000\text{ ms/s}$):

$$f(x) = \frac{1000}{50 - x}$$

### c) Justificativa da Escolha da Função Racional
1. **Representação da Barreira Assintótica:** Recursos computacionais (núcleos de CPU, *threads* de I/O, memória RAM, conexões de banco de dados) são estritamente finitos. Quando a taxa de requisições se aproxima da taxa máxima de serviço ($\mu = 50$), o tempo de enfileiramento cresce assintoticamente ao infinito. Modelos polinomiais ou lineares falham categoricamente por não possuírem assíntotas verticais.
2. **Aderência Perfeita aos Dados Empíricos:**
   - $f(10) = \frac{1000}{50 - 10} = \frac{1000}{40} = 25.00\text{ ms}$ (Erro: $0.0\%$)
   - $f(20) = \frac{1000}{50 - 20} = \frac{1000}{30} = 33.33\text{ ms} \approx 33\text{ ms}$ (Erro: $1.0\%$)
   - $f(30) = \frac{1000}{50 - 30} = \frac{1000}{20} = 50.00\text{ ms}$ (Erro: $0.0\%$)
   - $f(35) = \frac{1000}{50 - 35} = \frac{1000}{15} = 66.67\text{ ms} \approx 67\text{ ms}$ (Erro: $0.5\%$)
   - $f(40) = \frac{1000}{50 - 40} = \frac{1000}{10} = 100.00\text{ ms}$ (Erro: $0.0\%$)
   - $f(45) = \frac{1000}{50 - 45} = \frac{1000}{5} = 200.00\text{ ms}$ (Erro: $0.0\%$)
   - $f(48) = \frac{1000}{50 - 48} = \frac{1000}{2} = 500.00\text{ ms}$ (Erro: $0.0\%$)

### d) Identificação do Ponto e Região Crítica
- **Ponto Crítico:** $x = 50\text{ req/s}$ (ponto de descontinuidade infinita / singularidade assintótica).
- **Região Crítica:** Intervalo $[45, 50)\text{ req/s}$ (utilização $\ge 90\%$, onde pequenas flutuações de tráfego disparam a latência para milhares de milissegundos).

### e) Significado Técnico no Contexto da Engenharia de Software
Representa o esgotamento completo da capacidade de *throughput* do nó de computação: saturação do *pool* de *threads* do servidor web (ex.: Tomcat / Uvicorn / NGINX), esgotamento de conexões TCP, acúmulo no buffer de sockets e disparo de erros `HTTP 504 Gateway Timeout` por estouro de *timeout* dos clientes.

---

> ### 📌 **Questão Obrigatória 3.1**
> **Pergunta:** *A capacidade estimada de 50 requisições por segundo significa necessariamente que o sistema consegue operar normalmente com exatamente 50 requisições por segundo? Fundamente a resposta utilizando o modelo construído.*  
> 
> **Resposta Fundamentada:** **Não, categoricamente não.** O sistema é absolutamente incapaz de operar com estabilidade em exatamente $50\text{ req/s}$. Avaliando o modelo analítico no ponto $x = 50$:
> $$f(50) = \frac{1000}{50 - 50} = \frac{1000}{0}$$
> Temos uma divisão por zero (indeterminação matemática). Pelo limite lateral $\lim_{x \to 50^-} f(x) = +\infty$, quando a taxa de chegada atinge a capacidade máxima do servidor, a fila de espera cresce infinitamente sem nunca ser drenada. Operacionalmente, isso provoca estouro de memória (*Out Of Memory*), esgotamento de conexões e travamento total da aplicação (*crash*).
"""))

    # -------------------------------------------------------------
    # Célula 3: Código - Definição do Modelo com SymPy e Ajuste Estatístico
    # -------------------------------------------------------------
    nb['cells'].append(nbf.v4.new_code_cell(r"""# dps_streamlit_canary = "vega_8241"
# Importação das bibliotecas científicas essenciais
import sympy as sp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score, mean_squared_error
from IPython.display import display, HTML

# Configurações visuais do Matplotlib / Seaborn
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 120

# 1. Definição simbólica da variável x e da função analítica f(x) com SymPy
x = sp.Symbol('x', real=True)
f = 1000 / (50 - x)

print("="*65)
print("       MODELO MATEMÁTICO ANALÍTICO SIMBÓLICO (SymPy)")
print("="*65)
sp.pprint(f)

# 2. Validação Estatística por Regressão Não Linear (Curve Fitting)
cargas_exp = np.array([10, 20, 30, 35, 40, 45, 48], dtype=float)
tempos_exp = np.array([25, 33, 50, 67, 100, 200, 500], dtype=float)

def modelo_generico(x_in, k_param, mu_param):
    return k_param / (mu_param - x_in)

popt, pcov = curve_fit(modelo_generico, cargas_exp, tempos_exp, p0=[1000, 50])
k_ajustado, mu_ajustado = popt
tempos_preditos = modelo_generico(cargas_exp, *popt)
r2 = r2_score(tempos_exp, tempos_preditos)
mse = mean_squared_error(tempos_exp, tempos_preditos)

print("\n" + "="*65)
print("     VALIDAÇÃO ESTATÍSTICA POR MÍNIMOS QUADRADOS (Curve Fit)")
print("="*65)
print(f"Parâmetro k ajustado:        {k_ajustado:.4f} (Teórico: 1000.0)")
print(f"Capacidade mu ajustada:      {mu_ajustado:.4f} req/s (Teórico: 50.0 req/s)")
print(f"Coeficiente R²:              {r2:.6f} (Ajuste quase perfeito > 0.9999)")
print(f"Erro Quadrático Médio (MSE): {mse:.4f}")
print("="*65)
"""))

    # -------------------------------------------------------------
    # Célula 4: Critério 3.2 - Análise Matemática com Limites e Derivadas
    # -------------------------------------------------------------
    nb['cells'].append(nbf.v4.new_markdown_cell(r"""---

## 📈 3. Análise Matemática Utilizando Limites e Cálculo Diferencial (Critério 3.2 — 2,0 pontos)

Para investigar rigorosamente o comportamento da API em todas as regiões, realizamos a análise matemática por limites e derivadas:

### a) e b) Cálculo e Interpretação dos Limites Simbólicos

| Limite Simbólico | Valor | Classificação | Significado Gráfico | Significado Operacional no Sistema Real |
| :--- | :---: | :---: | :--- | :--- |
| $\lim_{x \to 0^+} \frac{1000}{50 - x}$ | **$20\text{ ms}$** | **Finito** | Intercepto com o eixo $y$ em $(0, 20)$. | **Latência em repouso (baseline):** Tempo de processamento e overhead de rede sem contenção de recursos. |
| $\lim_{x \to 50^-} \frac{1000}{50 - x}$ | **$+\infty$** | **Infinito Positivo** | A curva diverge verticalmente ao infinito ao se aproximar de $x = 50$ pela esquerda. | **Colapso por saturação:** Fila de espera cresce sem limites, gerando estouro de memória e *timeouts*. |
| $\lim_{x \to 50^+} \frac{1000}{50 - x}$ | **$-\infty$** | **Infinito Negativo** | A curva parte de $-\infty$ à direita da assíntota. | **Sem significado físico:** Representa uma região matematicamente existente, mas operacionalmente inacessível (não existe latência negativa). |
| $\lim_{x \to 50} \frac{1000}{50 - x}$ | **$\nexists$** | **Inexistente** | Limites laterais divergem ($\lim_{x \to 50^-} \neq \lim_{x \to 50^+}$). | Descontinuidade essencial que confirma a impossibilidade de operação pontual em $x = 50$. |
| $\lim_{x \to +\infty} \frac{1000}{50 - x}$ | **$0$** | **Finito** | Assíntota horizontal $y = 0$. | Limite algébrico formal sem correspondência prática, pois o sistema colapsa antes de ultrapassar $x = 50$. |

### c) Estudo do Cálculo Diferencial (Taxa de Crescimento e Convexidade)
- **Derivada Primeira (Taxa de Variação da Latência):**
  $$f'(x) = \frac{d}{dx}\left[1000(50 - x)^{-1}\right] = \frac{1000}{(50 - x)^2} > 0 \quad \forall x \in [0, 50)$$
  *Interpretação:* A função é estritamente crescente. Para $x=10$, a sensibilidade é de $0.625\text{ ms/(req/s)}$, enquanto para $x=48$, a sensibilidade sobe para $250\text{ ms/(req/s)}$ ($400\times$ maior!).
- **Derivada Segunda (Aceleração da Degradação):**
  $$f''(x) = \frac{d^2}{dx^2}f(x) = \frac{2000}{(50 - x)^3} > 0 \quad \forall x \in [0, 50)$$
  *Interpretação:* A função possui concavidade voltada para cima (estritamente convexa), comprovando que o crescimento da latência acelera de forma explosiva ao se aproximar do limite.

### d) Análise de Percentis de Cauda (*Tail Latency* - p95 e p99)
Em filas $M/M/1$, o tempo de resposta segue distribuição exponencial com parâmetro $(\mu - \lambda)$. Assim:
- **$p95$:** $T_{p95} = -f(x) \cdot \ln(1 - 0.95) = f(x) \cdot \ln(20) \approx 2.996 \cdot f(x)$
- **$p99$:** $T_{p99} = -f(x) \cdot \ln(1 - 0.99) = f(x) \cdot \ln(100) \approx 4.605 \cdot f(x)$
Isso demonstra matematicamente que mesmo quando a média é $100\text{ ms}$ ($x=40$), $1\%$ das requisições mais lentas já experimentam **$460\text{ ms}$** de latência!

---

> ### 📌 **Questão Obrigatória 3.2**
> **Pergunta:** *Qual é o significado operacional de uma assíntota vertical em um modelo de desempenho de software?*  
> 
> **Resposta Fundamentada:** Em Engenharia de Software e Arquitetura de Nuvem, uma **assíntota vertical** demarca a **fronteira física e lógica intransponível de capacidade máxima** de um sistema de software. Ela representa a condição limite em que a taxa de requisições de entrada iguala a capacidade de vazão máxima do servidor ($\lambda \to \mu$). A partir desse limite, o tempo de enfileiramento cresce infinitamente, impossibilitando o esvaziamento do buffer. Operacionalmente, a assíntota vertical indica falha catastrófica: esgotamento de *threads*, travamento do *garbage collector*, acúmulo de requisições em memória e queda completa do serviço (*crash/outage*).
"""))

    # -------------------------------------------------------------
    # Célula 5: Código - Cálculo Simbólico de Limites e Derivadas com SymPy
    # -------------------------------------------------------------
    nb['cells'].append(nbf.v4.new_code_cell(r"""# 1. Cálculo simbólico de todos os limites com SymPy
lim_repouso = sp.limit(f, x, 0, dir='+')
lim_colapso_esq = sp.limit(f, x, 50, dir='-')
lim_invalido_dir = sp.limit(f, x, 50, dir='+')
lim_infinito = sp.limit(f, x, sp.oo)

# 2. Cálculo simbólico das derivadas
f_prime = sp.diff(f, x)
f_double_prime = sp.diff(f, x, 2)

print("="*70)
print("             ANÁLISE DE LIMITES SIMBÓLICOS (SymPy)")
print("="*70)
print(f"1. Limite em Repouso (x -> 0+):       {lim_repouso} ms     (Finito - Latência Base)")
print(f"2. Limite de Colapso (x -> 50-):       {lim_colapso_esq}          (Infinito Positivo - Saturação)")
print(f"3. Limite pela Direita (x -> 50+):     {lim_invalido_dir}         (Infinito Negativo - Sem sentido físico)")
print(f"4. Limite no Infinito (x -> +oo):      {lim_infinito}             (Assíntota horizontal matemática)")
print("="*70)
print("\n" + "="*70)
print("             ESTUDO DE DERIVADAS E TAXA DE VARIAÇÃO")
print("="*70)
print("Derivada Primeira f'(x):")
sp.pprint(f_prime)
print("\nDerivada Segunda f''(x):")
sp.pprint(f_double_prime)
print("="*70)
"""))

    # -------------------------------------------------------------
    # Célula 6: Critério 3.3 - Implementação Computacional e Simulações
    # -------------------------------------------------------------
    nb['cells'].append(nbf.v4.new_markdown_cell(r"""---

## 💻 4. Implementação Computacional no Notebook (Critério 3.3 — 2,0 pontos)

Validamos computacionalmente as propriedades assintóticas e os percentis de cauda para todas as **cargas obrigatórias** solicitadas pelo enunciado:
$$\{10,\ 20,\ 30,\ 40,\ 45,\ 48,\ 49,\ 49.5,\ 49.9\} \text{ req/s}$$
"""))

    # -------------------------------------------------------------
    # Célula 7: Código - Tabela Numérica Formatada e Percentis
    # -------------------------------------------------------------
    nb['cells'].append(nbf.v4.new_code_cell(r"""# Dados empíricos coletados no teste de carga
dados_exp_map = {10: 25, 20: 33, 30: 50, 35: 67, 40: 100, 45: 200, 48: 500}

# Cargas obrigatórias solicitadas pelo enunciado oficial
cargas_simulacao = [10.0, 20.0, 30.0, 35.0, 40.0, 45.0, 48.0, 49.0, 49.5, 49.9]

tabela = []
for c in cargas_simulacao:
    tempo_teorico = float(f.subs(x, c))
    tempo_medido = dados_exp_map.get(int(c) if c.is_integer() else c, "N/A")
    utilizacao = (c / 50.0) * 100.0
    p95 = tempo_teorico * np.log(20.0)
    p99 = tempo_teorico * np.log(100.0)
    fator_aumento = tempo_teorico / 20.0  # Latência base = 20ms
    
    if c < 35.0:
        regiao = "🟢 Segura"
    elif c < 45.0:
        regiao = "🟡 Atenção"
    else:
        regiao = "🔴 Crítica / Saturação"
        
    tabela.append({
        "Carga (req/s)": f"{c:.1f}",
        "Denominador (50 - x)": f"{50.0 - c:.2f}",
        "Latência Média f(x) (ms)": f"{tempo_teorico:.2f} ms",
        "p95 (ms)": f"{p95:.2f} ms",
        "p99 (ms)": f"{p99:.2f} ms",
        "Tempo Medido (ms)": f"{tempo_medido} ms" if tempo_medido != "N/A" else "N/A",
        "Utilização (%)": f"{utilizacao:.1f}%",
        "Fator vs Repouso": f"{fator_aumento:.1f}x",
        "Zona Operacional": regiao
    })

df_simulacao = pd.DataFrame(tabela)
display(HTML("<h3>📊 TABELA DE SIMULAÇÃO DE DESEMPENHO E PERCENTIS DE CAUDA</h3>"))
display(df_simulacao)
"""))

    # -------------------------------------------------------------
    # Célula 8: Investigação Computacional 3.3
    # -------------------------------------------------------------
    nb['cells'].append(nbf.v4.new_markdown_cell(r"""
> ### 🔍 **Investigação Computacional 3.3**
> **Pergunta:** *O que os valores numéricos parecem indicar quando a carga se aproxima da capacidade crítica? Como essa observação se relaciona com o limite calculado simbolicamente?*  
> 
> **Resposta Fundamentada:** A análise dos dados computacionais evidencia claramente o **efeito hiperbólico e não-linear da saturação de filas**:
> 1. **Comportamento em Baixa e Média Carga:** De $10$ para $30\text{ req/s}$ ($+20\text{ req/s}$ de aumento), o tempo de resposta aumenta de forma branda, passando de $25\text{ ms}$ para $50\text{ ms}$ (acréscimo de apenas $+25\text{ ms}$).
> 2. **Comportamento Explosivo na Região Crítica:** Quando a carga passa de $48.0$ para $49.9\text{ req/s}$ (uma variação sutil de apenas $+1.9\text{ req/s}$), a latência média sobe de **$500\text{ ms}$ para $10.000\text{ ms}$ ($10\text{ segundos}$)** — um aumento de $20\times$! O percentil de cauda $p99$ salta para estarrecedores **$46\text{ segundos}$**.
> 
> Essa observação numérica corrobora com absoluta exatidão o limite simbólico calculado $\lim_{x \to 50^-} f(x) = +\infty$. À medida que $x \to 50$, o denominador $(50 - x) \to 0^+$, resultando na divisão de uma constante finita por um valor infinitesimal, impulsionando a latência assintoticamente para o infinito.
"""))

    # -------------------------------------------------------------
    # Célula 9: Código - Gráfico Matplotlib / Seaborn
    # -------------------------------------------------------------
    nb['cells'].append(nbf.v4.new_code_cell(r"""# Geração do Gráfico Completo de Desempenho e Limites
plt.figure(figsize=(13, 7))

# Curva teórica contínua
x_curve = np.linspace(0, 49.85, 800)
y_curve = 1000.0 / (50.0 - x_curve)

# 1. Plotagem da curva teórica
plt.plot(x_curve, y_curve, color='#1E40AF', linewidth=2.5, label=r'Modelo Teórico: $f(x) = \frac{1000}{50 - x}$')

# 2. Plotagem dos pontos empíricos do teste de carga
cargas_emp = [10, 20, 30, 35, 40, 45, 48]
tempos_emp = [25, 33, 50, 67, 100, 200, 500]
plt.scatter(cargas_emp, tempos_emp, color='#DC2626', s=80, zorder=5, label='Dados do Teste de Carga Real')

# 3. Linhas de referência técnica
plt.axvline(x=50, color='#991B1B', linestyle='--', linewidth=2.2, label=r'Assíntota Vertical: $x = 50\text{ req/s}$ (Capacidade Limite)')
plt.axhline(y=200, color='#EA580C', linestyle=':', linewidth=2, label='SLA Máximo de Latência (200 ms)')

# 4. Zonas operacionais sombreadas
plt.axvspan(0, 35, color='green', alpha=0.08, label='Zona Segura (0 - 35 req/s)')
plt.axvspan(35, 45, color='yellow', alpha=0.12, label='Zona de Atenção (35 - 45 req/s)')
plt.axvspan(45, 50, color='red', alpha=0.10, label='Zona Crítica / Saturação (45 - 50 req/s)')

# 5. Anotações técnicas e destaques
plt.annotate('Latência Base: 20 ms\n(lim x->0+ f(x) = 20)', xy=(0, 20), xytext=(3, 140),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
             fontweight='bold', color='#1E3A8A')
plt.annotate('Colapso Assintótico\n(lim x->50- f(x) = +inf)', xy=(49.5, 1400), xytext=(27, 1600),
             arrowprops=dict(facecolor='red', shrink=0.05, width=1.5, headwidth=6),
             fontweight='bold', color='#991B1B')

# Configurações de eixos, títulos e unidades
plt.title('Desempenho da API vivoCloud: Tempo de Resposta vs. Carga de Requisições', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Taxa de Requisições (x em req/s)', fontsize=12, labelpad=10)
plt.ylabel('Tempo Médio de Resposta (f(x) em ms)', fontsize=12, labelpad=10)
plt.xlim(-1, 52)
plt.ylim(0, 2000)
plt.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
plt.tight_layout()
plt.show()
"""))

    # -------------------------------------------------------------
    # Célula 10: Critério 3.4 - Aplicação Interativa em Streamlit
    # -------------------------------------------------------------
    nb['cells'].append(nbf.v4.new_markdown_cell(r"""---

## 🌐 5. Aplicação Interativa em Streamlit (Critério 3.4 — 2,0 pontos)

Para capacitar gestores técnicos, arquitetos de software e engenheiros de confiabilidade (SRE) a explorarem interativamente o modelo, desenvolvemos a aplicação interativa **Streamlit** (`app.py`).

### 5.1. Recursos e Funcionalidades Implementadas
1. **Modos de Simulação:** Simulação em Nó Único ($1\text{ Pod}$) ou Cluster Escalável ($N\text{ Pods}$).
2. **Controle Interativo:** `st.slider()` e `st.number_input()` para controle fino de carga e parâmetros.
3. **Métricas Completas:** Exibição da Latência Média, Percentis de Cauda ($p95$, $p99$), Degradação e SLA.
4. **Tratamento de Falha / Modo Colapso:** Se $x \ge 50\text{ req/s}$, a aplicação simula o colapso visual do sistema (`HTTP 504 Gateway Timeout`).
5. **Calculadora de Dimensionamento de Pods:** Ferramenta interativa de *Capacity Planning* para dimensionar réplicas com base no pico de tráfego.

### 5.2. Comando para Execução Local
Abra o terminal no diretório do projeto e execute:
```bash
streamlit run app.py
```

---

> ### 📌 **Questão Obrigatória 3.4**
> **Pergunta:** *Como a aplicação transforma o resultado matemático em uma informação útil para uma pessoa responsável por operação, arquitetura ou infraestrutura de software?*  
> 
> **Resposta Fundamentada:** A aplicação Streamlit atua como uma **ponte direta entre a teoria matemática abstrata e a tomada de decisão operacional no mundo real**. Em vez de exigir que engenheiros resolvam equações diferenciais ou calculem limites manualmente, a ferramenta:
> 1. **Permite Simulação de Cenários (*What-If*):** O operador consegue testar instantaneamente o impacto de uma campanha de marketing (ex.: pico de tráfego de $120\text{ req/s}$) sobre a latência e a violação de SLA.
> 2. **Fornece Limiares Precisos de Alarme e Autoscaling:** Define com base em dados analíticos os gatilhos para disparo de alertas e criação de novas réplicas no Kubernetes antes que a saturação ocorra.
> 3. **Apoia o Planejamento de Capacidade (*Capacity Planning*):** Converte limites analíticos em custos de infraestrutura e dimensionamento seguro de pods e nós de computação.
"""))

    # -------------------------------------------------------------
    # Célula 11: Código - Geração física do arquivo app.py com %%writefile
    # -------------------------------------------------------------
    with open("app.py", "r", encoding="utf-8") as f_app:
        app_content = f_app.read()
    
    app_cell_source = "%%writefile app.py\n" + app_content
    nb['cells'].append(nbf.v4.new_code_cell(app_cell_source))

    # -------------------------------------------------------------
    # Célula 12: Critério 3.5 - Tomada de Decisão e Interpretação Técnica
    # -------------------------------------------------------------
    nb['cells'].append(nbf.v4.new_markdown_cell(r"""---

## 🏛️ 6. Notebook Técnico, Interpretação e Tomada de Decisão (Critério 3.5 — 2,0 pontos)

Com base nos resultados matemáticos, simulações, limites e derivadas, fundamentamos as seguintes decisões técnicas de engenharia de software:

### a) Comportamento Matemático que Caracteriza a Saturação
A saturação é caracterizada pela **divergência assintótica vertical** $\lim_{x \to 50^-} f(x) = +\infty$. A derivada primeira $f'(x) = \frac{1000}{(50 - x)^2} > 0$ e a derivada segunda $f''(x) = \frac{2000}{(50 - x)^3} > 0$ comprovam que a taxa de degradação da latência não apenas cresce, mas **acelera quadraticamente** conforme a carga se aproxima de $50\text{ req/s}$.

### b) Delimitação das Regiões Operacionais
- **Zona Segura:** $0 \le x \le 35\text{ req/s}$ (Utilização $\le 70\%$, latência média $\le 66.7\text{ ms}$, $p99 \le 307\text{ ms}$).
- **Zona de Atenção:** $35 < x \le 45\text{ req/s}$ (Utilização entre $70\%$ e $90\%$, latência média entre $66.7\text{ ms}$ e $200\text{ ms}$).
- **Zona Crítica / Colapso:** $45 < x < 50\text{ req/s}$ (Utilização $> 90\%$, latência $> 200\text{ ms}$ convergindo rapidamente para infinito).

### c) Análise de Risco: Operar Próximo da Capacidade Máxima
**Operar próximo da capacidade máxima ($\ge 45\text{ req/s}$) é uma estratégia inaceitável e de altíssimo risco.** Qualquer oscilação estocástica natural de tráfego empurrará o sistema para a zona de fila infinita, gerando falhas em cascata, bloqueio de *threads* e indisponibilidade generalizada.

### d) Diferença entre Capacidade Teórica e Capacidade Operacional Segura
- **Capacidade Teórica ($\mu = 50\text{ req/s}$):** Limite assintótico estrutural inatingível em regime contínuo de produção estável.
- **Capacidade Operacional Segura ($x_{\text{segura}} \le 35\text{ req/s}$):** Carga máxima recomendada em produção ($70\%$ da capacidade teórica), garantindo latências baixas ($< 67\text{ ms}$), cumprimento do SLA contratual e margem de segurança de $30\%$ para amortecer picos de tráfego.

### e) Recomendações Técnicas para a Equipe de Infraestrutura
1. **Autoscaling Horizontal (HPA - Kubernetes):** Provisionar réplicas adicionais automaticamente quando a taxa por pod atingir **$35\text{ req/s}$** ou a utilização de CPU ultrapassar $70\%$, utilizando a fórmula:
   $$N_{\text{pods}} = \left\lceil \frac{\lambda_{\text{pico}}}{35\text{ req/s}} \right\rceil$$
2. **Balanceamento de Carga (Load Balancing):** Configurar balanceadores (AWS ALB / NGINX) com o algoritmo *Least Connections* para evitar concentração de requisições.
3. **Rate Limiting & Throttling:** Implementar controle de taxa com retorno de status `HTTP 429 Too Many Requests` (algoritmo *Token Bucket* no Kong / AWS API Gateway) para descartar requisições excedentes.
4. **Camada de Cache Distribuído (Redis):** Armazenar em cache dados consultados repetidamente para aliviar a carga sobre a CPU da API principal.
5. **Mensageria e Filas Assíncronas:** Desacoplar operações pesadas de gravação na nuvem usando RabbitMQ, Apache Kafka ou AWS SQS.
6. **Circuit Breaker:** Implementar disjuntores lógicos (ex.: Resilience4j) para cortar chamadas e degradar o serviço graciosamente caso a latência exceda o SLA de $200\text{ ms}$.

### f) Limitações do Modelo e Próximos Passos
- **Limitações:** O modelo analítico $M/M/1$ assume tempo de processamento com distribuição exponencial e nós independentes sem dependências externas (como travas de banco de dados ou latência de rede externa).
- **Próximos Passos:** Realizar testes de estresse contínuos via **k6** ou **Locust** coletando percentis de latência (**p95**, **p99**) para modelar o comportamento de cauda (*tail latency*).

---

## 🎯 7. Conclusão Técnica
O modelo analítico $f(x) = \frac{1000}{50 - x}$ descreve com precisão cirúrgica o comportamento empírico observado e evidencia como o conceito matemático de limites é crucial para o planejamento de capacidade, arquitetura resiliente e engenharia de software de alta disponibilidade.
"""))

    # Execução do notebook
    print("Executando o notebook para preencher todas as saídas...")
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    ep.preprocess(nb, {'metadata': {'path': '.'}})

    output_path = "checkpoint.ipynb"
    with open(output_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Notebook {output_path} executado e salvo com sucesso com 100% de saídas e gráficos!")

if __name__ == "__main__":
    create_and_execute_notebook()
