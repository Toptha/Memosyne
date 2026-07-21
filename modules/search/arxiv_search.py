import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

class ArxivSearch:
    """
    A module to search research papers on arXiv.
    This can be used in Mnemosyne to search papers before uploading them
    or downloading them for the semantic search system.
    """
    
    BASE_URL = "http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    
    def search(self, query: str, max_results: int = 5) -> list:
        """
        Searches arXiv for the given query and returns a list of dictionaries containing paper details.
        """
        encoded_query = urllib.parse.quote(query)
        url = self.BASE_URL.format(query=encoded_query, max_results=max_results)
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()
        except Exception as e:
            print(f"Error fetching data from arXiv: {e}")
            return []
            
        return self._parse_xml_to_dicts(xml_data)
        
    def _parse_xml_to_dicts(self, xml_data: bytes) -> list:
        """
        Parses the Atom XML response from arXiv into a list of dictionaries.
        """
        root = ET.fromstring(xml_data)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        
        for entry in root.findall('atom:entry', namespace):
            # Extract basic text fields
            title = entry.find('atom:title', namespace).text.replace('\n', ' ').strip()
            published = entry.find('atom:published', namespace).text[:4] # Extracting just the year
            summary = entry.find('atom:summary', namespace).text.replace('\n', ' ').strip()
            
            # Extract authors
            authors = [author.find('atom:name', namespace).text for author in entry.findall('atom:author', namespace)]
            
            # Extract PDF link
            pdf_link = "Not available"
            for link in entry.findall('atom:link', namespace):
                if link.attrib.get('title') == 'pdf':
                    pdf_link = link.attrib.get('href')
                    break
                    
            # Creating a dictionary for the paper
            paper_dict = {
                'Title': title,
                'Authors': ", ".join(authors),
                'Published': published,
                'PDF': pdf_link,
                'Summary': summary
            }
            
            papers.append(paper_dict)
            
        return papers
        
    def display_results(self, papers: list):
        """
        Displays the search results, demonstrating dictionary access methods.
        """
        if not papers:
            print("No papers found.")
            return
            
        for paper in papers:
            # Demonstration of dictionary access methods
            
            # 1. Dictionary access using keys directly (could raise KeyError if missing)
            # print(f"Title:\n{paper['Title']}") # Usually handled by .get() safely
            
            # 2. Using .get() for safe access
            print(f"Title:\n{paper.get('Title', 'No Title')}\n")
            print(f"Authors:\n{paper.get('Authors', 'Unknown Authors')}\n")
            print(f"Published:\n{paper.get('Published', 'Unknown Date')}\n")
            print(f"PDF:\n{paper.get('PDF', 'No Link')}\n")
            print(f"Summary:\n{paper.get('Summary', 'No Summary')}\n")
            
            # 3. Using .keys()
            # keys = list(paper.keys())
            # print(f"Available fields: {', '.join(keys)}")
            
            # 4. Using .values()
            # values_count = len(list(paper.values()))
            # print(f"Number of data points for this paper: {values_count}")
            
            # 5. Using .items() for dynamic traversal (useful for JSON/XML dumping)
            # print("Raw Data Dump:")
            # for key, value in paper.items():
            #     print(f"  {key}: {str(value)[:50]}...")
                
            print("-" * 50)


# Example Usage
if __name__ == "__main__":
    arxiv = ArxivSearch()
    
    # Prompt the user for a search query
    user_query = input("Enter your search query for arXiv: ").strip()
    
    if user_query:
        print(f"\nSearching for: {user_query}...\n")
        
        # Searching the user's query
        results = arxiv.search(user_query, max_results=2)
        
        # Showcase dictionary processing
        if results:
            print("--- Dictionary Processing Showcase ---")
            first_paper = results[0]
            print(f".keys() output: {list(first_paper.keys())}")
            print(f".values() output: {list(first_paper.values())[:2]}...") # Printing first 2 values to save space
            print(f".items() output: ")
            for k, v in first_paper.items():
                print(f"  {k} -> {str(v)[:30]}...")
            print("-" * 50)
            print("\n--- Formatted Output ---")
            
        arxiv.display_results(results)
    else:
        print("Search query cannot be empty.")
