from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class TimetableEntry:
    day: str
    period: int
    subject_id: str
    teacher_id: str
    room_id: str
    section_id: str
    is_elective: bool = False
    elective_group: Optional[str] = None
    is_locked: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "day": self.day,
            "period": self.period,
            "subject_id": self.subject_id,
            "teacher_id": self.teacher_id,
            "room_id": self.room_id,
            "section_id": self.section_id,
            "is_elective": self.is_elective,
            "elective_group": self.elective_group,
            "is_locked": self.is_locked,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimetableEntry":
        return cls(
            day=data.get("day", ""),
            period=int(data.get("period", 1)),
            subject_id=data.get("subject_id", ""),
            teacher_id=data.get("teacher_id", ""),
            room_id=data.get("room_id", ""),
            section_id=data.get("section_id", ""),
            is_elective=bool(data.get("is_elective", False)),
            elective_group=data.get("elective_group"),
            is_locked=bool(data.get("is_locked", False)),
        )
