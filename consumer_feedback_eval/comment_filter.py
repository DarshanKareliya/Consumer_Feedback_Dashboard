# 100 YouTube Comment Samples for Zero-Shot Classification Evaluation
# Categories: "product review" (25), "question" (25), "general comment" (25), "spam" (25)

from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support, accuracy_score
from transformers import pipeline
import torch
# EVALUATION_DATASET = [
#     # =========================================================================
#     # Category 1: product review (25 samples)
#     # =========================================================================
#     {"text": "I've been daily driving this laptop for three weeks. The battery lasts about 14 hours easily, but the thermals get quite warm under heavy Blender renders.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "The active noise cancellation on these earbuds is top-tier, noticeably better than the previous generation, though the hinge on the case feels a bit flimsy.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Honestly regret buying this monitor. The ghosting in competitive FPS games is unbearable, and color accuracy out of the box was way too green.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Camera quality in daylight is phenomenal with crisp dynamic range, but night mode introduces tons of watercolor-like smoothing.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Picked this phone up on launch day. The 120Hz display is buttery smooth, but standby battery drain has been roughly 12% every night.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Build quality is solid aluminum and feels premium, but the lack of a headphone jack and microSD slot really hurts the overall value.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Best mechanical keyboard I've owned so far. The pre-lubed switches sound creamy and the wireless latency is completely imperceptible.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "The software is full of bugs. Apps crash constantly after the latest update, and the fingerprint reader fails 4 out of 10 times.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "For $300, the audio fidelity punches well above its weight class. Punchy bass without muddying the mids.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "I returned mine yesterday. The fan noise sounds like a jet engine even when just watching 4K YouTube videos in Chrome.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Trackpad is massive and responsive, but the keyboard travel feels mushy compared to the 2021 model.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Battery life is disappointing. Barely pushes 4 hours of screen-on time with moderate Slack and browser usage.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "The haptic feedback engine is on par with Apple's Taptic Engine, and the haptic click feels extraordinarily realistic.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Great ergonomics for big hands. My wrist pain completely vanished after two weeks of using this vertical mouse.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Speakers are loud and clear without distortion at 80% volume, making it great for casual Netflix watching.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "The HDR brightness doesn't come anywhere near the claimed 1000 nits peak; highlights look washed out.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Charges to 80% in about 25 minutes with the included brick. Easily the fastest charging tech I have tested.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Port selection is awful. Having only two USB-C ports means you are forced to carry a dongle everywhere you go.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "The matte anti-reflective coating works miracles under office fluorescent lighting, zero annoying reflections.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Microphone pick-up is hollow and robotic during Zoom calls; definitely invest in a separate USB mic.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Swapped out my M1 for this unit. Video export times in Premiere cut down by nearly 40%, totally worth the upgrade.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "The ear pads got hot and sweaty after an hour session. Sound is decent, but long-term comfort is poor.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Solid 8 out of 10 device. Fast UI, great haptics, decent cameras, but let down by subpar indoor low-light video.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "The hinge wobble when typing on your lap makes it practically unusable on trains or flights.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},
#     {"text": "Amazing value for money. Performs identical to $80 competitors at half the price.",
#         "expected": "A consumer sharing their personal experience, opinion, or feedback about a product."},

#     # =========================================================================
#     # Category 2: question (25 samples)
#     # =========================================================================
#     {"text": "Does this model support dual external displays natively over Thunderbolt?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Can anyone confirm if the 16GB RAM variant throttles less than the 8GB base model?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Is this worth upgrading if I already own last year's flagship version?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "What wireless charging standard does this use? Will an old Qi pad work?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Does anyone know what time the embargo lifts for the full technical benchmarks?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Can you use this keyboard wired via USB-C or is it strictly Bluetooth?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Has anyone tested running local LLMs with Ollama on this specific GPU config?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Will this case fit the older version or did the camera bump dimensions change?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Why did they remove the 3.5mm headphone jack on this revision?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Is there any noticeable coil whine when the laptop is plugged into a 100W PD charger?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Do the replacement ear cushions use memory foam or standard silicone?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "What software do you use to record your desktop screen at 60fps in this video?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Could someone explain what the difference between the base and Pro chip is in simple terms?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Does this support high-res audio codecs like LDAC or aptX Adaptive?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Where can I download that minimalist wallpaper you have on your desktop at 04:15?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Is the warranty international or only valid within the country of purchase?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Can you upgrade the internal NVMe SSD after purchase or is it soldered down?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "How does the microphone noise suppression perform in loud outdoor cafe environments?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Are those keycaps double-shot PBT or just ABS plastic?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Does anyone know if this works plug-and-play on Ubuntu 24.04 without custom drivers?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Should I buy this now or wait for the rumored refresh coming out in fall?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Can this output 4K at 144Hz via HDMI 2.1 or only through DisplayPort?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Did they fix the hinge cracking issue that plagued the first generation model?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "What colorway looks better in person: the space gray or the midnight blue?",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Is anyone else experiencing audio desync issues while streaming on Twitch?",
#         "expected": "A comment that does not review or evaluate a product."},

