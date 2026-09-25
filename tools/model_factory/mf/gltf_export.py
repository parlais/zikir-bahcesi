"""Node ağacını tek dosyalık .glb olarak yazar.

Renkler köşe rengi (COLOR_0) olarak gider; glTF köşe renklerini doğrusal
(linear) uzayda beklediği için paletteki sRGB değerleri burada çevrilir.
Her malzeme adı için tek bir glTF malzemesi üretilir.
"""
from __future__ import annotations

import math
import struct
from pathlib import Path

import numpy as np
import pygltflib as g

from .scene import Node

# Godot tarafı bu adlara göre stil shader'ı atar (scenes/stil). Buradaki değerler
# shader atanmamış görüntüleyiciler (önizleme) içindir.
MATERIALS = {
    "mat": dict(roughness=0.85, metallic=0.0),
    "tas": dict(roughness=0.6, metallic=0.0),
    "zemin": dict(roughness=0.95, metallic=0.0),
    "yaprak": dict(roughness=0.8, metallic=0.0),
    "cimen_ot": dict(roughness=0.8, metallic=0.0),
    "cicek": dict(roughness=0.7, metallic=0.0),
    "govde": dict(roughness=0.9, metallic=0.0),
    "cini": dict(roughness=0.3, metallic=0.0),
    "altin": dict(roughness=0.3, metallic=0.9),
    "kursun": dict(roughness=0.45, metallic=0.6),
    "uzak": dict(roughness=1.0, metallic=0.0),
    "metal": dict(roughness=0.45, metallic=0.55),
    "nur": dict(roughness=0.4, metallic=0.0, emissive=(1.0, 0.78, 0.42)),
    "cam": dict(roughness=0.15, metallic=0.0, alpha=0.55),
    "su": dict(roughness=0.1, metallic=0.0, alpha=0.8),
    "inci": dict(roughness=0.25, metallic=0.1),
    # Cennet mekânı: ırmaklar, çağlayan, tuğla, kumaş
    "sut": dict(roughness=0.2, metallic=0.0, alpha=0.95),
    "bal": dict(roughness=0.1, metallic=0.0, alpha=0.85),
    "serbet": dict(roughness=0.1, metallic=0.0, alpha=0.85),
    "selale": dict(roughness=0.2, metallic=0.0, alpha=0.8),
    "selale_pus": dict(roughness=1.0, metallic=0.0, alpha=0.3),
    "tugla": dict(roughness=0.4, metallic=0.4),
    "kumas": dict(roughness=0.95, metallic=0.0),
    "bulut": dict(roughness=1.0, metallic=0.0),
    "tavan": dict(roughness=1.0, metallic=0.0, emissive=(0.55, 0.75, 0.95)),
    # Dokulu malzemeler (K15): doku game/assets/dokular/ altındadır, glTF'e dış dosya olarak
    # bağlanır (önizleme için). "yaprak_*" adları yaprak kümesi atlasıdır (alfa kesmeli).
    "kabuk": dict(roughness=0.9, metallic=0.0, doku="kabuk.png"),
    "meyve": dict(roughness=0.5, metallic=0.0),
}
DOKU_KLASORU = "../dokular/"


def _malzeme_tanimi(name: str) -> dict:
    if name in MATERIALS:
        return MATERIALS[name]
    if name.startswith("yaprak_"):
        return dict(roughness=0.8, metallic=0.0, doku=f"{name}.png", maske=True)
    if name.startswith(("kabuk_", "yuzey_")):
        return dict(roughness=0.9, metallic=0.0, doku=f"{name}.png")
    raise KeyError(name)


def srgb_to_linear(c: np.ndarray) -> np.ndarray:
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _quat_from_euler(rx, ry, rz):
    """XYZ Euler (derece) -> (x, y, z, w)."""
    hx, hy, hz = (math.radians(a) / 2 for a in (rx, ry, rz))
    cx, sx = math.cos(hx), math.sin(hx)
    cy, sy = math.cos(hy), math.sin(hy)
    cz, sz = math.cos(hz), math.sin(hz)
    # q = qz * qy * qx (önce X, sonra Y, sonra Z dönüşü)
    w = cz * cy * cx + sz * sy * sx
    x = cz * cy * sx - sz * sy * cx
    y = cz * sy * cx + sz * cy * sx
    z = sz * cy * cx - cz * sy * sx
    return [x, y, z, w]


