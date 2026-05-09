# ============================================================
# Análisis de Bondad de Ajuste: Prueba de Kolmogorov-Smirnov
# CON filtrado por tiempo muerto
#
# Este script evalúa si los intervalos entre eventos siguen
# una distribución exponencial truncada.
#
# Autor: YnerPoe 
# Fecha: 23 abril 2026
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import kstest, expon
import os
from datetime import datetime

# ============================================================
# 1. CARGA Y PREPROCESAMIENTO
# ============================================================
# Cargar datos ignorando problemas de comas/puntos decimales
file_path = "datos\Muon_Data_27abril2026_v4.6_filtrado.xlsx"

df = pd.read_excel(file_path)

df["tiempo_s"] = df["tiempo_s"].astype(str).str.replace(",", ".").astype(float)

# Calcular intervalos de tiempo (Delta t)
tiempos = df["tiempo_s"].values
dt = np.diff(tiempos)

# ============================================================
# 2. ESTIMACIÓN DE TIEMPO MUERTO MEDIANTE AJUSTE EXPONENCIAL TRUNCADO
# ============================================================
from scipy.optimize import minimize

def neg_log_likelihood(params, data):
    lam, tau = params
    if lam <= 0 or tau < 0 or tau >= np.min(data):
        return 1e10  # Large penalty
    shifted = data - tau
    if np.any(shifted <= 0):
        return 1e10
    return -(len(data) * np.log(lam) - lam * np.sum(shifted))

# Estimación inicial
lam0 = 1 / np.mean(dt)
tau0 = 0.01

# Bounds
min_dt = np.min(dt)
bounds = [(1e-6, None), (0, min_dt - 1e-6)]

res = minimize(neg_log_likelihood, x0=[lam0, tau0], args=(dt,),
               method='SLSQP', bounds=bounds, options={'ftol': 1e-9, 'maxiter': 1000})

print("Optimization success:", res.success)
print("Message:", res.message)
lam_hat, tau_hat = res.x
print("λ estimado:", lam_hat)
print("τ estimado (tiempo muerto):", tau_hat)

# Filtro basado en el tiempo muerto estimado
dt_filtrado = dt[dt > tau_hat]

# ============================================================
# 3. PRUEBA DE KOLMOGOROV-SMIRNOV CON EXPONENCIAL TRUNCADO
# ============================================================
def cdf_trunc_exp(x, lam, tau):
    return np.where(x >= tau, 1 - np.exp(-lam * (x - tau)), 0)

# Prueba KS con la distribución truncada
d_stat, p_value = kstest(dt_filtrado, lambda x: cdf_trunc_exp(x, lam_hat, tau_hat), args=())

# ============================================================
# 4. REPORTE DE RESULTADOS
# ============================================================
print("\n" + "="*50)
print("ANÁLISIS DE BONDAD DE AJUSTE: KOLMOGOROV-SMIRNOV")
print("CON AJUSTE EXPONENCIAL TRUNCADO")
print("="*50)
print(f"Intervalos procesados:   {len(dt_filtrado)}")
print(f"Tasa (lambda):           {lam_hat:.4f} Hz")
print(f"Tiempo muerto (tau):     {tau_hat:.4f} s")
print(f"KS statistic:            {d_stat:.4f}")
print(f"p-value:                 {p_value:.4f}")
print("-" * 50)

if p_value > 0.05:
    conclusion = "CONCLUSIÓN: No se rechaza la hipótesis nula (H0). Los datos son consistentes con una Distribución Exponencial Truncada."
else:
    conclusion = "CONCLUSIÓN: Se rechaza la hipótesis nula (H0). Los datos NO siguen una Distribución Exponencial Truncada."

print(conclusion)
print("="*50 + "\n")

# Exportar resultados a archivo .txt (misma carpeta/nombre base que el archivo de datos)
base_out = os.path.splitext(file_path)[0]
out_txt = base_out + "_KS_trunc_analysis.txt"

with open(out_txt, "w", encoding="utf-8") as f:
    f.write("Análisis Kolmogorov–Smirnov (Exponencial Truncada)\n")
    f.write(f"Fecha: {datetime.now().isoformat()}\n")
    f.write("="*60 + "\n")
    f.write(f"Archivo de datos: {file_path}\n")
    f.write(f"Intervalos procesados (después de filtrar por tau): {len(dt_filtrado)}\n")
    f.write(f"Lambda (tasa) estimada: {lam_hat:.6f} Hz\n")
    f.write(f"Tau (tiempo muerto) estimado: {tau_hat:.6f} s\n")
    f.write("\n--Resultados KS--\n")
    f.write(f"KS statistic: {d_stat:.6e}\n")
    f.write(f"p-value:      {p_value:.6e}\n")
    f.write(conclusion + "\n")
    f.write("="*60 + "\n")
    f.write("Intervalos Δt filtrados (s) - uno por línea:\n")
    for val in dt_filtrado:
        f.write(f"{val:.9e}\n")

print(f"Resultados guardados en: {out_txt}")

# ============================================================
# 5. VISUALIZACIÓN DE LA CDF (Comparativa)
# ============================================================
#plt.figure(figsize=(10, 6))

# CDF Empírica (los datos reales)
#x_sorted = np.sort(dt_filtrado)
#y_empirica = np.arange(1, len(x_sorted) + 1) / len(x_sorted)

# CDF Teórica truncada
#y_teorica = cdf_trunc_exp(x_sorted, lam_hat, tau_hat)

#plt.step(x_sorted, y_empirica, where='post', label='CDF Empírica (Datos)', color='blue', alpha=0.7)
#plt.plot(x_sorted, y_teorica, 'r--', label='CDF Teórica (Exponencial Truncada)', lw=2)

#plt.title("Comparación de Funciones de Distribución Acumulada (CDF)")
#plt.xlabel("Intervalo de tiempo Δt [s]")
#plt.ylabel("Probabilidad Acumulada")
#plt.legend()
#plt.grid(True, linestyle=':', alpha=0.6)
#plt.show()

# Ejecutar el análisis
if __name__ == "__main__":
    pass  # El código se ejecuta directamente