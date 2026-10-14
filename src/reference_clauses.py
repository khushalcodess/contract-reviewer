PERSPECTIVE = "customer"

REFERENCE = {
    "Governing Law": {
        "standard": "The agreement is governed by the law of the customer's home jurisdiction or a neutral one, and disputes go to courts there or to courts both sides agreed on.",
        "high_risk": [
            "Law and exclusive courts of a distant foreign country chosen by the other party",
            "Mandatory arbitration in the other party's country",
        ],
        "medium_risk": [
            "Law and exclusive courts of the other party's home state, same country as the customer",
        ],
        "low_risk": [
            "Customer's home jurisdiction, a neutral jurisdiction, or one the parties negotiated",
        ],
        "safe_wording": "This Agreement is governed by the laws of [Customer's jurisdiction]. The parties submit to the non-exclusive jurisdiction of the courts located in [Customer's jurisdiction].",
    },
    "Renewal Term": {
        "standard": "Renewal happens only by written agreement, or automatically for short periods with a clear reminder and an easy way to cancel.",
        "high_risk": [
            "Automatic renewal for long successive terms (a year or more each time)",
            "Cancellation notice window of 90 days or more, with no reminder from the provider",
        ],
        "medium_risk": [
            "Automatic annual renewal with a 30-60 day cancellation window and no reminder",
        ],
        "low_risk": [
            "Renewal only by mutual written agreement",
            "Automatic renewal with a window of 30 days or less and a reminder before the deadline",
        ],
        "safe_wording": "This Agreement renews only by mutual written agreement. Alternatively, it renews for successive one-year periods unless either party gives 30 days' written notice, and the Provider will send a reminder at least 60 days before each renewal date.",
    },
    # Add: Notice Period To Terminate Renewal, Termination For Convenience,
    # Non-Compete, Cap On Liability, Uncapped Liability, Indemnification
}