class _Writer:
    def __init__(self):
        self.gltf = g.GLTF2(asset=g.Asset(generator="ZB model fabrikası", version="2.0"))
        self.blob = bytearray()
        self.mat_index: dict[str, int] = {}

    def _view(self, data: bytes, target=None) -> int:
        while len(self.blob) % 4:
            self.blob.append(0)
        off = len(self.blob)
        self.blob += data
        self.gltf.bufferViews.append(g.BufferView(buffer=0, byteOffset=off, byteLength=len(data), target=target))
        return len(self.gltf.bufferViews) - 1

    def _indeksli(self, ms, mat) -> "g.Primitive":
        """Köşeleri paylaşılan mesh'ler: tek köşe tablosu, köşe renkleri (16 bit), uint32 indeks."""
        P = np.vstack([m.V for m in ms]).astype(np.float32)
        N = np.vstack([m.NV for m in ms]).astype(np.float32)
        C = np.vstack([np.hstack([srgb_to_linear(m.CV), m.W[:, None]]) for m in ms])
        F, off = [], 0
        for m in ms:
            F.append(m.F + off)
            off += len(m.V)
        F = np.vstack(F).astype(np.uint32)
        C16 = np.round(np.clip(C, 0, 1) * 65535).astype(np.uint16)
        view = self._view(np.ascontiguousarray(C16).tobytes(), g.ARRAY_BUFFER)
        self.gltf.accessors.append(g.Accessor(bufferView=view, componentType=g.UNSIGNED_SHORT, normalized=True,
                                              count=len(C16), type=g.VEC4))
        ci = len(self.gltf.accessors) - 1
        view = self._view(np.ascontiguousarray(F.ravel()).tobytes(), g.ELEMENT_ARRAY_BUFFER)
        self.gltf.accessors.append(g.Accessor(bufferView=view, componentType=g.UNSIGNED_INT, count=F.size,
                                              type=g.SCALAR))
        ii = len(self.gltf.accessors) - 1
        attrs = g.Attributes(POSITION=self._accessor(P, g.VEC3, True), NORMAL=self._accessor(N, g.VEC3), COLOR_0=ci)
        if any(m.UV is not None for m in ms):
            UV = np.vstack([m.UV if m.UV is not None else np.zeros((len(m.V), 2)) for m in ms])
            attrs.TEXCOORD_0 = self._accessor(UV, g.VEC2)
        return g.Primitive(attributes=attrs, indices=ii, material=self.material(mat))

    def _accessor(self, arr: np.ndarray, typ: str, with_bounds=False) -> int:
        arr = np.ascontiguousarray(arr, dtype=np.float32)
        view = self._view(arr.tobytes(), g.ARRAY_BUFFER)
        acc = g.Accessor(bufferView=view, componentType=g.FLOAT, count=len(arr), type=typ)
        if with_bounds:
            acc.min = arr.min(axis=0).tolist()
            acc.max = arr.max(axis=0).tolist()
        self.gltf.accessors.append(acc)
        return len(self.gltf.accessors) - 1

    def material(self, name: str) -> int:
        if name in self.mat_index:
            return self.mat_index[name]
        p = _malzeme_tanimi(name)
        m = g.Material(
            name=name,
            pbrMetallicRoughness=g.PbrMetallicRoughness(
                baseColorFactor=[1.0, 1.0, 1.0, p.get("alpha", 1.0)],
                metallicFactor=p["metallic"], roughnessFactor=p["roughness"]),
            doubleSided=False,
        )
        if "doku" in p:
            if not self.gltf.samplers:
                self.gltf.samplers.append(g.Sampler(magFilter=g.LINEAR, minFilter=g.LINEAR_MIPMAP_LINEAR))
            self.gltf.images.append(g.Image(uri=DOKU_KLASORU + p["doku"]))
            self.gltf.textures.append(g.Texture(sampler=0, source=len(self.gltf.images) - 1))
            m.pbrMetallicRoughness.baseColorTexture = g.TextureInfo(index=len(self.gltf.textures) - 1)
        if p.get("maske"):
            m.alphaMode = g.MASK
            m.alphaCutoff = 0.5
            m.doubleSided = True
        if "emissive" in p:
            m.emissiveFactor = list(p["emissive"])
        if "alpha" in p:
            m.alphaMode = g.BLEND
        self.gltf.materials.append(m)
        self.mat_index[name] = len(self.gltf.materials) - 1
        return self.mat_index[name]

    def mesh(self, node: Node) -> int | None:
        if not node.meshes:
            return None
        groups: dict[str, list] = {}
        for m in node.meshes:
            groups.setdefault(m.material, []).append(m)
        prims = []
        for mat, ms in groups.items():
            if all(m.CV is not None for m in ms):
                prims.append(self._indeksli(ms, mat))
                continue
            P, N, C = [], [], []
            A, T = [], []
            doku = any(m.UV is not None for m in ms)
            for m in ms:
                tri = m.V[m.F]                                  # (t, 3, 3)
                n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
                ln = np.linalg.norm(n, axis=1, keepdims=True)
                ok = ln[:, 0] > 1e-12                           # dejenere üçgenleri at
                F = m.F[ok]
                tri, col = tri[ok], m.C[ok]
                cn = corner_normals(m.V, F, m.S[ok])
                elle = m.NV[F]                                   # (t, 3, 3)
                var = np.linalg.norm(elle, axis=2, keepdims=True) > 0.5
                cn = np.where(var, elle, cn).astype(np.float32)
                P.append(tri.reshape(-1, 3))
                N.append(cn.reshape(-1, 3))
                C.append(np.repeat(srgb_to_linear(col), 3, axis=0))
                A.append(m.W[F].reshape(-1, 1))
                if doku:
                    T.append(m.UV[F].reshape(-1, 2) if m.UV is not None else np.zeros((F.size, 2)))
            P, N, C = np.vstack(P), np.vstack(N), np.vstack(C)
            C4 = np.hstack([C, np.vstack(A)]).astype(np.float32)
            attrs = g.Attributes(POSITION=self._accessor(P, g.VEC3, True),
                                 NORMAL=self._accessor(N, g.VEC3),
                                 COLOR_0=self._accessor(C4, g.VEC4))
            if doku:
                attrs.TEXCOORD_0 = self._accessor(np.vstack(T), g.VEC2)
            prims.append(g.Primitive(attributes=attrs, material=self.material(mat)))
        self.gltf.meshes.append(g.Mesh(name=node.name, primitives=prims))
        return len(self.gltf.meshes) - 1

    def node(self, node: Node) -> int:
        children = [self.node(c) for c in node.children]
        gn = g.Node(name=node.name, children=children)
        mi = self.mesh(node)
        if mi is not None:
            gn.mesh = mi
        if any(node.translation):
            gn.translation = list(node.translation)
        if any(node.rotation_deg):
            gn.rotation = _quat_from_euler(*node.rotation_deg)
        if node.scale != (1.0, 1.0, 1.0):
            gn.scale = list(node.scale)
        self.gltf.nodes.append(gn)
        return len(self.gltf.nodes) - 1


