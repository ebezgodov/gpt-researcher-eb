from typing import Any, Dict, List, Optional
import requests
import os
import xml.etree.ElementTree as ET
import json


class CustomRetriever:
    """
    Custom API Retriever
    """

    def __init__(self, query: str):
        self.endpoint = os.getenv('RETRIEVER_ENDPOINT')
        if not self.endpoint:
            raise ValueError("RETRIEVER_ENDPOINT environment variable not set")

        self.params = self._populate_params()
        self.query = query

    def _populate_params(self) -> Dict[str, Any]:
        """
        Populates parameters from environment variables prefixed with 'RETRIEVER_ARG_'
        """
        return {
            key[len('RETRIEVER_ARG_'):].lower(): value
            for key, value in os.environ.items()
            if key.startswith('RETRIEVER_ARG_')
        }

    def search(self, max_results: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Performs the search using the custom retriever endpoint.

        :param max_results: Maximum number of results to return (not currently used)
        :return: JSON response in the format:
            [
              {
                "url": "http://example.com/page1",
                "raw_content": "Content of page 1"
              },
              {
                "url": "http://example.com/page2",
                "raw_content": "Content of page 2"
              }
            ]
        """
        try:
            response = requests.get(self.endpoint, params={**self.params, 'query': self.query})
            response.raise_for_status()
            root = ET.fromstring(response.content)
            
            # Convert to JSON
            json_list = []
            for group in root.findall('.//grouping/group'):
                categ = group.find('categ').attrib['name']
                for doc in group.findall('doc'):
                    url = doc.find('url').text
                    raw_content = doc.find('passages').text
                    json_list.append({
                        "url": url,
                        "raw_content": raw_content
                    })
            json_result = json.dumps(json_list, indent=2, ensure_ascii=False)

            return json_result

        except requests.RequestException as e:
            print(f"Failed to retrieve search results: {e}")
            return None