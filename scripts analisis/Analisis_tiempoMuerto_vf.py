# Análisis de ajuste de distribución exponencial truncada 
# a los intervalos entre eventos de muones detectados, considerando un tiempo muerto.
# El código carga los datos, estima los parámetros de la distribución,
# genera la curva teórica y grafica los resultados con estilo científico clásico.
# Autor: YnerPoe
# fecha: 23 de abril de 2026

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import os
from datetime import datetime

# ---------------------------------------------------------
# 1. Cargar datos
# ---------------------------------------------------------
file_path = "datos\Muon_Data_27abril2026_v4.6_filtrado.xlsx"
df = pd.read_excel(file_path)

df["tiempo_s"] = df["tiempo_s"].astype(str).str.replace(",", ".").astype(float)

# Intervalos entre eventos
dt = df["tiempo_s"].diff().dropna().values

# Filtrar intervalos no positivos
dt = dt[dt > 0]

if len(dt) == 0:
    raise ValueError("No hay intervalos positivos en los datos")

print(f"Total de intervalos: {len(dt)}")
print(f"Intervalo mínimo: {np.min(dt):.6f} s")
print(f"Intervalo máximo: {np.max(dt):.6f} s")
print(f"Media: {np.mean(dt):.6f} s\n")

# ---------------------------------------------------------
# 2. Función de verosimilitud para exponencial truncada
# ---------------------------------------------------------
def neg_log_likelihood(params, data, penalty=1e10):
    """Negative log-likelihood para exponencial truncada.
    
    Parámetros:
        params: [lambda, tau] - rate y punto de truncamiento
        data: array de intervalos
        penalty: penalidad por violación de restricciones (no inf)
    """
    lam, tau = params
    
    # Validaciones
    if lam <= 0:
        return penalty
    if tau < 0:
        return penalty
    if tau >= np.min(data):
        return penalty
    
    shifted = data - tau
    
    # Verificar que el shift produzca valores válidos
    if np.any(shifted <= 0):
        return penalty
    
    # Calcular log-likelihood
    try:
        nll = -(len(data) * np.log(lam) - lam * np.sum(shifted))
        if not np.isfinite(nll):
            return penalty
        return nll
    except:
        return penalty

# Estimación inicial - usar percentiles para robustez
dt_mean = np.mean(dt)
dt_p10 = np.percentile(dt, 10)  # 10 percentil
lam0 = 1 / dt_mean
tau0 = 0.5 * dt_p10  # Estimar tau como mitad del percentil 10

print(f"Estimación inicial: λ₀={lam0:.4f}, τ₀={tau0:.6f}\n")

# Bounds robusto
min_dt = np.min(dt)
max_tau = 0.99 * min_dt  # Tau debe ser < min(dt)
min_lam = 1e-8
max_lam = 100.0  # Límite superior razonable

bounds = [(min_lam, max_lam), (1e-8, max_tau)]

print(f"Bounds - Lambda: [{min_lam}, {max_lam}]")
print(f"Bounds - Tau: [1e-8, {max_tau:.6f}]\n")

# Optimización con método robusto
res = minimize(neg_log_likelihood, x0=[lam0, tau0], args=(dt, 1e10),
               method='SLSQP', bounds=bounds, 
               options={'ftol': 1e-12, 'maxiter': 2000})

print(f"Optimización exitosa: {res.success}")
print(f"Mensaje: {res.message}")
print(f"Iteraciones: {res.nit}")
print(f"Evaluaciones de función: {res.nfev}\n")

lam_hat, tau_hat = res.x

print("="*50)
print("RESULTADOS DE ESTIMACIÓN")
print("="*50)
print(f"λ estimado: {lam_hat:.6f} s⁻¹")
print(f"τ estimado (tiempo muerto): {tau_hat:.6f} s")
print(f"Tasa de eventos (1/λ): {1/lam_hat:.6f} s")
print("="*50 + "\n")

# ---------------------------------------------------------
# 3. Generar curva teórica
# ---------------------------------------------------------
x = np.linspace(0, np.max(dt), 500)
pdf_trunc = np.where(x >= tau_hat, lam_hat * np.exp(-lam_hat * (x - tau_hat)), 0)

