import networkx as nx
from engine.validation_engine import ValidationEngine

def test_validation_logic():
    graph = nx.Graph()
    graph.add_node("PLC_1")
    graph.add_node("Switch_1")
    graph.add_edge("PLC_1", "Switch_1")
    
    print("--- Test 1: Simple Valid Connection ---")
    val = ValidationEngine.validate_connection(graph, "Servo_A", "Switch_1", "Drive")
    print(f"Is Valid: {val['is_valid']}, Errors: {val['errors']}")
    assert val['is_valid'] == True
    
    print("\n--- Test 2: Cycle Detection (Loop) ---")
    # Adding Switch_2 connected to Switch_1
    graph.add_node("Switch_2")
    graph.add_edge("Switch_1", "Switch_2")
    # Trying to connect Switch_2 directly back to PLC_1 (Infinite Loop)
    val = ValidationEngine.validate_connection(graph, "Switch_2", "PLC_1", "Switch")
    print(f"Is Valid: {val['is_valid']}, Errors: {val['errors']}")
    assert val['is_valid'] == False
    assert "Bucle infinito" in val['errors'][0]
    
    print("\n--- Test 3: Training Exercise Validation ---")
    val = ValidationEngine.validate_connection(graph, "Servo_2", "PLC_1", "Drive")
    print(f"Is Valid: {val['is_valid']}, Errors: {val['errors']}")
    assert val['is_valid'] == False
    assert "entrenamiento" in val['errors'][0].lower()

    print("\nAll validation tests passed successfully!")

if __name__ == "__main__":
    test_validation_logic()
