"""Model kaydı. Her model fonksiyonu @model("ZB_...") ile kaydolur ve bir Node döndürür.

Dosya adları asset listesindeki kuraldır: ZB_[kategori]_[isim]_a[aşama].
Aşamalı modellerde fonksiyon aşama numarasını parametre olarak alır ve
@asamali("ZB_agac_hurma", 4) her aşama için ayrı bir kayıt açar.
"""
from __future__ import annotations

REGISTRY: dict[str, callable] = {}


def model(name: str):
    def deco(fn):
        assert name not in REGISTRY, name
        REGISTRY[name] = fn
        return fn
    return deco


def asamali(stem: str, count: int):
    def deco(fn):
        for i in range(1, count + 1):
            name = f"{stem}_a{i}"
            assert name not in REGISTRY, name
            REGISTRY[name] = (lambda i=i: fn(i))
        return fn
    return deco


def load_all():
    # Modüller içe aktarıldıkça kendilerini kaydeder.
    from . import bitkiler, cennet, cennet_bitkileri, cennet_yapilari, objeler, sahne, yapilar, zemin  # noqa: F401
    return REGISTRY
