# ============================================================
# Analisis de ajuste de Poisson para los datos de muones detectados. 
# Se construyen intervalos de tiempo, se cuentan eventos por intervalo,
# Se ajusta una distribución de Poisson a los datos y 
# se evalúa la bondad del ajuste mediante una prueba de chi-cuadrado.
# Se visualizan los resultados con gráficos mejorados.
# Se incluyen también análisis de los intervalos entre eventos (Δt) 
# para verificar si siguen una distribución exponencial 
# utilizando tanto un ajuste por mínimos cuadrados como una prueba de Kolmogorov Smirnov (KS).
# Autor: YnerPoe
# Fecha: 23 de abril de 2026
# NOTA: No se filtran los intervalos menores al tiempo muerto para la prueba Kolmogorov-Smirnov. 
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import poisson, chi2
from scipy.ndimage import gaussian_filter1d

# ============================================================
# 1. Cargar datos
# ============================================================
file_path = "datos\Muon_Data_27abril2026_v4.6_filtrado.xlsx"

df = pd.read_excel(file_path)

df["tiempo_s"] = df["tiempo_s"].astype(str).str.replace(",", ".").astype(float)
df["cpm"] = df["cpm"].astype(str).str.replace(",", ".").astype(float)

t = df["tiempo_s"].values

# ============================================================
# 2. Construcción de intervalos de 300 s
# ============================================================

bin_width = 300
t_max = t.max()
n_bins = int(np.ceil(t_max / bin_width))

