# Importación de librerías
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date

# Configuración de la página de Streamlit
st.set_page_config(page_title="ETFs - Análisis de Rendimiento y Riesgo", layout="wide")

# Título de la aplicación
st.title("📊 Análisis Financiero de ETFs: Rendimiento y Comparación")

# Parámetros de consulta en la barra lateral
st.sidebar.header("Configuración del análisis")

# Entrada del símbolo del ETF
ticker = st.sidebar.text_input("Ingrese el símbolo del ETF (Ej: QQQ, VOO, ARKK)", value="QQQ")

# Fechas de inicio y fin para la consulta de datos
start_date = st.sidebar.date_input("Fecha de inicio", value=pd.to_datetime("2014-01-01"))
end_date = st.sidebar.date_input("Fecha de fin", value=pd.to_datetime(date.today()))

# Función para calcular rendimiento y volatilidad
def calculate_returns(data):
    returns = data['Adj Close'].pct_change().dropna()
    return returns

def annualized_performance(returns, periods_per_year=252):
    mean_return = np.mean(returns) * periods_per_year
    volatility = np.std(returns) * np.sqrt(periods_per_year)
    return mean_return, volatility

# Botón para realizar la consulta
if st.sidebar.button("Consultar y Analizar"):
    try:
        # Descargar los datos del ETF solicitado y del SPY
        data_etf = yf.download(ticker, start=start_date, end=end_date)
        data_spy = yf.download("SPY", start=start_date, end=end_date)

        if not data_etf.empty and not data_spy.empty:
            # Mostrar los datos en tablas
            st.subheader(f"Datos Históricos del ETF: {ticker.upper()}")
            st.dataframe(data_etf.tail())

            # Cálculo de rendimientos diarios
            returns_etf = calculate_returns(data_etf)
            returns_spy = calculate_returns(data_spy)

            # Gráfico de comparación de precios ajustados entre el ETF y SPY
            st.subheader(f"📉 Comparación del Precio Ajustado: {ticker.upper()} vs SPY")
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(data_etf['Adj Close'], label=f"{ticker.upper()} - Precio Ajustado")
            ax.plot(data_spy['Adj Close'], label="SPY - Precio Ajustado", linestyle='--')
            ax.set_title(f"Comparación de Precios Ajustados: {ticker.upper()} vs SPY")
            ax.set_xlabel("Fecha")
            ax.set_ylabel("Precio ($)")
            ax.legend()
            st.pyplot(fig)

            # Cálculo del rendimiento acumulado
            cumulative_returns_etf = (1 + returns_etf).cumprod()
            cumulative_returns_spy = (1 + returns_spy).cumprod()

            # Gráfico de comparación del rendimiento acumulado
            st.subheader(f"📊 Rendimiento Acumulado: {ticker.upper()} vs SPY")
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(cumulative_returns_etf, label=f"{ticker.upper()} - Rendimiento Acumulado")
            ax.plot(cumulative_returns_spy, label="SPY - Rendimiento Acumulado", linestyle='--')
            ax.set_title(f"Rendimiento Acumulado: {ticker.upper()} vs SPY")
            ax.set_xlabel("Fecha")
            ax.set_ylabel("Rendimiento Acumulado")
            ax.legend()
            st.pyplot(fig)

            # Cálculo de rendimiento y volatilidad para diferentes períodos
            periods = {
                "1 mes": 21,
                "3 meses": 63,
                "6 meses": 126,
                "1 año": 252,
                "YTD": len(data_etf[data_etf.index.year == end_date.year]),
                "3 años": 252 * 3,
                "5 años": 252 * 5,
                "10 años": 252 * 10,
            }

            performance_data = []
            for period_name, days in periods.items():
                period_returns_etf = returns_etf[-days:]
                period_returns_spy = returns_spy[-days:]

                mean_etf, vol_etf = annualized_performance(period_returns_etf)
                mean_spy, vol_spy = annualized_performance(period_returns_spy)

                performance_data.append({
                    "Período": period_name,
                    f"Rendimiento {ticker.upper()} (%)": mean_etf * 100,
                    f"Volatilidad {ticker.upper()} (%)": vol_etf * 100,
                    "Rendimiento SPY (%)": mean_spy * 100,
                    "Volatilidad SPY (%)": vol_spy * 100,
                })

            # Crear un DataFrame con los resultados
            performance_df = pd.DataFrame(performance_data)

            # Mostrar la tabla de rendimiento y volatilidad
            st.subheader("📈 Rendimiento y Volatilidad por Período")
            st.dataframe(performance_df)

            # Gráfico comparativo de rendimiento y volatilidad
            fig, ax = plt.subplots(figsize=(12, 6))
            performance_df.plot(
                kind='bar',
                x='Período',
                y=[f"Rendimiento {ticker.upper()} (%)", "Rendimiento SPY (%)"],
                ax=ax
            )
            ax.set_title(f"Comparación de Rendimiento Anualizado: {ticker.upper()} vs SPY")
            ax.set_xlabel("Período")
            ax.set_ylabel("Rendimiento (%)")
            st.pyplot(fig)

        else:
            st.error("No se encontraron datos para el ETF o el SPY en las fechas seleccionadas.")

    except Exception as e:
        st.error(f"Error al descargar los datos: {e}")

else:
    st.write("Introduzca un símbolo de ETF y presione 'Consultar y Analizar' para comenzar.")

# Pie de página
st.sidebar.markdown("Desarrollado por Angel Ibarra")
