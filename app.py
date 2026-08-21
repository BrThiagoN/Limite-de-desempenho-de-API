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
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .status-badge-safe {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .status-badge-warn {
        background-color: #FEF08A;
        color: #854D0E;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
    .status-badge-crit {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# Modelo Matemático
# ==========================================
CAPACIDADE_MAXIMA = 50.0  # req/s (Assíntota vertical)
K_FATOR = 1000.0          # ms * req/s

def calcular_tempo_resposta(x: float) -> float:
    """Calcula o tempo de resposta f(x) = 1000 / (50 - x) em milissegundos."""
    if x >= CAPACIDADE_MAXIMA:
        return float('inf')
    return K_FATOR / (CAPACIDADE_MAXIMA - x)

# Dados empíricos coletados no teste de carga
dados_empiricos = pd.DataFrame({
    'Carga (req/s)': [10, 20, 30, 35, 40, 45, 48],
    'Tempo Medido (ms)': [25, 33, 50, 67, 100, 200, 500]
})

# ==========================================
# Barra Lateral (Controles e Parâmetros)
# ==========================================
with st.sidebar:
    st.image("https://img.shields.io/badge/FIAP-DPS%20Checkpoint%204-blue?style=for-the-badge", width='stretch')
    st.title("⚙️ Parâmetros da API")
    st.markdown("Ajuste a carga simulada e os parâmetros de infraestrutura.")
    
    st.subheader("1. Carga de Entrada ($x$)")
    carga_selecionada = st.slider(
        "Taxa de Requisições (req/s):",
        min_value=0.0,
        max_value=49.9,
        value=30.0,
        step=0.1,
        help="Taxa de requisições por segundo direcionadas ao endpoint da API."
    )
    
    st.subheader("2. Parâmetros de SLA")
    sla_limite = st.number_input(
        "SLA Máximo de Latência (ms):",
        min_value=30,
        max_value=2000,
        value=200,
        step=10,
        help="Acordo de Nível de Serviço (SLA) para o tempo médio de resposta."
    )
    
    st.divider()
    st.markdown("### 📌 Contexto da Empresa")
    st.markdown("""
    **API:** *vivoCloud Storage Service*  
    **Empresa:** JOVI (Vivo)  
    **Capacidade Teórica ($\mu$):** $50\\text{ req/s}$  
    **Latência em Repouso ($f(0)$):** $20\\text{ ms}$
    """)
    
    st.divider()
    st.markdown("### 👥 Integrantes")
    st.markdown("""
    - **Thiago Gomes Nascimento** (RM 569436)
    - **Gabriel Henrique Ongarelli Reis** (RM 572636)
    - **Vinicius Scalone Ramires** (RM 573783)
    - **Matheus de Amorim Brito** (RM 572435)
    - **Eduardo Felix Frois Silva** (RM 574103)
    """)
    
    st.info("💡 **Dica Técnica:** O colapso assintótico ocorre em $x \\to 50^-$, onde a fila cresce infinitamente.")

# ==========================================
# Cabeçalho Principal
# ==========================================
st.markdown('<div class="main-header">⚡ Análise de Desempenho & Saturação de API</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Modelagem Matemática, Análise Assintótica por Limites e Apoio à Tomada de Decisão em Engenharia de Software</div>', unsafe_allow_html=True)

# Cálculo em tempo real
tempo_calculado = calcular_tempo_resposta(carga_selecionada)
utilizacao = (carga_selecionada / CAPACIDADE_MAXIMA) * 100.0
latencia_base = calcular_tempo_resposta(0.0) # 20 ms
degradacao = ((tempo_calculado - latencia_base) / latencia_base) * 100.0

# Classificação de Zona
if carga_selecionada < 35.0:
    zona_nome = "🟢 Zona Segura (Operação Estável)"
    zona_classe = "status-badge-safe"
    zona_msg = "O sistema opera com folga de recursos. Tempo de resposta sob controle."
elif carga_selecionada < 45.0:
    zona_nome = "🟡 Zona de Atenção (Degradação Moderada)"
    zona_classe = "status-badge-warn"
    zona_msg = "Utilização elevada. Recomenda-se acionar autoscaling preventivo."
else:
    zona_nome = "🔴 Zona Crítica (Risco de Colapso / Saturação)"
    zona_classe = "status-badge-crit"
    zona_msg = "Perigo iminente de esgotamento de threads, fila infinita e timeout de clientes!"

# Exibição de Métricas no Topo
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="⚡ Carga Atual Selecionada",
        value=f"{carga_selecionada:.1f} req/s",
        delta=f"{utilizacao:.1f}% da capacidade"
    )

with col2:
    st.metric(
        label="⏱️ Tempo Médio de Resposta",
        value=f"{tempo_calculado:.1f} ms",
        delta=f"+{degradacao:.1f}% vs repouso",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="🎯 Limite de SLA Definido",
        value=f"{sla_limite} ms",
        delta="Margem: " + (f"{sla_limite - tempo_calculado:.1f} ms" if tempo_calculado <= sla_limite else f"Violado em {tempo_calculado - sla_limite:.1f} ms"),
        delta_color="normal" if tempo_calculado <= sla_limite else "inverse"
    )

with col4:
    st.markdown(f"**Status Operacional:**")
    st.markdown(f'<div class="{zona_classe}">{zona_nome}</div>', unsafe_allow_html=True)
    if tempo_calculado > sla_limite:
        st.error(f"❌ **SLA Violado!** ({tempo_calculado:.1f} ms > {sla_limite} ms)")
    else:
        st.success(f"✅ **SLA Cumprido** ({tempo_calculado:.1f} ms ≤ {sla_limite} ms)")

st.divider()

# ==========================================
# Abas de Conteúdo
# ==========================================
tab_sim, tab_math, tab_table, tab_arch = st.tabs([
    "📊 Simulador & Gráfico Interativo",
    "🧮 Fundamentação Matemática & Limites",
    "📋 Tabela de Simulação de Carga",
    "🏗️ Decisão Técnica & Arquitetura"
])

# ----------------------------------------------------
# ABA 1: Simulador & Gráfico
# ----------------------------------------------------
with tab_sim:
    st.subheader("Comportamento do Tempo de Resposta vs. Carga de Requisições")
    
    # Gerando curva analítica
    x_vals = np.linspace(0, 49.85, 500)
    y_vals = K_FATOR / (CAPACIDADE_MAXIMA - x_vals)
    
    fig = go.Figure()
    
    # Faixas de operação (Zonas de Risco)
    fig.add_vrect(x0=0, x1=35, fillcolor="rgba(34, 197, 94, 0.12)", layer="below", line_width=0,
                  annotation_text="Zona Segura (0 - 35 req/s)", annotation_position="top left")
    fig.add_vrect(x0=35, x1=45, fillcolor="rgba(234, 179, 8, 0.12)", layer="below", line_width=0,
                  annotation_text="Zona de Atenção (35 - 45 req/s)", annotation_position="top left")
    fig.add_vrect(x0=45, x1=50, fillcolor="rgba(239, 68, 68, 0.15)", layer="below", line_width=0,
                  annotation_text="Zona Crítica (45 - 50 req/s)", annotation_position="top left")
    
    # Curva teórica f(x)
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines',
        name='Modelo Teórico: f(x) = 1000 / (50 - x)',
        line=dict(color='#2563EB', width=3)
    ))
    
    # Pontos empíricos observados
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
    
    # Assíntota vertical x = 50
    fig.add_vline(
        x=50,
        line_dash="dot",
        line_color="#991B1B",
        line_width=2.5,
        annotation_text="Assíntota Vertical x = 50 req/s (Capacidade Limite)",
        annotation_position="top right"
    )
    
    # Ponto atual selecionado
    fig.add_trace(go.Scatter(
        x=[carga_selecionada],
        y=[tempo_calculado],
        mode='markers+text',
        name='Carga Atual Simulada',
        text=[f"({carga_selecionada:.1f} req/s, {tempo_calculado:.1f} ms)"],
        textposition="top left",
        marker=dict(color='#7C3AED', size=14, symbol='circle')
    ))
    
    fig.update_layout(
        title="Curva de Latência e Comportamento Assintótico da API",
        xaxis_title="Carga de Requisições (x em req/s)",
        yaxis_title="Tempo Médio de Resposta (f(x) em ms)",
        yaxis=dict(range=[0, min(max(tempo_calculado * 1.5, 600), 2500)]),
        xaxis=dict(range=[0, 52]),
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02),
        margin=dict(l=40, r=40, t=60, b=40),
        height=550
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # Caixa explicativa da simulação
    st.markdown(f"""
    > **🔍 Análise do Ponto Atual:** Para uma taxa de **{carga_selecionada:.1f} req/s**, o tempo médio previsto de resposta é de **{tempo_calculado:.2f} ms**.  
    > O sistema está operando a **{utilizacao:.1f}%** de sua capacidade máxima teórica. {zona_msg}
    """)