# Filtrar datos para visualización
dt_filtrado = dt[dt > tau_hat]

# ---------------------------------------------------------
# 4. Gráficos separados
# ---------------------------------------------------------
# Figura 1: Todos los datos con la curva truncada
fig1 = plt.figure(figsize=(8, 5))
ax1 = fig1.add_subplot(111)
ax1.hist(dt, bins=40, density=True, alpha=0.6, color="steelblue",
         edgecolor="black", label="Datos (intervalos)")
ax1.plot(x, pdf_trunc, "r-", linewidth=2,
         label=f"Exponencial truncada\nλ={lam_hat:.6f} s⁻¹")
ax1.axvline(tau_hat, color="k", linestyle="--", linewidth=1.5,
            label=f"Tiempo muerto τ={tau_hat:.6f} s")
ax1.set_xlabel("Intervalo entre eventos Δt (s)")
ax1.set_ylabel("Densidad de probabilidad")
ax1.set_title("Histograma: Todos los intervalos")
ax1.legend()
ax1.grid(alpha=0.3)
fig1.tight_layout()
fig1.savefig("exponencial_truncada_vs_datos.png", dpi=300)

# Figura 2: Datos filtrados y la exponencial pura
fig2 = plt.figure(figsize=(8, 5))
ax2 = fig2.add_subplot(111)
ax2.hist(dt_filtrado, bins=40, density=True, alpha=0.6, color="steelblue",
         edgecolor="black", label="Datos filtrados (Δt > τ)")
x_filt = np.linspace(tau_hat, np.max(dt_filtrado), 500)
pdf_pure = lam_hat * np.exp(-lam_hat * (x_filt - tau_hat))
ax2.plot(x_filt, pdf_pure, "r-", linewidth=2,
         label=f"Exponencial pura\nλ={lam_hat:.6f} s⁻¹")
ax2.set_xlabel("Intervalo entre eventos Δt (s)")
ax2.set_ylabel("Densidad de probabilidad")
ax2.set_title(f"Datos filtrados (τ = {tau_hat:.6f} s)")
ax2.legend()
ax2.grid(alpha=0.3)
fig2.tight_layout()
fig2.savefig("exponencial_pura_filtrada.png", dpi=300)

plt.show()

print(f"Intervalos después de filtro: {len(dt_filtrado)} / {len(dt)} ({100*len(dt_filtrado)/len(dt):.1f}%)")

# -----------------------
# Exportar resultados a .txt
# -----------------------
base_out = os.path.splitext(file_path)[0]
out_txt = base_out + "_trunc_estimation.txt"

with open(out_txt, "w", encoding="utf-8") as f:
    f.write("Estimación: Exponencial Truncada\n")
    f.write(f"Fecha: {datetime.now().isoformat()}\n")
    f.write("="*60 + "\n")
    f.write(f"Archivo de datos: {file_path}\n")
    f.write("\n--Estadísticos de los intervalos--\n")
    f.write(f"Total intervalos (positivos): {len(dt)}\n")
    f.write(f"Intervalos después de filtro (Δt > τ): {len(dt_filtrado)}\n")
    f.write(f"Intervalo mínimo: {np.min(dt):.6f} s\n")
    f.write(f"Intervalo máximo: {np.max(dt):.6f} s\n")
    f.write(f"Media de Δt: {np.mean(dt):.6f} s\n")
    f.write("\n--Resultados de la estimación--\n")
    f.write(f"λ estimado: {lam_hat:.6f} s⁻¹\n")
    f.write(f"τ estimado: {tau_hat:.6f} s\n")
    f.write("\n--Información de optimización--\n")
    f.write(f"Optimización exitosa: {res.success}\n")
    f.write(f"Mensaje: {res.message}\n")
    f.write(f"Iteraciones: {getattr(res, 'nit', 'N/A')}\n")
    f.write(f"Evaluaciones de función: {getattr(res, 'nfev', 'N/A')}\n")
    f.write("\nIntervalos filtrados (Δt > τ) - uno por línea:\n")
    for val in dt_filtrado:
        f.write(f"{val:.9e}\n")

print(f"Resultados guardados en: {out_txt}")
