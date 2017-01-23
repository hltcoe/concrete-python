from concrete.access import FetchCommunicationService
from concrete.util.service_wrapper import (
    ConcreteServiceClientWrapper,
    ConcreteServiceWrapper,
    SubprocessConcreteServiceWrapper)


FetchCommunicationClientWrapper = type(
    'FetchCommunicationClientWrapper',
    (ConcreteServiceClientWrapper,),
    {'concrete_service_class': FetchCommunicationService})


FetchCommunicationServiceWrapper = type(
    'FetchCommunicationServiceWrapper',
    (ConcreteServiceWrapper,),
    {'concrete_service_class': FetchCommunicationService})


SubprocessFetchCommunicationServiceWrapper = type(
    'SubprocessFetchCommunicationServiceWrapper',
    (SubprocessConcreteServiceWrapper,),
    {'concrete_service_wrapper_class': FetchCommunicationServiceWrapper})
