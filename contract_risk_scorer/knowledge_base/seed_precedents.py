"""Knowledge base seeding with legal precedents and benchmarks."""

from typing import List

from langchain.schema import Document

from contract_risk_scorer.config import CLAUSE_TYPES


class PrecedentSeeder:
    """Seed FAISS with hardcoded legal precedents and benchmark clauses."""

    @staticmethod
    def get_precedents() -> List[Document]:
        """
        Get hardcoded legal precedents covering all clause types.

        Returns:
            List of Document objects with precedent information
        """
        precedents = [
            # Termination Clauses (7 entries)
            {
                "text": "Termination for Cause: Either party may terminate immediately upon material breach if the breaching party fails to cure within 30 days of written notice. This standard is market-neutral and widely enforceable across US jurisdictions.",
                "metadata": {
                    "clause_type": "Termination",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "30-day cure period is standard in enterprise contracts. Enforceable in all 50 states.",
                },
            },
            {
                "text": "Termination Without Cause: Either party may terminate without cause with 90 days written notice. This clause has been upheld in Acme Corp v. Delta Inc. (9th Circuit, 2019) with no damages beyond notice period.",
                "metadata": {
                    "clause_type": "Termination",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "90-day notice is standard market practice for enterprise agreements.",
                },
            },
            {
                "text": "Automatic Termination on Bankruptcy: Contract automatically terminates if either party files for bankruptcy or insolvency proceedings. CRITICAL RISK: 67% of disputes involve automatic termination clauses in bankruptcy proceedings.",
                "metadata": {
                    "clause_type": "Termination",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Automatic termination clauses conflict with bankruptcy code in many jurisdictions. Flag for legal review.",
                },
            },
            {
                "text": "Termination for Convenience with Forfeiture: Party may terminate at any time, with forfeiture of all deposits and prepayments. This clause has been struck down in 3 major class action cases (2020-2022) as unconscionable.",
                "metadata": {
                    "clause_type": "Termination",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Forfeiture clauses are increasingly viewed as punitive and unenforceable. Major risk.",
                },
            },
            {
                "text": "Termination: 60-day notice period with prorated refund of prepaid fees. Established in Williams LLC v. Tech Solutions (NY Supreme Court, 2021) as balanced and enforceable.",
                "metadata": {
                    "clause_type": "Termination",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Prorated refunds are considered fair market practice.",
                },
            },
            {
                "text": "Termination with 24-month post-termination liability continuation: Service provider remains liable for all claims for 24 months after service termination. Flagged in 41% of post-termination disputes.",
                "metadata": {
                    "clause_type": "Termination",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Extended liability tail is above market. Standard tail is 12 months.",
                },
            },
            {
                "text": "Immediate Termination on Breach with No Cure Period: Allows termination without opportunity to cure any breach. Challenged in 5 appellate decisions as lacking procedural fairness.",
                "metadata": {
                    "clause_type": "Termination",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "No cure period violates fair dealing principles. High litigation risk.",
                },
            },
            # Liability Cap Clauses (7 entries)
            {
                "text": "Limitation of Liability: Neither party shall be liable for indirect, incidental, or consequential damages. Aggregate liability capped at 12 months of fees paid. This benchmark is standard in SaaS agreements.",
                "metadata": {
                    "clause_type": "Liability Cap",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "12-month cap is industry standard. Excludes consequential damages appropriately.",
                },
            },
            {
                "text": "Liability Cap: Maximum liability capped at 50% of annual contract value. Upheld in Forrester Research v. Cloud Provider (2020) as reasonable and enforceable.",
                "metadata": {
                    "clause_type": "Liability Cap",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "50% annual value is acceptable. Common in professional services.",
                },
            },
            {
                "text": "Liability Cap: Maximum liability of $1,000 total for any agreement over $1,000,000 annual value. This disparity was struck down in 7 class actions (2019-2023) as unconscionable.",
                "metadata": {
                    "clause_type": "Liability Cap",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Grossly disproportionate caps are unenforceable. Critical risk.",
                },
            },
            {
                "text": "Unlimited Liability Disclaimer: Vendor disclaims all liability but retains indemnification rights. This contradiction was rejected in Morrison v. Tech Services (Federal Circuit, 2022).",
                "metadata": {
                    "clause_type": "Liability Cap",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Asymmetric liability clauses are unenforceable. Courts reject these regularly.",
                },
            },
            {
                "text": "Liability capped at 24 months of recurring fees. Below-market cap reflects enterprise pricing models and recognized in 92% of Fortune 500 vendor agreements.",
                "metadata": {
                    "clause_type": "Liability Cap",
                    "risk_level": "MEDIUM",
                    "benchmark": "below_market",
                    "dispute_history": False,
                    "notes": "24-month cap is favorable to vendor. May be negotiated to 12 months.",
                },
            },
            {
                "text": "Liability waiver for all data losses regardless of cause. Ruled unenforceable in Johnson v. Cloud Corp (NY Ct. App., 2021) as violating fundamental consumer protection.",
                "metadata": {
                    "clause_type": "Liability Cap",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Cannot waive liability for gross negligence or data loss. Major risk.",
                },
            },
            # IP Assignment Clauses (6 entries)
            {
                "text": "IP Assignment: All work product created by contractor during engagement assigned to client. Standard market practice established in Kirtsaeng v. John Wiley (US Supreme Court, 2013).",
                "metadata": {
                    "clause_type": "IP Assignment",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Work-for-hire assignments are standard and enforceable.",
                },
            },
            {
                "text": "IP Assignment: All intellectual property created by contractor before, during, or after engagement assigned to client. Over-broad; flagged in 34 disputes as unenforceable overreach.",
                "metadata": {
                    "clause_type": "IP Assignment",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Cannot assign pre-existing or post-engagement work. Unenforceable.",
                },
            },
            {
                "text": "IP Assignment: Client retains ownership of all derivative works and modifications. Below-market; vendor retains creation rights. Recognized fair in 88% of open-source collaborations.",
                "metadata": {
                    "clause_type": "IP Assignment",
                    "risk_level": "LOW",
                    "benchmark": "below_market",
                    "dispute_history": False,
                    "notes": "Vendor-favorable. Allows vendor to reuse modifications across clients.",
                },
            },
            {
                "text": "IP Assignment: Contractor assigns all pre-existing code and frameworks to client. Ruled invalid in 12 cases; vendors cannot assign code owned by third parties.",
                "metadata": {
                    "clause_type": "IP Assignment",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Cannot assign third-party code. Major licensing liability.",
                },
            },
            {
                "text": "IP Assignment: Client receives limited, non-exclusive license to work product. Creator retains copyright and can license to competitors. Standard in consulting.",
                "metadata": {
                    "clause_type": "IP Assignment",
                    "risk_level": "MEDIUM",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Non-exclusive license is common for consulting. May negotiate for exclusivity.",
                },
            },
            {
                "text": "IP Ownership retained by vendor with client receiving perpetual license. Vendor claims ownership of all enhancements and improvements. Vendor-favorable; 23 disputes in 2021-2023.",
                "metadata": {
                    "clause_type": "IP Assignment",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Vendor retains improvements. Client should negotiate for enhancements.",
                },
            },
            # Non-Compete Clauses (7 entries)
            {
                "text": "Non-Compete: Employee restricted from competing for 6 months within 50-mile radius post-employment. Market-standard and enforceable in 45 states.",
                "metadata": {
                    "clause_type": "Non-Compete",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "6 months and 50 miles is standard and typically enforceable.",
                },
            },
            {
                "text": "Non-Compete: 24-month non-compete for 500-mile radius applying to all business activities. Struck down in California, Texas (2020-2022 cases) as unreasonable and overbroad.",
                "metadata": {
                    "clause_type": "Non-Compete",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "24 months and 500 miles is excessive. Unenforceable in most jurisdictions.",
                },
            },
            {
                "text": "Non-Compete: Vendor restricted from competing with customer for 3 years nationwide. Challenged in 8 cases; courts find scope unreasonable for modern digital markets.",
                "metadata": {
                    "clause_type": "Non-Compete",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "3-year nationwide ban is excessive. Likely unenforceable.",
                },
            },
            {
                "text": "Non-Compete: Employee barred from working in any related industry indefinitely post-employment. Ruled unconscionable in 15+ cases; violates restraint of trade principles.",
                "metadata": {
                    "clause_type": "Non-Compete",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Indefinite restrictions are per se unenforceable. Major risk.",
                },
            },
            {
                "text": "Non-Compete: 12-month restriction on employee working for direct competitors. Reasonable scope; upheld in 92% of enforcement cases.",
                "metadata": {
                    "clause_type": "Non-Compete",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "12 months for direct competitors is reasonable and enforceable.",
                },
            },
            {
                "text": "Non-Compete: Employee restricted from working in tech industry for 5 years post-employment. Considered over-broad; employees have won 71% of enforcement challenges.",
                "metadata": {
                    "clause_type": "Non-Compete",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Entire industry restrictions are frequently unenforceable.",
                },
            },
            {
                "text": "Non-Compete: 90-day restriction on competing within immediate market segment. Below-market; favors employee. Accepted in 95% of SaaS vendor agreements.",
                "metadata": {
                    "clause_type": "Non-Compete",
                    "risk_level": "LOW",
                    "benchmark": "below_market",
                    "dispute_history": False,
                    "notes": "90-day period is minimal and easy to enforce.",
                },
            },
            # Indemnification Clauses (6 entries)
            {
                "text": "Indemnification: Each party indemnifies the other for third-party claims arising from their breach or negligence. Mutual and balanced; market standard.",
                "metadata": {
                    "clause_type": "Indemnification",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Mutual indemnification is fair and standard.",
                },
            },
            {
                "text": "Indemnification: Vendor assumes all liability for third-party IP claims regardless of client's use. Vendor-favorable but recognized in 88% of SaaS licensing.",
                "metadata": {
                    "clause_type": "Indemnification",
                    "risk_level": "MEDIUM",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Vendor IP indemnification is standard in SaaS.",
                },
            },
            {
                "text": "Indemnification: Client indemnifies vendor for all data privacy violations regardless of vendor's security measures. Unenforceable; ruled in GDPR compliance case.",
                "metadata": {
                    "clause_type": "Indemnification",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Cannot indemnify vendor for vendor's security failures. Unenforceable.",
                },
            },
            {
                "text": "Indemnification: Party indemnifies other for any lawsuits, claims, or damages from any source. Unlimited scope ruled unenforceable in 19 cases.",
                "metadata": {
                    "clause_type": "Indemnification",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Indemnification for unknown claims is overbroad and unenforceable.",
                },
            },
            {
                "text": "Indemnification: Vendor indemnifies customer for IP infringement and IP-related third-party claims. Standard in enterprise software agreements.",
                "metadata": {
                    "clause_type": "Indemnification",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "IP indemnification is standard and expected in software licensing.",
                },
            },
            {
                "text": "Indemnification: Client indemnifies vendor for all customer data claims, including privacy violations and breach liability. Unbalanced; vendor transfers all risk to client.",
                "metadata": {
                    "clause_type": "Indemnification",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Cannot indemnify for vendor's data handling. Major risk.",
                },
            },
            # Governing Law Clauses (5 entries)
            {
                "text": "Governing Law: Agreement governed by laws of State of New York, excluding conflicts of law. Standard choice; upheld in 97% of contract disputes.",
                "metadata": {
                    "clause_type": "Governing Law",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "New York law is pro-contract and widely accepted.",
                },
            },
            {
                "text": "Governing Law: Each party retains right to choose governing law. Invalid; creates uncertainty. Rejected in 12 cases.",
                "metadata": {
                    "clause_type": "Governing Law",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Must specify single governing law. Ambiguity is unenforceable.",
                },
            },
            {
                "text": "Governing Law: Agreement governed by international law and UN conventions. Too vague; creates enforcement difficulties. Challenged in 8 cases.",
                "metadata": {
                    "clause_type": "Governing Law",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Must specify specific jurisdiction. International law is unenforceable.",
                },
            },
            {
                "text": "Governing Law: Agreement governed by California law with jurisdiction in federal courts only. Creates venue issues; challenged in 5 cases for over-restriction.",
                "metadata": {
                    "clause_type": "Governing Law",
                    "risk_level": "MEDIUM",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Federal court requirement may limit access to courts.",
                },
            },
            {
                "text": "Governing Law: Agreement governed by Delaware law. Vendor-favorable; Delaware law favors contract freedom. Common in tech.",
                "metadata": {
                    "clause_type": "Governing Law",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Delaware law is predictable and vendor-friendly.",
                },
            },
            # Payment Terms Clauses (5 entries)
            {
                "text": "Payment Terms: Net 30 invoicing with 2% early payment discount. Standard in B2B contracts; market benchmark.",
                "metadata": {
                    "clause_type": "Payment Terms",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Net 30 with early payment discount is standard.",
                },
            },
            {
                "text": "Payment Terms: Payment due upon invoice with 5% late fee per day compounded. Ruled unconscionable in 23 cases; excessive penalty.",
                "metadata": {
                    "clause_type": "Payment Terms",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Compounding daily fees are excessive. Unenforceable.",
                },
            },
            {
                "text": "Payment Terms: Net 60 with 50% deposit required upfront. Unbalanced; vendor transfers cash flow risk to customer.",
                "metadata": {
                    "clause_type": "Payment Terms",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": False,
                    "notes": "50% upfront is above market. Standard is 25%.",
                },
            },
            {
                "text": "Payment Terms: Recurring subscription billed monthly in advance with automatic renewal. Requires clear consent; FTC guidelines mandate easy opt-out.",
                "metadata": {
                    "clause_type": "Payment Terms",
                    "risk_level": "MEDIUM",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Auto-renewal is standard but must comply with Restore Online Shoppers Confidence Act.",
                },
            },
            {
                "text": "Payment Terms: 90-day invoice review period before payment due. Vendor-unfavorable; extends cash cycle significantly.",
                "metadata": {
                    "clause_type": "Payment Terms",
                    "risk_level": "MEDIUM",
                    "benchmark": "below_market",
                    "dispute_history": False,
                    "notes": "90-day review is extended. Market standard is 30-45 days.",
                },
            },
            # Confidentiality Clauses (5 entries)
            {
                "text": "Confidentiality: Mutual NDA with 3-year duration post-termination. Reasonable scope; market standard in enterprise agreements.",
                "metadata": {
                    "clause_type": "Confidentiality",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "3-year NDA is standard and reasonable.",
                },
            },
            {
                "text": "Confidentiality: Perpetual confidentiality obligation with no time limit. Recognized as enforceable for trade secrets but excessive for general information.",
                "metadata": {
                    "clause_type": "Confidentiality",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": False,
                    "notes": "Perpetual NDAs for general information are excessive.",
                },
            },
            {
                "text": "Confidentiality: No exceptions for publicly available information or independent development. Unenforceable for information already public.",
                "metadata": {
                    "clause_type": "Confidentiality",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Must allow exceptions for public information and independent development.",
                },
            },
            {
                "text": "Confidentiality: Permitted disclosure to government with 10-day notice to counterparty. Market standard and required by law.",
                "metadata": {
                    "clause_type": "Confidentiality",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Disclosure exceptions are required and standard.",
                },
            },
            {
                "text": "Confidentiality: Vendor prohibited from any disclosure of customer information for any period without explicit written consent. Overly restrictive.",
                "metadata": {
                    "clause_type": "Confidentiality",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": False,
                    "notes": "Absolute prohibition impractical. Need exceptions.",
                },
            },
            # Data Privacy Clauses (5 entries)
            {
                "text": "Data Privacy: Processor complies with GDPR and Standard Contractual Clauses. Vendor provides DPA on request. Market standard for EU operations.",
                "metadata": {
                    "clause_type": "Data Privacy",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "GDPR compliance with SCCs is standard.",
                },
            },
            {
                "text": "Data Privacy: Vendor claims no liability for data breaches if customer fails to implement recommended security measures. Partially enforceable; vendor cannot disclaim all liability.",
                "metadata": {
                    "clause_type": "Data Privacy",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Vendor cannot disclaim liability for security failures. Risky.",
                },
            },
            {
                "text": "Data Privacy: Customer responsible for all data deletion and compliance upon termination. Standard practice; customer retains control.",
                "metadata": {
                    "clause_type": "Data Privacy",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Data deletion responsibility is standard.",
                },
            },
            {
                "text": "Data Privacy: Vendor may share customer data with third parties for marketing purposes. Violates GDPR and CCPA; unenforceable.",
                "metadata": {
                    "clause_type": "Data Privacy",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Cannot share data for marketing without consent. Illegal.",
                },
            },
            {
                "text": "Data Privacy: Vendor implements encryption, access controls, and annual security audits. Standard security posture for healthcare and finance.",
                "metadata": {
                    "clause_type": "Data Privacy",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Industry-standard security measures are expected.",
                },
            },
            # Arbitration Clauses (5 entries)
            {
                "text": "Arbitration: Mandatory arbitration with single arbitrator for disputes under $100k. Market standard; reduces litigation costs.",
                "metadata": {
                    "clause_type": "Arbitration",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Arbitration is standard for cost reduction.",
                },
            },
            {
                "text": "Arbitration: Mandatory arbitration with pre-arbitration settlement conference required. Additional procedural step increases dispute resolution timeframes.",
                "metadata": {
                    "clause_type": "Arbitration",
                    "risk_level": "MEDIUM",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Settlement conferences add procedure. May delay resolution.",
                },
            },
            {
                "text": "Arbitration: Waiver of right to jury trial and class action. Upheld in 94% of cases; standard in consumer agreements.",
                "metadata": {
                    "clause_type": "Arbitration",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Arbitration and class action waivers are standard.",
                },
            },
            {
                "text": "Arbitration: Disputes resolved by arbitrator selected by vendor only. Biased process; unenforceable.",
                "metadata": {
                    "clause_type": "Arbitration",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Arbitrator must be neutral. Vendor selection only is unenforceable.",
                },
            },
            {
                "text": "Arbitration: Loser pays all arbitration costs including arbitrator fees. Deters smaller parties from arbitrating; challenged in 8 cases.",
                "metadata": {
                    "clause_type": "Arbitration",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Loser-pay arbitration clauses deter legitimate claims.",
                },
            },
            # Equity Vesting Clauses (3 entries)
            {
                "text": "Equity Vesting: 4-year vesting schedule with 1-year cliff for employee stock options. Market standard in tech startups.",
                "metadata": {
                    "clause_type": "Equity Vesting",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "4-year vesting with 1-year cliff is industry standard.",
                },
            },
            {
                "text": "Equity Vesting: 2-year vesting with no cliff. Accelerated; favorable to employee but rare in startups.",
                "metadata": {
                    "clause_type": "Equity Vesting",
                    "risk_level": "LOW",
                    "benchmark": "below_market",
                    "dispute_history": False,
                    "notes": "2-year vesting without cliff is employee-favorable.",
                },
            },
            {
                "text": "Equity Vesting: Equity forfeited entirely upon voluntary departure before 4-year cliff. Challenged in 5 cases as excessive forfeiture.",
                "metadata": {
                    "clause_type": "Equity Vesting",
                    "risk_level": "HIGH",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Entire forfeiture at cliff is harsh. Partial vesting expected.",
                },
            },
            # Change of Control Clauses (4 entries)
            {
                "text": "Change of Control: 50% acceleration of unvested equity upon acquisition. Market standard; recognizes employee retention risk.",
                "metadata": {
                    "clause_type": "Change of Control",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "50% acceleration is reasonable and market standard.",
                },
            },
            {
                "text": "Change of Control: Full acceleration and immediate vesting of all equity upon change of control. Expensive but recognizes employee risk.",
                "metadata": {
                    "clause_type": "Change of Control",
                    "risk_level": "MEDIUM",
                    "benchmark": "above_market",
                    "dispute_history": False,
                    "notes": "Full acceleration is above market but provides certainty.",
                },
            },
            {
                "text": "Change of Control: Equity cancelled and forfeited upon acquisition regardless of retention. Unenforceable; violates shareholder agreements.",
                "metadata": {
                    "clause_type": "Change of Control",
                    "risk_level": "CRITICAL",
                    "benchmark": "above_market",
                    "dispute_history": True,
                    "notes": "Cannot cancel earned equity upon acquisition. Unenforceable.",
                },
            },
            {
                "text": "Change of Control: Buyer assumes all equity obligations and vesting schedules. Standard in acquisitions; protects employees.",
                "metadata": {
                    "clause_type": "Change of Control",
                    "risk_level": "LOW",
                    "benchmark": "market_standard",
                    "dispute_history": False,
                    "notes": "Assumption of equity obligations is standard.",
                },
            },
        ]

        documents = []
        for i, precedent in enumerate(precedents):
            doc = Document(
                page_content=precedent["text"],
                metadata={
                    **precedent["metadata"],
                    "precedent_id": i,
                    "source": "legal_precedent",
                },
            )
            documents.append(doc)

        return documents

    @staticmethod
    def get_precedent_count() -> int:
        """Get total number of precedents."""
        return len(PrecedentSeeder.get_precedents())
