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
            print("111", response.content)
                
            # Парсинг XML данных
            root = ET.fromstring(response.content)
            print("222", root)

            # Ищем все документы в XML
            docs = root.findall('.//group/doc')
            print("333", len(docs))

            # Создаем список для JSON данных
            json_data = []

            # Обходим все найденные документы и добавляем их в JSON массив
            for doc in docs:
                url = doc.find('url').text
                print("444", url)
                raw_content = ' '.join(ET.tostring(passage, encoding='utf-8', method='text').strip().decode('utf-8') for passage in doc.findall('.//passage'))
                print("555", raw_content)
                json_data.append({'href': url, 'raw_content': raw_content})
                print("666", len(json_data))

            return json_data

        except requests.RequestException as e:
            print(f"Failed to retrieve search results: {e}")
            return None