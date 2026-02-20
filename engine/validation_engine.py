import networkx as nx

class ValidationEngine:
    @staticmethod
    def validate_connection(graph, source_id, target_id, device_type):
        """
        Analyzes the graph to prevent topology errors.
        - Detects infinite loops (cycles) in non-ring protocols.
        - Validates industrial VLAN segments (simulated).
        """
        errors = []
        
        # 1. Loop Detection
        # Industrial ethernet (except MRP/HSR rings) should typically be tree-like
        # If adding an edge creates a cycle, we need to flag it.
        temp_graph = graph.copy()
        temp_graph.add_edge(source_id, target_id)
        
        try:
            cycles = nx.find_cycle(temp_graph, orientation='original')
            if cycles:
                # In this simulator, we only allow rings if explicitly configured (future expansion)
                # For now, we flag it as a risk of broadcast storm.
                errors.append("RIESGO: Bucle infinito detectado (Tormenta de broadcast). Use un Switch con STP/MRP.")
        except nx.NetworkXNoCycle:
            pass
            
        # 2. VLAN / Segment Validation
        # Rule: Servo Drives should not be connected directly to public IPs or different subnets
        # (Simplified check for this training module)
        if device_type == "Drive" and "Main_PLC" not in [source_id, target_id]:
             # Check if it's connected to a Switch at least
             pass # Placeholder for more complex VLAN logic
             
        # 3. Training specific validation
        # Exercise 1: Connect Servo_2 to SCALANCE_1
        if source_id == "Servo_2" and target_id != "SCALANCE_1":
            errors.append("ENTRENAMIENTO: Para completar el ejercicio 1, debe conectar el Servo_2 al Switch SCALANCE.")

        # Exercise 2: Ring closure
        if source_id == "SCALANCE_2" and target_id not in ["SCALANCE_1", "S7-1500_Main"]:
             errors.append("ENTRENAMIENTO: Conecta el SCALANCE_2 a SCALANCE_1 o al PLC para avanzar en el anillo.")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
