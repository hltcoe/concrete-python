from ..search import SearchService, SearchProxyService, FeedbackService
from .service_wrapper import (
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


SearchProxyClientWrapper = type(
    'SearchProxyClientWrapper',
    (ConcreteServiceClientWrapper,),
    {'concrete_service_class': SearchProxyService})


SearchProxyServiceWrapper = type(
    'SearchProxyServiceWrapper',
    (ConcreteServiceWrapper,),
    {'concrete_service_class': SearchProxyService})


SubprocessSearchProxyServiceWrapper = type(
    'SubprocessSearchProxyServiceWrapper',
    (SubprocessConcreteServiceWrapper,),
    {'concrete_service_wrapper_class': SearchProxyServiceWrapper})


FeedbackClientWrapper = type(
    'FeedbackClientWrapper',
    (ConcreteServiceClientWrapper,),
    {'concrete_service_class': FeedbackService})


FeedbackServiceWrapper = type(
    'FeedbackServiceWrapper',
    (ConcreteServiceWrapper,),
    {'concrete_service_class': FeedbackService})


SubprocessFeedbackServiceWrapper = type(
    'SubprocessFeedbackServiceWrapper',
    (SubprocessConcreteServiceWrapper,),
    {'concrete_service_wrapper_class': FeedbackServiceWrapper})
