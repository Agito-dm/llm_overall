import pytest

from llm_overall.classification.categories import Category
from llm_overall.classification.routing import ROUTING_INSTRUCTIONS, get_route


@pytest.mark.parametrize(
    ("category", "expected_fragment"),
    [
        (Category.SUPPORT, "troubleshooting"),
        (Category.FEEDBACK, "feedback"),
        (Category.COMPLAINT, "empathy"),
        (Category.SALES, "sales-oriented"),
        (Category.GENERAL_QUESTION, "question"),
    ],
)
def test_category_routing(
    category: Category,
    expected_fragment: str,
) -> None:
    instruction = get_route(category)

    assert expected_fragment in instruction


def test_all_categories_have_routes() -> None:
    assert set(ROUTING_INSTRUCTIONS) == set(Category)


def test_routes_are_different() -> None:
    instructions = [get_route(category) for category in Category]

    assert len(instructions) == len(set(instructions))


def test_unknown_category() -> None:
    with pytest.raises(
        ValueError,
        match="Unknown routing category",
    ):
        get_route("unknown")


def test_category_string_value() -> None:
    assert Category.SUPPORT.value == "support"


def test_category_from_string() -> None:
    assert Category("sales") is Category.SALES
