from ..access import (
    FetchCommunicationService,
    StoreCommunicationService)
from .service_wrapper import (
    ConcreteServiceClientWrapper,
    ConcreteServiceWrapper,
    HTTPConcreteServiceClientWrapper,
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


HTTPFetchCommunicationClientWrapper = type(
    'HTTPFetchCommunicationClientWrapper',
    (HTTPConcreteServiceClientWrapper,),
    {'concrete_service_class': FetchCommunicationService})


HTTPStoreCommunicationClientWrapper = type(
    'HTTPStoreCommunicationClientWrapper',
    (HTTPConcreteServiceClientWrapper,),
    {'concrete_service_class': StoreCommunicationService})


StoreCommunicationClientWrapper = type(
    'StoreCommunicationClientWrapper',
    (ConcreteServiceClientWrapper,),
    {'concrete_service_class': StoreCommunicationService})


StoreCommunicationServiceWrapper = type(
    'StoreCommunicationServiceWrapper',
    (ConcreteServiceWrapper,),
    {'concrete_service_class': StoreCommunicationService})


SubprocessStoreCommunicationServiceWrapper = type(
    'SubprocessStoreCommunicationServiceWrapper',
    (SubprocessConcreteServiceWrapper,),
    {'concrete_service_wrapper_class': StoreCommunicationServiceWrapper})
