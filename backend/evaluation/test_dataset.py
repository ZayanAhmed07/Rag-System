"""
Test Dataset for RAG Evaluation

Contains sample questions with ground truth answers for benchmarking
"""

TEST_DATASET = [
    {
        "question": "What is Zero Knowledge Proof?",
        "ground_truth": "Zero Knowledge Proof is a cryptographic method where one party (the prover) can prove to another party (the verifier) that a statement is true without revealing any information beyond the validity of the statement itself.",
        "category": "cryptography"
    },
    {
        "question": "How does Retrieval Augmented Generation work?",
        "ground_truth": "Retrieval Augmented Generation (RAG) combines information retrieval with text generation. It first retrieves relevant documents from a knowledge base, then uses those documents as context for a language model to generate accurate, grounded responses.",
        "category": "ai"
    },
    {
        "question": "What is the difference between BM25 and semantic search?",
        "ground_truth": "BM25 is a keyword-based ranking function that scores documents based on term frequency and inverse document frequency. Semantic search uses dense vector embeddings to find documents based on meaning and context, not just keyword matches. Hybrid search combines both approaches for better results.",
        "category": "information_retrieval"
    },
    {
        "question": "What is HyDE in the context of RAG?",
        "ground_truth": "HyDE (Hypothetical Document Embeddings) is a technique where you generate a hypothetical answer to a question, then use that answer's embedding to search for relevant documents. This often improves retrieval quality because the hypothetical answer is semantically closer to actual answer documents than the question itself.",
        "category": "rag"
    },
    {
        "question": "What metrics are used to evaluate RAG systems?",
        "ground_truth": "Common RAG evaluation metrics include: Faithfulness (does the answer stick to the retrieved context), Context Precision (are retrieved documents relevant), Context Recall (is all needed information retrieved), Answer Relevancy (is the answer relevant to the question), and Citation Precision (are citations accurate).",
        "category": "evaluation"
    },
    {
        "question": "What is Reciprocal Rank Fusion?",
        "ground_truth": "Reciprocal Rank Fusion (RRF) is a method for combining results from multiple ranking systems. It scores each document as 1/(k + rank) where k is typically 60, then sums scores across all ranking systems. This provides a simple yet effective way to merge semantic and keyword search results in hybrid search.",
        "category": "information_retrieval"
    },
    {
        "question": "How do you optimize token usage in RAG?",
        "ground_truth": "Token optimization strategies include: limiting the number of retrieved documents, truncating long contexts, compressing context using summarization, dynamic filtering to keep only relevant chunks, and using query enhancement to improve retrieval precision so fewer documents are needed.",
        "category": "optimization"
    },
    {
        "question": "What is the purpose of chunking in RAG?",
        "ground_truth": "Chunking breaks large documents into smaller, manageable pieces that can be individually embedded and retrieved. This allows for more precise retrieval of relevant information, improves embedding quality, and helps stay within token limits. Common strategies include fixed-size chunking, recursive chunking, and semantic chunking.",
        "category": "rag"
    },
    {
        "question": "What is context window in LLMs?",
        "ground_truth": "The context window is the maximum number of tokens an LLM can process in a single request, including both input (prompt + retrieved context) and output (generated response). Different models have different context windows - e.g., GPT-3.5 has 4K tokens, GPT-4 can have up to 128K tokens.",
        "category": "llm"
    },
    {
        "question": "How does caching improve RAG performance?",
        "ground_truth": "Caching stores previously computed results (embeddings, retrieved documents, or generated answers) so they can be reused for identical or similar queries. This reduces latency, lowers API costs, and decreases compute requirements. Common caching strategies use Redis or in-memory stores with TTL (time-to-live) policies.",
        "category": "optimization"
    }
]


DOMAIN_SPECIFIC_TESTS = {
    "technical_documentation": [
        {
            "question": "How do I install the package?",
            "ground_truth": "Installation instructions typically include package manager commands like 'pip install package-name' or 'npm install package-name', along with any system dependencies required."
        },
        {
            "question": "What are the system requirements?",
            "ground_truth": "System requirements specify minimum hardware, operating system versions, and software dependencies needed to run the application."
        }
    ],
    "customer_support": [
        {
            "question": "How do I reset my password?",
            "ground_truth": "Password reset typically involves clicking 'Forgot Password', entering your email, receiving a reset link, and creating a new password."
        },
        {
            "question": "What is your refund policy?",
            "ground_truth": "Refund policies specify the time window for returns, conditions for eligibility, and the refund process."
        }
    ]
}


def get_test_dataset(category: str = None, limit: int = None):
    """
    Get test dataset, optionally filtered by category
    
    Args:
        category: Filter by category (cryptography, ai, rag, etc.)
        limit: Maximum number of test cases to return
        
    Returns:
        List of test cases
    """
    dataset = TEST_DATASET.copy()
    
    if category:
        dataset = [t for t in dataset if t.get("category") == category]
    
    if limit:
        dataset = dataset[:limit]
    
    return dataset


def get_domain_tests(domain: str):
    """
    Get domain-specific test cases
    
    Args:
        domain: Domain name (technical_documentation, customer_support)
        
    Returns:
        List of test cases for that domain
    """
    return DOMAIN_SPECIFIC_TESTS.get(domain, [])
