// Copyright Steinwurf ApS 2015.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#include <boost/python.hpp>
#include <boost/python/docstring_options.hpp>

#include <string>

namespace kodo_python
{
    // Forward declarations of "create" functions implemented in other cpp files
    void create_full_vector_stacks();
    void create_on_the_fly_stacks();
    void create_sliding_window_stacks();
    void create_perpertual_stacks();
    void create_carousel_stacks();
    void create_fulcrum_stacks();

    void create_stacks()
    {
        create_full_vector_stacks();
        create_on_the_fly_stacks();
        create_sliding_window_stacks();
        create_perpertual_stacks();
        create_carousel_stacks();
        create_fulcrum_stacks();
    }

    std::string version()
    {
        std::string version = std::string("kodo-python: ");
        version += STEINWURF_KODO_PYTHON_VERSION;

        // Add dependency versions:
        version += std::string("\n\tboost: ");
#ifdef STEINWURF_BOOST_VERSION
        version += std::string(STEINWURF_BOOST_VERSION);
#endif
        version += std::string("\n\tcpuid: ");
#ifdef STEINWURF_CPUID_VERSION
        version += std::string(STEINWURF_CPUID_VERSION);
#endif
        version += std::string("\n\tfifi: ");
#ifdef STEINWURF_FIFI_VERSION
        version += std::string(STEINWURF_FIFI_VERSION);
#endif
        version += std::string("\n\tkodo: ");
#ifdef STEINWURF_KODO_VERSION
        version += std::string(STEINWURF_KODO_VERSION);
#endif
        version += std::string("\n\tplatform: ");
#ifdef STEINWURF_PLATFORM_VERSION
        version += std::string(STEINWURF_PLATFORM_VERSION);
#endif
        version += std::string("\n\trecycle: ");
#ifdef STEINWURF_RECYCLE_VERSION
        version += std::string(STEINWURF_RECYCLE_VERSION);
#endif
        version += std::string("\n\tsak: ");
#ifdef STEINWURF_SAK_VERSION
        version += std::string(STEINWURF_SAK_VERSION);
#endif

        return version;
    }

    void create_version_function()
    {
        using namespace boost::python;
        scope().attr("__version__") = version();
    }

    BOOST_PYTHON_MODULE(kodo)
    {
        boost::python::docstring_options doc_options;
        doc_options.disable_signatures();
        create_version_function();
        create_stacks();
    }
}
