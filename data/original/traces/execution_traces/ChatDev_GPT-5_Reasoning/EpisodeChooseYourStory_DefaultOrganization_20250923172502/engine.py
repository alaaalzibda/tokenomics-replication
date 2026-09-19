'''
Core story engine: state management, condition evaluation, nodes and choices, and progression logic.
'''
from typing import Dict, List, Optional, Any, Set
class GameState:
    """
    Tracks items, variables, relationships, flags, and visited nodes.
    """
    def __init__(self):
        self.items: Set[str] = set()
        self.variables: Dict[str, int] = {}
        self.relationships: Dict[str, int] = {}
        self.flags: Dict[str, bool] = {}
        self.visited_nodes: List[str] = []
    # Items
    def add_item(self, item: str):
        self.items.add(item)
    def remove_item(self, item: str):
        self.items.discard(item)
    def has_item(self, item: str) -> bool:
        return item in self.items
    # Variables
    def adjust_var(self, name: str, delta: int):
        self.variables[name] = self.variables.get(name, 0) + int(delta)
    def set_var(self, name: str, value: int):
        self.variables[name] = int(value)
    def get_var(self, name: str, default: int = 0) -> int:
        return self.variables.get(name, default)
    # Relationships
    def adjust_relationship(self, name: str, delta: int):
        self.relationships[name] = self.relationships.get(name, 0) + int(delta)
    def get_relationship(self, name: str, default: int = 0) -> int:
        return self.relationships.get(name, default)
    # Flags
    def set_flag(self, name: str, value: bool):
        self.flags[name] = bool(value)
    def is_flag(self, name: str) -> bool:
        return bool(self.flags.get(name, False))
    # Visited nodes
    def mark_visited(self, node_id: str):
        self.visited_nodes.append(node_id)
    # Serialization
    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": sorted(list(self.items)),
            "variables": dict(self.variables),
            "relationships": dict(self.relationships),
            "flags": dict(self.flags),
            "visited_nodes": list(self.visited_nodes),
        }
    def from_dict(self, data: Dict[str, Any]):
        self.items = set(data.get("items", []))
        self.variables = dict(data.get("variables", {}))
        self.relationships = dict(data.get("relationships", {}))
        self.flags = dict(data.get("flags", {}))
        self.visited_nodes = list(data.get("visited_nodes", []))
def check_conditions(conditions: Optional[Dict[str, Any]], state: GameState) -> bool:
    """
    Evaluate structured conditions against game state.
    Supported keys:
      - items_have: [str]
      - items_not_have: [str]
      - vars_min: {name: min_value}
      - vars_max: {name: max_value}
      - vars_eq: {name: exact_value}
      - relationships_min: {name: min_value}
      - flags_set: [flag_name]
      - flags_not_set: [flag_name]
      - visited_nodes_include: [node_id]
      - visited_nodes_exclude: [node_id]
    """
    if not conditions:
        return True
    # Items must have
    for item in conditions.get("items_have", []):
        if not state.has_item(item):
            return False
    # Items must not have
    for item in conditions.get("items_not_have", []):
        if state.has_item(item):
            return False
    # Variables >= min
    for name, min_val in conditions.get("vars_min", {}).items():
        if state.get_var(name) < int(min_val):
            return False
    # Variables <= max
    for name, max_val in conditions.get("vars_max", {}).items():
        if state.get_var(name) > int(max_val):
            return False
    # Variables equal
    for name, eq_val in conditions.get("vars_eq", {}).items():
        if state.get_var(name) != int(eq_val):
            return False
    # Relationships >= min
    for name, min_val in conditions.get("relationships_min", {}).items():
        if state.get_relationship(name) < int(min_val):
            return False
    # Flags set (True)
    for flag in conditions.get("flags_set", []):
        if not state.is_flag(flag):
            return False
    # Flags not set (False or absent)
    for flag in conditions.get("flags_not_set", []):
        if state.is_flag(flag):
            return False
    # Visited nodes include
    for node_id in conditions.get("visited_nodes_include", []):
        if node_id not in state.visited_nodes:
            return False
    # Visited nodes exclude
    for node_id in conditions.get("visited_nodes_exclude", []):
        if node_id in state.visited_nodes:
            return False
    return True