#     # =========================================================================
#     # Category 3: general comment (25 samples)
#     # =========================================================================
#     {"text": "Your b-roll and lighting in this video are next-level, always love your camera angles!",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Tech companies really need to stop removing features and calling it innovation.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "First time watching your channel, instantly subscribed. Very straightforward breakdown.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "I can't believe it's already been four years since the M1 chips first launched, time flies.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "The pacing and editing of this entire video made a 20-minute tech review fly by.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "The thumbnail made me laugh way harder than it should have haha.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Glad to see reviewers finally holding companies accountable for planned obsolescence.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Watching this while sitting next to my dying 2015 laptop barely loading the page.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "This creator consistently puts out the cleanest, most objective tech videos on YouTube.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "The tech industry feels so stagnant right now, every annual release is just a 5% spec bump.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "That transition at 02:45 was absolutely seamless, kudos to your editor!",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "I love how you show real-world benchmarks instead of just meaningless Geekbench synthetic numbers.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Honestly didn't expect this video to drop today, perfect timing for my lunch break.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Been following your channel since 10k subscribers, so proud to see you hit 1 million!",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "The sound design in your intro sequence is criminally underrated.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Never thought I'd sit through an entire 30-minute video about monitor color science, but here I am.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Competition between AMD and Intel is the best thing that ever happened to consumers.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "I wish more reviewers tested devices on Linux instead of solely focusing on macOS and Windows.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "That cat walking across your desk in the background made my entire day.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "No sponsored segments and straight to the point without 5 minutes of fluff, respect.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Can't wait to see what your next studio tour video looks like with this new desk setup.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "These release prices are getting completely out of hand for average consumers.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Bro dropped the cleanest review on the internet and thought we wouldn't notice.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "The background music selection during the teardown segment was immaculate.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Shoutout to the team for including full timestamps and chapters in the description bar.",
#         "expected": "A comment that does not review or evaluate a product."},

#     # =========================================================================
#     # Category 4: spam (25 samples)
#     # =========================================================================
#     {"text": "Make $500 a day working from home using this automated crypto bot! Check my bio link 🚀",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Mr. Beast is giving away free MacBooks to the first 500 commenters click here: t.me/giveaway2026",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "SUB4SUB? Sub to my channel and I will subscribe back to you with 3 active accounts!",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "I recovered my lost crypto assets thanks to Mrs. Brenda on Telegram @Brenda_Recovery_Expert!",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Free Amazon gift cards right now! Claim yours before they run out: http://bit.ly/claim-giftcard-now",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "WhatsApp me at +1 (555) 019-2834 for 100% guaranteed binary trading signals.",
#      "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Hey check out my new gaming montage channel, drop a like and subscribe if you enjoy gaming content!",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Congratulations! You have been selected as today's winner! Contact our manager on Telegram @RewardClaim",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Cheap v-bucks and Robux instant generator no human verification needed: www.freerobux-glitch.xyz",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "I made $12,000 in just one week trading forex with Mr. David's algorithm. Message him on IG: @david_fx_official",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "CLICK MY PROFILE PICTURE FOR ADULT DATING NEAR YOU 🔞💦",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Want to boost your Instagram followers to 50k organically? Visit www.buyfollowersfast.net today!",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Check out my music video on my profile, I am a 14 year old rapper trying to make it out the hood!",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "URGENT: Your channel has copyright strikes. Email support-youtube-security@mail-verify.com immediately.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Crypto investment is real! I doubted until Mrs. Sarah paid out my first $4,500 profit. Contact her!",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Get 1000 free TikTok views per hour using this secret cloud exploit: t.me/tiktok_views_glitch",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "HOT SINGLES IN YOUR AREA LOOKING TO CHAT RIGHT NOW ➡️ CLICK LINK IN PROFILE",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Don't fall for fake traders, only trust Agent Thomas on WhatsApp +44 7700 900077 for real returns.",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Anyone who wants free Steam wallet keys add me on Discord: FreeGamerKeys#9999",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "My mom earned $85/hour typing captcha codes online from her phone. Start here: www.easy-captcha-jobs.cc",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Like this comment if you want a free iPhone 15 Pro Max shipped to your door tomorrow morning!!",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Financial freedom is possible with Ethereum smart arbitrage! Join our group: t.me/eth_arbitrage_club",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Subscribe to my channel and comment 'DONE' on my latest video for a free shoutout to 200k followers!",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Work from home full time or part time! Daily payouts guaranteed. Telegram: @remote_career_hr",
#         "expected": "A comment that does not review or evaluate a product."},
#     {"text": "Exclusive discount promo code 80% OFF for all electronics: visit discount-warehouse-clearance.org",
#         "expected": "A comment that does not review or evaluate a product."},
# ]


