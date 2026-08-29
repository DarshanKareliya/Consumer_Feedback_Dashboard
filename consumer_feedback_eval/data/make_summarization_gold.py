import json

data = [
    {
        "id": "sum_01",
        "keyword": "WirelessBuds Pro",
        "source_text": (
            "Comment 1: The battery only lasts about two hours now, way less than the six hours advertised.\n"
            "Comment 2: Mine died after three months and the case won't charge them anymore either.\n"
            "Comment 3: Battery drains fast even when I'm not using them, must be a firmware issue.\n"
            "Comment 4: Sound quality is nice but I'm returning them because of the battery problem.\n"
            "Comment 5: Support told me to reset them but that didn't fix the short battery life at all."
        ),
        "reference_summary": "Customers consistently report that the WirelessBuds Pro suffer from significantly shorter battery life than advertised, with some units failing entirely after a few months, and support's reset suggestion has not resolved the issue."
    },
    {
        "id": "sum_02",
        "keyword": "SmartHome Hub X2",
        "source_text": (
            "Comment 1: The app keeps losing connection to my hub every few hours and I have to restart it.\n"
            "Comment 2: Setup was actually really easy and it paired with my lights instantly.\n"
            "Comment 3: It randomly disconnects from wifi at night and my automations stop working.\n"
            "Comment 4: Great product when it works, but the connection drops are frustrating.\n"
            "Comment 5: I love the design and voice control, wish the wifi stability was better though."
        ),
        "reference_summary": "While customers appreciate the SmartHome Hub X2's easy setup and voice control features, the most frequent complaint is unstable wifi connectivity that causes automations to fail and requires periodic restarts."
    },
    {
        "id": "sum_03",
        "keyword": "FreshBrew Coffee Maker",
        "source_text": (
            "Comment 1: It arrived with a cracked carafe and customer service has not responded to my replacement request.\n"
            "Comment 2: Makes great coffee but the water reservoir leaks onto the counter every morning.\n"
            "Comment 3: I contacted support three times about my broken unit and still no resolution.\n"
            "Comment 4: The leaking issue seems common based on other reviews I've read, mine does it too.\n"
            "Comment 5: Coffee tastes good when it's not leaking, but the build quality feels flimsy."
        ),
        "reference_summary": "Customers report recurring hardware issues with the FreshBrew Coffee Maker, particularly reservoir leaks and shipping damage, compounded by slow or unresponsive customer support when requesting replacements."
    },
    {
        "id": "sum_04",
        "keyword": "TrailRunner Hiking Boots",
        "source_text": (
            "Comment 1: Super comfortable right out of the box, no break-in period needed at all.\n"
            "Comment 2: Great grip on wet rocks, I felt very secure on my last hike.\n"
            "Comment 3: A bit pricier than similar boots but the comfort makes it worth it for me.\n"
            "Comment 4: My only wish is that they came in wide sizes, the standard fit is a bit narrow.\n"
            "Comment 5: Held up well after several muddy trail runs, no wear and tear yet."
        ),
        "reference_summary": "Customers are largely satisfied with the TrailRunner Hiking Boots, praising immediate comfort, strong wet-terrain grip, and durability, with the main suggestion being to offer a wider fit option."
    },
    {
        "id": "sum_05",
        "keyword": "CloudSync Backup App",
        "source_text": (
            "Comment 1: I was charged for the premium plan twice this month and support hasn't refunded me yet.\n"
            "Comment 2: Billing page shows an incorrect renewal date and it charged me a week early.\n"
            "Comment 3: Great app otherwise, syncing is fast, but the double charge really annoyed me.\n"
            "Comment 4: Requested a refund for the duplicate charge five days ago, still waiting.\n"
            "Comment 5: The subscription billing seems buggy, I've seen other users mention the same double charge."
        ),
        "reference_summary": "Multiple customers report being incorrectly double-billed for CloudSync's premium subscription, with refund requests going unresolved for days, despite otherwise positive impressions of the app's syncing performance."
    },
    {
        "id": "sum_06",
        "keyword": "PowerMax Portable Charger",
        "source_text": (
            "Comment 1: This thing charges my phone from zero to full twice, exactly as advertised.\n"
            "Comment 2: Compact and light, fits easily in my bag pocket without adding much weight.\n"
            "Comment 3: Charges fast and the LED indicators are handy for checking remaining battery.\n"
            "Comment 4: Wish it supported wireless charging too, otherwise no complaints.\n"
            "Comment 5: Best power bank I've owned, reliable every time I've needed it while traveling."
        ),
        "reference_summary": "Customers are highly satisfied with the PowerMax Portable Charger's advertised capacity, fast charging, and compact design, with the only minor request being the addition of wireless charging support."
    },
    {
        "id": "sum_07",
        "keyword": "StreamCast 4K Dongle",
        "source_text": (
            "Comment 1: It froze on the setup screen and I had to factory reset it twice before it worked.\n"
            "Comment 2: Streaming quality is great once it's running, but the app crashes randomly during playback.\n"
            "Comment 3: I contacted support about the constant buffering and they just told me to restart my router.\n"
            "Comment 4: The remote pairing bug is really annoying, it disconnects mid show almost every night.\n"
            "Comment 5: When it works it's excellent, but these software bugs need to be patched soon."
        ),
        "reference_summary": "Customers find the StreamCast 4K Dongle's picture quality strong, but frequent software bugs such as setup freezes, app crashes, and remote disconnections are undermining the experience, and support's generic troubleshooting has not addressed the root cause."
    },
    {
        "id": "sum_08",
        "keyword": "UrbanCommute Backpack",
        "source_text": (
            "Comment 1: Zipper broke off within the first week of light daily use, very disappointing.\n"
            "Comment 2: I reached out for a replacement and it took over two weeks just to get a response.\n"
            "Comment 3: Material feels sturdy but the stitching on the side pocket is already coming undone.\n"
            "Comment 4: Laptop compartment padding is great, but I'm worried about the zipper quality long term.\n"
            "Comment 5: Support finally offered a replacement, but the whole process took nearly a month."
        ),
        "reference_summary": "Several customers report early hardware failures with the UrbanCommute Backpack, especially broken zippers and loose stitching, and describe the replacement process through customer support as slow, often taking weeks."
    },
]

with open("/home/claude/eval_project/data/summarization_gold.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Wrote {len(data)} examples")
