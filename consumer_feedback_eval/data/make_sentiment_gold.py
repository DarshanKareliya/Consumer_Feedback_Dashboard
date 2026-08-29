import csv

# label: 0=Very Negative, 1=Negative, 2=Neutral, 3=Positive, 4=Very Positive
rows = [
    # Very Negative (0)
    ("This laptop died after two weeks. Complete waste of money, I want a full refund.", 0),
    ("Absolutely terrible product. It arrived broken and customer service ignored every email.", 0),
    ("Worst purchase I have ever made. It stopped charging on day one and support was useless.", 0),
    ("Do not buy this. It caught fire while charging and the company refuses to respond.", 0),
    ("I am furious. The screen shattered on arrival and they will not process my refund.", 0),
    ("Garbage build quality, it fell apart in my hands within a week. Never buying this brand again.", 0),
    ("Total scam, the product never arrived and support keeps closing my tickets without a reply.", 0),
    ("This app deletes my data constantly and support has ghosted me for a month. Disgraceful.", 0),
    ("The battery swelled up and nearly damaged my bag. Extremely dangerous and unacceptable.", 0),
    ("I regret this purchase entirely, it is defective and the seller is dodging my refund request.", 0),
    ("Completely unusable out of the box, and the return window had already closed by the time it arrived.", 0),
    # Negative (1)
    ("The battery life is much worse than advertised and it overheats during normal use.", 1),
    ("Shipping took three weeks longer than promised and the box arrived dented.", 1),
    ("The app crashes frequently and I have to restart my phone to fix it.", 1),
    ("Customer support took days to respond and the solution they gave did not work.", 1),
    ("The build feels cheap and a button already stopped working after a month.", 1),
    ("I was charged twice for the same order and it took forever to get one refund back.", 1),
    ("The camera quality is disappointing in low light, noticeably worse than the previous model.", 1),
    ("Setup was frustrating and the included manual barely explains anything.", 1),
    ("The fabric started pilling after just two washes, not what I expected for the price.", 1),
    ("Tracking says delivered but I never received the package, still waiting on a response.", 1),
    ("The fan is louder than my old laptop and gets distracting during calls.", 1),
    ("A software update broke a feature I relied on daily and there is no fix yet.", 1),
    # Neutral (2)
    ("It works as described, nothing special but nothing wrong either.", 2),
    ("Arrived on time. Packaging was standard, product matches the listing.", 2),
    ("It's an average headset, sound quality is fine for casual use.", 2),
    ("The instructions were okay, I figured out the rest on my own.", 2),
    ("Does the job. I have no strong opinion about it either way.", 2),
    ("Delivery was fine, the size is as expected based on the description.", 2),
    ("It's a decent mid-range option, comparable to similar products at this price.", 2),
    ("Some features are useful, others I never use. Overall it is an okay purchase.", 2),
    ("The color is slightly different from the photo but otherwise matches expectations.", 2),
    ("It replaced my old one with no real improvement or downgrade that I noticed.", 2),
    ("Customer service answered my question, though it took a couple of days.", 2),
    # Positive (3)
    ("I'm happy with this purchase, the battery lasts most of the day and setup was easy.", 3),
    ("Good value for the price, the build quality feels solid so far.", 3),
    ("Shipping was faster than expected and the packaging protected it well.", 3),
    ("The app is smooth and the recent update fixed the bugs I had before.", 3),
    ("Support resolved my issue within a day, appreciated the quick help.", 3),
    ("The sound quality is quite good for this price range, I'd recommend it.", 3),
    ("Comfortable to wear all day and the material feels nicer than I expected.", 3),
    ("Works well with my other devices and the setup guide was clear.", 3),
    ("Noticeably better battery life than my previous model, happy with the upgrade.", 3),
    ("The customer support team was polite and fixed my billing issue quickly.", 3),
    ("Great little upgrade over the last version, camera improvements are noticeable.", 3),
    # Very Positive (4)
    ("Absolutely love this product! Battery lasts two full days and the screen is gorgeous.", 4),
    ("Best purchase I've made all year, exceeded every expectation I had.", 4),
    ("Incredible build quality and the customer support team went above and beyond to help me.", 4),
    ("This exceeded my expectations in every way, I recommend it to everyone I know.", 4),
    ("Flawless experience from ordering to delivery, and the product itself is outstanding.", 4),
    ("The performance boost is amazing, everything feels instant now. Worth every penny.", 4),
    ("I'm blown away by the sound quality, easily the best headphones I've owned.", 4),
    ("Support fixed my problem in minutes and even followed up the next day. Fantastic service.", 4),
    ("This is a masterpiece of design, comfortable, fast, and beautiful. Couldn't be happier.", 4),
    ("Ten out of ten, would buy again in a heartbeat. Genuinely impressed by the quality.", 4),
    ("Perfect in every way, arrived early, works flawlessly, and looks even better in person.", 4),
]

with open("/home/claude/eval_project/data/sentiment_gold.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["text", "label"])
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows")
label_counts = {}
for _, l in rows:
    label_counts[l] = label_counts.get(l, 0) + 1
print(label_counts)
