from scraper import extract_item


class FakeItem:
    def find_element(self, *args):
        class E:
            text = "Test"

            def get_attribute(self, _):
                return "http://test.com"

        return E()


def test_extract_item_schema():
    data = extract_item(FakeItem())

    assert "titulo" in data
    assert "precio" in data
    assert "link" in data
