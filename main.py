from dataclasses import dataclass, replace
import pygraphviz as pgv

accuracy = .65 

@dataclass
class Transition:
    label: str
    weight: float
    target: object

@dataclass
class State:
    attacks: int
    bonusActions: int
    hasInspiration: bool
    hasCriticaled: bool
    transitions: list
    
    def to_label(self):
        return f"A:{self.attacks}\\nBA:{self.bonusActions}\\nI:{self.hasInspiration}\\nC:{self.hasCriticaled}"

def addHit(state: State):
    newState = replace(state, attacks=state.attacks - 1, transitions=[])
    process(newState)
    transition = Transition(label="Hit", weight=accuracy, target=newState)
    state.transitions.append(transition)

def addInspiredHit(state: State):
    newState = replace(state, attacks=state.attacks - 1, hasInspiration=False, transitions=[])  
    process(newState)
    transition = Transition(label="InspiredHit", weight=accuracy, target=newState)
    state.transitions.append(transition)

def addMiss(state: State):
    newState = replace(state, attacks=state.attacks - 1, transitions=[]) 
    process(newState)
    transition = Transition(label="Miss", weight=1-accuracy, target=newState)
    state.transitions.append(transition)

def addCritical(state: State):
    newState = replace(state, attacks=state.attacks - 1, hasCriticaled=True, transitions=[]) 
    process(newState)
    transition = Transition(label="Critical", weight=0.05, target=newState)
    state.transitions.append(transition)

def addHew(state: State):
    newState = replace(state, bonusActions=state.bonusActions-1, transitions=[])
    process(newState)
    transition = Transition(label="Hew", weight=1.0, target=newState)
    state.transitions.append(transition)

def process(state: State):
    if state.attacks > 0:
        addHit(state)
        if state.hasInspiration:
            addInspiredHit(state)
        addMiss(state)
        addCritical(state)
    elif state.bonusActions > 0 and state.hasCriticaled:
        addHew(state)

def render_graph(start_state: State, filename: str = "state_graph.png"):
    G = pgv.AGraph(directed=True, strict=False)
    G.graph_attr['nodesep'] = 0.5
    G.graph_attr['ranksep'] = 5
    # G.node_attr['shape'] = 'box'
    # G.node_attr['style'] = 'rounded'
    
    visited = set()
    
    def add_nodes_and_edges(state: State):
        state_id = id(state)
        if state_id in visited:
            return
        visited.add(state_id)
        
        # Add node for current state
        G.add_node(state_id, label=state.to_label())
        
        # Add edges to target states
        for transition in state.transitions:
            target_id = id(transition.target)
            G.add_node(target_id, label=transition.target.to_label())
            G.add_edge(state_id, target_id, 
                      label=f"{transition.label}\\n{transition.weight:.2f}",
                      weight=transition.weight)
            
            # Recursively process target state
            add_nodes_and_edges(transition.target)
    
    add_nodes_and_edges(start_state)
    G.layout(prog='twopi')
    G.draw(filename)
    print(f"Graph saved to {filename}")

def main():
    start = State(attacks=3, bonusActions=1, hasInspiration=True, hasCriticaled=False, transitions=[])
    process(start)
    render_graph(start, "dnd_state_graph.png")
    print("State graph rendered!")

if __name__ == "__main__":
    main()
