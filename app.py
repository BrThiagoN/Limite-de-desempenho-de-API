import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# Configurações da Página Streamlit
# ==========================================
st.set_page_config(
    page_title="Simulador de Desempenho de API | DPS FIAP",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .status-badge-safe {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
    }
    .status-badge-warn {
        background-color: #FEF08A;
        color: #854D0E;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
    }
    .status-badge-crit {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
    }
    .status-badge-fatal {
        background-color: #7F1D1D;
        color: #FFFFFF;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# Constantes e Funções do Modelo Matemático
# ==========================================
CAPACIDADE_NODO = 50.0  # req/s por réplica
K_FATOR = 1000.0        # ms * req/s

def calcular_tempo_resposta(x: float, num_replicas: int = 1) -> float:
    """
    Calcula o tempo médio de resposta f(x) = 1000 / (50 - x/N) em ms.
    Para x/N >= 50, retorna infinito (saturação/colapso).
    """
    carga_por_pod = x / num_replicas
    if carga_por_pod >= CAPACIDADE_NODO:
        return float('inf')
    return K_FATOR / (CAPACIDADE_NODO - carga_por_pod)

def calcular_percentil_latencia(latencia_media: float, percentil: float) -> float:
    """
    Calcula percentis de latência para distribuição exponencial M/M/1:
    T_p = -latencia_media * ln(1 - p)
    """
    if latencia_media == float('inf'):
        return float('inf')
    p = percentil / 100.0
    return -latencia_media * np.log(1.0 - p)

# Dados empíricos coletados no teste de carga
dados_empiricos = pd.DataFrame({
    'Carga (req/s)': [10, 20, 30, 35, 40, 45, 48],
    'Tempo Medido (ms)': [25, 33, 50, 67, 100, 200, 500]
})

# ==========================================
# Barra Lateral (Controles e Parâmetros)
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="background-color: #1E3A8A; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; text-align: center; margin-bottom: 15px;">
        🎓 FIAP — DPS Checkpoint 4 (2026)
    </div>
    """, unsafe_allow_html=True)

    st.title("⚙️ Parâmetros de Simulação")
    st.markdown("Ajuste a carga simulada e os parâmetros de infraestrutura.")

    modo_simulacao = st.radio(
        "Modo de Simulação:",
        ["Nó Único (Monolítico / 1 Pod)", "Cluster Escalável (Multi-Pod / HPA)"],
        index=0
    )

    if modo_simulacao == "Nó Único (Monolítico / 1 Pod)":
        num_pods = 1
        st.subheader("1. Carga de Entrada ($x$)")
        carga_selecionada = st.slider(
            "Taxa de Requisições por Segundo (req/s):",
            min_value=0.0,
            max_value=52.0,
            value=30.0,
            step=0.1,
            help="Cargas >= 50 req/s ultrapassam a assíntota e provocam colapso operacional."
        )
    else:
        st.subheader("1. Dimensionamento do Cluster")
        num_pods = st.number_input("Quantidade de Réplicas (Pods):", min_value=1, max_value=10, value=2, step=1)
        capacidade_total = num_pods * CAPACIDADE_NODO
        st.caption(f"Capacidade Teórica Total do Cluster: **{capacidade_total:.0f} req/s**")

        st.subheader("2. Carga Global de Entrada ($x$)")
        carga_selecionada = st.slider(
            "Taxa de Requisições Globais (req/s):",
            min_value=0.0,
            max_value=float(capacidade_total + 10.0),
            value=float(num_pods * 30.0),
            step=0.5
        )

    st.subheader("3. Acordo de Nível de Serviço (SLA)")
    sla_limite = st.number_input(
        "SLA Máximo de Latência (ms):",
        min_value=30,
        max_value=2000,
        value=200,
        step=10,
        help="Limite contratual de latência média tolerada pela aplicação."
    )

    st.divider()
    st.markdown("### 📌 Contexto da Empresa")
    st.markdown(r"""
    **API:** *vivoCloud Storage Service*  
    **Empresa:** JOVI (Vivo)  
    **Capacidade Teórica ($\mu$):** $50\text{ req/s / pod}$  
    **Latência em Repouso ($f(0)$):** $20\text{ ms}$
    """)

    st.divider()
    st.markdown("### 👥 Integrantes do Grupo")
    st.markdown("""
    - **Thiago Gomes Nascimento** (RM 569436)
    - **Gabriel Henrique Ongarelli Reis** (RM 572636)
    - **Vinicius Scalone Ramires** (RM 573783)
    - **Matheus de Amorim Brito** (RM 572435)
    - **Eduardo Felix Frois Silva** (RM 574103)
    - **Lucas Rodrigues dos Santos** (RM 571778)
    """)

# ==========================================
# Processamento dos Cálculos em Tempo Real
# ==========================================
carga_efetiva_pod = carga_selecionada / num_pods
tempo_calculado = calcular_tempo_resposta(carga_selecionada, num_pods)
utilizacao = (carga_efetiva_pod / CAPACIDADE_NODO) * 100.0
latencia_base = 20.0  # f(0) = 20 ms

if tempo_calculado != float('inf'):
    p95_calculado = calcular_percentil_latencia(tempo_calculado, 95.0)
    p99_calculado = calcular_percentil_latencia(tempo_calculado, 99.0)
    degradacao = ((tempo_calculado - latencia_base) / latencia_base) * 100.0
else:
    p95_calculado = float('inf')
    p99_calculado = float('inf')
    degradacao = float('inf')

# Determinação do Status Operacional
if carga_efetiva_pod >= CAPACIDADE_NODO:
    zona_nome = "💥 COLAPSO OPERACIONAL (HTTP 504 / Fila Infinita)"
    zona_classe = "status-badge-fatal"
    zona_msg = "A carga ultrapassou a capacidade do hardware! O sistema está indisponível com 100% de perda de pacotes."
elif carga_efetiva_pod >= 45.0:
    zona_nome = "🔴 Zona Crítica (Risco Severo de Saturação)"
    zona_classe = "status-badge-crit"
    zona_msg = "Utilização > 90%. Fila de espera explodindo! Timeouts iminentes."
elif carga_efetiva_pod >= 35.0:
    zona_nome = "🟡 Zona de Atenção (Degradação Não-Linear)"
    zona_classe = "status-badge-warn"
    zona_msg = "Utilização entre 70% e 90%. Latência sensível a pequenas variações de carga."
else:
    zona_nome = "🟢 Zona Segura (Operação Estável)"
    zona_classe = "status-badge-safe"
    zona_msg = "Operação normal com folga de processamento e latência sob controle."

# ==========================================
# Cabeçalho Principal
# ==========================================
st.markdown('<div class="main-header">⚡ Análise de Desempenho & Saturação de API</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Modelagem Matemática, Teoria de Limites, Percentis de Cauda e Apoio à Tomada de Decisão em Engenharia de Software</div>', unsafe_allow_html=True)

# Exibição de Métricas no Topo
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="⚡ Carga Simulada (Global / Por Pod)",
        value=f"{carga_selecionada:.1f} req/s" if num_pods == 1 else f"{carga_selecionada:.1f} req/s ({carga_efetiva_pod:.1f}/pod)",
        delta=f"{utilizacao:.1f}% da capacidade" if utilizacao <= 100 else "SOBRECARGA (>100%)",
        delta_color="normal" if utilizacao <= 70 else "inverse"
    )

with col2:
    if tempo_calculado == float('inf'):
        st.metric(label="⏱️ Latência Média Prevista", value="∞ ms (Colapso)", delta="Saturação Total", delta_color="inverse")
    else:
        st.metric(
            label="⏱️ Latência Média Prevista",
            value=f"{tempo_calculado:.1f} ms",
            delta=f"+{degradacao:.1f}% vs repouso",
            delta_color="inverse"
        )

with col3:
    if p99_calculado == float('inf'):
        st.metric(label="📊 Latência de Cauda (p99)", value="∞ ms", delta="Timeout Geral", delta_color="inverse")
    else:
        st.metric(
            label="📊 Latência de Cauda (p99)",
            value=f"{p99_calculado:.1f} ms",
            delta=f"p95: {p95_calculado:.1f} ms",
            delta_color="inverse" if p99_calculado > sla_limite else "normal"
        )

with col4:
    st.markdown("**Status Operacional:**")
    st.markdown(f'<div class="{zona_classe}">{zona_nome}</div>', unsafe_allow_html=True)
    if tempo_calculado == float('inf') or tempo_calculado > sla_limite:
        st.error(f"❌ **SLA Violado!** ({'∞' if tempo_calculado == float('inf') else f'{tempo_calculado:.1f}'} ms > {sla_limite} ms)")
    else:
        st.success(f"✅ **SLA Cumprido** ({tempo_calculado:.1f} ms ≤ {sla_limite} ms)")

st.divider()

# ==========================================
# Abas de Conteúdo
# ==========================================
tab_sim, tab_math, tab_table, tab_arch = st.tabs([
    "📊 Simulador & Gráfico Interativo",
    "🧮 Fundamentação Matemática & Derivadas",
    "📋 Tabela Numérica & Percentis",
    "🏗️ Engenharia de Software & Dimensionamento"
])

# ----------------------------------------------------
# ABA 1: Simulador & Gráfico
# ----------------------------------------------------
with tab_sim:
    st.subheader("Comportamento do Tempo de Resposta vs. Carga de Requisições")

    cap_max_total = num_pods * CAPACIDADE_NODO
    x_max_plot = cap_max_total - 0.15
    x_vals = np.linspace(0, x_max_plot, 600)
    y_vals = K_FATOR / (CAPACIDADE_NODO - (x_vals / num_pods))

    fig = go.Figure()

    # Zonas de operação sombreadas
    fig.add_vrect(x0=0, x1=35.0 * num_pods, fillcolor="rgba(34, 197, 94, 0.12)", layer="below", line_width=0,
                  annotation_text=f"Zona Segura (0 - {35*num_pods:.0f} req/s)", annotation_position="top left")
    fig.add_vrect(x0=35.0 * num_pods, x1=45.0 * num_pods, fillcolor="rgba(234, 179, 8, 0.12)", layer="below", line_width=0,
                  annotation_text=f"Zona de Atenção ({35*num_pods:.0f} - {45*num_pods:.0f} req/s)", annotation_position="top left")
    fig.add_vrect(x0=45.0 * num_pods, x1=cap_max_total, fillcolor="rgba(239, 68, 68, 0.15)", layer="below", line_width=0,
                  annotation_text=f"Zona Crítica ({45*num_pods:.0f} - {cap_max_total:.0f} req/s)", annotation_position="top left")

    # Curva teórica f(x)
    nome_curva = f'Modelo Teórico ({num_pods} Pods): f(x) = 1000 / (50 - x/{num_pods})' if num_pods > 1 else 'Modelo Teórico: f(x) = 1000 / (50 - x)'
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines',
        name=nome_curva,
        line=dict(color='#2563EB', width=3)
    ))

    # Pontos empíricos (para 1 pod)
    if num_pods == 1:
        fig.add_trace(go.Scatter(
            x=dados_empiricos['Carga (req/s)'],
            y=dados_empiricos['Tempo Medido (ms)'],
            mode='markers',
            name='Dados do Teste de Carga Real',
            marker=dict(color='#DC2626', size=9, symbol='diamond')
        ))

    # Linha de SLA
    fig.add_hline(
        y=sla_limite,
        line_dash="dash",
        line_color="#EA580C",
        annotation_text=f"SLA Alvo = {sla_limite} ms",
        annotation_position="bottom right"
    )

    # Assíntota vertical
    fig.add_vline(
        x=cap_max_total,
        line_dash="dot",
        line_color="#991B1B",
        line_width=2.5,
        annotation_text=f"Assíntota Vertical x = {cap_max_total:.0f} req/s",
        annotation_position="top right"
    )

    # Ponto atual simulado
    if tempo_calculado != float('inf'):
        fig.add_trace(go.Scatter(
            x=[carga_selecionada],
            y=[tempo_calculado],
            mode='markers+text',
            name='Carga Atual Simulada',
            text=[f"({carga_selecionada:.1f} req/s, {tempo_calculado:.1f} ms)"],
            textposition="top left",
            marker=dict(color='#7C3AED', size=14, symbol='circle')
        ))

    y_max_view = min(max((tempo_calculado if tempo_calculado != float('inf') else 1000) * 1.5, 600), 3000)
    fig.update_layout(
        title=f"Curva de Latência e Comportamento Assintótico ({num_pods} Pod{'s' if num_pods > 1 else ''})",
        xaxis_title="Carga de Requisições (x em req/s)",
        yaxis_title="Tempo Médio de Resposta (f(x) em ms)",
        yaxis=dict(range=[0, y_max_view]),
        xaxis=dict(range=[0, cap_max_total + (2.0 if num_pods == 1 else 10.0)]),
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02),
        margin=dict(l=40, r=40, t=60, b=40),
        height=540
    )

    st.plotly_chart(fig, use_container_width=True)

    # Análise textual do ponto
    if tempo_calculado == float('inf'):
        st.error(f"🚨 **ALERTA DE SISTEMA DOWN:** A carga de **{carga_selecionada:.1f} req/s** excede a barreira assintótica de **{cap_max_total:.0f} req/s**. Todos os clientes receberão erro `HTTP 504 Gateway Timeout`.")
    else:
        st.markdown(f"""
        > **🔍 Diagnóstico Operacional:** Para **{carga_selecionada:.1f} req/s** distribuídos em **{num_pods} réplica(s)** ({carga_efetiva_pod:.1f} req/s/pod), a latência média estimada é de **{tempo_calculado:.2f} ms** (com **p95 = {p95_calculado:.2f} ms** e **p99 = {p99_calculado:.2f} ms**).  
        > Utilização do cluster: **{utilizacao:.1f}%**. {zona_msg}
        """)

# ----------------------------------------------------
# ABA 2: Fundamentação Matemática & Derivadas
# ----------------------------------------------------
with tab_math:
    st.subheader("Modelagem Matemática Rigorosa, Limites e Cálculo Diferencial")

    st.markdown(r"""
    ### 1. Definição Formal da Função Racional
    Com base na **Teoria de Filas (Modelo $M/M/1$)**, o tempo de resposta médio $f(x)$ para uma taxa de chegada $\lambda = x$ e taxa de serviço $\mu = 50\text{ req/s}$ é dado por:

    $$f(x) = \frac{1000}{50 - x}$$

    - **Variável Independente ($x$):** Taxa de requisições que chegam à API por segundo ($\text{req/s}$).
    - **Variável Dependente ($f(x)$):** Tempo médio de resposta / latência ($\text{ms}$).
    - **Domínio Matemático:** $\text{Dom}(f) = \{x \in \mathbb{R} \mid x \neq 50\}$.
    - **Domínio Operacional Válido:** $x \in [0, 50)\text{ req/s}$.

    ---

    ### 2. Estudo dos Limites Fundamentais

    | Limite Simbólico | Resultado | Classificação | Significado Físico / Computacional |
    | :--- | :---: | :---: | :--- |
    | $\lim_{x \to 0^+} \frac{1000}{50 - x}$ | **$20\text{ ms}$** | **Finito** | **Latência em Repouso:** Overhead de rede e tempo de CPU de uma requisição isolada sem concorrência. |
    | $\lim_{x \to 50^-} \frac{1000}{50 - x}$ | **$+\infty$** | **Infinito Positivo** | **Colapso Assintótico:** Esgotamento de threads, fila de espera infinita e estouro de timeouts. |
    | $\lim_{x \to 50^+} \frac{1000}{50 - x}$ | **$-\infty$** | **Infinito Negativo** | Região matematicamente existente, mas **sem sentido operacional** (não existe latência negativa). |
    | $\lim_{x \to 50} \frac{1000}{50 - x}$ | **$\nexists$** | **Inexistente** | Descontinuidade infinita essencial: o sistema não pode operar em $x=50$. |
    | $\lim_{x \to +\infty} \frac{1000}{50 - x}$ | **$0$** | **Finito** | Assíntota horizontal puramente algébrica. |

    ---

    ### 3. Cálculo Diferencial: Taxa de Variação e Aceleração da Degradação

    - **Derivada Primeira (Taxa de Crescimento da Latência):**
      $$f'(x) = \frac{d}{dx}\left[1000(50 - x)^{-1}\right] = \frac{1000}{(50 - x)^2} > 0 \quad \forall x \in [0, 50)$$
      *Significado:* A latência é **estritamente crescente**. Para $x=10$, $f'(10) = 0.625\text{ ms/(req/s)}$, enquanto para $x=48$, $f'(48) = 250\text{ ms/(req/s)}$ ($400\times$ mais sensível!).

    - **Derivada Segunda (Aceleração da Degradação / Convexidade):**
      $$f''(x) = \frac{d^2}{dx^2}f(x) = \frac{2000}{(50 - x)^3} > 0 \quad \forall x \in [0, 50)$$
      *Significado:* A função é **estritamente convexa**, comprovando que a degradação acelera de forma hiperbólica conforme a carga aumenta.

    ---

    ### 4. Percentis de Latência de Cauda (*Tail Latency*)
    Em regimes de fila estocástica $M/M/1$, a distribuição do tempo de permanência é exponencial: $P(T \le t) = 1 - e^{-(\mu - \lambda) t}$.  
    Portanto, os percentis de cauda são múltiplos diretos da média:
    - **$p50$ (Mediana):** $t_{50} = f(x) \cdot \ln(2) \approx 0.693 \cdot f(x)$
    - **$p95$:** $t_{95} = f(x) \cdot \ln(20) \approx 2.996 \cdot f(x)$
    - **$p99$:** $t_{99} = f(x) \cdot \ln(100) \approx 4.605 \cdot f(x)$

    > **⚠️ Lição Arquitetural:** Mesmo quando a média é de $100\text{ ms}$ ($x=40\text{ req/s}$), $1\%$ dos usuários mais lentos (**p99**) já experimentam **$460\text{ ms}$** de espera!
    """)

# ----------------------------------------------------
# ABA 3: Tabela Numérica & Percentis
# ----------------------------------------------------
with tab_table:
    st.subheader("Resultados Computacionais e Análise Multicritério de Carga")
    st.markdown("Validação numérica obrigatória para as cargas de teste solicitadas no enunciado:")

    cargas_simuladas = [10.0, 20.0, 30.0, 35.0, 40.0, 45.0, 48.0, 49.0, 49.5, 49.9]
    tabela_dados = []

    for c in cargas_simuladas:
        t_med = calcular_tempo_resposta(c, 1)
        p95 = calcular_percentil_latencia(t_med, 95.0)
        p99 = calcular_percentil_latencia(t_med, 99.0)
        ut = (c / 50.0) * 100.0

        if c < 35:
            stt = "🟢 Segura"
        elif c < 45:
            stt = "🟡 Atenção"
        else:
            stt = "🔴 Crítica"

        tabela_dados.append({
            "Carga (req/s)": f"{c:.1f}",
            "Denominador (50 - x)": f"{50 - c:.1f}",
            "Latência Média (ms)": f"{t_med:.2f} ms",
            "p95 (ms)": f"{p95:.2f} ms",
            "p99 (ms)": f"{p99:.2f} ms",
            "Utilização (%)": f"{ut:.1f}%",
            "Fator vs Repouso": f"{t_med / 20.0:.1f}x",
            "Zona": stt
        })

    df_resultado = pd.DataFrame(tabela_dados)
    st.dataframe(df_resultado, use_container_width=True)

    st.markdown(r"""
    **💡 Destaque Analítico:** Note como uma variação de apenas $+0.9\text{ req/s}$ (de $49.0$ para $49.9\text{ req/s}$) faz a latência média saltar de **$1.000\text{ ms}$** para **$10.000\text{ ms}$** ($10\text{ segundos}$), e o **p99** atingir **$46\text{ segundos}$**!
    """)

# ----------------------------------------------------
# ABA 4: Engenharia de Software & Dimensionamento
# ----------------------------------------------------
with tab_arch:
    st.subheader("Calculadora de Capacidade & Recomendações de Arquitetura")

    st.markdown("### 🧮 Calculadora de Dimensionamento de Pods (Capacity Planning)")
    col_calc1, col_calc2 = st.columns(2)

    with col_calc1:
        pico_esperado = st.number_input("Pico de Tráfego Previsto (req/s total):", min_value=10, max_value=5000, value=150, step=10)
        limite_seguro_pod = st.number_input("Carga Máxima Segura por Pod (req/s):", min_value=10, max_value=45, value=35, step=5)

    with col_calc2:
        pods_necessarios = int(np.ceil(pico_esperado / limite_seguro_pod))
        capacidade_cluster = pods_necessarios * 50
        carga_por_pod_calculada = pico_esperado / pods_necessarios
        latencia_estimada_calc = calcular_tempo_resposta(pico_esperado, pods_necessarios)

        st.markdown(f"""
        <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 15px;">
            <h4 style="margin: 0; color: #1E40AF;">📋 Resultado do Dimensionamento:</h4>
            <p style="margin: 5px 0 0 0; font-size: 1.1rem;"><strong>Pods Recomendados no Kubernetes:</strong> <span style="color: #2563EB; font-size: 1.3rem; font-weight: bold;">{pods_necessarios} réplicas</span></p>
            <p style="margin: 3px 0 0 0; font-size: 0.95rem;">• Carga balanceada por réplica: <strong>{carga_por_pod_calculada:.1f} req/s</strong> (Utilização: {carga_por_pod_calculada/50*100:.1f}%)</p>
            <p style="margin: 3px 0 0 0; font-size: 0.95rem;">• Latência média esperada sob pico: <strong>{latencia_estimada_calc:.1f} ms</strong> (SLA cumprido)</p>
            <p style="margin: 3px 0 0 0; font-size: 0.95rem;">• Capacidade máxima teórica do cluster: <strong>{capacidade_cluster} req/s</strong></p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(r"""
        ### 🛡️ 1. Governança de Tráfego & Resiliência
        - **Rate Limiting (HTTP 429):** Bloquear tráfego excedente via API Gateway (*Token Bucket*) quando $x > 35\text{ req/s}$ por nó.
        - **Circuit Breaker:** Abrir o circuito para proteger bancos de dados e serviços dependentes caso a latência exceda $200\text{ ms}$.
        - **Filas Assíncronas (Kafka / SQS):** Desacoplar operações pesadas de I/O em filas de background.
        """)

    with col_b:
        st.markdown(r"""
        ### 🚀 2. Escalabilidade & Otimização
        - **HPA no Kubernetes:** Escalar pods com base em $70\%$ de CPU ou métrica personalizada de $35\text{ req/s}$ por pod.
        - **Balanceamento Least Connections:** Distribuir conexões TCP uniformemente entre as réplicas ativas.
        - **Cache Redis:** Absorver leituras repetidas na camada intermediária antes de atingir a API.
        """)

# ==========================================
# Rodapé
# ==========================================
st.divider()
st.markdown("""
<div style="text-align: center; color: #4B5563; font-size: 0.95rem; margin-bottom: 8px;">
    <strong>👥 Integrantes do Grupo:</strong><br>
    Thiago Gomes Nascimento (RM 569436) • Gabriel Henrique Ongarelli Reis (RM 572636) • Vinicius Scalone Ramires (RM 573783)<br>
    Matheus de Amorim Brito (RM 572435) • Eduardo Felix Frois Silva (RM 574103) • Lucas Rodrigues dos Santos (RM 571778)
</div>
<div style="text-align: center; color: #6B7280; font-size: 0.85rem;">
    <strong>DPS — Differentiated Problem Solving</strong> | Checkpoint 4 — Modelagem Matemática & Streamlit | <strong>FIAP 2026</strong> | Prof. Jones Egydio
</div>
""", unsafe_allow_html=True)
