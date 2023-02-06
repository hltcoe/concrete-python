API Reference
=============

.. automodule:: concrete
    :members:
    :undoc-members:
    :show-inheritance:


High-level interface
--------------------

.. toctree::

   concrete.inspect
   concrete.util
   concrete.validate
   concrete.version


Low-level interface (Concrete schema)
-------------------------------------

Note that all data types defined by the Concrete schema---except for
services---can be imported directly from the top-level ``concrete``
package.  For example, instead of
``from concrete.communication.ttypes import Communication`` you can
write ``from concrete import Communication``.

.. toctree::

    concrete.access
    concrete.annotate
    concrete.audio
    concrete.clustering
    concrete.communication
    concrete.context
    concrete.convert
    concrete.email
    concrete.entities
    concrete.exceptions
    concrete.language
    concrete.learn
    concrete.linking
    concrete.metadata
    concrete.nitf
    concrete.property
    concrete.search
    concrete.services
    concrete.situations
    concrete.spans
    concrete.structure
    concrete.summarization
    concrete.twitter
    concrete.uuid
