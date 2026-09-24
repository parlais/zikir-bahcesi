"""Model ağacı: isimli düğümler, her düğümde sıfır veya daha çok mesh.

Düğüm isimleri Godot'ya aynen geçer. Kural:
  - "kanat_*", "kapak" gibi hareketli parçalar ayrı düğümdür (animasyon için).
  - "isik_*" boş düğümleri Godot'da ışık konacak yeri işaretler.
  - "water_*" boş düğümleri su yüzeyi shader'ının konacağı yeri işaretler.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .mesh import Mesh


@dataclass
class Node:
    name: str
    meshes: list[Mesh] = field(default_factory=list)
    children: list["Node"] = field(default_factory=list)
    translation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation_deg: tuple[float, float, float] = (0.0, 0.0, 0.0)  # XYZ Euler
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)

    def add(self, *items) -> "Node":
        for it in items:
            if it is None:
                continue
            if isinstance(it, Node):
                self.children.append(it)
            elif isinstance(it, Mesh):
                self.meshes.append(it)
            else:
                for x in it:
                    self.add(x)
        return self

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()

    def tri_count(self) -> int:
        return sum(m.tri_count for n in self.walk() for m in n.meshes)


def model(name: str, *items, **kw) -> Node:
    return Node(name, **kw).add(*items)
