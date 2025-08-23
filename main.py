from dataclasses import dataclass, replace

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
    transition = Transition(label="Miss", weight=accuracy, target=newState)
    state.transitions.append(transition)

def addCritical(state: State):
    newState = replace(state, attacks=state.attacks - 1, hasCriticaled=True, transitions=[]) 
    process(newState)
    transition = Transition(label="Critical", weight=accuracy, target=newState)
    state.transitions.append(transition)

def addHew(state: State):
    newState = replace(state, bonusActions=state.bonusActions-1, transitions=[])
    process(newState)
    transition = Transition(label="Hew", weight=accuracy, target=newState)
    state.transitions.append(transition)

def process(state: State):
    if state.attacks > 0:
        addHit(state)
        if state.hasInspiration:
            addInspiredHit(state)
        addMiss(state)
        addCritical(state)
    if state.bonusActions > 0 and state.hasCriticaled:
        addHew(state)

def main():
    start = State(attacks=3, bonusActions=1, hasInspiration=True, hasCriticaled=False, transitions=[])
    process(start)
    print(start)

if __name__ == "__main__":
    main()
