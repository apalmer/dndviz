from dataclasses import dataclass, replace
import pygraphviz as pgv

accuracy = .65 
adv_rate = 0.5
crit_rate = 0.05

adv_accuracy = 1 - ((1 - accuracy) * (1 - accuracy))
adv_crit_rate = 1 - ((1 - crit_rate) * (1 - crit_rate))

hew_dice_damage = 3.25
weapon_dice_damage = 5.8
other_damage = 9

def damage(dice_damage:float, is_critical:bool):
    if is_critical:
        return (2 * dice_damage) + other_damage
    else:
        return (dice_damage + other_damage)

@dataclass
class Transition:
    label: str
    weight: float
    target: object

@dataclass
class State:
    attacks: int
    bonusActions: int
    hasAdvantage: bool
    hasInspiration: bool
    hasCriticaled: bool
    accuracy: float
    crit_rate: float
    reciever: object
    action: callable
    trigger: callable
    transitions: list
    
    def to_label(self):
        return f"A:{self.attacks}\\nBA:{self.bonusActions}\\nAdv:{self.hasAdvantage}\\nI:{self.hasInspiration}\\nC:{self.hasCriticaled}"

def calcHitProb(state: State):
    return (1 - adv_rate) * (state.accuracy - state.crit_rate) 

def calcHitAdvProb(state: State):
    return (adv_rate) * (state.accuracy - state.crit_rate)

def calcCritProb(state: State):
    return (1 - adv_rate) * (state.crit_rate)

def calcCritAdvProb(state: State):
    return (adv_rate) * (state.crit_rate)

def calcInspiredHitProb(state: State):
    return (1 - adv_rate) * ((1 - state.accuracy) * state.accuracy)

def calcInspiredHitAdvProb(state: State):
    return (adv_rate) * ((1 - state.accuracy) * state.accuracy)

def calcInspiredMissProb(state: State):
    return (1 - state.accuracy) * (1 - state.accuracy) 

def calcMissProb(state: State):
    return 1 - state.accuracy

def calcHewProb(state: State):
    return 1

def add_transition(state: State, label: str, weight_func, state_kwargs: dict):
    newState = replace(state, **state_kwargs, transitions=[])
    process(newState)
    transition = Transition(label=label, weight=weight_func(state), target=newState)
    state.transitions.append(transition)

def addHit(state: State):
    on_action = lambda state: state.trigger('Hit', damage(weapon_dice_damage, False))
    add_transition(state, "Hit", calcHitProb, {"attacks": state.attacks - 1, "action": on_action})

def addHitAdvantage(state: State):
    on_action = lambda state: state.trigger('Hit', damage(weapon_dice_damage, False))
    add_transition(state, "HitAdv", calcHitAdvProb, {"attacks": state.attacks - 1, "hasAdvantage": True, "accuracy":adv_accuracy, "crit_rate":adv_crit_rate, "action": on_action})

def addCritical(state: State):
    on_action = lambda state: state.trigger('CriticalHit', damage(weapon_dice_damage, True))
    add_transition(state, "Critical", calcCritProb, {"attacks": state.attacks - 1, "hasCriticaled": True, "action": on_action})

def addCriticalAdvantage(state: State):
    on_action = lambda state: state.trigger('CriticalHit', damage(weapon_dice_damage, True))
    add_transition(state, "CriticalAdv", calcCritAdvProb, {"attacks": state.attacks - 1, "hasCriticaled": True, "hasAdvantage": True, "accuracy":adv_accuracy, "crit_rate":adv_crit_rate, "action": on_action})

def addInspiredHit(state: State):
    on_action = lambda state: state.trigger('Hit', damage(weapon_dice_damage, False))
    add_transition(state, "InspiredHit", calcInspiredHitProb, {"attacks": state.attacks - 1, "hasInspiration": False, "action": on_action})

def addInspiredHitAdvantage(state: State):
    on_action = lambda state: state.trigger('Hit', damage(weapon_dice_damage, False))
    add_transition(state, "InspiredHitAdv", calcInspiredHitAdvProb, {"attacks": state.attacks - 1, "hasInspiration": False, "hasAdvantage": True, "accuracy":adv_accuracy, "crit_rate":adv_crit_rate, "action": on_action})

def addInspiredMiss(state: State):
    add_transition(state, "InspiredMiss", calcInspiredMissProb, {"attacks": state.attacks - 1, "hasInspiration": False})

def addMiss(state: State):
    add_transition(state, "HewMiss", calcMissProb, {"attacks": state.attacks - 1})
    
