"""
Command-line interface for ReSynth
"""

import argparse
import sys
import json
from typing import List

from src.fetchers import ArxivFetcher, PubmedFetcher
from src.processors import SemanticChunker
from src.embeddings import VectorStore
from src.retrieval import Retriever
from src.synthesis import AnswerSynthesizer
from config import Config

def setup_argparser():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(
        description="ReSynth - Research Paper Synthesis Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search and process papers
  python cli.py --search "machine learning interpretability" --source arxiv --max-papers 5
  
  # Query existing papers
  python cli.py --query "What are the main challenges in deep learning interpretability?"
  
  # Get system statistics
  python cli.py --stats
  
  # Clear database
  python cli.py --clear
        """
    )
    
    # Main actions
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--search", help="Search for papers to process")
    group.add_argument("--query", help="Query the processed papers")
    group.add_argument("--stats", action="store_true", help="Show system statistics")
    group.add_argument("--papers", action="store_true", help="List papers in database")
    group.add_argument("--clear", action="store_true", help="Clear the database")
    
    # Search options
    parser.add_argument("--source", choices=["arxiv", "pubmed", "both"], 
                       default="arxiv", help="Source to search papers from")
    parser.add_argument("--max-papers", type=int, default=5, 
                       help="Maximum number of papers to fetch")
    parser.add_argument("--no-content", action="store_true", 
                       help="Don't fetch full paper content (faster)")
    
    # Query options
    parser.add_argument("--top-k", type=int, default=5, 
                       help="Number of top results to retrieve")
    parser.add_argument("--threshold", type=float, default=0.7, 
                       help="Similarity threshold for retrieval")
    parser.add_argument("--citation-style", choices=["numeric", "apa", "mla", "author_date"], 
                       default="numeric", help="Citation style")
    
    # Output options
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    return parser

def search_and_process_papers(query: str, source: str, max_papers: int, 
                             fetch_content: bool, verbose: bool):
    """Search for papers and process them"""
    print(f"Searching for papers: '{query}'")
    print(f"Source: {source}")
    print(f"Max papers: {max_papers}")
    
    # Initialize fetchers
    arxiv_fetcher = ArxivFetcher(max_results=max_papers)
    pubmed_fetcher = PubmedFetcher(max_results=max_papers)
    
    # Search for papers
    papers = []
    if source in ["arxiv", "both"]:
        print("Searching arXiv...")
        arxiv_papers = arxiv_fetcher.search(query)
        papers.extend(arxiv_papers)
        print(f"   Found {len(arxiv_papers)} papers from arXiv")
    
    if source in ["pubmed", "both"]:
        print("Searching PubMed...")
        pubmed_papers = pubmed_fetcher.search(query)
        papers.extend(pubmed_papers)
        print(f"   Found {len(pubmed_papers)} papers from PubMed")
    
    if not papers:
        print("No papers found")
        return
    
    papers = papers[:max_papers]
    print(f"Processing {len(papers)} papers")
    
    # Fetch full content if requested
    if fetch_content:
        print("Fetching full paper content...")
        for i, paper in enumerate(papers):
            if verbose:
                print(f"   [{i+1}/{len(papers)}] {paper.title[:50]}...")
            
            if paper.arxiv_id:
                content = arxiv_fetcher.fetch_paper_content(paper)
                paper.content = content
            elif paper.pubmed_id:
                content = pubmed_fetcher.fetch_paper_content(paper)
                paper.content = content
    
    # Chunk papers
    print("Chunking papers...")
    chunker = SemanticChunker(chunk_size=Config.CHUNK_SIZE, chunk_overlap=Config.CHUNK_OVERLAP)
    chunks = chunker.chunk_multiple_papers(papers)
    print(f"   Created {len(chunks)} chunks")
    
    # Add to vector store
    print("Adding to vector store...")
    vector_store = VectorStore()
    success = vector_store.add_chunks(chunks)
    
    if success:
        print("Successfully processed papers!")
        print("\nProcessed papers:")
        for i, paper in enumerate(papers):
            print(f"   {i+1}. {paper.title}")
            print(f"      Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
            if paper.arxiv_id:
                print(f"      arXiv ID: {paper.arxiv_id}")
            if paper.pubmed_id:
                print(f"      PubMed ID: {paper.pubmed_id}")
            print()
    else:
        print("Failed to add chunks to vector store")

def query_papers(query: str, top_k: int, threshold: float, citation_style: str, 
                json_output: bool, verbose: bool):
    """Query the processed papers"""
    print(f"Querying papers: '{query}'")
    
    # Initialize components
    vector_store = VectorStore()
    retriever = Retriever(vector_store)
    synthesizer = AnswerSynthesizer()
    
    # Retrieve relevant chunks
    print("Retrieving relevant chunks...")
    chunks = retriever.retrieve(query, top_k=top_k, similarity_threshold=threshold)
    
    if not chunks:
        print("No relevant information found")
        print("Try processing some papers first using --search")
        return
    
    if verbose:
        print(f"Retrieved {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            metadata = chunk.get('metadata', {})
            print(f"   [{i+1}] {metadata.get('paper_title', 'Unknown')} (similarity: {chunk.get('similarity', 0):.3f})")
    
    # Validate retrieval quality
    quality = retriever.validate_retrieval_quality(query, chunks)
    if verbose:
        print(f"Retrieval quality: {'Good' if quality['valid'] else 'Needs improvement'}")
        if quality['quality_issues']:
            for issue in quality['quality_issues']:
                print(f"   Warning: {issue}")
    
    # Synthesize answer
    print("Synthesizing answer...")
    answer_obj = synthesizer.synthesize_answer(query, chunks, citation_style=citation_style)
    
    # Output results
    if json_output:
        result = {
            "query": query,
            "answer": answer_obj.answer,
            "confidence_score": answer_obj.confidence_score,
            "source_chunks_count": len(chunks),
            "retrieval_quality": quality,
            "citations": {
                title: {
                    "authors": citation.authors,
                    "year": citation.year,
                    "journal": citation.journal
                }
                for title, citation in answer_obj.citations.items()
            }
        }
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "="*60)
        print("ANSWER")
        print("="*60)
        print(answer_obj.answer)
        
        if answer_obj.bibliography:
            print("\n" + "="*60)
            print("REFERENCES")
            print("="*60)
            print(answer_obj.bibliography)
        
        print(f"\nConfidence Score: {answer_obj.confidence_score:.2f}")
        print(f"Source Chunks: {len(chunks)}")
        
        if quality['quality_issues']:
            print("Quality Issues:")
            for issue in quality['quality_issues']:
                print(f"   - {issue}")

def show_stats():
    """Show system statistics"""
    print("System Statistics")
    print("="*40)
    
    vector_store = VectorStore()
    retriever = Retriever(vector_store)
    
    stats = retriever.get_retrieval_statistics()
    
    collection_stats = stats.get('collection_stats', {})
    print(f"Collection: {collection_stats.get('collection_name', 'Unknown')}")
    print(f"Total Chunks: {collection_stats.get('total_chunks', 0)}")
    print(f"Storage: {collection_stats.get('persist_directory', 'Unknown')}")
    
    papers = stats.get('papers', [])
    print(f"Total Papers: {stats.get('total_papers', 0)}")
    
    if papers:
        print("\nRecent Papers:")
        for i, paper in enumerate(papers[:5], 1):
            print(f"   {i}. {paper}")
        if len(papers) > 5:
            print(f"   ... and {len(papers) - 5} more")

def list_papers():
    """List all papers in the database"""
    print("Papers in Database")
    print("="*40)
    
    vector_store = VectorStore()
    papers = vector_store.get_papers_in_collection()
    
    if not papers:
        print("No papers found in database")
        print("Try processing some papers first using --search")
        return
    
    print(f"Total Papers: {len(papers)}\n")
    
    for i, paper in enumerate(papers, 1):
        print(f"{i:2d}. {paper}")

def clear_database():
    """Clear the database"""
    print("Clearing database...")
    
    vector_store = VectorStore()
    success = vector_store.clear_collection()
    
    if success:
        print("Database cleared successfully")
    else:
        print("Failed to clear database")

def main():
    """Main CLI entry point"""
    parser = setup_argparser()
    args = parser.parse_args()
    
    # Validate configuration
    Config.validate()
    
    try:
        if args.search:
            search_and_process_papers(
                args.search, args.source, args.max_papers,
                not args.no_content, args.verbose
            )
        elif args.query:
            query_papers(
                args.query, args.top_k, args.threshold,
                args.citation_style, args.json, args.verbose
            )
        elif args.stats:
            show_stats()
        elif args.papers:
            list_papers()
        elif args.clear:
            clear_database()
    
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
