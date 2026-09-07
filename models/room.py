from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Room:
    id: str
    type: str = "regular"  # "regular" or "lab"
    capacity: int = 60
    branch: str = "GENERAL"

    @property
    def is_lab(self) -> bool:
        return self.type.lower() == "lab"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "capacity": self.capacity,
            "branch": self.branch,
            "is_lab": self.is_lab,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Room":
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "regular"),
            capacity=int(data.get("capacity", 60)),
            branch=data.get("branch", "GENERAL"),
        )
