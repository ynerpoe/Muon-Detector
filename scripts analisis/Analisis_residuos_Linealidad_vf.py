# ============================================================
# Análisis de Residuos para Verificación de Linealidad
# Este código realiza un análisis de residuos para verificar 
# la linealidad de la relación entre ln(N(Δt)) y Δt,
# utilizando datos de intervalos de tiempo entre eventos muónicos.
# El análisis incluye:
# 1. Carga y procesamiento de datos.
# 2. Análisis estadístico con regresión lineal y prueba KS.
# 3. Reporte de resultados.
# 4. Generación de gráficos independientes para linealización, residuos y distribución.
# Autor: Ynerpoe
# Fecha: 23 de abril de 2026
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import kstest, linregress

# ============================================================
# 1. Carga y Procesamiento de Datos
# ============================================================
file_path = "datos\Muon_Data_27abril2026_v4.6_filtrado.xlsx"

df = pd.read_excel(file_path)

df["tiempo_s"] = df["tiempo_s"].astype(str).str.replace(",", ".").astype(float)

# Calcular intervalos de tiempo (Delta t)
tiempos = df["tiempo_s"].values
dt = np.diff(tiempos) 
dt = dt[dt > 0.1]  # Filtro de tiempo muerto/ruido

# ============================================================
# 2. Análisis Estadístico
# ============================================================
# Histograma para linealización
counts, bin_edges = np.histogram(dt, bins='auto')
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

# Evitar log(0)
mask = counts > 0
x_bins = bin_centers[mask]
y_log_n = np.log(counts[mask])

# Regresión Lineal (Linealización)
slope, intercept, r_value, p_val_lin, std_err = linregress(x_bins, y_log_n)
lambda_ls = -slope
y_pred = intercept + slope * x_bins

# Cálculo de Residuos
residuos = y_log_n - y_pred

# Prueba de Kolmogorov-Smirnov (KS) - Escala corregida
lambda_exp = 1.0 / np.mean(dt)
ks_stat, ks_p_value = kstest(dt, 'expon', args=(0, 1/lambda_exp))

# ============================================================
# 3. Reporte de Resultados
# ============================================================
print("-" * 50)
print("VERIFICACIÓN ESTADÍSTICA DE LA DISTRIBUCIÓN")
print("-" * 50)
print(f"R² (Linealidad): {r_value**2:.4f}")
print(f"Lambda estimado: {lambda_ls:.4f} s⁻¹")
print(f"P-valor KS:      {ks_p_value:.4f}")
print("-" * 50)

# ============================================================
# 4. Generación de Gráficos (Independientes)
# ============================================================

# Gráfico 1: Linealización
plt.figure(figsize=(8, 5))
plt.scatter(x_bins, y_log_n, color='blue', label='Datos ln(N)')
plt.plot(x_bins, y_pred, 'r--', label=f'Ajuste (R²={r_value**2:.3f})')
plt.title("Prueba de Linealidad: ln N(Δt) vs Δt")
plt.xlabel("Δt (s)")
plt.ylabel("ln N(Δt)")
plt.legend()
plt.grid(True, alpha=0.3)

# Gráfico 2: Análisis de Residuos
plt.figure(figsize=(8, 5))
plt.scatter(x_bins, residuos, color='purple', edgecolors='k')
plt.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
plt.title("Análisis de Residuos (Diagnóstico de Linealidad)")
plt.xlabel("Δt (s)")
plt.ylabel("Residuo (Observado - Predicho)")
plt.grid(True, alpha=0.3)
# Nota: Busca una dispersión aleatoria sin patrones en este gráfico.

# Gráfico 3: Histograma y PDF Teórica
plt.figure(figsize=(8, 5))
plt.hist(dt, bins='auto', density=True, alpha=0.6, color='seagreen', label='Datos Exp.')
t_range = np.linspace(0, max(dt), 200)
plt.plot(t_range, lambda_exp * np.exp(-lambda_exp * t_range), 'r-', lw=2, label='Teoría')
plt.title("Distribución de Intervalos")
plt.xlabel("Δt (s)")
plt.ylabel("Densidad")
plt.legend()
plt.grid(True, alpha=0.3)

plt.show()