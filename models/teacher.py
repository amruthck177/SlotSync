from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Teacher:
    id: str
    name: str
    branch: str
    subjects: List[str] = field(default_factory=list)
    cross_branch_subjects: List[Dict[str, str]] = field(default_factory=list)
    max_hours_per_day: int = 4
    max_hours_per_week: int = 20

    @property
    def num_subjects(self) -> int:
        return len(self.subjects) + len(self.cross_branch_subjects)

    @property
    def all_qualified_subject_codes(self) -> List[str]:
        codes = list(self.subjects)
        for item in self.cross_branch_subjects:
            if isinstance(item, dict) and "code" in item:
                codes.append(item["code"])
            elif isinstance(item, str):
                codes.append(item)
        return list(dict.fromkeys(codes))

    def can_teach(self, subject_id: str) -> bool:
        return subject_id in self.all_qualified_subject_codes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "branch": self.branch,
            "subjects": self.subjects,
            "cross_branch_subjects": self.cross_branch_subjects,
            "num_subjects": self.num_subjects,
            "max_hours_per_day": self.max_hours_per_day,
            "max_hours_per_week": self.max_hours_per_week,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Teacher":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            branch=data.get("branch", ""),
            subjects=list(data.get("subjects", [])),
            cross_branch_subjects=list(data.get("cross_branch_subjects", [])),
            max_hours_per_day=int(data.get("max_hours_per_day", 4)),
            max_hours_per_week=int(data.get("max_hours_per_week", 20)),
        )
