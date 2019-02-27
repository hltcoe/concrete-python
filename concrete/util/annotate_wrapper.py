from ..annotate import AnnotateCommunicationService
from .service_wrapper import (
    ConcreteServiceClientWrapper,
    ConcreteServiceWrapper,
    HTTPConcreteServiceClientWrapper,
    SubprocessConcreteServiceWrapper)


AnnotateCommunicationClientWrapper = type(
    'AnnotateCommunicationClientWrapper',
    (ConcreteServiceClientWrapper,),
    {'concrete_service_class': AnnotateCommunicationService})


AnnotateCommunicationServiceWrapper = type(
    'AnnotateCommunicationServiceWrapper',
    (ConcreteServiceWrapper,),
    {'concrete_service_class': AnnotateCommunicationService})


HTTPAnnotateCommunicationClientWrapper = type(
    'HTTPAnnotateCommunicationClientWrapper',
    (HTTPConcreteServiceClientWrapper,),
    {'concrete_service_class': AnnotateCommunicationService})


SubprocessAnnotateCommunicationServiceWrapper = type(
    'SubprocessAnnotateCommunicationServiceWrapper',
    (SubprocessConcreteServiceWrapper,),
    {'concrete_service_wrapper_class': AnnotateCommunicationServiceWrapper})
