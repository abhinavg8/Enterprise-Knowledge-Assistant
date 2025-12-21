"""
Comprehensive Test Suite for Enterprise Knowledge Assistant
Tests all components and measures performance
"""
import sys
from pathlib import Path
import json
import time
from typing import List, Dict
import numpy as np

sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_pipeline import EnterpriseKnowledgeAssistant


class RAGTester:
    """Comprehensive testing for RAG pipeline"""
    
    def __init__(self, assistant: EnterpriseKnowledgeAssistant):
        """
        Initialize tester
        
        Args:
            assistant: EnterpriseKnowledgeAssistant instance
        """
        self.assistant = assistant
        self.results = {
            "search_tests": [],
            "qa_tests": [],
            "performance_metrics": {},
        }
    
    def test_document_loading(self) -> bool:
        """Test document loading functionality"""
        print("\n" + "="*70)
        print("TEST 1: Document Loading")
        print("="*70)
        
        try:
            stats = self.assistant.document_loader.get_document_stats()
            
            print(f"\n✓ Document stats retrieved:")
            print(f"  - Total files: {stats['total_files']}")
            print(f"  - Total size: {stats['total_size_mb']} MB")
            print(f"  - File types: {dict((k,v) for k,v in stats.items() if k.startswith('.'))}")
            
            if stats['total_files'] == 0:
                print("✗ FAILED: No documents found")
                return False
            
            print("\n✓ PASSED: Documents loaded successfully")
            return True
            
        except Exception as e:
            print(f"✗ FAILED: {str(e)}")
            return False
    
    def test_vector_store(self) -> bool:
        """Test vector store functionality"""
        print("\n" + "="*70)
        print("TEST 2: Vector Store")
        print("="*70)
        
        try:
            stats = self.assistant.vector_manager.get_stats()
            
            print(f"\n✓ Vector store stats:")
            print(f"  - Total vectors: {stats['total_vectors']}")
            print(f"  - Vector dimension: {stats['vector_dimension']}")
            print(f"  - Is trained: {stats['is_trained']}")
            
            if stats['total_vectors'] == 0:
                print("✗ FAILED: No vectors in store")
                return False
            
            print("\n✓ PASSED: Vector store operational")
            return True
            
        except Exception as e:
            print(f"✗ FAILED: {str(e)}")
            return False
    
    def test_similarity_search(self, queries: List[str], k: int = 3) -> Dict:
        """
        Test similarity search functionality
        
        Args:
            queries: List of test queries
            k: Number of results to retrieve
            
        Returns:
            Dictionary with test results
        """
        print("\n" + "="*70)
        print("TEST 3: Similarity Search")
        print("="*70)
        
        search_times = []
        results_summary = []
        
        for query in queries:
            print(f"\nQuery: '{query}'")
            
            start_time = time.time()
            results = self.assistant.search_documents(query, k=k, with_scores=True)
            search_time = time.time() - start_time
            
            search_times.append(search_time)
            
            print(f"  Retrieved {len(results)} results in {search_time:.3f}s")
            
            if results:
                avg_score = np.mean([r['similarity_score'] for r in results])
                print(f"  Average similarity score: {avg_score:.4f}")
                print(f"  Top result: {results[0]['source']} (score: {results[0]['similarity_score']:.4f})")
                
                results_summary.append({
                    "query": query,
                    "num_results": len(results),
                    "search_time": search_time,
                    "avg_score": avg_score,
                    "top_source": results[0]['source']
                })
        
        avg_search_time = np.mean(search_times)
        
        print(f"\n✓ Search Performance:")
        print(f"  - Average search time: {avg_search_time:.3f}s")
        print(f"  - Searches per second: {1/avg_search_time:.1f}")
        
        self.results["search_tests"] = results_summary
        self.results["performance_metrics"]["avg_search_time"] = avg_search_time
        
        print("\n✓ PASSED: Similarity search working")
        return results_summary
    
    def test_question_answering(self, queries: List[str]) -> Dict:
        """
        Test Q&A functionality
        
        Args:
            queries: List of test queries
            
        Returns:
            Dictionary with test results
        """
        print("\n" + "="*70)
        print("TEST 4: Question Answering")
        print("="*70)
        
        qa_times = []
        qa_results = []
        
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] Question: '{query}'")
            
            start_time = time.time()
            result = self.assistant.ask(query, return_sources=True)
            qa_time = time.time() - start_time
            
            qa_times.append(qa_time)
            
            answer_length = len(result['answer'])
            num_sources = len(result.get('sources', []))
            
            print(f"  Answer length: {answer_length} characters")
            print(f"  Sources used: {num_sources}")
            print(f"  Response time: {qa_time:.2f}s")
            print(f"  Answer preview: {result['answer'][:150]}...")
            
            qa_results.append({
                "question": query,
                "answer_length": answer_length,
                "num_sources": num_sources,
                "response_time": qa_time
            })
        
        avg_qa_time = np.mean(qa_times)
        avg_answer_length = np.mean([r['answer_length'] for r in qa_results])
        
        print(f"\n✓ Q&A Performance:")
        print(f"  - Average response time: {avg_qa_time:.2f}s")
        print(f"  - Average answer length: {avg_answer_length:.0f} characters")
        print(f"  - Throughput: {60/avg_qa_time:.1f} queries per minute")
        
        self.results["qa_tests"] = qa_results
        self.results["performance_metrics"]["avg_qa_time"] = avg_qa_time
        self.results["performance_metrics"]["avg_answer_length"] = avg_answer_length
        
        print("\n✓ PASSED: Question answering working")
        return qa_results
    
    def test_batch_processing(self, queries: List[str]) -> Dict:
        """
        Test batch processing performance
        
        Args:
            queries: List of queries to process
            
        Returns:
            Dictionary with batch test results
        """
        print("\n" + "="*70)
        print("TEST 5: Batch Processing")
        print("="*70)
        
        print(f"\nProcessing {len(queries)} queries in batch...")
        
        start_time = time.time()
        results = self.assistant.batch_ask(queries, return_sources=False)
        total_time = time.time() - start_time
        
        avg_time_per_query = total_time / len(queries)
        throughput = len(queries) / total_time * 60  # queries per minute
        
        print(f"\n✓ Batch Performance:")
        print(f"  - Total time: {total_time:.2f}s")
        print(f"  - Average per query: {avg_time_per_query:.2f}s")
        print(f"  - Throughput: {throughput:.1f} queries/minute")
        
        self.results["performance_metrics"]["batch_total_time"] = total_time
        self.results["performance_metrics"]["batch_throughput"] = throughput
        
        print("\n✓ PASSED: Batch processing working")
        return {
            "total_time": total_time,
            "avg_time": avg_time_per_query,
            "throughput": throughput
        }
    
    def calculate_time_savings(self) -> Dict:
        """
        Calculate time savings compared to manual search
        Assumes manual search takes 5 minutes per query on average
        """
        print("\n" + "="*70)
        print("PERFORMANCE ANALYSIS: Time Savings")
        print("="*70)
        
        avg_qa_time = self.results["performance_metrics"]["avg_qa_time"]
        manual_search_time = 300  # 5 minutes in seconds
        
        time_saved_per_query = manual_search_time - avg_qa_time
        time_saved_percentage = (time_saved_per_query / manual_search_time) * 100
        
        # For 100 queries per day
        queries_per_day = 100
        daily_time_saved = (time_saved_per_query * queries_per_day) / 3600  # hours
        
        print(f"\n✓ Time Savings Analysis:")
        print(f"  - Manual search time (baseline): {manual_search_time}s ({manual_search_time/60:.1f} min)")
        print(f"  - RAG system time: {avg_qa_time:.2f}s")
        print(f"  - Time saved per query: {time_saved_per_query:.2f}s ({time_saved_per_query/60:.1f} min)")
        print(f"  - Percentage reduction: {time_saved_percentage:.1f}%")
        print(f"\n  For {queries_per_day} queries/day:")
        print(f"  - Daily time saved: {daily_time_saved:.1f} hours")
        print(f"  - Weekly time saved: {daily_time_saved * 5:.1f} hours")
        print(f"  - Monthly time saved: {daily_time_saved * 20:.1f} hours")
        
        savings = {
            "time_saved_per_query": time_saved_per_query,
            "percentage_reduction": time_saved_percentage,
            "daily_hours_saved": daily_time_saved,
            "weekly_hours_saved": daily_time_saved * 5,
            "monthly_hours_saved": daily_time_saved * 20
        }
        
        self.results["performance_metrics"]["time_savings"] = savings
        
        return savings
    
    def generate_report(self, output_file: str = None) -> str:
        """
        Generate comprehensive test report
        
        Args:
            output_file: Path to save report (optional)
            
        Returns:
            Report as string
        """
        report = []
        report.append("=" * 70)
        report.append("ENTERPRISE KNOWLEDGE ASSISTANT - TEST REPORT")
        report.append("=" * 70)
        report.append("")
        
        # System Info
        report.append("SYSTEM CONFIGURATION")
        report.append("-" * 70)
        stats = self.assistant.get_system_stats()
        report.append(f"Documents Directory: {stats['docs_directory']}")
        report.append(f"Total Vectors: {stats['vector_store']['total_vectors']}")
        report.append(f"Embedding Model: {stats['embedding_model']['model_name']}")
        report.append(f"LLM: {stats['llm']['model_name']}")
        report.append("")
        
        # Performance Metrics
        report.append("PERFORMANCE METRICS")
        report.append("-" * 70)
        metrics = self.results["performance_metrics"]
        report.append(f"Average Search Time: {metrics.get('avg_search_time', 0):.3f}s")
        report.append(f"Average Q&A Time: {metrics.get('avg_qa_time', 0):.2f}s")
        report.append(f"Batch Throughput: {metrics.get('batch_throughput', 0):.1f} queries/min")
        report.append("")
        
        # Time Savings
        if "time_savings" in metrics:
            savings = metrics["time_savings"]
            report.append("TIME SAVINGS (vs Manual Search)")
            report.append("-" * 70)
            report.append(f"Reduction: {savings['percentage_reduction']:.1f}%")
            report.append(f"Time Saved per Query: {savings['time_saved_per_query']:.1f}s")
            report.append(f"Daily Hours Saved (100 queries): {savings['daily_hours_saved']:.1f}h")
            report.append(f"Monthly Hours Saved: {savings['monthly_hours_saved']:.1f}h")
            report.append("")
        
        # Sample Q&A Results
        if self.results["qa_tests"]:
            report.append("SAMPLE Q&A RESULTS")
            report.append("-" * 70)
            for i, test in enumerate(self.results["qa_tests"][:5], 1):
                report.append(f"\n{i}. {test['question']}")
                report.append(f"   Response Time: {test['response_time']:.2f}s")
                report.append(f"   Sources Used: {test['num_sources']}")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"\n✓ Report saved to: {output_file}")
        
        return report_text
    
    def run_all_tests(self, sample_queries: List[str]) -> None:
        """
        Run all tests
        
        Args:
            sample_queries: List of queries to test
        """
        print("\n" + "="*70)
        print("RUNNING COMPREHENSIVE TEST SUITE")
        print("="*70)
        
        # Run tests
        self.test_document_loading()
        self.test_vector_store()
        
        # Use subset of queries for different tests
        search_queries = sample_queries[:5]
        qa_queries = sample_queries[:3]
        batch_queries = sample_queries[:5]
        
        self.test_similarity_search(search_queries)
        self.test_question_answering(qa_queries)
        self.test_batch_processing(batch_queries)
        self.calculate_time_savings()
        
        # Generate report
        print("\n" + "="*70)
        print("GENERATING TEST REPORT")
        print("="*70)
        report = self.generate_report()
        print("\n" + report)


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("ENTERPRISE KNOWLEDGE ASSISTANT - COMPREHENSIVE TESTING")
    print("="*70)
    
    # Load sample queries
    queries_file = Path(__file__).parent / "data" / "sample_queries.json"
    with open(queries_file, 'r') as f:
        queries_data = json.load(f)
    
    # Flatten all queries
    all_queries = []
    for category_data in queries_data["test_queries"]:
        all_queries.extend(category_data["queries"])
    
    print(f"\nLoaded {len(all_queries)} test queries")
    
    # Initialize assistant
    print("\nInitializing Enterprise Knowledge Assistant...")
    assistant = EnterpriseKnowledgeAssistant(
        model_type="huggingface",
        model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        rebuild_index=False
    )
    
    # Run tests
    tester = RAGTester(assistant)
    tester.run_all_tests(all_queries)
    
    print("\n" + "="*70)
    print("✓ ALL TESTS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
