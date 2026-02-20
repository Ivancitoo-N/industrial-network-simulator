import networkx as nx
import random
import time
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel

class Protocol(str, Enum):
    PROFINET_RT = "PROFINET_RT"
    PROFINET_IRT = "PROFINET_IRT"
    ETHERCAT = "EtherCAT"
    MODBUS_TCP = "Modbus TCP"

class DeviceType(str, Enum):
    PLC = "PLC"
    DRIVE = "Drive"
    IOLINK = "IO-Link"
    SWITCH = "Switch"

class DeviceStatus(str, Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"
    ALARM = "Alarm"
    SAFETY_MODE = "Safety Mode"

class Device(BaseModel):
    id: str
    type: DeviceType
    ip: Optional[str] = None
    status: DeviceStatus = DeviceStatus.ONLINE
    protocol: Protocol = Protocol.PROFINET_RT
    cycle_time_ms: float = 1.0  # Configured cycle time
    display_name: Optional[str] = None

class NetworkEngine:
    def __init__(self):
        self.graph = nx.Graph()
        self.devices: Dict[str, Device] = {}
        self.controller_id: Optional[str] = None
        self.safety_active: bool = False

    def rename_device(self, device_id: str, new_name: str):
        if device_id in self.devices:
            self.devices[device_id].display_name = new_name
            return True
        return False
        
    def trigger_random_fault(self):
        # Exclude PLC from random faults to avoid total network death unless desired
        eligible = [d_id for d_id, d in self.devices.items() if d.type != DeviceType.PLC]
        if eligible:
            target = random.choice(eligible)
            self.devices[target].status = DeviceStatus.OFFLINE
            self.safety_active = True
            return target
        return None

    def add_device(self, device: Device, connect_to: Optional[str] = None):
        """Adds a device to the topology and connects it to an existing node."""
        self.devices[device.id] = device
        self.graph.add_node(device.id, data=device)
        
        if device.type == DeviceType.PLC:
            self.controller_id = device.id

        if connect_to and connect_to in self.devices:
            # Base propagation delay 0.1ms per link
            self.graph.add_edge(device.id, connect_to, weight=0.1, active=True)

    def remove_device(self, device_id: str):
        if device_id in self.devices:
            self.graph.remove_node(device_id)
            del self.devices[device_id]
            if self.controller_id == device_id:
                self.controller_id = None

    def set_link_status(self, u: str, v: str, active: bool):
        """Simulates physical cable connection/disconnection. Adds link if it doesn't exist."""
        if not self.graph.has_edge(u, v):
            self.graph.add_edge(u, v, weight=0.1, active=active)
        else:
            self.graph[u][v]['active'] = active

    def calculate_performance(self) -> List[Dict]:
        """Calculates latency and status for all devices relative to the PLC."""
        if not self.controller_id:
            return []

        results = []
        
        # Create a view of the graph with only ACTIVE edges AND ONLINE nodes
        online_nodes = [node_id for node_id, dev in self.devices.items() if dev.status != DeviceStatus.OFFLINE]
        active_edges = [
            (u, v) for u, v, d in self.graph.edges(data=True) 
            if d.get('active', True) and u in online_nodes and v in online_nodes
        ]
        
        active_graph = nx.Graph()
        active_graph.add_nodes_from(online_nodes)
        active_graph.add_edges_from(active_edges)

        for dev_id, device in self.devices.items():
            if dev_id == self.controller_id:
                continue

            try:
                # 1. Connectivity Check
                if nx.has_path(active_graph, self.controller_id, dev_id):
                    path = nx.shortest_path(active_graph, self.controller_id, dev_id, weight='weight')
                    
                    # 2. Latency Logic
                    # L = Sum(PropDelay) + Sum(SwitchProcDelay) + ProtocolOverhead
                    base_latency = 0.0
                    for i in range(len(path) - 1):
                        base_latency += self.graph[path[i]][path[i+1]]['weight']
                    
                    # Protocolspecific Jitter
                    jitter = 0.0
                    if device.protocol == Protocol.PROFINET_RT:
                        jitter = random.uniform(0.01, 0.05)
                    elif device.protocol == Protocol.MODBUS_TCP:
                        jitter = random.uniform(0.1, 0.5)
                    elif device.protocol == Protocol.PROFINET_IRT or device.protocol == Protocol.ETHERCAT:
                        jitter = random.uniform(0.001, 0.005) # Very low jitter

                    total_latency = base_latency + jitter
                    
                    # Resilience logic: if path is longer than original, it's a backup path
                    # (Simplified: if we have to use more than 1 hop for a simple connection)
                    status = DeviceStatus.ONLINE
                    if len(path) > 2: # Potential redundant path being used
                         status = DeviceStatus.ALARM
                    
                    if total_latency >= (device.cycle_time_ms * 2):
                        status = DeviceStatus.ALARM

                    results.append({
                        "id": dev_id,
                        "latency_ms": round(total_latency, 3),
                        "jitter_ms": round(jitter, 3),
                        "status": status,
                        "path": path,
                        "redundant": len(path) > 2
                    })
                else:
                    results.append({
                        "id": dev_id,
                        "latency_ms": -1,
                        "jitter_ms": 0,
                        "status": DeviceStatus.OFFLINE,
                        "path": [],
                        "redundant": False
                    })
            except Exception as e:
                print(f"Error calculating performance for {dev_id}: {e}")

        return results

    def get_topology(self) -> Dict:
        """Returns JSON-friendly topology for D3.js."""
        nodes = []
        for dev_id, device in self.devices.items():
            nodes.append({
                "id": dev_id,
                "type": device.type,
                "protocol": device.protocol,
                "status": device.status,
                "display_name": device.display_name or device.id
            })
        
        links = []
        for u, v, d in self.graph.edges(data=True):
            links.append({
                "source": u,
                "target": v,
                "active": d.get('active', True),
                "weight": d.get('weight', 0.1)
            })
            
        return {"nodes": nodes, "links": links}
