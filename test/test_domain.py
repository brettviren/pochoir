#!/usr/bin/env pytest
from pochoir.domain import Domain
from pochoir.persist import tempstore

def test_domain_creation():
    with tempstore("test-domain") as s:
        dom = Domain([20,10], [0.1, 0.1], [200.0, 100.0])
        md = dom.asdict
        s.put("test-key", (), **md)
        arr, md2 = s.get("test-key", True)
        assert len(arr) == 0
        assert md == md2


