from engine.network_engine import NetworkEngine, Device, DeviceType, Protocol, DeviceStatus

def test_simulation_logic():
    engine = NetworkEngine()
    
    # 1. Add PLC
    plc = Device(id="PLC_1", type=DeviceType.PLC, protocol=Protocol.PROFINET_IRT)
    engine.add_device(plc)
    
    # 2. Add devices
    drive = Device(id="Drive_1", type=DeviceType.DRIVE, protocol=Protocol.PROFINET_RT, cycle_time_ms=2.0)
    engine.add_device(drive, connect_to="PLC_1")
    
    io_link = Device(id="IO_Link_1", type=DeviceType.IOLINK, protocol=Protocol.MODBUS_TCP, cycle_time_ms=10.0)
    engine.add_device(io_link, connect_to="Drive_1")
    
    print("--- Topology Test ---")
    topo = engine.get_topology()
    print(f"Nodes: {[n['id'] for n in topo['nodes']]}")
    print(f"Links: {len(topo['links'])}")
    
    # 3. Calculate Performance (Healthy)
    print("\n--- Performance Test (Normal) ---")
    results = engine.calculate_performance()
    for res in results:
        print(f"ID: {res['id']}, Latency: {res['latency_ms']}ms, Status: {res['status']}")
        assert res['status'] != DeviceStatus.OFFLINE
    
    # 4. Physical Break (Cable between PLC and Drive)
    print("\n--- Fault Test (Link Failure) ---")
    engine.set_link_status("PLC_1", "Drive_1", False)
    results = engine.calculate_performance()
    for res in results:
        print(f"ID: {res['id']}, Status: {res['status']}")
        assert res['status'] == DeviceStatus.OFFLINE

    print("\nTest passed successfully!")

if __name__ == "__main__":
    test_simulation_logic()