# ----------------------------------------------------
# ABA 2: Fundamentação Matemática & Limites
# ----------------------------------------------------
with tab_math:
    st.subheader("Modelagem Matemática e Teoria de Limites")
    
    st.markdown(r"""
    ### 1. Definição Formal da Função
    A latência do sistema sob regime de filas com capacidade finita $\mu = 50\text{ req/s}$ é descrita pela função racional:
    
    $$f(x) = \frac{1000}{50 - x}$$
    
    - **Variável Independente ($x$):** Taxa de requisições que chegam à API por segundo ($\text{req/s}$).
    - **Variável Dependente ($f(x)$):** Tempo médio de resposta / latência ($\text{ms}$).
    - **Domínio Matemático:** $\text{Dom}(f) = \{x \in \mathbb{R} \mid x \neq 50\}$.
    - **Domínio Operacional Válido:** $x \in [0, 50)\text{ req/s}$ (cargas negativas não existem e $x \ge 50$ causa colapso total da infraestrutura).
    
    ---
    
    ### 2. Análise dos Limites Principais
    
    #### a) Latência em Repouso (Carga Zero / Baseline)
    $$\lim_{x \to 0^+} \frac{1000}{50 - x} = \frac{1000}{50} = 20\text{ ms}$$
    *Significado Operacional:* Representa o tempo intrínseco de processamento de uma requisição isolada sem concorrência ou contenção de recursos.
    
    #### b) Comportamento de Saturação (Aproximação pela Esquerda)
    $$\lim_{x \to 50^-} \frac{1000}{50 - x} = \frac{1000}{0^+} = +\infty$$
    *Significado Operacional:* Conforme a taxa de requisições se aproxima da capacidade máxima de processamento, a fila de espera e o tempo de resposta tendem ao infinito. Na prática, a API trava, estoura timeouts e para de responder.
    
    #### c) Limite Lateral pela Direita (Região Inacessível)
    $$\lim_{x \to 50^+} \frac{1000}{50 - x} = \frac{1000}{0^-} = -\infty$$
    *Significado Operacional:* Embora algebricamente resulte em $-\infty$, esse valor **não possui sentido físico/computacional**, pois não existe tempo de resposta negativo.
    
    ---
    
    ### 3. Assíntota Vertical e Descontinuidade
    A reta **$x = 50$** é uma **assíntota vertical**, caracterizando uma descontinuidade infinita (não-removível).
    - **Significado Técnico em Engenharia de Software:** A assíntota vertical demarca o limite intransponível de *throughput* do nó. Ela prova matematicamente que o sistema **jamais** pode operar estavelmente em $x = 50\text{ req/s}$.
    """)