EVALUATION_DATASET = [
    # =========================================================================
    # Category 1: product review (25 samples)
    # =========================================================================
    {"text": "I've been daily driving this laptop for three weeks. The battery lasts about 14 hours easily, but the thermals get quite warm under heavy Blender renders.", "expected": "product review"},
    {"text": "The active noise cancellation on these earbuds is top-tier, noticeably better than the previous generation, though the hinge on the case feels a bit flimsy.", "expected": "product review"},
    {"text": "Honestly regret buying this monitor. The ghosting in competitive FPS games is unbearable, and color accuracy out of the box was way too green.", "expected": "product review"},
    {"text": "Camera quality in daylight is phenomenal with crisp dynamic range, but night mode introduces tons of watercolor-like smoothing.", "expected": "product review"},
    {"text": "Picked this phone up on launch day. The 120Hz display is buttery smooth, but standby battery drain has been roughly 12% every night.", "expected": "product review"},
    {"text": "Build quality is solid aluminum and feels premium, but the lack of a headphone jack and microSD slot really hurts the overall value.", "expected": "product review"},
    {"text": "Best mechanical keyboard I've owned so far. The pre-lubed switches sound creamy and the wireless latency is completely imperceptible.", "expected": "product review"},
    {"text": "The software is full of bugs. Apps crash constantly after the latest update, and the fingerprint reader fails 4 out of 10 times.", "expected": "product review"},
    {"text": "For $300, the audio fidelity punches well above its weight class. Punchy bass without muddying the mids.",
        "expected": "product review"},
    {"text": "I returned mine yesterday. The fan noise sounds like a jet engine even when just watching 4K YouTube videos in Chrome.",
        "expected": "product review"},
    {"text": "Trackpad is massive and responsive, but the keyboard travel feels mushy compared to the 2021 model.",
        "expected": "product review"},
    {"text": "Battery life is disappointing. Barely pushes 4 hours of screen-on time with moderate Slack and browser usage.",
        "expected": "product review"},
    {"text": "The haptic feedback engine is on par with Apple's Taptic Engine, and the haptic click feels extraordinarily realistic.",
        "expected": "product review"},
    {"text": "Great ergonomics for big hands. My wrist pain completely vanished after two weeks of using this vertical mouse.",
        "expected": "product review"},
    {"text": "Speakers are loud and clear without distortion at 80% volume, making it great for casual Netflix watching.",
        "expected": "product review"},
    {"text": "The HDR brightness doesn't come anywhere near the claimed 1000 nits peak; highlights look washed out.",
        "expected": "product review"},
    {"text": "Charges to 80% in about 25 minutes with the included brick. Easily the fastest charging tech I have tested.",
        "expected": "product review"},
    {"text": "Port selection is awful. Having only two USB-C ports means you are forced to carry a dongle everywhere you go.",
        "expected": "product review"},
    {"text": "The matte anti-reflective coating works miracles under office fluorescent lighting, zero annoying reflections.",
        "expected": "product review"},
    {"text": "Microphone pick-up is hollow and robotic during Zoom calls; definitely invest in a separate USB mic.",
        "expected": "product review"},
    {"text": "Swapped out my M1 for this unit. Video export times in Premiere cut down by nearly 40%, totally worth the upgrade.",
        "expected": "product review"},
    {"text": "The ear pads got hot and sweaty after an hour session. Sound is decent, but long-term comfort is poor.",
        "expected": "product review"},
    {"text": "Solid 8 out of 10 device. Fast UI, great haptics, decent cameras, but let down by subpar indoor low-light video.",
        "expected": "product review"},
    {"text": "The hinge wobble when typing on your lap makes it practically unusable on trains or flights.",
        "expected": "product review"},
    {"text": "Amazing value for money. Performs identical to $80 competitors at half the price.",
        "expected": "product review"},

    # =========================================================================
    # Category 2: question (25 samples)
    # =========================================================================
    {"text": "Does this model support dual external displays natively over Thunderbolt?",
        "expected": "question"},
    {"text": "Can anyone confirm if the 16GB RAM variant throttles less than the 8GB base model?",
        "expected": "question"},
    {"text": "Is this worth upgrading if I already own last year's flagship version?",
        "expected": "question"},
    {"text": "What wireless charging standard does this use? Will an old Qi pad work?",
        "expected": "question"},
    {"text": "Does anyone know what time the embargo lifts for the full technical benchmarks?",
        "expected": "question"},
    {"text": "Can you use this keyboard wired via USB-C or is it strictly Bluetooth?",
        "expected": "question"},
    {"text": "Has anyone tested running local LLMs with Ollama on this specific GPU config?",
        "expected": "question"},
    {"text": "Will this case fit the older version or did the camera bump dimensions change?",
        "expected": "question"},
    {"text": "Why did they remove the 3.5mm headphone jack on this revision?",
        "expected": "question"},
    {"text": "Is there any noticeable coil whine when the laptop is plugged into a 100W PD charger?",
        "expected": "question"},
    {"text": "Do the replacement ear cushions use memory foam or standard silicone?",
        "expected": "question"},
    {"text": "What software do you use to record your desktop screen at 60fps in this video?",
        "expected": "question"},
    {"text": "Could someone explain what the difference between the base and Pro chip is in simple terms?",
        "expected": "question"},
    {"text": "Does this support high-res audio codecs like LDAC or aptX Adaptive?",
        "expected": "question"},
    {"text": "Where can I download that minimalist wallpaper you have on your desktop at 04:15?",
        "expected": "question"},
    {"text": "Is the warranty international or only valid within the country of purchase?",
        "expected": "question"},
    {"text": "Can you upgrade the internal NVMe SSD after purchase or is it soldered down?",
        "expected": "question"},
    {"text": "How does the microphone noise suppression perform in loud outdoor cafe environments?",
        "expected": "question"},
    {"text": "Are those keycaps double-shot PBT or just ABS plastic?",
        "expected": "question"},
    {"text": "Does anyone know if this works plug-and-play on Ubuntu 24.04 without custom drivers?",
        "expected": "question"},
    {"text": "Should I buy this now or wait for the rumored refresh coming out in fall?",
        "expected": "question"},
    {"text": "Can this output 4K at 144Hz via HDMI 2.1 or only through DisplayPort?",
        "expected": "question"},
    {"text": "Did they fix the hinge cracking issue that plagued the first generation model?",
        "expected": "question"},
    {"text": "What colorway looks better in person: the space gray or the midnight blue?",
        "expected": "question"},
    {"text": "Is anyone else experiencing audio desync issues while streaming on Twitch?",
        "expected": "question"},

    # =========================================================================
    # Category 3: general comment (25 samples)
    # =========================================================================
    {"text": "Your b-roll and lighting in this video are next-level, always love your camera angles!",
        "expected": "general comment"},
    {"text": "Tech companies really need to stop removing features and calling it innovation.",
        "expected": "general comment"},
    {"text": "First time watching your channel, instantly subscribed. Very straightforward breakdown.",
        "expected": "general comment"},
    {"text": "I can't believe it's already been four years since the M1 chips first launched, time flies.",
        "expected": "general comment"},
    {"text": "The pacing and editing of this entire video made a 20-minute tech review fly by.",
        "expected": "general comment"},
    {"text": "The thumbnail made me laugh way harder than it should have haha.",
        "expected": "general comment"},
    {"text": "Glad to see reviewers finally holding companies accountable for planned obsolescence.",
        "expected": "general comment"},
    {"text": "Watching this while sitting next to my dying 2015 laptop barely loading the page.",
        "expected": "general comment"},
    {"text": "This creator consistently puts out the cleanest, most objective tech videos on YouTube.",
        "expected": "general comment"},
    {"text": "The tech industry feels so stagnant right now, every annual release is just a 5% spec bump.",
        "expected": "general comment"},
    {"text": "That transition at 02:45 was absolutely seamless, kudos to your editor!",
        "expected": "general comment"},
    {"text": "I love how you show real-world benchmarks instead of just meaningless Geekbench synthetic numbers.",
        "expected": "general comment"},
    {"text": "Honestly didn't expect this video to drop today, perfect timing for my lunch break.",
        "expected": "general comment"},
    {"text": "Been following your channel since 10k subscribers, so proud to see you hit 1 million!",
        "expected": "general comment"},
    {"text": "The sound design in your intro sequence is criminally underrated.",
        "expected": "general comment"},
    {"text": "Never thought I'd sit through an entire 30-minute video about monitor color science, but here I am.",
        "expected": "general comment"},
    {"text": "Competition between AMD and Intel is the best thing that ever happened to consumers.",
        "expected": "general comment"},
    {"text": "I wish more reviewers tested devices on Linux instead of solely focusing on macOS and Windows.",
        "expected": "general comment"},
    {"text": "That cat walking across your desk in the background made my entire day.",
        "expected": "general comment"},
    {"text": "No sponsored segments and straight to the point without 5 minutes of fluff, respect.",
        "expected": "general comment"},
    {"text": "Can't wait to see what your next studio tour video looks like with this new desk setup.",
        "expected": "general comment"},
    {"text": "These release prices are getting completely out of hand for average consumers.",
        "expected": "general comment"},
    {"text": "Bro dropped the cleanest review on the internet and thought we wouldn't notice.",
        "expected": "general comment"},
    {"text": "The background music selection during the teardown segment was immaculate.",
        "expected": "general comment"},
    {"text": "Shoutout to the team for including full timestamps and chapters in the description bar.",
        "expected": "general comment"},

    # =========================================================================
    # Category 4: spam (25 samples)
    # =========================================================================
    {"text": "Make $500 a day working from home using this automated crypto bot! Check my bio link 🚀", "expected": "spam"},
    {"text": "Mr. Beast is giving away free MacBooks to the first 500 commenters click here: t.me/giveaway2026", "expected": "spam"},
    {"text": "SUB4SUB? Sub to my channel and I will subscribe back to you with 3 active accounts!", "expected": "spam"},
    {"text": "I recovered my lost crypto assets thanks to Mrs. Brenda on Telegram @Brenda_Recovery_Expert!", "expected": "spam"},
    {"text": "Free Amazon gift cards right now! Claim yours before they run out: http://bit.ly/claim-giftcard-now", "expected": "spam"},
    {"text": "WhatsApp me at +1 (555) 019-2834 for 100% guaranteed binary trading signals.",
     "expected": "spam"},
    {"text": "Hey check out my new gaming montage channel, drop a like and subscribe if you enjoy gaming content!", "expected": "spam"},
    {"text": "Congratulations! You have been selected as today's winner! Contact our manager on Telegram @RewardClaim", "expected": "spam"},
    {"text": "Cheap v-bucks and Robux instant generator no human verification needed: www.freerobux-glitch.xyz", "expected": "spam"},
    {"text": "I made $12,000 in just one week trading forex with Mr. David's algorithm. Message him on IG: @david_fx_official", "expected": "spam"},
    {"text": "CLICK MY PROFILE PICTURE FOR ADULT DATING NEAR YOU 🔞💦", "expected": "spam"},
    {"text": "Want to boost your Instagram followers to 50k organically? Visit www.buyfollowersfast.net today!", "expected": "spam"},
    {"text": "Check out my music video on my profile, I am a 14 year old rapper trying to make it out the hood!", "expected": "spam"},
    {"text": "URGENT: Your channel has copyright strikes. Email support-youtube-security@mail-verify.com immediately.", "expected": "spam"},
    {"text": "Crypto investment is real! I doubted until Mrs. Sarah paid out my first $4,500 profit. Contact her!", "expected": "spam"},
    {"text": "Get 1000 free TikTok views per hour using this secret cloud exploit: t.me/tiktok_views_glitch", "expected": "spam"},
    {"text": "HOT SINGLES IN YOUR AREA LOOKING TO CHAT RIGHT NOW ➡️ CLICK LINK IN PROFILE",
        "expected": "spam"},
    {"text": "Don't fall for fake traders, only trust Agent Thomas on WhatsApp +44 7700 900077 for real returns.", "expected": "spam"},
    {"text": "Anyone who wants free Steam wallet keys add me on Discord: FreeGamerKeys#9999", "expected": "spam"},
    {"text": "My mom earned $85/hour typing captcha codes online from her phone. Start here: www.easy-captcha-jobs.cc", "expected": "spam"},
    {"text": "Like this comment if you want a free iPhone 15 Pro Max shipped to your door tomorrow morning!!", "expected": "spam"},
    {"text": "Financial freedom is possible with Ethereum smart arbitrage! Join our group: t.me/eth_arbitrage_club", "expected": "spam"},
    {"text": "Subscribe to my channel and comment 'DONE' on my latest video for a free shoutout to 200k followers!", "expected": "spam"},
    {"text": "Work from home full time or part time! Daily payouts guaranteed. Telegram: @remote_career_hr", "expected": "spam"},
    {"text": "Exclusive discount promo code 80% OFF for all electronics: visit discount-warehouse-clearance.org", "expected": "spam"},
]
# =========================================================================
# 1. Dataset Loading
# =========================================================================
# If you saved the previous dataset in a separate file (e.g., dataset.py):
# from dataset import EVALUATION_DATASET
#
# Alternatively, ensure EVALUATION_DATASET is defined as a list of dicts:
# [{"text": "...", "expected": "product review" | "question" | "general comment" | "spam"}, ...]
# try:
#     from dataset import EVALUATION_DATASET
# except ImportError:
#     # Placeholder if not importing from a separate file
#     EVALUATION_DATASET = [
#         # Paste or reference your list of 100 samples here
#     ]