counts_per_bin = np.zeros(n_bins, dtype=int)
for time in t:
    bin_index = int(time // bin_width)
    counts_per_bin[bin_index] += 1

# ============================================================
# 3. Histograma observado
# ============================================================

unique, freq_obs = np.unique(counts_per_bin, return_counts=True)
hist_obs = dict(zip(unique, freq_obs))

# ============================================================
# 4. Estimación del parámetro μ
# ============================================================

mu_hat = counts_per_bin.mean()

# ============================================================
# 5. Frecuencias esperadas según Poisson
# ============================================================

k_vals = np.arange(unique.min(), unique.max() + 1)
p_k = poisson.pmf(k_vals, mu_hat)
E_k = n_bins * p_k
O_k = np.array([hist_obs.get(k, 0) for k in k_vals])

# ============================================================
# 6. Agrupación automática para asegurar E >= 5
# ============================================================

def group_categories(k_vals, O_k, E_k, min_expected=5):
    grouped = []
    current_k = []
    current_O = 0
    current_E = 0

    for k, O, E in zip(k_vals, O_k, E_k):
        current_k.append(k)
        current_O += O
        current_E += E

        if current_E >= min_expected:
            grouped.append((current_k.copy(), current_O, current_E))
            current_k = []
            current_O = 0
            current_E = 0

    if current_k:
        last = grouped.pop()
        new_k = last[0] + current_k
        new_O = last[1] + current_O
        new_E = last[2] + current_E
        grouped.append((new_k, new_O, new_E))

    return grouped

grouped = group_categories(k_vals, O_k, E_k)

# ============================================================
# 7. Cálculo del chi-cuadrado
# ============================================================

chi2_stat = 0
residuals = []

for ks, O, E in grouped:
    chi2_stat += (O - E)**2 / E
    residuals.append((O - E) / np.sqrt(E))

dof = len(grouped) - 1 - 1
p_value = 1 - chi2.cdf(chi2_stat, dof)

# ============================================================
# 8. Histograma de intervalos Δt y ajuste exponencial
# ============================================================
# Intervalos entre eventos consecutivos
dt = df["tiempo_s"].diff().dropna()

# Parámetro de la exponencial
dt_mean = dt.mean()
lambda_exp = 1.0 / dt_mean

# ============================================================
# 9. Verificación de la distribución exponencial de Δt
# ============================================================

from scipy.stats import kstest

# Intervalos entre eventos
dt = df["tiempo_s"].diff().dropna()

# Parámetro exponencial teórico
dt_mean = dt.mean()
lambda_exp = 1.0 / dt_mean

print("\n===== VERIFICACIÓN DE LA DISTRIBUCIÓN EXPONENCIAL =====")
print(f"Media de Δt: {dt_mean:.4f} s")
print(f"λ estimado (1/mean): {lambda_exp:.4f} s⁻¹")

# ============================================================
# 10. Ajuste por mínimos cuadrados (linealización)
# ============================================================
# Construcción del histograma
counts_dt, bins_dt = np.histogram(dt, bins=40)
bin_centers = 0.5 * (bins_dt[:-1] + bins_dt[1:])

# Filtrar bins con conteo > 0 para poder aplicar log
mask = counts_dt > 0
x = bin_centers[mask]
y = np.log(counts_dt[mask])

# Ajuste lineal: ln(N) = ln(N0) - λ t
coef = np.polyfit(x, y, 1)
slope, intercept = coef
lambda_ls = -slope
N0_ls = np.exp(intercept) # valor de N(0) según el ajuste lineal

print("\n=== Ajuste por mínimos cuadrados ===")
print(f"λ (LS): {lambda_ls:.4f} s⁻¹")
print(f"N0 (LS): {N0_ls:.2f}")

# ============================================================
# 11. Prueba de Kolmogorov–Smirnov (KS)
# ============================================================
# CDF exponencial teórica
cdf_exp = lambda t: 1 - np.exp(-lambda_exp * t)

ks_stat, ks_p = kstest(dt, cdf_exp)

print("\n=== Prueba de Kolmogorov–Smirnov (KS) ===")
print(f"KS statistic: {ks_stat:.4f}")
print(f"p-value: {ks_p:.4f}")

if ks_p > 0.05:
        print("CONCLUSIÓN: No se rechaza la hipótesis nula (H0).")
        print("Los datos son consistentes con una Distribución Exponencial.")
else:
        print("\nCONCLUSIÓN: Se rechaza la hipótesis nula (H0).")
        print("Los datos NO siguen una Distribución Exponencial.")
print("="*50)

# ============================================================
# 12. Resultados finales
# ============================================================

print("\n===== RESULTADOS DEL AJUSTE DE POISSON =====")
print(f"Total de intervalos: {n_bins}")
print(f"Media por intervalo (mu): {mu_hat:.4f}")
print(f"Chi-cuadrado: {chi2_stat:.4f}")
print(f"Grados de libertad: {dof}")
print(f"p-value: {p_value:.4f}")

print("\n===== TABLA AGRUPADA =====")
for ks, O, E in grouped:
    label = f"{ks[0]}" if len(ks) == 1 else f"{ks[0]}–{ks[-1]}"
    print(f"Categoría {label:>6}: Observado={O:3d}, Esperado={E:8.3f}")

# ============================================================
# GRÁFICOS
# ============================================================

# ------------------------------------------------------------
# 1) CPM vs tiempo
# ------------------------------------------------------------

plt.figure(figsize=(12, 5))
plt.scatter(df["tiempo_s"], df["cpm"], s=8, alpha=0.5, label="Datos CPM")

# Suavizado tipo LOESS usando filtro gaussiano
smooth_cpm = gaussian_filter1d(df["cpm"], sigma=10)
plt.plot(df["tiempo_s"], smooth_cpm, color="red", linewidth=2, label="Suavizado")

plt.xlabel("Tiempo (s)")
plt.ylabel("CPM")
plt.title("CPM vs Tiempo")
plt.grid(True)
plt.legend()

# ------------------------------------------------------------
# 2) Histograma de cuentas por intervalo con ajuste exponencial
# ------------------------------------------------------------

plt.figure(figsize=(10, 5))

bins = np.arange(counts_per_bin.max()+2)-0.5
hist_vals, _, _ = plt.hist(counts_per_bin, bins=bins, density=True,
                           alpha=0.6, edgecolor="black", label="Datos")

# Ajuste exponencial (Poisson → exponencial discreta)
plt.plot(k_vals, poisson.pmf(k_vals, mu_hat), "r-", linewidth=2,
         label=f"Ajuste Poisson (μ={mu_hat:.2f})")

plt.xlabel("Cuentas por intervalo (300 s)")
plt.ylabel("Densidad")
plt.title("Histograma con ajuste Poisson")
plt.grid(True)
plt.legend()

# ------------------------------------------------------------
# 3) Observado vs Poisson con línea continua
# ------------------------------------------------------------

plt.figure(figsize=(10, 5))

plt.bar(k_vals, O_k, width=0.6, alpha=0.6, label="Frecuencia observada", edgecolor="black")
plt.plot(k_vals, E_k, "r-", linewidth=2, label="Poisson esperada")

plt.xlabel("Número de cuentas por intervalo de 300s")
plt.ylabel("Frecuencia")
plt.title("Distribución de cuentas por intervalo y ajuste de Poisson")
plt.grid(True)
plt.legend()

# ------------------------------------------------------------
# 4) Residuos normalizados del ajuste chi-cuadrado
# ------------------------------------------------------------

plt.figure(figsize=(10, 5))
plt.bar(range(len(residuals)), residuals, color="purple")
plt.axhline(0, color="black")
plt.xlabel("Categoría agrupada")
plt.ylabel("Residuo normalizado")
plt.title("4) Residuos normalizados del ajuste chi-cuadrado")
plt.grid(True)

# ------------------------------------------------------------
# 5) Histograma de intervalos Δt y ajuste exponencial
# ------------------------------------------------------------

plt.figure(figsize=(10, 5))
counts, bins, _ = plt.hist(
    dt, bins=40, density=True, alpha=0.6,
    edgecolor="black", label="Datos (Δt)"
)

# Curva exponencial teórica
x_exp = np.linspace(0, dt.max(), 500)
pdf_exp = lambda_exp * np.exp(-lambda_exp * x_exp)

plt.plot(
    x_exp, pdf_exp, "r-", linewidth=2,
    label=f"Ajuste exponencial\nλ = {lambda_exp:.4f} s⁻¹"
)

plt.xlabel("Intervalo entre eventos Δt (s)")
plt.ylabel("Densidad de probabilidad")
plt.title("Distribución de intervalos entre eventos (Δt)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

# Guardar figura
#plt.savefig("hist_intervalos_exponencial.png", dpi=300)

# ------------------------------------------------------------
# 6) Linealización del histograma de Δt
# ------------------------------------------------------------

plt.figure(figsize=(10, 5))
plt.scatter(x, y, s=20, label="Datos log(N)")
plt.plot(x, intercept + slope * x, "r-", linewidth=2,
         label=f"Ajuste lineal\nλ = {lambda_ls:.4f} s⁻¹")
plt.xlabel("Δt (s)")
plt.ylabel("ln N(Δt)")
plt.title("Linealización del histograma de Δt")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.show()
