from time import time

from concrete.services import Annotator
from concrete.metadata.ttypes import AnnotationMetadata


class NoopAnnotator(Annotator.Iface):
    METADATA_TOOL = 'No-op Annotator'

    def annotate(self, communication):
        return communication

    def getMetadata(self,):
        metadata = AnnotationMetadata(tool=self.METADATA_TOOL,
                                      timestamp=int(time()))
        return metadata

    def getDocumentation(self):
        return 'Annotator that returns communication unmodified'

    def shutdown(self):
        pass