# =========================================================================
# 2. Model Pipeline Initialization
# =========================================================================
device = 0 if torch.cuda.is_available(
) else (-1 if not torch.backends.mps.is_available() else "mps")

print(f"Loading cross-encoder/nli-deberta-v3-base on device: {device}...")
classifier = pipeline(
    "zero-shot-classification",
    model="/Users/darshankareliya/.cache/huggingface/hub/models--cross-encoder--nli-deberta-v3-base/snapshots/6c749ce3425cd33b46d187e45b92bbf96ee12ec7",
    device=device
)
CANDIDATE_LABELS = ["product review", "question", "general comment", "spam"]
TARGET_LABEL = "product review"
THRESHOLDS = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60,
              0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.99]

# =========================================================================
# 3. Single-Pass Inference (Caches raw predictions to avoid recomputing)
# =========================================================================


def run_single_pass_inference(dataset, batch_size=16):
    """
    Runs model inference once across all texts.
    Returns cached raw scores so threshold comparisons run instantaneously.
    """
    texts = [item["text"] for item in dataset]
    ground_truth = [item["expected"] for item in dataset]

    print(
        f"\nRunning zero-shot inference over {len(texts)} samples (Batch size: {batch_size})...")

    # Process texts in batches for efficiency
    raw_outputs = classifier(
        texts,
        candidate_labels=CANDIDATE_LABELS,
        multi_label=False,
        batch_size=batch_size
    )

    inference_cache = []
    for item, output, expected in zip(dataset, raw_outputs, ground_truth):
        top_label = output["labels"][0]
        top_score = output["scores"][0]

        # Also extract specific score for the target label if needed
        target_score = output["scores"][output["labels"].index(TARGET_LABEL)]

        inference_cache.append({
            "text": item["text"],
            "expected_label": expected,
            "is_target_ground_truth": (expected == TARGET_LABEL),
            "top_label": top_label,
            "top_score": top_score,
            "target_score": target_score
        })

    return inference_cache