def apply_effects(effects: Optional[Dict[str, Any]], state: GameState):
    """
    Apply effects to game state.
    Supported keys:
      - add_items: [str]
      - remove_items: [str]
      - vars_delta: {name: delta}
      - vars_set: {name: value}
      - relationships_delta: {name: delta}
      - set_flags: {flag_name: bool}
    """
    if not effects:
        return
    for item in effects.get("add_items", []):
        state.add_item(item)
    for item in effects.get("remove_items", []):
        state.remove_item(item)
    for name, delta in effects.get("vars_delta", {}).items():
        state.adjust_var(name, int(delta))
    for name, value in effects.get("vars_set", {}).items():
        state.set_var(name, int(value))
    for name, delta in effects.get("relationships_delta", {}).items():
        state.adjust_relationship(name, int(delta))
    for name, value in effects.get("set_flags", {}).items():
        state.set_flag(name, bool(value))
class Choice:
    """
    Represents a decision the player can take at a node.
    """
    def __init__(self, text: str, target: str,
                 conditions: Optional[Dict[str, Any]] = None,
                 effects: Optional[Dict[str, Any]] = None):
        self.text = text
        self.target = target
        self.conditions = conditions or {}
        self.effects = effects or {}
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Choice":
        return cls(
            text=data["text"],
            target=data["target"],
            conditions=data.get("conditions"),
            effects=data.get("effects"),
        )
    def is_available(self, state: GameState) -> bool:
        return check_conditions(self.conditions, state)
    def apply_effects(self, state: GameState):
        apply_effects(self.effects, state)
class StoryNode:
    """
    A narrative segment containing text and a list of choices.
    """
    def __init__(self, node_id: str, text: str, choices: List[Choice]):
        self.node_id = node_id
        self.text = text
        self.choices = choices
    @classmethod
    def from_dict(cls, node_id: str, data: Dict[str, Any]) -> "StoryNode":
        choices = [Choice.from_dict(c) for c in data.get("choices", [])]
        return cls(node_id=node_id, text=data.get("text", ""), choices=choices)
    def available_choices(self, state: GameState) -> List[Choice]:
        return [c for c in self.choices if c.is_available(state)]
class StoryEngine:
    """
    Drives the story by managing state and advancing between nodes.
    """
    def __init__(self, story_data: Dict[str, Any]):
        self.story_data = story_data
        self.start_node_id: str = self.story_data.get("start", "")
        self.nodes: Dict[str, StoryNode] = {}
        for node_id, node_data in self.story_data.get("nodes", {}).items():
            self.nodes[node_id] = StoryNode.from_dict(node_id, node_data)
        if not self.start_node_id or self.start_node_id not in self.nodes:
            # Use the first node as start fallback
            self.start_node_id = next(iter(self.nodes.keys()), "")
        self.state = GameState()
        self.current_node_id: str = self.start_node_id
        # Initialize state
        self.reset()
    def reset(self):
        self.state = GameState()
        self.current_node_id = self.start_node_id
        # Mark first node as visited
        self.state.mark_visited(self.current_node_id)
    def get_current_node(self) -> StoryNode:
        return self.nodes[self.current_node_id]
    def get_available_choices(self) -> List[Choice]:
        node = self.get_current_node()
        return node.available_choices(self.state)
    def choose(self, choice: Choice) -> bool:
        """
        Attempt to apply a choice and advance to its target node.
        Returns:
            True if the choice was valid and the engine advanced; False otherwise.
        """
        node = self.get_current_node()
        # Ensure the choice belongs to the current node and is available
        if choice not in node.choices or not choice.is_available(self.state):
            return False
        target = choice.target
        # Ensure target exists before mutating state
        if target not in self.nodes:
            return False
        # Apply effects and move to target
        choice.apply_effects(self.state)
        self.current_node_id = target
        self.state.mark_visited(self.current_node_id)
        return True
    def is_end(self) -> bool:
        # A node with no available choices is considered an end
        return len(self.get_available_choices()) == 0
    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_node_id": self.current_node_id,
            "state": self.state.to_dict(),
        }
    def from_dict(self, data: Dict[str, Any]):
        node_id = data.get("current_node_id", self.start_node_id)
        if node_id in self.nodes:
            self.current_node_id = node_id
        else:
            self.current_node_id = self.start_node_id
        self.state.from_dict(data.get("state", {}))
        # If visited_nodes is empty after load, ensure the current node is marked
        if not self.state.visited_nodes:
            self.state.mark_visited(self.current_node_id)