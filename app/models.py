from dataclasses import dataclass

from django.contrib.auth.models import User
from django.db import models


@dataclass
class Department:
    """Simple helper class to map groups to resources"""

    name: str

    def __str__(self):
        return self.name

    @classmethod
    def from_group_name(cls, group_name: str):
        parts = group_name.split("_")
        return cls(name=parts[1])

    @property
    def resources(self) -> tuple[str, str]:
        return (f"departments/{self.name}/records", f"departments/{self.name}/metadata")


class ProxyUser(User):
    class Meta:
        proxy = True

    @property
    def departments(self) -> list[Department]:
        return [Department.from_group_name(g.name) for g in self.groups.all()]

    @property
    def resources(self):
        return [d.resources for d in self.departments]
