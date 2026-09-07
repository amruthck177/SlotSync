from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ElectiveGroup:
    group: str
    options: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group": self.group,
            "options": self.options
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ElectiveGroup":
        return cls(
            group=data.get("group", ""),
            options=list(data.get("options", []))
        )

@dataclass
class Section:
    id: str
    branch: str
    subjects: List[str] = field(default_factory=list)
    electives: List[ElectiveGroup] = field(default_factory=list)
    semester: int = 5

    @property
    def all_elective_subject_ids(self) -> List[str]:
        res = []
        for eg in self.electives:
            res.extend(eg.options)
        return res

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "branch": self.branch,
            "subjects": self.subjects,
            "electives": [eg.to_dict() for eg in self.electives],
            "semester": self.semester,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Section":
        raw_electives = data.get("electives", [])
        electives_list = []
        for eg in raw_electives:
            if isinstance(eg, dict):
                electives_list.append(ElectiveGroup.from_dict(eg))
            elif isinstance(eg, ElectiveGroup):
                electives_list.append(eg)
        return cls(
            id=data.get("id", ""),
            branch=data.get("branch", ""),
            subjects=list(data.get("subjects", [])),
            electives=electives_list,
            semester=int(data.get("semester", 5)),
        )
