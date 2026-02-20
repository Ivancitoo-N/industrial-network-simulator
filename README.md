# Industrial Network Simulator 🌐

[![GitHub License](https://img.shields.io/github/license/Ivancitoo-N/industrial-network-simulator)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)

Un simulador de redes industriales de alto rendimiento diseñado para modelar, visualizar y evaluar topologías críticas (**PROFINET**, **EtherCAT**, **Modbus TCP**) en tiempo real. 

Ideal para ingenieros de automatización, estudiantes y arquitectos de sistemas industriales que buscan validar resiliencia de red y redundancia (**anillos MRP**) sin necesidad de hardware físico.

---

## ✨ Características Principales

*   **⚡ Motor de Simulación en Tiempo Real**: Basado en `NetworkX`, simula jitter, latencia y tiempos de ciclo específicos para protocolos industriales.
*   **🕸️ Topologías Dinámicas e Interactivas**: Visualización tipo grafo usando **D3.js** con partículas animadas que representan el tráfico de datos.
*   **💍 Resiliencia y Redundancia**: Crea anillos industriales y evalúa cómo el sistema sobrevive a fallos mediante el cálculo automático de rutas alternativas.
*   **🛠️ Inyección de Fallos Interactiva**: Induce fallos manuales, aleatorios o mediante clics directos sobre los cables para ver la respuesta del sistema.
*   **🎓 Sistema de Entrenamiento Progresivo**: 3 niveles de ejercicios guiados con validación automática y lecciones pedagógicas integradas.
*   **📊 Reportes Profesionales**: Generación de informes en PDF con KPIs de rendimiento y estado de los dispositivos.

---

## 🚀 Instalación y Uso Rápido

### Requisitos Previos
*   **Python 3.10+** instalado en el sistema.

### Instalación (Windows)
El proyecto incluye un script de instalación automática. Simplemente:

1.  **Descarga** o clona este repositorio:
    ```bash
    git clone https://github.com/Ivancitoo-N/industrial-network-simulator.git
    cd industrial-network-simulator
    ```
2.  Ejecuta el asistente de instalación:
    ```cmd
    install_and_run.bat
    ```
3.  Abre tu navegador en [http://localhost:5000](http://localhost:5000).

---

## 🛠️ Tecnologías Utilizadas

*   **Backend**: Python, Flask, Flask-SocketIO (Real-time events).
*   **Motor de Red**: NetworkX (Algoritmos de grafos).
*   **Frontend**: HTML5, Vanilla CSS, D3.js (Visualización).
*   **Reportes**: ReportLab (Generación de PDF profesional).
*   **Modelado de Datos**: Pydantic V2.

---

## 📖 Guía de Uso del Simulador

1.  **Añadir Dispositivos**: Usa el panel lateral para elegir entre PLCs, Servos o Módulos IO-Link.
2.  **Configurar Nombres**: Haz **doble clic** en cualquier nodo para personalizar su nombre según tu proyecto real.
3.  **Simular Fallos**: Haz clic en cualquier "cable" para cortarlo, o usa el **Fallo Aleatorio 🎲** para estresar la red.
4.  **Reparar**: Haz clic en cualquier nodo gris (`OFFLINE`) para restaurar su servicio instantáneamente.
5.  **Entrenamiento**: Sigue las instrucciones de la sección inferior para completar los retos de diseño de red.

---

## 🤝 Contribuciones e Ideas

¿Tienes alguna idea para mejorar el simulador? ¡Las contribuciones son bienvenidas! Siéntete libre de abrir un **Issue** o enviar un **Pull Request**.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

Desarrollado con ❤️ para la comunidad de automatización industrial. 🚀🏗️
