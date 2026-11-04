import streamlit as st
import re
from itertools import product
import pandas as pd

st.set_page_config(title="Calculadora Tabla de la Verdad", layout="centered")

st.title("🧮 Calculadora de Tabla de la Verdad")
st.markdown("Construye tu expresión haciendo clic. El resultado se muestra en $0$ y $1$.")

if 'expr' not in st.session_state:
    st.session_state.expr = ""

st.subheader("🛠️ Constructor de Expresión")

st.markdown("**Variables:**")
cols_vars = st.columns(6)
variables_disponibles = ['p', 'q', 'r', 's', 't', 'w']
for i, var in enumerate(variables_disponibles):
    with cols_vars[i]:
        if st.button(var, use_container_width=True):
            st.session_state.expr += var

st.markdown("**Operadores:**")
operadores = ['∧', '∨', '¬', '→', '↔', '(', ')']
cols_ops = st.columns(7)
for i, op in enumerate(operadores):
    with cols_ops[i]:
        if st.button(op, use_container_width=True, key=f"op_{i}"):
            st.session_state.expr += op

col_clear, col_undo, col_empty = st.columns([1, 1, 2])
with col_clear:
    if st.button("🗑️ Limpiar Todo", use_container_width=True, type="secondary"):
        st.session_state.expr = ""
with col_undo:
    if st.button("↩️ Borrar Último", use_container_width=True):
        st.session_state.expr = st.session_state.expr[:-1]

st.text_input("Expresión actual:", value=st.session_state.expr, disabled=True)

def normalizar_expresion(expr):
    expr = expr.replace('∧', ' and ')
    expr = expr.replace('∨', ' or ')
    expr = expr.replace('¬', ' not ')
    expr = expr.replace('→', ' <= ')
    expr = expr.replace('↔', ' == ')
    return expr

def extraer_variables(expr):
    return sorted(list(set(re.findall(r'\b[pqrstw]\b', expr))))

def generar_tabla(expr_norm):
    variables = extraer_variables(expr_norm)
    if not variables:
        return [], pd.DataFrame()
    
    tabla = []
    for valores in product([0, 1], repeat=len(variables)):
        entorno = dict(zip(variables, valores))
        try:
            resultado = int(bool(eval(expr_norm, {"__builtins__": None}, entorno)))
            fila = list(valores) + [resultado]
            tabla.append(fila)
        except Exception:
            return variables, pd.DataFrame()
            
    columnas = variables + ["Resultado"]
    df = pd.DataFrame(tabla, columns=columnas)
    return variables, df

if not st.session_state.expr.strip():
    st.info("💡 Ingresa o construye una expresión primero.")
else:
    expr_norm = normalizar_expresion(st.session_state.expr)
    vars, df = generar_tabla(expr_norm)
    
    if df.empty:
        st.error("⚠️ Expresión inválida o variables detectadas incorrectamente.")
    else:
        st.success(f"✅ Tabla generada para {len(vars)} variables.")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar tabla de verdad (CSV)",
            data=csv,
            file_name="tabla_verdad.csv",
            mime="text/csv",
        )