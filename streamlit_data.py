import pandas as pd
import streamlit as st
from datetime import datetime

#Страничка
st.set_page_config(
    page_title="Погода в Szeged",
    page_icon="🌤️",
    layout="centered"
)

#Заголовок
st.title("🌦️ Погода в Szeged за 10 лет")
st.write("Смотри как менялась погода с 2006 по 2016 год")

#Данные
@st.cache_data
def load_data():
    data = pd.read_csv("weatherHistory.csv")
    data['Formatted Date'] = pd.to_datetime(data['Formatted Date'], utc=True)
    data['Year'] = data['Formatted Date'].dt.year
    data['Month'] = data['Formatted Date'].dt.month
    data['Day'] = data['Formatted Date'].dt.day
    data['Date'] = data['Formatted Date'].dt.date
    return data

df = load_data()

st.sidebar.header("⚙️ Настройки")

group_by = st.sidebar.radio(
    "Группировать данные:",
    ["По дням", "По неделям"],
    index=0
)

#Тип графика
chart_type = st.sidebar.radio(
    "Что показывать на графике:",
    ["Все данные", "Средние значения"],
    help="Можно показывать все точки или только средние за день/неделю"
)

#Фильтр
if group_by == "По дням":
    year = st.sidebar.selectbox(
        "Выберите год:",
        sorted(df['Year'].unique()),
        index=len(df['Year'].unique())-1
    )

    month = st.sidebar.selectbox(
        "Выберите месяц:",
        range(1, 13)
    )
    
    filtered = df[(df['Year'] == year) & (df['Month'] == month)]
    
    if chart_type == "Средние значения":
        filtered = filtered.groupby('Date').mean(numeric_only=True).reset_index()
    else:
        filtered = filtered.sort_values('Date')
    
    x_axis = 'Date'
    
else:  # Если по неделям
    year = st.sidebar.selectbox(
        "Выберите год:",
        sorted(df['Year'].unique()),
        index=len(df['Year'].unique())-1
    )
    
    filtered = df[df['Year'] == year].copy()
    filtered['Week'] = filtered['Formatted Date'].dt.isocalendar().week
    
    if chart_type == "Средние значения":
        filtered = filtered.groupby('Week').mean(numeric_only=True).reset_index()
    
    x_axis = 'Week'

#Температура
temp_filter = st.sidebar.slider(
    "Диапазон температур (°C):",
    float(df['Temperature (C)'].min()),
    float(df['Temperature (C)'].max()),
    (10.0, 20.0)
)

filtered = filtered[
    (filtered['Temperature (C)'] >= temp_filter[0]) & 
    (filtered['Temperature (C)'] <= temp_filter[1])
]

#Данные графика
metrics = st.sidebar.multiselect(
    "Какие данные показать:",
    ['Temperature (C)', 'Humidity', 'Wind Speed (km/h)'],
    default=['Temperature (C)', 'Humidity']
)

#Заголовок от выбора
if group_by == "По дням":
    st.header(f"Погода в {month}.{year} ({'средние' if chart_type == 'Средние значения' else 'все данные'})")
else:
    st.header(f"Погода в {year} ({'средние за недели' if chart_type == 'Средние значения' else 'по неделям'})")

#Цвет
st.subheader("🎨 Выбери цвета графиков")
colors = {}
for m in metrics:
    colors[m] = st.color_picker(
        f"Цвет для {m}",
        "#4CAF50" if m == 'Temperature (C)' else "#2196F3" if m == 'Humidity' else "#FF5722"
    )

#График
st.subheader("📈 График погоды")
st.line_chart(
    filtered,
    x=x_axis,
    y=metrics,
    color=[colors[m] for m in metrics]
)

#"Сырые данные"
if st.button("Показать таблицу данных"):
    st.write(filtered)

with st.expander("📊 Статистика"):
    st.write(f"Всего записей: {len(filtered)}")
    st.write(filtered.describe())

#Вывод
avg_temp = filtered['Temperature (C)'].mean()

st.subheader("🔍 Что это значит?")
if avg_temp > 20:
    st.success(f"☀️ Было жарко! Средняя температура: {avg_temp:.1f}°C")
elif avg_temp > 10:
    st.info(f"🌤️ Было тепло! Средняя температура: {avg_temp:.1f}°C")
else:
    st.warning(f"❄️ Было холодно! Средняя температура: {avg_temp:.1f}°C")

#Обновить, если что то сломалост
if st.button("Обновить данные"):
    st.rerun()