# =========================================================================
# 4. Threshold Sweep & Evaluation Functions
# =========================================================================


def evaluate_binary_thresholds(cached_results, thresholds, target_label=TARGET_LABEL):
    """
    Evaluates Binary Review Filtering:
    An item is flagged as 'product review' if and only if:
    top_label == target_label AND top_score >= threshold
    """
    y_true = [item["is_target_ground_truth"] for item in cached_results]
    sweep_results = []

    print("\n" + "=" * 80)
    print(
        f"BINARY CLASSIFICATION THRESHOLD SWEEP (Target Label: '{target_label}')")
    print("=" * 80)
    print(f"{'Threshold':<10} | {'Accuracy':<9} | {'Precision':<10} | {'Recall':<8} | {'F1-Score':<9} | {'TP':<4} {'FP':<4} {'FN':<4} {'TN':<4}")
    print("-" * 80)

    best_f1 = -1.0
    best_tau = None

    for tau in thresholds:
        y_pred = [
            (item["top_label"] == target_label and item["top_score"] >= tau)
            for item in cached_results
        ]

        acc = accuracy_score(y_true, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average="binary", zero_division=0
        )
        tn, fp, fn, tp = confusion_matrix(
            y_true, y_pred, labels=[False, True]).ravel()

        sweep_results.append({
            "threshold": tau,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "confusion_matrix": (tp, fp, fn, tn)
        })

        if f1 > best_f1:
            best_f1 = f1
            best_tau = tau

        print(f"{tau:<10.2f} | {acc:<9.3f} | {prec:<10.3f} | {rec:<8.3f} | {f1:<9.3f} | {tp:<4} {fp:<4} {fn:<4} {tn:<4}")

    print("=" * 80)
    print(
        f"Optimal Threshold by F1-Score: {best_tau:.2f} (F1 = {best_f1:.3f})")

    return best_tau, sweep_results


