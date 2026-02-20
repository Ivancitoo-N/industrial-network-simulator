import pytest
import os
import sys
# Add current dir to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.network_engine import NetworkEngine, Device, DeviceType, Protocol, DeviceStatus

@pytest.fixture
def engine():
    return NetworkEngine()

def test_topology_management(engine):
    # Add PLC
    plc = Device(id="PLC_1", type=DeviceType.PLC)
    engine.add_device(plc)
    
    # Add Drive
    drive = Device(id="Drive_1", type=DeviceType.DRIVE)
    engine.add_device(drive, connect_to="PLC_1")
    
    topo = engine.get_topology()
    assert len(topo['nodes']) == 2
    assert len(topo['links']) == 1
    link = topo['links'][0]
    nodes = {link['source'], link['target']}
    assert nodes == {"Drive_1", "PLC_1"}

def test_fault_detection(engine):
    plc = Device(id="PLC_1", type=DeviceType.PLC)
    engine.add_device(plc)
    
    drive = Device(id="Drive_1", type=DeviceType.DRIVE)
    engine.add_device(drive, connect_to="PLC_1")
    
    # Break link
    engine.set_link_status("PLC_1", "Drive_1", False)
    
    perf = engine.calculate_performance()
    drive_perf = next(p for p in perf if p['id'] == "Drive_1")
    assert drive_perf['status'] == DeviceStatus.OFFLINE
    assert drive_perf['latency_ms'] == -1

def test_protocol_jitter(engine):
    plc = Device(id="PLC_1", type=DeviceType.PLC)
    engine.add_device(plc)
    
    # Modbus TCP (High jitter)
    modbus_dev = Device(id="Modbus_Dev", type=DeviceType.IOLINK, protocol=Protocol.MODBUS_TCP)
    engine.add_device(modbus_dev, connect_to="PLC_1")
    
    # EtherCAT (Low jitter)
    ethercat_dev = Device(id="EtherCAT_Dev", type=DeviceType.DRIVE, protocol=Protocol.ETHERCAT)
    engine.add_device(ethercat_dev, connect_to="PLC_1")
    
    perf = engine.calculate_performance()
    m_perf = next(p for p in perf if p['id'] == "Modbus_Dev")
    e_perf = next(p for p in perf if p['id'] == "EtherCAT_Dev")
    
    # Jitter comparison (statistical, might fail once in a blue moon but should pass)
    assert m_perf['jitter_ms'] > 0.05
    assert e_perf['jitter_ms'] < 0.01

def test_iot_link_propagation(engine):
    plc = Device(id="PLC", type=DeviceType.PLC)
    engine.add_device(plc)
    
    sw = Device(id="SW", type=DeviceType.SWITCH)
    engine.add_device(sw, connect_to="PLC")
    
    dr = Device(id="DR", type=DeviceType.DRIVE)
    engine.add_device(dr, connect_to="SW")
    
    perf = engine.calculate_performance()
    dr_perf = next(p for p in perf if p['id'] == "DR")
    
    # Expected latency: 0.1ms (PLC-SW) + 0.1ms (SW-DR) + Jitter
    assert dr_perf['latency_ms'] > 0.2
