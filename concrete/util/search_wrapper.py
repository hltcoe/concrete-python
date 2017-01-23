from concrete.search import SearchService
from concrete.util.service_wrapper import (
    ConcreteServiceClientWrapper,
    ConcreteServiceWrapper,
    SubprocessConcreteServiceWrapper)


SearchClientWrapper = type(
    'SearchClientWrapper',
    (ConcreteServiceClientWrapper,),
    {'concrete_service_class': SearchService})


SearchServiceWrapper = type(
    'SearchServiceWrapper',
    (ConcreteServiceWrapper,),
    {'concrete_service_class': SearchService})


SubprocessSearchServiceWrapper = type(
    'SubprocessSearchServiceWrapper',
    (SubprocessConcreteServiceWrapper,),
    {'concrete_service_wrapper_class': SearchServiceWrapper})
