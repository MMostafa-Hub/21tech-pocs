from elasticsearch import Elasticsearch


class ElasticSearchVectorStore:
    def __init__(self, es_host: str, index_name: str):
        self.es = Elasticsearch(es_host)
        self.index_name = index_name

    def search(self, query: dict) -> dict:
        return self.es.search(index=self.index_name, body=query)
