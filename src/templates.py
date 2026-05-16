"""Email templates for the 7-step sequence."""

EMAIL_TEMPLATES = {
    1: {
        "subject": "Transforming your outbound strategy with A2go.ai",
        "html": "<p>Hello {first_name},</p><p>We help companies like {company} scale their outreach using intelligent orchestration...</p>"
    },
    2: {
        "subject": "Quick question about {company}'s lead flow",
        "html": "<p>Hi {first_name}, following up on my previous email. Many businesses in {industry} struggle with...</p>"
    },
    3: {
        "subject": "Case Study: How we helped a similar firm in {location}",
        "html": "<p>Hi {first_name}, I wanted to share how we solved the exact problem you might be facing...</p>"
    },
    4: {
        "subject": "Are you the right person to talk to at {company}?",
        "html": "<p>Hi {first_name}, just checking in to see if I should be speaking with someone else about your digital marketing...</p>"
    },
    5: {
        "subject": "New features for {industry} leaders",
        "html": "<p>Hello again, {first_name}. We just launched a new orchestration tool that I think you'd find valuable...</p>"
    },
    6: {
        "subject": "Let's connect on a brief 10-min call?",
        "html": "<p>Hi {first_name}, would you have a few minutes later this week to discuss how A2go.ai can help {company}?</p>"
    },
    7: {
        "subject": "One last thing...",
        "html": "<p>Hi {first_name}, this is my final follow-up for now. If you're ever interested in scaling your outreach, you know where to find us.</p>"
    }
}

LINKEDIN_TEMPLATES = {
    "connection_request": "Hi {first_name}, cold connect, won't pretend otherwise. Building out my network of {industry} leaders deliberately and you came up. No pitch.",
    "colleague": "Hi {first_name}, I saw your background in {industry} and wanted to share a colleague's perspective on {company}...",
    "customer": "Hi {first_name}, quick question about how {company} handles lead flow in {location}?",
    "bridge": "Hi {first_name}, we've been helping firms in {industry} with A2go.ai and I thought of {company}...",
    "final": "Hi {first_name}, just closing the loop. If you're ever looking to scale outreach, feel free to reach out."
}