# ----------------------------------------------------
# ABA 3: Tabela de Simulação de Carga
# ----------------------------------------------------
with tab_table:
    st.subheader("Resultados Computacionais para Cargas Críticas")
    st.markdown("Simulação numérica obrigatória demonstrando o crescimento hiperbólico da latência:")
    
    cargas_simuladas = [10.0, 20.0, 30.0, 40.0, 45.0, 48.0, 49.0, 49.5, 49.9]
    tabela_dados = []
    
    for c in cargas_simuladas:
        t = calcular_tempo_resposta(c)
        ut = (c / CAPACIDADE_MAXIMA) * 100.0
        
        if c < 35:
            stt = "🟢 Operação Segura"
        elif c < 45:
            stt = "🟡 Atenção / Degradação"
        else:
            stt = "🔴 Crítico / Quase Saturação"
            
        tabela_dados.append({
            "Carga (req/s)": f"{c:.1f}",
            "Denominador (50 - x)": f"{50 - c:.1f}",
            "Tempo Calculado f(x) (ms)": f"{t:.2f} ms",
            "Utilização (%)": f"{ut:.1f}%",
            "Fator de Aumento vs Repouso": f"{t / 20.0:.1f}x",
            "Status Operacional": stt
        })
        
    df_resultado = pd.DataFrame(tabela_dados)
    st.dataframe(df_resultado, width='stretch')
    
    st.markdown("""
    **💡 Observação Chave:** Note como a variação de $48.0$ para $49.9\\text{ req/s}$ (apenas $+1.9\\text{ req/s}$) faz a latência saltar de **500 ms** para **10.000 ms** ($10\\text{ segundos}$)! 
    Isso evidencia a natureza não-linear e explosiva da curva assintótica.
    """)

