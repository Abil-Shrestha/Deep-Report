from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
import os
from dotenv import load_dotenv
# Correct import according to the README
from google import genai
# from tavily import TavilyClient
from exa_py import Exa

load_dotenv()

@dataclass
class Perspective:
    content: str
    source: str

@dataclass
class Conversation:
    questions: List[str] = None
    answers: List[str] = None

    def __post_init__(self):
        self.questions = [] if self.questions is None else self.questions
        self.answers = [] if self.answers is None else self.answers
class STORM:
    def __init__(self):
        """Initialize STORM by loading API keys from environment variables and setting up models."""
        # Initialize Gemini client
        gemini_api_key = os.getenv("GEMINI_LLM_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_LLM_KEY environment variable is not set")
        self.gemini_client = genai.Client(api_key=gemini_api_key)

        # Initialize Exa client
        exa_api_key = os.getenv("EXA_API_KEY")
        if not exa_api_key:
            raise ValueError("EXA_API_KEY environment variable is not set")
        self.exa_client = Exa(api_key=exa_api_key)
    
    def gen_related_topics(self, topic: str) -> List[str]:
        """Generate related topics for the given input topic using Gemini.

        Args:
            topic (str): The main topic to find related topics for

        Returns:
            List[str]: List of related topics
        """
        prompt = f"""
        Given the topic '{topic}', generate 5 highly relevant and specific related topics.
        Each topic should explore a different aspect or perspective of the main topic.
        Format the output as a Python list of strings, with each topic being clear and concise.
        Example format: ['Topic 1', 'Topic 2', 'Topic 3', 'Topic 4', 'Topic 5']
        Make sure each topic is specific enough to yield meaningful search results.
        """

        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-pro',
                contents=prompt
            )
            
            # The response should be in a format that can be evaluated as a Python list
            # We'll use a safer approach to extract the list items
            text_response = response.text.strip()
            
            # Extract the list part (assuming it's properly formatted)
            if '[' in text_response and ']' in text_response:
                list_part = text_response[text_response.find('['):text_response.rfind(']')+1]
                try:
                    topics = eval(list_part)  # Safe in this context as we're expecting a list literal
                    if isinstance(topics, list) and all(isinstance(x, str) for x in topics):
                        return topics
                except:
                    pass  # Fall through to default return if eval fails
            
            # Fallback: split by newlines and clean up
            topics = [line.strip().strip("'[]") for line in text_response.split('\n') 
                     if line.strip() and not line.strip().startswith('[') and not line.strip().endswith(']')]
            return [topic for topic in topics if topic][:5]  # Return up to 5 topics
            
        except Exception as e:
            print(f"Error generating related topics: {str(e)}")
            # Fallback to ensure we always return something
            return [f"{topic} - aspect {i+1}" for i in range(3)]

    def get_wiki_article(self, topic: str) -> Optional[str]:
        """Fetch Wikipedia article content for a given topic.

        Args:
            topic (str): Topic to search for

        Returns:
            Optional[str]: Article content if found, None otherwise
        """
        try:
            url = f"https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "titles": topic,
                "prop": "extracts",
                "exintro": True
            }
            response = requests.get(url, params=params)
            data = response.json()
            pages = data["query"]["pages"]
            page = next(iter(pages.values()))
            return page.get("extract")
        except Exception:
            return None

    def web_search(self, query: str) -> List[dict]:
        """Perform a web search for the given query using Exa API.

        Args:
            query (str): Search query string

        Returns:
            List[dict]: List of search results, each containing url, title, and content
        """
        try:
            # Use Exa's search_and_contents API with highlights for better content extraction
            response = self.exa_client.search_and_contents(
                query,
                num_results=8,  # Get more results for better coverage
                highlights={"num_sentences": 5},  # Get 5 sentences per highlight
                use_autoprompt=True  # Let Exa optimize the query
            )
            
            # Convert Exa results to match our expected format
            formatted_results = [{
                'url': result.url,
                'title': result.title,
                'content': result.highlights[0] if result.highlights else result.text,  # Use highlight if available
                'score': result.score if hasattr(result, 'score') else 0,
                'published_date': result.published_date if hasattr(result, 'published_date') else ''
            } for result in response.results]  # Access results through response.results
            
            return formatted_results
            
        except Exception as e:
            print(f"Error in web search: {str(e)}")
            return []
            return []

    def fetch_web_content(self, url: str) -> Optional[str]:
        """Fetch the web content from the given URL.

        Args:
            url (str): URL to fetch content from

        Returns:
            Optional[str]: Content of the web page if successful, None otherwise
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                return None
        except Exception:
            return None

    def re_rank_results(self, results: List[str]) -> List[str]:
        """Re-rank search results using a simple algorithm.

        Args:
            results (List[str]): Unranked list of search result URLs

        Returns:
            List[str]: Re-ranked list of URLs
        """
        # Placeholder: simple alphabetical sort. Replace with a better ranking algorithm if needed.
        return sorted(results)

    def extract_structure(self, search_results: List[dict]) -> List[str]:
        """Extract key topics and structure from search results using Gemini.

        Args:
            search_results (List[dict]): List of search results with content

        Returns:
            List[str]: List of key topics and structural elements
        """
        # Combine all content with their titles for context
        combined_content = "\n\n".join(
            f"Title: {result['title']}\n\nContent: {result['content']}"
            for result in search_results
        )

        prompt = f"""
        Analyze the following content and extract 5-7 key topics or themes that would be valuable 
        for creating a comprehensive outline. Each topic should be specific and informative.

        Content to analyze:
        {combined_content[:8000]}  # Limit content length to avoid token limits

        Format your response as a Python list of strings, where each string is a key topic.
        Example format: ['Topic 1: Specific detail', 'Topic 2: Specific detail']
        Make each topic informative and self-contained.
        """

        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-pro',
                contents=prompt
            )
            
            # Parse the response similar to gen_related_topics
            text_response = response.text.strip()
            
            if '[' in text_response and ']' in text_response:
                list_part = text_response[text_response.find('['):text_response.rfind(']')+1]
                try:
                    topics = eval(list_part)
                    if isinstance(topics, list) and all(isinstance(x, str) for x in topics):
                        return topics
                except:
                    pass

            # Fallback: split by newlines and clean up
            topics = [line.strip().strip("'[]")
                     for line in text_response.split('\n')
                     if line.strip() and not line.strip().startswith('[') 
                     and not line.strip().endswith(']')]
            return [topic for topic in topics if topic][:7]  # Return up to 7 topics

        except Exception as e:
            print(f"Error extracting structure: {str(e)}")
            # Fallback to basic topic extraction
            return [f"Key Point {i+1}" for i in range(5)]

    def gen_perspectives(self, topic: str, key_topics: List[str], search_results: List[dict]) -> List[Perspective]:
        """Generate insightful perspectives using Gemini based on key topics and search results.

        Args:
            topic (str): Main topic
            key_topics (List[str]): Key topics extracted from content
            search_results (List[dict]): Original search results for context

        Returns:
            List[Perspective]: Generated perspectives with supporting content
        """
        # Prepare context from search results
        context = "\n\n".join(
            f"Source {i+1}:\nTitle: {result['title']}\nContent: {result['content'][:500]}"  # Limit content length
            for i, result in enumerate(search_results[:3])  # Use top 3 results for context
        )

        prompt = f"""
        Topic: {topic}
        Key Topics Identified: {', '.join(key_topics)}

        Based on the following context and key topics, generate 3-5 unique analytical perspectives on the topic.
        Each perspective should:
        1. Focus on a specific aspect, trend, or element of the topic
        2. Include concrete examples and evidence from the sources
        3. Analyze its significance and impact within the broader context

        Context:
        {context}

        Format each perspective as a JSON object with 'content' (the analytical perspective) and 'source' (key topic or source it's derived from).
        Example format: [{{'content': 'A detailed analysis of a specific aspect...', 'source': 'Relevant Source or Topic'}}]
        """

        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-pro',
                contents=prompt
            )

            text_response = response.text.strip()
            
            # Try to parse as JSON list first
            if '[' in text_response and ']' in text_response:
                list_part = text_response[text_response.find('['):text_response.rfind(']')+1]
                try:
                    perspectives_data = eval(list_part)  # Safe as we expect a list of dicts
                    if isinstance(perspectives_data, list):
                        return [
                            Perspective(
                                content=p.get('content', ''),
                                source=p.get('source', 'Generated')
                            )
                            for p in perspectives_data
                            if isinstance(p, dict) and 'content' in p
                        ]
                except:
                    pass

            # Fallback: Generate basic perspectives from key topics
            return [
                Perspective(
                    content=f"Analysis of {topic} from the perspective of {key_topic}",
                    source=key_topic
                )
                for key_topic in key_topics[:5]  # Limit to 5 perspectives
            ]

        except Exception as e:
            print(f"Error generating perspectives: {str(e)}")
            # Final fallback
            return [
                Perspective(
                    content=f"General perspective {i+1} on {topic}",
                    source=f"Generated perspective {i+1}"
                )
                for i in range(3)
            ]

    def gen_qn(self, topic: str, perspective: Perspective, history: List[str]) -> str:
        """Generate an insightful question based on the topic and perspective using Gemini.

        Args:
            topic (str): Main topic
            perspective (Perspective): Current perspective
            history (List[str]): Conversation history

        Returns:
            str: Generated question
        """
        # Format conversation history for context
        history_context = "\n".join(history[-4:]) if history else "No previous conversation"
        
        prompt = f"""
        Topic: {topic}
        Perspective: {perspective.content}
        Source: {perspective.source}
        Previous Conversation:
        {history_context}

        Generate a thought-provoking question that:
        1. Explores the relationship between the main topic and the given perspective
        2. Avoids repeating questions from the conversation history
        3. Is specific enough to yield meaningful answers
        4. Encourages analytical thinking and detailed responses

        Format: Return only the question text, without any prefixes or explanations.
        """

        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-pro',
                contents=prompt
            )
            return response.text.strip().rstrip('?') + '?'
        except Exception as e:
            print(f"Error generating question: {str(e)}")
            return f"How does {perspective.content} influence or relate to {topic}?"

    def gen_queries(self, topic: str, question: str) -> List[str]:
        """Generate optimized search queries using Gemini.

        Args:
            topic (str): Main topic
            question (str): Current question

        Returns:
            List[str]: List of optimized search queries
        """
        prompt = f"""
        Topic: {topic}
        Question: {question}

        Generate 3 different search queries that will help find relevant information to answer the question.
        Each query should:
        1. Use different phrasings and keywords
        2. Be specific enough to find relevant results
        3. Include important context from the topic

        Format: Return a Python list of strings containing only the queries.
        Example format: ['query 1', 'query 2', 'query 3']
        """

        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-pro',
                contents=prompt
            )
            
            text_response = response.text.strip()
            if '[' in text_response and ']' in text_response:
                list_part = text_response[text_response.find('['):text_response.rfind(']')+1]
                try:
                    queries = eval(list_part)
                    if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
                        return queries
                except:
                    pass
            
            # Fallback: split by newlines and clean up
            queries = [q.strip().strip("'[]")
                      for q in text_response.split('\n')
                      if q.strip() and not q.strip().startswith('[')]
            return queries[:3] if queries else [f"{topic} {question}"]
            
        except Exception as e:
            print(f"Error generating queries: {str(e)}")
            return [f"{topic} {question}", f"{topic} analysis", f"{question} detailed explanation"]

    def gen_ans(self, question: str, search_results: List[dict]) -> str:
        """Generate a comprehensive answer using Gemini based on the question and search results.

        Args:
            question (str): Current question
            search_results (List[dict]): Search results with content

        Returns:
            str: Generated answer
        """
        # Prepare context from search results
        context = "\n\n".join(
            f"Source {i+1}:\nTitle: {result['title']}\nContent: {result['content']}"
            for i, result in enumerate(search_results)
        )

        prompt = f"""
        Question: {question}

        Based on the following sources, provide a comprehensive and well-structured answer.
        Focus on accuracy and relevance to the question.

        Sources:
        {context[:8000]}  # Limit context length

        Guidelines for the answer:
        1. Be specific and detailed
        2. Use information from multiple sources when possible
        3. Maintain objectivity
        4. Address all aspects of the question
        """

        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-pro',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            return "I apologize, but I couldn't generate a complete answer based on the available information."

    def direct_gen_outline(self, topic: str, search_results: List[dict]) -> List[str]:
        """Generate initial outline using Gemini based on the topic and search results.

        Args:
            topic (str): Main topic
            search_results (List[dict]): Search results with content

        Returns:
            List[str]: Initial outline points
        """
        # Prepare context from search results
        context = "\n\n".join(
            f"Source {i+1}:\nTitle: {result['title']}\nContent: {result['content'][:500]}"
            for i, result in enumerate(search_results[:5])  # Use top 5 results
        )

        prompt = f"""
        Topic: {topic}

        Based on the following sources, generate a detailed outline for a comprehensive analysis.
        The outline should:
        1. Have a clear hierarchical structure (use proper numbering)
        2. Focus on the most significant elements, developments, or aspects of the topic
        3. Include specific examples, data points, and supporting evidence
        4. Cover 3-5 main points with 2-3 key subpoints each

        Sources:
        {context}

        Format: Return the outline as a Python list of strings, with proper indentation indicated by prefixes.
        Example format: ['1. Major Aspect', '   1.1. Key Finding or Development', '   1.2. Supporting Evidence and Impact', '2. Next Major Aspect', ...]
        """

        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-pro',
                contents=prompt
            )
            
            # Parse the response
            text_response = response.text.strip()
            if '[' in text_response and ']' in text_response:
                list_part = text_response[text_response.find('['):text_response.rfind(']')+1]
                try:
                    outline = eval(list_part)
                    if isinstance(outline, list) and all(isinstance(x, str) for x in outline):
                        return outline
                except:
                    pass
            
            # Fallback: split by newlines and clean up
            outline = [line.strip().strip("'[]")
                      for line in text_response.split('\n')
                      if line.strip() and not line.strip().startswith('[')]
            return outline
            
        except Exception as e:
            print(f"Error generating initial outline: {str(e)}")
            return [f"{i}. Section on {topic}" for i in range(1, 4)]

    def refine_outline(self, topic: str, initial_outline: List[str], 
                      conversations: List[Conversation]) -> List[str]:
        """Refine outline using Gemini based on the initial outline and conversation insights.

        Args:
            topic (str): Main topic
            initial_outline (List[str]): Initial outline
            conversations (List[Conversation]): Conversation history

        Returns:
            List[str]: Refined outline
        """
        # Prepare conversation insights
        conversation_context = ""
        for conv in conversations:
            conversation_context += "\nQ: " + "\nQ: ".join(conv.questions)
            conversation_context += "\nA: " + "\nA: ".join(conv.answers)

        prompt = f"""
        Topic: {topic}

        Initial Outline:
        {chr(10).join(initial_outline)}

        Conversation Insights:
        {conversation_context}

        Refine and improve the initial outline based on the insights from the conversations.
        The refined outline should:
        1. Incorporate key insights from the conversations
        2. Maintain a clear structure while potentially adding or merging sections
        3. Be more specific and detailed where the conversations revealed important aspects
        4. Remove or revise any sections that the conversations proved less relevant

        Format: Return the refined outline as a Python list of strings, maintaining the same format as the initial outline.
        """

        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-pro',
                contents=prompt
            )
            
            # Parse the response
            text_response = response.text.strip()
            if '[' in text_response and ']' in text_response:
                list_part = text_response[text_response.find('['):text_response.rfind(']')+1]
                try:
                    outline = eval(list_part)
                    if isinstance(outline, list) and all(isinstance(x, str) for x in outline):
                        return outline
                except:
                    pass
            
            # Fallback: split by newlines and clean up
            outline = [line.strip().strip("'[]")
                      for line in text_response.split('\n')
                      if line.strip() and not line.strip().startswith('[')]
            return outline if outline else initial_outline
            
        except Exception as e:
            print(f"Error refining outline: {str(e)}")
            return initial_outline

    def run(self, topic: str, max_perspectives: int = 3, max_rounds: int = 2) -> tuple[List[str], List[Conversation]]:
        """Run the enhanced STORM algorithm using Gemini for intelligent content generation and analysis.

        Args:
            topic (str): Main topic to explore
            max_perspectives (int, optional): Maximum number of perspectives to generate. Defaults to 3.
            max_rounds (int, optional): Maximum number of conversation rounds per perspective. Defaults to 2.

        Returns:
            tuple[List[str], List[Conversation]]: Final outline and list of conversations that led to it
        """
        try:
            conversations: List[Conversation] = []
            print(f"Starting STORM analysis for topic: {topic}")

            # Step 1: Initial search to gather context
            print("Step 1: Gathering initial context...")
            initial_queries = self.gen_queries(topic, f"comprehensive overview of {topic}")
            search_results = []
            for query in initial_queries:
                results = self.web_search(query)
                if results:
                    search_results.extend(results)

            if not search_results:
                raise ValueError("No search results found for the initial queries")

            # Step 2: Generate initial outline
            print("Step 2: Generating initial outline...")
            initial_outline = self.direct_gen_outline(topic, search_results)

            # Step 3: Extract key topics and generate perspectives
            print("Step 3: Extracting key topics and generating perspectives...")
            key_topics = self.extract_structure(search_results)
            perspectives = self.gen_perspectives(topic, key_topics, search_results)

            if not perspectives:
                raise ValueError("No perspectives could be generated")

            # Step 4: Explore each perspective through conversation
            print(f"Step 4: Exploring {min(len(perspectives), max_perspectives)} perspectives...")
            for i, perspective in enumerate(perspectives[:max_perspectives], 1):
                print(f"\nExploring perspective {i}/{min(len(perspectives), max_perspectives)}")
                conversation = Conversation()
                history: List[str] = []  # Track conversation history for this perspective
                
                for round_num in range(max_rounds):
                    print(f"Round {round_num + 1}/{max_rounds}")
                    # Generate and ask a question
                    question = self.gen_qn(topic, perspective, history)
                    conversation.questions.append(question)
                    history.append(f"Q: {question}")
                    print(f"Generated question: {question}")

                    # Generate search queries and gather information
                    queries = self.gen_queries(topic, question)
                    round_results = []
                    for query in queries:
                        results = self.web_search(query)
                        if results:
                            round_results.extend(results)

                    # Generate and store the answer
                    answer = self.gen_ans(question, round_results)
                    conversation.answers.append(answer)
                    history.append(f"A: {answer}")
                    print("Answer generated")

                conversations.append(conversation)

            # Step 5: Refine the outline based on conversation insights
            print("\nStep 5: Refining final outline...")
            final_outline = self.refine_outline(topic, initial_outline, conversations)

            print("\nSTORM analysis completed successfully!")
            return final_outline, conversations

        except Exception as e:
            print(f"\nError during STORM analysis: {str(e)}")
            # Return a basic outline and empty conversations list in case of error
            return [f"1. Introduction to {topic}", 
                    f"2. Key aspects of {topic}", 
                    f"3. Conclusion about {topic}"], []