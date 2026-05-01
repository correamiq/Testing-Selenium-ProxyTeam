def test_schema():
    sample = {
        "titulo": "x",
        "precio": 100,
        "link": "http://test.com",
        "tienda_oficial": None,
        "envio_gratis": True,
        "cuotas_sin_interes": None,
    }

    assert isinstance(sample["titulo"], str)
    assert isinstance(sample["precio"], int)
    assert sample["precio"] > 0
    assert sample["link"].startswith("http")
