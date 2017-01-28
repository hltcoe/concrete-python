from ..services.results import ResultsServerService
from .service_wrapper import (
    ConcreteServiceClientWrapper,
    ConcreteServiceWrapper,
    SubprocessConcreteServiceWrapper)


ResultsServerClientWrapper = type(
    'ResultsServerClientWrapper',
    (ConcreteServiceClientWrapper,),
    {'concrete_service_class': ResultsServerService})


ResultsServerServiceWrapper = type(
    'ResultsServerServiceWrapper',
    (ConcreteServiceWrapper,),
    {'concrete_service_class': ResultsServerService})


SubprocessResultsServerServiceWrapper = type(
    'SubprocessResultsServerServiceWrapper',
    (SubprocessConcreteServiceWrapper,),
    {'concrete_service_wrapper_class': ResultsServerServiceWrapper})
