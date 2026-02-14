"""
Command-line interface for ReSynth package
"""

import argparse
import sys
import os

def main():
    """Main CLI entry point for the package"""
    parser = argparse.ArgumentParser(
        description="ReSynth - Research Paper Synthesis Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search and process papers')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--source', choices=['arxiv', 'pubmed', 'both'], 
                              default='arxiv', help='Source to search')
    search_parser.add_argument('--max-papers', type=int, default=5, 
                              help='Maximum number of papers')
    search_parser.add_argument('--no-content', action='store_true',
                              help='Don\'t fetch full content')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query processed papers')
    query_parser.add_argument('question', help='Question to answer')
    query_parser.add_argument('--citation-style', choices=['apa', 'mla', 'numeric', 'author_date'],
                              default='numeric', help='Citation style')
    query_parser.add_argument('--top-k', type=int, default=5, help='Top K results')
    query_parser.add_argument('--threshold', type=float, default=0.7, help='Similarity threshold')
    
    # Stats command
    subparsers.add_parser('stats', help='Show system statistics')
    
    # Papers command
    subparsers.add_parser('papers', help='List papers in database')
    
    # Clear command
    subparsers.add_parser('clear', help='Clear database')
    
    # Web command
    subparsers.add_parser('web', help='Start web interface')
    
    # API command
    subparsers.add_parser('api', help='Start API server')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize agent
    from . import ReSynthAgent
    agent = ReSynthAgent()
    
    try:
        if args.command == 'search':
            papers = agent.search_and_process(
                args.query,
                source=args.source,
                max_papers=args.max_papers,
                fetch_content=not args.no_content
            )
            print(f"✅ Processed {len(papers)} papers")
            for paper in papers:
                print(f"   📄 {paper.title}")
        
        elif args.command == 'query':
            answer = agent.query(
                args.question,
                citation_style=args.citation_style,
                top_k=args.top_k,
                similarity_threshold=args.threshold
            )
            print(f"📝 Answer:\n{answer.answer}")
            if answer.bibliography:
                print(f"\n📚 References:\n{answer.bibliography}")
            print(f"\n📊 Confidence: {answer.confidence_score:.2f}")
        
        elif args.command == 'stats':
            stats = agent.get_stats()
            print("📊 System Statistics:")
            print(f"   Total Papers: {stats.get('total_papers', 0)}")
            print(f"   Total Chunks: {stats.get('collection_stats', {}).get('total_chunks', 0)}")
        
        elif args.command == 'papers':
            papers = agent.list_papers()
            print(f"📚 Papers in database ({len(papers)}):")
            for paper in papers:
                print(f"   📄 {paper}")
        
        elif args.command == 'clear':
            success = agent.clear_database()
            if success:
                print("✅ Database cleared")
            else:
                print("❌ Failed to clear database")
        
        elif args.command == 'web':
            from .web import main as web_main
            web_main()
        
        elif args.command == 'api':
            # Import main from project root
            import sys
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            sys.path.insert(0, project_root)
            from main import app
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8000)
    
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
