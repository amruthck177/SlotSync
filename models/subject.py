import re
from dataclasses import dataclass
from typing import Dict, Any, Optional

def extract_semester_from_code(code: str) -> int:
    """
    Extracts the semester (1-8) from a standard VTU or academic course code.
    Examples:
      - 21CS51 -> 5
      - 21CSL55 -> 5
      - 21MAT11 -> 1
      - 21MAT31 -> 3
      - 21EC61 -> 6
      - CS301 -> 3 (or 5)
      - IS401 -> 4
    """
    code = code.strip().upper()
    # Pattern for VTU 21/18/22 scheme: e.g. 21CS51, 21EC42, 21MAT11, 21CSL55, 21CSE561
    vtu_match = re.search(r'^\d{2}[A-Z]+(\d)', code)
    if vtu_match:
        sem_digit = int(vtu_match.group(1))
        if 1 <= sem_digit <= 8:
            return sem_digit

    # Pattern for 2-3 letter prefix followed by single or multi digit: e.g. CS301 -> 3, IS401 -> 4, CS5A -> 5
    prefix_match = re.search(r'^[A-Z]+(\d)', code)
    if prefix_match:
        sem_digit = int(prefix_match.group(1))
        if 1 <= sem_digit <= 8:
            return sem_digit

    return 5 # Default to semester 5 if undetermined

@dataclass
class Subject:
    id: str
    name: str
    branch: str
    weekly_hours: int = 4
    needs_lab: bool = False
    consecutive_hours: int = 1
    semester: int = 5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "branch": self.branch,
            "weekly_hours": self.weekly_hours,
            "needs_lab": self.needs_lab,
            "consecutive_hours": self.consecutive_hours,
            "semester": self.semester,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Subject":
        code = data.get("id", "")
        raw_sem = data.get("semester")
        if raw_sem is not None and str(raw_sem).isdigit() and 1 <= int(raw_sem) <= 8:
            sem = int(raw_sem)
        else:
            sem = extract_semester_from_code(code)

        return cls(
            id=code,
            name=data.get("name", ""),
            branch=data.get("branch", ""),
            weekly_hours=int(data.get("weekly_hours", 4)),
            needs_lab=bool(data.get("needs_lab", False)),
            consecutive_hours=int(data.get("consecutive_hours", 1)),
            semester=sem
        )
