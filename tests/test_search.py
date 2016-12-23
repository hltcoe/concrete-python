from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TCompactProtocol

from concrete.util.search_wrapper import SubprocessSearchServiceWrapper
from concrete.util.net import find_port


from time import time

from concrete.search import SearchService
from concrete.search.ttypes import (
    SearchType, SearchQuery, SearchResult, SearchResultItem
)
from concrete.uuid.ttypes import UUID
from concrete.metadata.ttypes import AnnotationMetadata


class FooSearch(SearchService.Iface):
    METADATA_TOOL = 'Foo Search'

    def search(self, search_query):
        return SearchResult(
            uuid=UUID(uuidString='12345678-1234-5678-1234-567812345678'),
            searchResultItems=[
                SearchResultItem(communicationId=term, score=42.)
                for term in search_query.terms
            ],
            metadata=AnnotationMetadata(tool=self.METADATA_TOOL,
                                        timestamp=int(time()))
        )

    def shutdown(self):
        pass


def test_search_communications():
    impl = FooSearch()
    host = 'localhost'
    port = find_port()
    timeout = 5

    terms = ['foo', 'bar']
    query = SearchQuery(type=SearchType.COMMUNICATIONS,
                        terms=[t for t in terms])

    with SubprocessSearchServiceWrapper(impl, host, port, timeout=timeout):
        transport = TSocket.TSocket(host, port)
        transport = TTransport.TFramedTransport(transport)
        protocol = TCompactProtocol.TCompactProtocol(transport)

        cli = SearchService.Client(protocol)
        transport.open()
        res = cli.search(query)
        transport.close()

        assert res.uuid.uuidString == '12345678-1234-5678-1234-567812345678'
        assert len(res.searchResultItems) == 2
        assert res.searchResultItems[0].communicationId == 'foo'
        assert res.searchResultItems[0].score == 42.
        assert res.searchResultItems[1].communicationId == 'bar'
        assert res.searchResultItems[1].score == 42.
        assert res.metadata.tool == 'Foo Search'
