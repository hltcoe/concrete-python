from ..learn import (
    ActiveLearnerClientService,
    ActiveLearnerServerService)
from .service_wrapper import (
    ConcreteServiceClientWrapper,
    ConcreteServiceWrapper,
    SubprocessConcreteServiceWrapper)


ActiveLearnerClientClientWrapper = type(
    'ActiveLearnerClientClientWrapper',
    (ConcreteServiceClientWrapper,),
    {'concrete_service_class': ActiveLearnerClientService})


ActiveLearnerClientServiceWrapper = type(
    'ActiveLearnerClientServiceWrapper',
    (ConcreteServiceWrapper,),
    {'concrete_service_class': ActiveLearnerClientService})


SubprocessActiveLearnerClientServiceWrapper = type(
    'SubprocessActiveLearnerClientServiceWrapper',
    (SubprocessConcreteServiceWrapper,),
    {'concrete_service_wrapper_class': ActiveLearnerClientServiceWrapper})


ActiveLearnerServerClientWrapper = type(
    'ActiveLearnerServerClientWrapper',
    (ConcreteServiceClientWrapper,),
    {'concrete_service_class': ActiveLearnerServerService})


ActiveLearnerServerServiceWrapper = type(
    'ActiveLearnerServerServiceWrapper',
    (ConcreteServiceWrapper,),
    {'concrete_service_class': ActiveLearnerServerService})


SubprocessActiveLearnerServerServiceWrapper = type(
    'SubprocessActiveLearnerServerServiceWrapper',
    (SubprocessConcreteServiceWrapper,),
    {'concrete_service_wrapper_class': ActiveLearnerServerServiceWrapper})
