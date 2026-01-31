import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(
    page_title="Dashboard de desempeño de Socialize Your Knowledge",
    page_icon="📊",
    layout="wide"
)

st.title("Conociendo el desempeño de los colaboradores de Socialize your knowledge")

def load_data():
    try:
        df = pd.read_csv('employee_data.csv', encoding='utf-8-sig')
        df['gender'] = df['gender'].str.strip()
        df['marital_status'] = df['marital_status'].str.strip()
        return df
    except FileNotFoundError:
        st.error("⚠️ El archivo 'employee_data.csv' no se encontró. Por favor, asegúrate de que esté en el directorio correcto.")
        return None

df = load_data()

if df is not None:
    st.sidebar.header("Filtros de Búsqueda")
    
    sex_map = {'Todos': 'Todos', 'Masculino': 'M', 'Femenino': 'F'}
    sex_display = st.sidebar.selectbox(
        "Selecciona el género:",
        list(sex_map.keys())
    )
    selected_sex = sex_map[sex_display]
    
    min_score = int(df['performance_score'].min())
    max_score = int(df['performance_score'].max())
    performance_rate = st.sidebar.slider(
        "Selecciona el rango de puntaje de desempeño:",
        min_value=min_score,
        max_value=max_score,
        value=(min_score, max_score)
    )
    
    marital_status_map = {
        'Todos': 'Todos',
        'Soltero': 'Single', 
        'Casado': 'Married',
        'Divorciado': 'Divorced',
        'Separado': 'Separated',
        'Viudo': 'Widowed'
    }
    marital_status_display = st.sidebar.selectbox(
        "Selecciona el estado civil:",
        list(marital_status_map.keys())
    )
    selected_marital_status = marital_status_map[marital_status_display]
    
    filter_data = df.copy()
    
    if selected_sex != 'Todos':
        filter_data = filter_data[filter_data['gender'] == selected_sex]
    
    filter_data = filter_data[
        (filter_data['performance_score'] >= performance_rate[0]) & 
        (filter_data['performance_score'] <= performance_rate[1])
    ]
    
    if selected_marital_status != 'Todos':
        filter_data = filter_data[filter_data['marital_status'] == selected_marital_status]
    
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    

    with col1:
        st.metric("Total de Empleados", len(filter_data))
    with col2:
        st.metric("Puntaje Promedio", f"{filter_data['performance_score'].mean():.2f}")
    with col3:
        st.metric("Satisfacción Promedio", f"{filter_data['satisfaction_level'].mean():.2f}")
    with col4:
        st.metric("Horas Promedio/Año", f"{filter_data['average_work_hours'].mean():.0f}")
    
    st.markdown("---")
    
    plt.style.use('default')
    colors = ['#0173B2', '#DE8F05', '#029E73', '#CC78BC', '#CA9161', '#949494']
    
    st.subheader("Distribución de Puntajes de Desempeño")
    fig1, ax1 = plt.subplots(figsize=(10, 8))
    
    counts = filter_data['performance_score'].value_counts().sort_index()
    bars = ax1.bar(counts.index, counts.values, color=colors[:len(counts)], 
                   edgecolor='black', linewidth=1.5)
    
    ax1.set_xlabel('Puntaje de Desempeño', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Número de Empleados', fontsize=12, fontweight='bold')
    ax1.set_title('Distribución de Puntajes de Desempeño', fontsize=14, fontweight='bold', pad=20)
    ax1.set_xticks(range(min_score, max_score + 1))
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_axisbelow(True)
    
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig1)
    
    st.subheader("Promedio de Horas Trabajadas por Género")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    
    hours_per_gender = filter_data.groupby('gender')['average_work_hours'].mean().sort_values(ascending=False)
    gender_labels = {'M': 'Masculino', 'F': 'Femenino'}
    hours_per_gender.index = hours_per_gender.index.map(gender_labels)
    
    bars = ax2.barh(hours_per_gender.index, hours_per_gender.values, 
                     color=['#0173B2', '#029E73'][:len(hours_per_gender)],
                     edgecolor='black', linewidth=1.5)
    
    ax2.set_xlabel('Promedio de Horas Anuales', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Género', fontsize=12, fontweight='bold')
    ax2.set_title('Promedio de Horas Trabajadas por Género', fontsize=14, fontweight='bold', pad=20)
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    ax2.set_axisbelow(True)
    
    for i, (bar, value) in enumerate(zip(bars, hours_per_gender.values)):
        ax2.text(value, i, f' {value:.0f}h', 
                va='center', fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig2)
    
    st.subheader("Relación entre Edad y Salario")
    fig3, ax3 = plt.subplots(figsize=(10, 8))
    
    scatter = ax3.scatter(filter_data['age'], filter_data['salary'], 
                         c=filter_data['performance_score'], 
                         cmap='YlOrRd', 
                         alpha=0.6, 
                         s=100,
                         edgecolors='black',
                         linewidth=0.5)
    
    ax3.set_xlabel('Edad (años)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Salario', fontsize=12, fontweight='bold')
    ax3.set_title('Relación entre Edad y Salario de los Empleados', fontsize=14, fontweight='bold', pad=20)
    ax3.grid(alpha=0.3, linestyle='--')
    ax3.set_axisbelow(True)
    
    cbar = plt.colorbar(scatter, ax=ax3)
    cbar.set_label('Puntaje de Desempeño', fontsize=10, fontweight='bold')
    
    z = np.polyfit(filter_data['age'], filter_data['salary'], 1)
    p = np.poly1d(z)
    ax3.plot(filter_data['age'].sort_values(), p(filter_data['age'].sort_values()), 
            "r--", alpha=0.8, linewidth=3, label='Tendencia')
    ax3.legend()
    
    plt.tight_layout()
    st.pyplot(fig3)
    
    st.subheader("Relación entre Horas Trabajadas y Desempeño")
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    
    ax4.scatter(filter_data['average_work_hours'], 
                filter_data['performance_score'],
                alpha=0.5, s=80, edgecolors='black', linewidth=0.5,
                color='#0173B2')
    
    z = np.polyfit(filter_data['average_work_hours'], filter_data['performance_score'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(filter_data['average_work_hours'].min(), 
                         filter_data['average_work_hours'].max(), 100)
    ax4.plot(x_line, p(x_line), color='#DE8F05', linewidth=2, label='Línea de regresión')
    
    ax4.set_xlabel('Promedio de Horas Trabajadas (anual)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Puntaje de Desempeño', fontsize=12, fontweight='bold')
    ax4.set_title('Relación entre Horas Trabajadas y Puntaje de Desempeño', 
                 fontsize=14, fontweight='bold', pad=20)
    ax4.grid(alpha=0.3, linestyle='--')
    ax4.set_axisbelow(True)
    ax4.legend()
    
    correlation = filter_data['average_work_hours'].corr(filter_data['performance_score'])
    ax4.text(0.05, 0.95, f'Correlación: {correlation:.3f}', 
            transform=ax4.transAxes, 
            fontsize=12, 
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    st.pyplot(fig4)
    
    st.markdown("---")
    st.subheader("Conclusiones del Análisis")
    
    average_performance = filter_data['performance_score'].mean()
    satisfaction_level = filter_data['satisfaction_level'].mean()
    avg_work_hours = filter_data['average_work_hours'].mean()
    
    st.markdown(f"""
    Con base en el análisis del desempeño de los colaboradores de **Socialize Your Knowledge**, 
    se pueden destacar los siguientes hallazgos:
    
    1. **Desempeño General**: El puntaje promedio de desempeño es de **{average_performance:.2f}** sobre 4, 
       lo que indica un nivel de rendimiento {'excelente' if average_performance >= 3.5 else 'bueno' if average_performance >= 2.5 else 'aceptable'}.
    
    2. **Satisfacción Laboral**: El nivel promedio de satisfacción de los empleados es de **{satisfaction_level:.2f}** sobre 5, 
       {'reflejando un ambiente laboral positivo' if satisfaction_level >= 4 else 'sugiriendo áreas de mejora en el clima organizacional'}.
    
    3. **Carga de Trabajo**: Los empleados trabajan en promedio **{avg_work_hours:.0f} horas anuales**, 
       con una correlación de **{correlation:.3f}** entre las horas trabajadas y el desempeño.

    """)
    

else:
    st.warning("No se pudieron cargar los datos. Por favor, verifica que el archivo CSV esté disponible.")
