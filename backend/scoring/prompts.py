"""LangChain prompts for risk scoring."""

from langchain.prompts import PromptTemplate

# Prompt for clause-level risk scoring
CLAUSE_RISK_PROMPT_TEMPLATE = """You are an expert contract lawyer specializing in risk analysis. 
Analyze the provided contract clause and compare it against similar precedents and industry benchmarks.

CLAUSE TO ANALYZE:
{clause_text}

SIMILAR PRECEDENTS FROM CASE LAW:
{precedents}

Based on the clause text and precedents, provide a JSON response with the following structure:
{{
    "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
    "risk_reason": "Brief explanation of why this risk level was assigned (max 150 words)",
    "benchmark_position": "market_standard|above_market|below_market",
    "dispute_prone": true|false,
    "suggested_revision": "Specific revision to reduce risk (max 200 words)",
    "confidence_score": 0.0-1.0
}}

Important: 
- Return ONLY valid JSON, no additional text
- Analyze based on legal precedents and market standards
- CRITICAL = likely unenforceable or causes litigation
- HIGH = unusual or risky compared to market standard
- MEDIUM = above market standard but potentially enforceable
- LOW = market standard, reasonable, and enforceable
- dispute_prone: true if clause has been subject to litigation in precedents"""

CLAUSE_RISK_PROMPT = PromptTemplate(
    input_variables=["clause_text", "precedents"],
    template=CLAUSE_RISK_PROMPT_TEMPLATE,
)

# System prompt for chat bot
CHAT_SYSTEM_PROMPT_TEMPLATE = """You are an expert contract advisor with deep knowledge of contract law, risk assessment, and industry best practices.

CONTRACT CONTEXT:
{contract_context}

RISK SUMMARY:
{risk_summary}

You have access to:
- Full contract text and structure
- Risk scores for each clause
- Similar legal precedents and case law
- Industry benchmarks

Answer questions about the contract, explain risks, suggest improvements, and provide legal guidance based on the contract and precedents.
Be concise but thorough. Always cite relevant clauses when discussing risks."""

CHAT_SYSTEM_PROMPT = PromptTemplate(
    input_variables=["contract_context", "risk_summary"],
    template=CHAT_SYSTEM_PROMPT_TEMPLATE,
)

# Prompt for combining retrieved context with question
CHAT_COMBINE_DOCUMENTS_TEMPLATE = """Using the provided contract context and precedents, answer the user's question accurately and thoroughly.

QUESTION: {question}

RELEVANT CONTRACT SECTIONS:
{context}

Provide a clear, direct answer based on the contract and legal precedents."""

CHAT_COMBINE_DOCUMENTS_PROMPT = PromptTemplate(
    input_variables=["question", "context"],
    template=CHAT_COMBINE_DOCUMENTS_TEMPLATE,
)