# ----------------------------------------------------
# ABA 4: Tomada de Decisão & Arquitetura
# ----------------------------------------------------
with tab_arch:
    st.subheader("Recomendações de Engenharia de Software e Infraestrutura")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
        ### 🛡️ 1. Governança de Tráfego & Resiliência
        - **Rate Limiting (HTTP 429):** Configurar políticas estritas de limitação de taxa (algoritmos *Token Bucket* ou *Leaky Bucket*) para descartar requisições quando a carga por nó ultrapassar $35\\text{ req/s}$.
        - **Circuit Breaker:** Implementar o padrão Circuit Breaker (ex.: Resilience4j ou Istio Service Mesh) para abrir o circuito e evitar falhas em cascata quando o tempo de resposta ultrapassar o SLA.
        - **Filas Assíncronas:** Desacoplar operações pesadas de gravação na nuvem usando corretores de mensagens (RabbitMQ / Apache Kafka / AWS SQS).
        """)
        
    with col_b:
        st.markdown("""
        ### 🚀 2. Escalabilidade & Otimização
        - **Autoscaling Horizontal (HPA):** Dimensionar novos pods/instâncias no Kubernetes quando a utilização da CPU/taxa de requisições atingir **$70\\%$ da capacidade nominal ($35\\text{ req/s}$)**.
        - **Balanceamento de Carga Inteligente:** Configurar balanceadores (NGINX / AWS ALB) com algoritmo *Least Connections* para distribuir a carga uniformemente entre réplicas.
        - **Camada de Cache Distribuído:** Integrar Redis / Memcached para responder a consultas de leitura repetidas sem onerar a CPU da API principal.
        """)
        
    st.info("""
    **🎯 Conclusão Executiva:** Capacidade teórica ($50\\text{ req/s}$) NÃO é capacidade operacional segura.  
    A operação recomendada em produção deve ser mantida em **$x \\le 35\\text{ req/s}$**, garantindo latências abaixo de $67\\text{ ms}$ e margem de segurança de $30\\%$ contra rajadas de tráfego.
    """)

# ==========================================
# Rodapé
# ==========================================
st.divider()
st.markdown("""
<div style="text-align: center; color: #4B5563; font-size: 0.95rem; margin-bottom: 8px;">
    <strong>👥 Integrantes do Grupo:</strong><br>
    Thiago Gomes Nascimento (RM 569436) • Gabriel Henrique Ongarelli Reis (RM 572636)<br>
    Vinicius Scalone Ramires (RM 573783) • Matheus de Amorim Brito (RM 572435) • Eduardo Felix Frois Silva (RM 574103)
</div>
<div style="text-align: center; color: #6B7280; font-size: 0.85rem;">
    <strong>DPS — Differentiated Problem Solving</strong> | Checkpoint 4 — Modelagem Matemática & Streamlit | <strong>FIAP 2026</strong> | Prof. Jones Egydio
</div>
""", unsafe_allow_html=True)