from dataclasses import dataclass

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
    newState = State( attacks=state.attacks - 1, bonusActions=state.bonusActions, hasInspiration=state.hasInspiration, hasCriticaled=state.hasCriticaled, transitions=[])
    process(newState)
    return Transition(label="Hit", weight=accuracy, target=newState)

def addInspiredHit(state: State):
    newState = State(attacks=state.attacks - 1, bonusActions=state.bonusActions, hasInspiration=False, hasCriticaled=state.hasCriticaled, transitions=[])
    process(newState)
    return Transition(label="InspiredHit", weight=accuracy, target=newState)

def addMiss(state: State):
    newState = State(attacks=state.attacks - 1, bonusActions=state.bonusActions, hasInspiration=state.hasInspiration, hasCriticaled=state.hasCriticaled, transitions=[])
    process(newState)
    return Transition(label="Miss", weight=accuracy, target=newState)

def addCritical(state: State):
    newState = State(attacks=state.attacks - 1, bonusActions=state.bonusActions, hasInspiration=state.hasInspiration, hasCriticaled=True, transitions=[])
    process(newState)
    return Transition(label="Critical", weight=accuracy, target=newState)

def addHew(state: State):
    newState = State(attacks=state.attacks, bonusActions=state.bonusActions -1, hasInspiration=state.hasInspiration, hasCriticaled=state.hasCriticaled, transitions=[])
    process(newState)
    return Transition(label="Hew", weight=accuracy, target=newState)

def process(state: State):
    if state.attacks > 0:
        state.transitions.append(addHit(state))
        if state.hasInspiration:
            state.transitions.append(addInspiredHit(state))
        state.transitions.append(addMiss(state))
        state.transitions.append(addCritical(state))
    if state.bonusActions > 0 and state.hasCriticaled:
        state.transitions.append(addHew(state))

def main():
    start = State(attacks=3, bonusActions=1, hasInspiration=True, hasCriticaled=False, transitions=[])
    possibilities = process(start)

if __name__ == "__main__":
    main()
