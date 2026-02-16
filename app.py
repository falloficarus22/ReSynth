"""
Streamlit web interface for ReSynth
"""

import streamlit as st
import sys
import os
from typing import List, Dict, Any

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.fetchers import ArxivFetcher, PubmedFetcher
from src.processors import SemanticChunker
from src.embeddings import VectorStore
from src.retrieval import Retriever
from src.synthesis import AnswerSynthesizer
from config import Config

# Page configuration
st.set_page_config(
    page_title="ReSynth - Research Paper Synthesis",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .paper-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .answer-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2ecc71;
        margin: 1rem 0;
    }
    .confidence-meter {
        background-color: #ecf0f1;
        border-radius: 10px;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }
    .chunk-info {
        font-size: 0.9rem;
        color: #7f8c8d;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_papers' not in st.session_state:
    st.session_state.processed_papers = []
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = VectorStore()
if 'retriever' not in st.session_state:
    st.session_state.retriever = Retriever(st.session_state.vector_store)
if 'synthesizer' not in st.session_state:
    st.session_state.synthesizer = AnswerSynthesizer()

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<div class="main-header">ReSynth</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #7f8c8d; font-size: 1.1rem;">Research Paper Synthesis Agent</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## Settings")
        
        # Citation style
        citation_style = st.selectbox(
            "Citation Style",
            options=["numeric", "apa", "mla", "author_date"],
            index=0
        )
        
        # Retrieval settings
        st.markdown("### Retrieval Settings")
        top_k = st.slider("Top K Results", min_value=1, max_value=20, value=5)
        similarity_threshold = st.slider("Similarity Threshold", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
        
        # System info
        st.markdown("### System Info")
        if st.button("Refresh Stats"):
            st.rerun()
        
        try:
            stats = st.session_state.retriever.get_retrieval_statistics()
            collection_stats = stats.get('collection_stats', {})
            st.metric("Total Chunks", collection_stats.get('total_chunks', 0))
            st.metric("Total Papers", stats.get('total_papers', 0))
        except Exception as e:
            st.error(f"Error loading stats: {e}")
        
        # Clear database button
        if st.button("Clear Database", type="secondary"):
            try:
                st.session_state.vector_store.clear_collection()
                st.success("Database cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing database: {e}")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["Search & Process", "Query Papers", "Database"])
    
    with tab1:
        search_and_process_tab()
    
    with tab2:
        query_tab(citation_style, top_k, similarity_threshold)
    
    with tab3:
        database_tab()

def search_and_process_tab():
    """Search and process papers tab"""
    st.markdown('<div class="section-header">Search & Process Papers</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        query = st.text_input(
            "Enter search query",
            placeholder="e.g., machine learning interpretability, transformer architectures, etc.",
            help="Search for research papers from arXiv and PubMed"
        )
    
    with col2:
        source = st.selectbox(
            "Source",
            options=["arxiv", "pubmed", "both"],
            index=0
        )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        max_papers = st.number_input("Max Papers", min_value=1, max_value=50, value=5)
    
    with col2:
        fetch_content = st.checkbox("Fetch Full Content", value=True)
    
    with col3:
        process_button = st.button("Process Papers", type="primary")
    
    if process_button and query:
        with st.spinner("Searching and processing papers..."):
            try:
                # Initialize fetchers
                arxiv_fetcher = ArxivFetcher(max_results=max_papers)
                pubmed_fetcher = PubmedFetcher(max_results=max_papers)
                
                # Search for papers
                papers = []
                if source in ["arxiv", "both"]:
                    st.info("🔎 Searching arXiv...")
                    arxiv_papers = arxiv_fetcher.search(query)
                    papers.extend(arxiv_papers)
                    st.success(f"Found {len(arxiv_papers)} papers from arXiv")
                
                if source in ["pubmed", "both"]:
                    st.info("🔎 Searching PubMed...")
                    pubmed_papers = pubmed_fetcher.search(query)
                    papers.extend(pubmed_papers)
                    st.success(f"Found {len(pubmed_papers)} papers from PubMed")
                
                if not papers:
                    st.error("No papers found")
                    return
                
                papers = papers[:max_papers]
                st.info(f"Processing {len(papers)} papers...")
                
                # Fetch full content if requested
                if fetch_content:
                    progress_bar = st.progress(0)
                    for i, paper in enumerate(papers):
                        if paper.arxiv_id:
                            content = arxiv_fetcher.fetch_paper_content(paper)
                            paper.content = content
                        elif paper.pubmed_id:
                            content = pubmed_fetcher.fetch_paper_content(paper)
                            paper.content = content
                        progress_bar.progress((i + 1) / len(papers))
                
                # Chunk papers
                st.info("Chunking papers...")
                chunker = SemanticChunker(chunk_size=Config.CHUNK_SIZE, chunk_overlap=Config.CHUNK_OVERLAP)
                chunks = chunker.chunk_multiple_papers(papers)
                
                # Add to vector store
                st.info("Adding to vector store...")
                success = st.session_state.vector_store.add_chunks(chunks)
                
                if success:
                    st.success(f"Successfully processed {len(papers)} papers into {len(chunks)} chunks!")
                    st.session_state.processed_papers.extend(papers)
                    
                    # Display processed papers
                    st.markdown('<div class="section-header">Processed Papers</div>', unsafe_allow_html=True)
                    
                    for i, paper in enumerate(papers):
                        with st.expander(f"{paper.title}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Authors:**")
                                authors_text = ", ".join(paper.authors[:3])
                                if len(paper.authors) > 3:
                                    authors_text += f" et al. ({len(paper.authors)} authors total)"
                                st.write(authors_text)
                                
                                if paper.published_date:
                                    st.write(f"**Published:** {paper.published_date}")
                                
                                if paper.journal:
                                    st.write(f"**Journal:** {paper.journal}")
                            
                            with col2:
                                if paper.arxiv_id:
                                    st.write(f"**arXiv ID:** {paper.arxiv_id}")
                                    st.markdown(f"[View Paper]({paper.url})")
                                
                                if paper.pubmed_id:
                                    st.write(f"**PubMed ID:** {paper.pubmed_id}")
                                    st.markdown(f"[View Paper]({paper.url})")
                                
                                if paper.doi:
                                    st.write(f"**DOI:** {paper.doi}")
                            
                            st.write("**Abstract:**")
                            st.write(paper.abstract)
                            
                            if fetch_content and paper.content:
                                with st.expander("Full Content"):
                                    st.text_area("", paper.content, height=300, disabled=True)
                else:
                    st.error("Failed to add chunks to vector store")
                    
            except Exception as e:
                st.error(f"Error processing papers: {e}")

def query_tab(citation_style: str, top_k: int, similarity_threshold: float):
    """Query papers tab"""
    st.markdown('<div class="section-header">Query Papers</div>', unsafe_allow_html=True)
    
    query = st.text_input(
        "Enter your question",
        placeholder="e.g., What are the main challenges in deep learning interpretability?",
        help="Ask questions about the processed research papers"
    )
    
    if st.button("Get Answer", type="primary") and query:
        with st.spinner("Retrieving relevant information and synthesizing answer..."):
            try:
                # Retrieve relevant chunks
                chunks = st.session_state.retriever.retrieve(
                    query, 
                    top_k=top_k, 
                    similarity_threshold=similarity_threshold
                )
                
                if not chunks:
                    st.warning("No relevant information found. Try processing some papers first.")
                    return
                
                # Validate retrieval quality
                quality = st.session_state.retriever.validate_retrieval_quality(query, chunks)
                
                # Synthesize answer
                answer_obj = st.session_state.synthesizer.synthesize_answer(
                    query, chunks, citation_style=citation_style
                )
                
                # Display answer
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown("### Answer")
                st.write(answer_obj.answer)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Display confidence
                confidence_color = "Green" if answer_obj.confidence_score > 0.7 else "Yellow" if answer_obj.confidence_score > 0.5 else "Red"
                st.markdown(f"### Confidence Score: {confidence_color} {answer_obj.confidence_score:.2f}")
                
                # Display retrieval quality
                with st.expander("Retrieval Quality Analysis"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Average Similarity", f"{quality.get('average_similarity', 0):.3f}")
                        st.metric("Min Similarity", f"{quality.get('min_similarity', 0):.3f}")
                        st.metric("Unique Papers", quality.get('unique_papers', 0))
                    
                    with col2:
                        st.metric("Total Results", quality.get('total_results', 0))
                        st.metric("Diversity Score", f"{quality.get('diversity_score', 0):.3f}")
                        st.metric("Quality", "Good" if quality.get('valid') else "Needs Improvement")
                    
                    if quality.get('quality_issues'):
                        st.write("**Quality Issues:**")
                        for issue in quality['quality_issues']:
                            st.write(f"Warning: {issue}")
                    
                    if quality.get('suggestions'):
                        st.write("**Suggestions:**")
                        for suggestion in quality['suggestions']:
                            st.write(f"Suggestion: {suggestion}")
                
                # Display source chunks
                with st.expander(f"Source Chunks ({len(chunks)})"):
                    for i, chunk in enumerate(chunks):
                        metadata = chunk.get('metadata', {})
                        
                        st.markdown(f"""
                        <div class="paper-card">
                            <strong>Chunk {i+1}</strong> - Similarity: {chunk.get('similarity', 0):.3f}
                            <br><strong>Paper:</strong> {metadata.get('paper_title', 'Unknown')}
                            <br><strong>Authors:</strong> {', '.join(metadata.get('paper_authors', [])[:3])}{'...' if len(metadata.get('paper_authors', [])) > 3 else ''}
                            <br><div class="chunk-info">{chunk.get('text', '')[:300]}...</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Display bibliography
                if answer_obj.bibliography:
                    with st.expander("References"):
                        st.markdown(answer_obj.bibliography)
                
            except Exception as e:
                st.error(f"Error processing query: {e}")

def database_tab():
    """Database information tab"""
    st.markdown('<div class="section-header">Database Information</div>', unsafe_allow_html=True)
    
    try:
        # Get statistics
        stats = st.session_state.retriever.get_retrieval_statistics()
        collection_stats = stats.get('collection_stats', {})
        papers = stats.get('papers', [])
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Chunks", collection_stats.get('total_chunks', 0))
        
        with col2:
            st.metric("Total Papers", stats.get('total_papers', 0))
        
        with col3:
            st.metric("Collection", collection_stats.get('collection_name', 'Unknown'))
        
        with col4:
            st.metric("Storage", collection_stats.get('persist_directory', 'Unknown'))
        
        # Display papers
        if papers:
            st.markdown("### Papers in Database")
            
            search_term = st.text_input("Search papers...", key="paper_search")
            
            if search_term:
                filtered_papers = [p for p in papers if search_term.lower() in p.lower()]
            else:
                filtered_papers = papers
            
            st.write(f"Showing {len(filtered_papers)} of {len(papers)} papers")
            
            for i, paper in enumerate(filtered_papers):
                with st.expander(f"{paper}"):
                    # Get chunks for this paper
                    paper_chunks = st.session_state.retriever.retrieve_by_paper(paper, top_k=10)
                    
                    if paper_chunks:
                        st.write(f"Chunks available: {len(paper_chunks)}")
                        
                        # Show sample chunks
                        for j, chunk in enumerate(paper_chunks[:3]):
                            with st.expander(f"Chunk {j+1} (Similarity: {chunk.get('similarity', 0):.3f})"):
                                st.write(chunk.get('text', ''))
                    else:
                        st.write("No chunks found for this paper")
        else:
            st.info("No papers in database. Use the Search & Process tab to add papers.")
            
    except Exception as e:
        st.error(f"Error loading database information: {e}")

if __name__ == "__main__":
    main()