def addHitBA(state: State):
    on_action = lambda state: state.trigger('Hit', damage(weapon_dice_damage, False))
    add_transition(state, "HewHit", calcHitProb, {"bonusActions": state.bonusActions - 1, "action": on_action})

def addHitAdvantageBA(state: State):
    on_action = lambda state: state.trigger('Hit', damage(weapon_dice_damage, False))
    add_transition(state, "HewHitAdv", calcHitAdvProb, {"bonusActions": state.bonusActions - 1, "hasAdvantage": True, "accuracy":adv_accuracy, "crit_rate":adv_crit_rate, "action": on_action})

def addCriticalBA(state: State):
    on_action = lambda state: state.trigger('CriticalHit', damage(weapon_dice_damage, True))
    add_transition(state, "HewCritical", calcCritProb, {"bonusActions": state.bonusActions - 1, "hasCriticaled": True, "action": on_action})

def addCriticalAdvantageBA(state: State):
    on_action = lambda state: state.trigger('CriticalHit', damage(weapon_dice_damage, True))
    add_transition(state, "HewCriticalAdv", calcCritAdvProb, {"bonusActions": state.bonusActions - 1, "hasCriticaled": True, "hasAdvantage": True, "accuracy":adv_accuracy, "crit_rate":adv_crit_rate, "action": on_action})

def addInspiredHitBA(state: State):
    on_action = lambda state: state.trigger('Hit', damage(weapon_dice_damage, False))
    add_transition(state, "HewInspiredHit", calcInspiredHitProb, {"bonusActions": state.bonusActions - 1, "hasInspiration": False, "action": on_action})

def addInspiredHitAdvantageBA(state: State):
    on_action = lambda state: state.trigger('Hit', damage(weapon_dice_damage, False))
    add_transition(state, "HewInspiredHitAdv", calcInspiredHitAdvProb, {"bonusActions": state.bonusActions - 1, "hasInspiration": False, "hasAdvantage": True, "accuracy":adv_accuracy, "crit_rate":adv_crit_rate, "action": on_action})

def addInspiredMissBA(state: State):
    add_transition(state, "HewInspiredMiss", calcInspiredMissProb, {"bonusActions": state.bonusActions - 1, "hasInspiration": False})

def addMissBA(state: State):
    add_transition(state, "HewMiss", calcMissProb, {"bonusActions": state.bonusActions - 1})


def addAttackTrasitions(state):
    addHit(state)
    addHitAdvantage(state)
    addCritical(state)
    addCriticalAdvantage(state)
    if state.hasInspiration:
        addInspiredHit(state)
        addInspiredHitAdvantage(state)
        addInspiredMiss(state)
    else: 
        addMiss(state)

def addHewTrasitions(state):
    addHit(state)
    addHitAdvantageBA(state)
    addCriticalBA(state)
    addCriticalAdvantageBA(state)
    if state.hasInspiration:
        addInspiredHitBA(state)
        addInspiredHitAdvantageBA(state)
        addInspiredMissBA(state)
    else: 
        addMissBA(state)

def process(state: State):
    if state.attacks > 0:
        addAttackTrasitions(state)
    elif state.bonusActions > 0:
        if state.hasCriticaled:
            addHewTrasitions(state)

def render_graph(start_state: State, filename: str = "state_graph.png"):
    G = pgv.AGraph(directed=True, strict=False)
    G.graph_attr['nodesep'] = 1
    G.graph_attr['ranksep'] = 20
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
                      label=f"{transition.label}\\n{transition.weight:.3f}",
                      weight=transition.weight)
            
            # Recursively process target state
            add_nodes_and_edges(transition.target)
    
    add_nodes_and_edges(start_state)
    G.layout(prog='twopi')
    G.draw(filename)
    print(f"Graph saved to {filename}")

def find_max_damage(start_state: State):
    # find_max_damage_transition = lambda transition: if label
    # # damage it does
    # # damageHandler = 

    # max_child_damage = 0
    # for transition in start_state.transitions:
    #     child_damage = find_max_damage_transition(transition)
    #     if(child_damage > max_child_damage):
    #         max_child_damage = child_damage
    
    # return damage + max_child_damage
    pass

def main():
    start = State(attacks=3, bonusActions=1, hasInspiration=True, hasCriticaled=False, hasAdvantage=False, accuracy=accuracy, crit_rate=crit_rate, opponent_health=0, transitions=[])
    process(start)
    find_max_damage(start)
    render_graph(start, "dnd_state_graph.png")
    print("State graph rendered!")

if __name__ == "__main__":
    main()
