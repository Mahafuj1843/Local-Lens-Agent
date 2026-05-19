from datetime import datetime, timedelta
from urllib.parse import quote_plus

from playwright.async_api import async_playwright

ACCOMMODATION_KEYWORDS = {
    "hotel", "hotels", "resort", "resorts", "hostel", "hostels",
    "motel", "motels", "inn", "accommodation", "stay", "lodge", "lodges",
}


def _is_accommodation(category: str) -> bool:
    words = set(category.lower().replace("-", " ").split())
    return bool(words & ACCOMMODATION_KEYWORDS)


def _booking_url(query: str) -> str:
    checkin = datetime.now() + timedelta(days=7)
    checkout = checkin + timedelta(days=1)
    return (
        f"https://www.booking.com/searchresults.html"
        f"?ss={quote_plus(query)}"
        f"&checkin_year={checkin.year}&checkin_month={checkin.month}&checkin_monthday={checkin.day}"
        f"&checkout_year={checkout.year}&checkout_month={checkout.month}&checkout_monthday={checkout.day}"
        f"&group_adults=2&no_rooms=1&lang=en-us"
    )


def _google_maps_url(query: str) -> str:
    return f"https://www.google.com/maps/search/{quote_plus(query)}"


async def _new_page(context):
    page = await context.new_page()
    await page.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return page


async def _scrape_booking(page) -> list:
    results = []
    try:
        await page.wait_for_selector('[data-testid="property-card"]', timeout=12000)
    except Exception as e:
        print(f"[Playwright][Booking] No cards found: {e}")
        return results

    cards = await page.locator('[data-testid="property-card"]').all()
    print(f"[Playwright][Booking] Found {len(cards)} cards")

    for card in cards[:5]:
        name, location, rating = "Unknown", "Unknown", None

        name_el = card.locator('[data-testid="title"]')
        if await name_el.count() > 0:
            name = (await name_el.first.text_content() or "").strip()

        address_el = card.locator('[data-testid="address"]')
        if await address_el.count() > 0:
            location = (await address_el.first.text_content() or "").strip()

        score_el = card.locator('[data-testid="review-score"]')
        if await score_el.count() > 0:
            raw = (await score_el.first.text_content() or "").replace(",", ".")
            for part in raw.split():
                try:
                    val = float(part)
                    if 1.0 <= val <= 10.0:
                        rating = val
                        break
                except ValueError:
                    continue

        results.append({"name": name, "location": location, "rating": rating})

    return results


async def _scrape_google_maps(page) -> list:
    results = []

    try:
        await page.wait_for_selector('[role="article"]', timeout=15000)
    except Exception as e:
        print(f"[Playwright][Google Maps] No results panel loaded: {e}")
        return results

    articles = await page.locator('[role="article"]').all()
    print(f"[Playwright][Google Maps] Found {len(articles)} result cards")

    for article in articles[:5]:
        name = "Unknown"
        location = "Unknown"
        rating = None

        aria_name = await article.get_attribute("aria-label")
        if aria_name:
            name = aria_name.strip()

        rating_el = article.locator('span[role="img"]')
        if await rating_el.count() > 0:
            aria_label = await rating_el.first.get_attribute("aria-label") or ""
            for part in aria_label.replace(",", ".").split():
                try:
                    val = float(part)
                    if 1.0 <= val <= 5.0:
                        rating = round(val * 2, 1)
                        break
                except ValueError:
                    continue

        text_lines = await article.locator("motion.div > span").all_text_contents()
        if not text_lines:
            text_lines = await article.locator("div > span").all_text_contents()
        for line in text_lines:
            line = line.strip()
            if line and not any(c.isdigit() for c in line[:3]) and len(line) > 5:
                location = line
                break

        if name != "Unknown":
            results.append({"name": name, "location": location, "rating": rating})

    return results


async def scrape_google_results(query: str, category: str = "") -> list:
    """
    Routes to Booking.com for hotels/resorts, otherwise Google Maps.
    `category` comes from parsed intent (dynamic for any business type).
    """
    use_booking = _is_accommodation(category or query)
    print(f"[Playwright] accommodation={use_booking} | Query: {query!r}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )

        page = await _new_page(context)

        if use_booking:
            url = _booking_url(query)
            print(f"[Playwright] → Booking.com: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            results = await _scrape_booking(page)

            if not results:
                print("[Playwright] Booking.com empty, falling back to Google Maps...")
                page2 = await _new_page(context)
                await page2.goto(_google_maps_url(query), wait_until="domcontentloaded", timeout=30000)
                results = await _scrape_google_maps(page2)
        else:
            url = _google_maps_url(query)
            print(f"[Playwright] → Google Maps: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            results = await _scrape_google_maps(page)

        await browser.close()

    print(f"[Playwright] Final results: {len(results)} items")
    return results
