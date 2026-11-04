import re
from decimal import Decimal, ROUND_HALF_UP
from playwright.sync_api import Playwright, sync_playwright, expect

BASE_URL = "https://www.saucedemo.com/"
COMPLETE_URL = "https://www.saucedemo.com/checkout-complete.html"
TAX_RATE = Decimal("0.08")


def parse_price(text: str) -> Decimal:
    match = re.search(r"\d+\.\d{2}", text)
    assert match is not None, f"No price found in: {text}"
    return Decimal(match.group())


def log_in(page) -> None:
    page.goto(BASE_URL)
    page.locator("[data-test=\"username\"]").fill("standard_user")
    page.locator("[data-test=\"password\"]").fill("secret_sauce")
    page.locator("[data-test=\"login-button\"]").click()


def add_highest_and_lowest_priced_items(page) -> None:
    page.locator("[data-test=\"product-sort-container\"]").select_option("hilo")
    inventory_items = page.locator("[data-test=\"inventory-item\"]")
    prices = [
        parse_price(price)
        for price in inventory_items.locator(".inventory_item_price").all_inner_texts()
    ]
    assert prices == sorted(prices, reverse=True), "Products are not sorted high to low"
    assert prices[0] >= prices[1], "First product is cheaper than the next product"

    highest_priced_item = inventory_items.nth(0)
    lowest_priced_item = inventory_items.nth(inventory_items.count() - 1)
    highest_price = parse_price(highest_priced_item.locator(".inventory_item_price").inner_text())
    lowest_price = parse_price(lowest_priced_item.locator(".inventory_item_price").inner_text())
    assert highest_price == max(prices), "First product is not the most expensive"
    assert lowest_price == min(prices), "Last product is not the cheapest"

    highest_priced_item.locator("button").click()
    lowest_priced_item.locator("button").click()


def fill_checkout_information(page) -> None:
    page.locator("[data-test=\"firstName\"]").fill("Jane")
    page.locator("[data-test=\"lastName\"]").fill("Doe")
    page.locator("[data-test=\"postalCode\"]").fill("12345")
    page.locator("[data-test=\"continue\"]").click()


def verify_checkout_totals(page) -> None:
    overview_prices = [
        parse_price(price)
        for price in page.locator("[data-test=\"inventory-item\"] .inventory_item_price").all_inner_texts()
    ]
    assert len(overview_prices) == 2, f"Expected 2 items in overview, found {len(overview_prices)}"

    item_total = parse_price(page.locator("[data-test=\"subtotal-label\"]").inner_text())
    expected_item_total = sum(overview_prices, Decimal("0.00"))
    assert item_total == expected_item_total, "Item Total does not match the item prices"

    tax = parse_price(page.locator("[data-test=\"tax-label\"]").inner_text())
    expected_tax = (item_total * TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    assert tax == expected_tax, f"Expected 8% tax of {expected_tax}, found {tax}"

    total = parse_price(page.locator("[data-test=\"total-label\"]").inner_text())
    assert total == item_total + tax, "Total does not equal Item Total plus Tax"


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(channel="msedge", headless=False)
    context = browser.new_context()
    page = context.new_page()

    log_in(page)
    add_highest_and_lowest_priced_items(page)
    expect(page.locator("[data-test=\"shopping-cart-badge\"]")).to_have_text("2")
    page.locator("[data-test=\"shopping-cart-link\"]").click()
    expect(page.locator("[data-test=\"inventory-item\"]")).to_have_count(2)
    page.locator("[data-test=\"checkout\"]").click()
    fill_checkout_information(page)
    verify_checkout_totals(page)

    page.locator("[data-test=\"finish\"]").click()
    expect(page).to_have_url(COMPLETE_URL)
    expect(page.get_by_text("Thank you for your order!")).to_be_visible()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