def print_detailed_breakdown_at_threshold(cached_results, optimal_threshold, fallback_label="general comment"):
    """
    Displays the complete multi-class classification report when low-confidence
    predictions are gated and assigned to a fallback class.
    """
    y_true = [item["expected_label"] for item in cached_results]
    y_pred = []

    for item in cached_results:
        # If model confidence does not meet the threshold, route to fallback
        if item["top_score"] >= optimal_threshold:
            y_pred.append(item["top_label"])
        else:
            y_pred.append(fallback_label)

    print("\n" + "=" * 65)
    print(
        f"FULL MULTI-CLASS REPORT AT THRESHOLD {optimal_threshold:.2f} (Fallback: '{fallback_label}')")
    print("=" * 65)
    print(classification_report(y_true, y_pred, digits=3, zero_division=0))


def extract_verified_reviews(cached_results, threshold, target_label=TARGET_LABEL):

    verified_reviews = []

    for item in cached_results:
        # Binary Filtering Logic: Must match the label AND meet the threshold
        if item["top_label"] == target_label and item["top_score"] >= threshold:
            verified_reviews.append({
                "text": item["text"],
                "confidence": round(item["top_score"], 3)
            })

    return verified_reviews


# =========================================================================
# 5. Execution
# =========================================================================
if __name__ == "__main__":
    if not EVALUATION_DATASET:
        raise ValueError(
            "EVALUATION_DATASET is empty. Please define or import your dataset.")

    # Step 1: Run inference once
    results_cache = run_single_pass_inference(
        EVALUATION_DATASET, batch_size=16)

    # Step 2: Sweep thresholds for binary product review filtering
    best_threshold, sweep_data = evaluate_binary_thresholds(
        results_cache, THRESHOLDS)

    # Step 3: Print multi-class breakdown at the optimal threshold
    print_detailed_breakdown_at_threshold(
        results_cache, optimal_threshold=best_threshold)

    # Step 4: Actively filter the dataset to isolate the verified reviews
    final_filtered_reviews = extract_verified_reviews(
        results_cache, threshold=best_threshold)

    print("\n" + "=" * 65)
    print(
        f"EXTRACTION COMPLETE: Found {len(final_filtered_reviews)} verified reviews.")
    print("=" * 65)

    # Print the first 3 verified reviews as a sanity check
    for review in final_filtered_reviews[:3]:
        print(f"[{review['confidence']}] {review['text']}")