def write_glb(root: Node, path: Path) -> int:
    w = _Writer()
    root_index = w.node(root)
    w.gltf.scenes = [g.Scene(name=root.name, nodes=[root_index])]
    w.gltf.scene = 0
    w.gltf.buffers = [g.Buffer(byteLength=len(w.blob))]
    w.gltf.set_binary_blob(bytes(w.blob))
    path.parent.mkdir(parents=True, exist_ok=True)
    w.gltf.save_binary(str(path))
    return path.stat().st_size


def signed_volume(mesh) -> float:
    """Kapalı mesh'te pozitifse yüzler dışarı bakıyor (sarım yönü doğru)."""
    tri = mesh.V[mesh.F].astype(np.float64)
    return float(np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6.0)


def corner_normals(V: np.ndarray, F: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Her üçgen köşesi için normal (t, 3, 3). S[f] > 0 olan yüzlerde, aynı
    konumu paylaşan ve normalleri arasındaki açı S'den küçük komşu yüzlerin
    (alan ağırlıklı) normalleri ortalanır; S = 0 düz gölgedir."""
    tri = V[F].astype(np.float64)
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])       # alan ağırlıklı
    unit = fn / (np.linalg.norm(fn, axis=1, keepdims=True) + 1e-20)
    out = np.repeat(unit[:, None, :], 3, axis=1)
    smooth = np.nonzero(S > 0)[0]
    if len(smooth) == 0:
        return out.astype(np.float32)
    keys = np.round(tri[smooth].reshape(-1, 3), 4)
    _, grp = np.unique(keys, axis=0, return_inverse=True)
    grp = grp.reshape(-1)
    faces_of = {}
    for i, g in enumerate(grp):
        faces_of.setdefault(g, []).append(smooth[i // 3])
    cos_lim = np.cos(np.radians(S))
    for i, g in enumerate(grp):
        f = smooth[i // 3]
        k = i % 3
        komsu = np.array(faces_of[g])
        yakin = komsu[(unit[komsu] @ unit[f]) >= cos_lim[f]]
        n = fn[yakin].sum(axis=0)
        out[f, k] = n / (np.linalg.norm(n) + 1e-20)
    return out.astype(np.float32)
