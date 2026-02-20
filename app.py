import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import os
from engine.network_engine import NetworkEngine, Device, DeviceType, Protocol, DeviceStatus
from engine.export_service import ExportService
from engine.validation_engine import ValidationEngine
from flask import send_file

app = Flask(__name__)
app.config['SECRET_KEY'] = 'industrial-secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', manage_session=False)

# Core engine instance
engine = NetworkEngine()

# Initialize with a default PLC
default_plc = Device(id="S7-1500_Main", type=DeviceType.PLC, ip="192.168.0.1", protocol=Protocol.PROFINET_IRT)
engine.add_device(default_plc)

def simulation_loop():
    """Background thread to update performance metrics and push to UI."""
    while True:
        perf = engine.calculate_performance()
        topo = engine.get_topology()
        
        socketio.emit('network_update', {
            'performance': perf,
            'topology': topo,
            'safety_active': engine.safety_active,
            'timestamp': time.time()
        })
        time.sleep(1.0)

def broadcast_update():
    """Triggers an immediate update to all clients."""
    with app.app_context():
        perf = engine.calculate_performance()
        topo = engine.get_topology()
        socketio.emit('network_update', {
            'performance': perf,
            'topology': topo,
            'safety_active': engine.safety_active,
            'timestamp': time.time()
        })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/devices', methods=['GET'])
def get_devices():
    return jsonify(engine.get_topology())

@app.route('/api/devices', methods=['POST'])
def add_device():
    data = request.json
    try:
        # 1. Topology Validation
        validation = ValidationEngine.validate_connection(
            engine.graph, 
            data['id'], 
            data.get('connect_to'),
            data['type']
        )
        
        if not validation['is_valid']:
            return jsonify({"status": "warn", "message": validation['errors'][0]}), 200

        # 2. Add Device
        new_dev = Device(
            id=data['id'],
            type=DeviceType(data['type']),
            ip=data.get('ip'),
            protocol=Protocol(data.get('protocol', Protocol.PROFINET_RT)),
            cycle_time_ms=float(data.get('cycle_time', 1.0))
        )
        engine.add_device(new_dev, connect_to=data.get('connect_to'))
        return jsonify({"status": "ok", "device": new_dev.model_dump()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/devices/<device_id>', methods=['PATCH'])
def rename_device(device_id):
    data = request.json
    new_name = data.get('display_name')
    if not new_name:
        return jsonify({"status": "error", "message": "display_name is required"}), 400
    
    if engine.rename_device(device_id, new_name):
        broadcast_update()
        return jsonify({"status": "ok", "new_name": new_name})
    return jsonify({"status": "error", "message": "Device not found"}), 404

@app.route('/api/link', methods=['POST'])
def manage_link():
    data = request.json
    engine.set_link_status(data['u'], data['v'], data['active'])
    broadcast_update()
    return jsonify({"status": "ok"})
@app.route('/api/export', methods=['GET'])
def export_report():
    topo = engine.get_topology()
    perf = engine.calculate_performance()
    
    report_path = os.path.join(os.getcwd(), "network_report.pdf")
    ExportService.generate_pdf_report(topo, perf, report_path)
    
    return send_file(report_path, as_attachment=True)

@socketio.on('trigger_fault')
def handle_fault(data):
    device_id = data.get('device_id')
    
    if data.get('random'):
        device_id = engine.trigger_random_fault()
        if device_id:
            print(f"Random fault triggered for {device_id}")
            broadcast_update()
            emit('fault_acknowledged', {'status': 'ok', 'device_id': device_id}, broadcast=True)
        return

    if device_id in engine.devices:
        device = engine.devices[device_id]
        if device.status != DeviceStatus.OFFLINE:
            device.status = DeviceStatus.OFFLINE
            engine.safety_active = True
        else:
            device.status = DeviceStatus.ONLINE
            # Check if any other device is offline before clearing safety_active
            any_offline = any(d.status == DeviceStatus.OFFLINE for d in engine.devices.values() if d.type != DeviceType.PLC)
            engine.safety_active = any_offline
            
        print(f"Fault toggled for {device_id}: {device.status}")
        broadcast_update()
        emit('fault_acknowledged', {'status': 'ok', 'device_id': device_id}, broadcast=True)

@socketio.on('restore_all')
def handle_restore_all():
    for device in engine.devices.values():
        device.status = DeviceStatus.ONLINE
    engine.safety_active = False
    print("System restored: All devices ONLINE")
    broadcast_update()
    emit('fault_acknowledged', {'status': 'ok', 'all': True}, broadcast=True)

if __name__ == '__main__':
    # Start simulation in a background task compatible with SocketIO/Eventlet
    socketio.start_background_task(simulation_loop)
    
    print("Industrial Network Simulator Backend running on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
