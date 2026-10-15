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
    "Cap On Liability": {
        "standard": "Each party's liability is capped at a meaningful amount, commonly the fees paid or payable in the previous 12 months or more. The cap has carve-outs for serious harms such as breach of confidentiality, indemnification obligations, gross negligence, and willful misconduct.",
        "high_risk": [
            "Only the provider's liability is capped, while the customer's liability is unlimited",
            "The cap is very low compared with the contract value, such as one month of fees or a small fixed amount",
            "The cap has no carve-outs, so it applies even to gross negligence, willful misconduct, or data breaches",
        ],
        "medium_risk": [
            "A mutual cap set at 6 months of fees, or at a fixed amount that is unrelated to the contract value",
            "A mutual cap at 12 months of fees with no carve-outs",
            "All consequential damages excluded with no exceptions",
        ],
        "low_risk": [
            "A mutual cap at or above 12 months of fees, with carve-outs for confidentiality, indemnification, gross negligence, and willful misconduct",
        ],
        "safe_wording": "Each party's total liability under this Agreement is limited to the greater of (a) the fees paid or payable in the 12 months before the claim arose and (b) [fixed amount]. This limit does not apply to liability for breach of confidentiality, indemnification obligations, gross negligence, willful misconduct, or any liability that cannot be limited by law.",
    },
    "Uncapped Liability": {
        "standard": "Liability is unlimited only for serious harms that law or fairness requires to be uncapped, such as fraud, gross negligence, willful misconduct, and death or personal injury. This applies equally to both parties.",
        "high_risk": [
            "The customer's liability is unlimited for any breach, while the provider's liability is capped",
            "The customer has unlimited liability for broad categories, such as any breach of the agreement or any indirect or consequential loss",
            "The customer has unlimited indemnification obligations for third-party claims",
        ],
        "medium_risk": [
            "Both parties have unlimited liability for breach of confidentiality or data protection, which is common but can lead to very large losses",
            "The customer has unlimited liability for one defined category, such as misuse of the provider's intellectual property, and the category is broad",
        ],
        "low_risk": [
            "Unlimited liability applies to both parties and only for fraud, gross negligence, willful misconduct, or death and personal injury",
            "Unlimited liability applies only to the provider's obligations, which favors the customer",
        ],
        "safe_wording": "Neither party's liability is limited for (a) fraud, gross negligence, or willful misconduct, (b) death or personal injury caused by negligence, or (c) any liability that cannot be limited by law. All other liability is subject to the limit in Section [X].",
    },
    "Termination For Convenience": {
        "standard": "Either party, or at least the customer, may end the agreement without cause by giving reasonable written notice, such as 30 days, without penalty, and with a refund of prepaid fees for the unused period. Note: a right to terminate only for cause, such as material breach or insolvency, is NOT termination for convenience.",
        "high_risk": [
            "Only the provider may terminate without cause, and the customer has no matching right",
            "The provider may terminate immediately or on very short notice, such as 7 days or less, with no refund of prepaid fees",
            "The customer may leave early only by paying the fees for the whole remaining term or a large termination fee",
        ],
        "medium_risk": [
            "A mutual right to terminate without cause, but with a notice period of 60 to 90 days",
            "The customer may terminate without cause only after a long minimum term, such as the first 12 months",
            "An early termination fee that is modest and fixed",
        ],
        "low_risk": [
            "A mutual right to terminate without cause on 30 days' notice or less, with no penalty and a pro-rata refund of prepaid fees",
            "Only the customer has the right to terminate without cause",
        ],
        "safe_wording": "Either party may terminate this Agreement for any reason by giving the other party [30] days' written notice. If the Provider terminates under this Section, the Provider will refund all prepaid fees for the period after the termination date. The Customer owes no early termination fee beyond fees for services already received.",
    },
    "Non-Compete": {
        "standard": "Any restriction on competing is narrow: it covers only the specific products or services the contract is about, lasts no longer than the contract plus a short period after it, covers only the places where the parties actually do business, and applies equally to both parties or is balanced by something in return. Note: confidentiality duties, non-solicitation of employees or customers, and general 'shall not' obligations are NOT non-competes. A non-compete restricts a party's right to operate a competing business.",
        "high_risk": [
            "The customer is barred from working with any competitor of the provider, or from competing in a broad market, with no limit on what counts as competing",
            "The restriction lasts for years after the contract ends, for example 2 years or more after termination",
            "The restriction covers a very wide area, such as worldwide or an entire industry, when the contract concerns a narrow product or region",
            "Only the customer is restricted, with nothing given in return",
        ],
        "medium_risk": [
            "A restriction that lasts through the contract term and up to 12 months after it, limited to the specific products or services in the contract",
            "A restriction limited to a defined territory where the parties do business, but that applies to one party only",
            "A mutual restriction that is somewhat broader than the contract subject",
        ],
        "low_risk": [
            "No restriction on competing at all",
            "A mutual restriction that applies only during the contract term and only to the specific products covered by the contract",
            "A restriction that binds only the provider",
        ],
        "safe_wording": "During the Term, neither party will knowingly sell products that directly compete with the other party's [specific product] in the [defined territory]. This restriction ends when this Agreement ends. Nothing in this Agreement restricts either party from conducting any other business.",
    },
    "Notice Period To Terminate Renewal": {
        "standard": "A party can stop an automatic renewal by giving notice a short time before the term ends, commonly 30 days or less. The deadline is stated clearly, notice can be given by simple means such as email, and the provider sends a reminder before the deadline. Note: this is the window to stop a renewal at the end of a term. A right to end the contract during the term is Termination For Convenience, which is a different clause.",
        "high_risk": [
            "The notice window is 90 days or more before the end of the term, with no reminder from the provider",
            "Missing the window locks the customer into a long new term, such as one year or more",
            "Notice must be given by a hard method, such as registered mail to a physical address, with no email option",
            "The deadline is unclear or has to be worked out from several sections",
        ],
        "medium_risk": [
            "A notice window of 60 days with no reminder",
            "A window of 30 to 60 days that requires formal written notice by post",
            "A window of 30 days or less, but the renewal term is a full year and there is no reminder",
        ],
        "low_risk": [
            "A window of 30 days or less, with a reminder from the provider before the deadline",
            "Renewal happens only by mutual written agreement, so no notice is needed to stop it",
        ],
        "safe_wording": "Either party may stop this Agreement from renewing by giving written notice, including by email, at least [30] days before the end of the then-current term. The Provider will send the Customer a written reminder of the renewal date and this deadline at least [60] days before the end of each term.",
    },
}
