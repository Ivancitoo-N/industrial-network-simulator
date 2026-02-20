# Industrial Network Simulator — Documentation 📘

## Arquitectura del Sistema
El simulador utiliza una arquitectura **Híbrida Event-Driven**:
- **Backend (Python/Flask)**: Gestiona la lógica de grafos con **NetworkX**. Cada "arista" tiene un peso que representa la latencia base ($T_{prop}$).
- **Frontend (D3.js)**: Renderiza la topología en tiempo real y simula el tráfico de paquetes mediante partículas animadas.

## Protocolos Simulados

### 1. PROFINET (IRT/RT)
- **IRT (Isochronous Real-Time)**: Latencia constante, jitter despreciable (< 1µs simulado). Ideal para control de movimiento síncrono.
- **RT (Real-Time)**: Latencia basada en saltos entre switches + jitter aleatorio (0.01ms - 0.05ms). Utiliza priorización de frames.

### 2. EtherCAT
- Simula la arquitectura "Master/Slave" donde la latencia es una función lineal del número de nodos en el bus:
  $L = N \times t_{proc} + \frac{Size}{Speed}$

### 3. Modbus TCP
- Basado en TCP estándar. Presenta el mayor jitter simulado (0.1ms - 0.5ms) debido a la pila TCP/IP convencional.

## Guía de Uso
1. Ejecuta `install_and_run.bat`.
2. Accede a `http://localhost:5000`.
3. Añade un PLC (Master) primero.
4. Añade Drives o IO-Link seleccionando el nodo de conexión para construir la topología.
5. **Simulación de Fallos**: Haz clic en cualquier enlace (línea) para "cortarlo". El sistema recalculará el camino y marcará los dispositivos aislados como `OFFLINE`.

## API Endpoints
- `GET /api/devices`: Retorna la topología actual.
- `POST /api/devices`: Añade un nuevo nodo.
- `POST /api/link`: Activa/Desactiva un enlace físico.
