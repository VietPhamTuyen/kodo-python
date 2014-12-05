// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <boost/python/args.hpp>

#include <kodo/trace.hpp>
#include <kodo/has_trace.hpp>

#include <string>
#include <Python.h>

namespace kodo_python
{

    template<class Coder>
    void trace(Coder& coder)
    {
        kodo::trace(coder);
    }

    template<class Coder>
    void trace_with_callback(Coder& coder, PyObject* function)
    {
        auto callback = [function](
            const std::string& zone, const std::string& message)
        {
            boost::python::call<void>(function, zone, message);
        };

        kodo::trace(coder, callback);
    }

    template<class TraceTag, bool has_trace, class Type>
    struct trace_methods
    {
        template<class CoderClass>
        trace_methods(CoderClass& coder_class)
        {
            (void) coder_class;
        }
    };

    template<class Type>
    struct trace_methods<kodo::enable_trace, true, Type>
    {
        template<class CoderClass>
        trace_methods(CoderClass& coder_class)
        {
            coder_class
            .def("trace", &trace<Type>,
                "Use a default callback to trace debug info to stdout.\n"
            )
            .def("trace", &trace_with_callback<Type>,
                boost::python::arg("callback"),
                "Write the trace information to a callback.\n\n"
                "\t:param callback: The callback which is called with the zone "
                "and message.");
        }
    };

    template<template<class, class> class Coder, class Field, class TraceTag>
    auto coder(const std::string& name) ->
        boost::python::class_<Coder<Field, TraceTag>, boost::noncopyable>
    {
        using namespace boost::python;
        using boost::python::arg;

        typedef Coder<Field, TraceTag> coder_type;
        auto coder_class = class_<coder_type, boost::noncopyable>(
            name.c_str(), "An (en/de)coder", no_init)
        .def("payload_size", &coder_type::payload_size,
            "Return the required payload buffer size in bytes.\n\n"
            "\t:returns: The required payload buffer size in bytes.\n"
        )
        .def("block_size", &coder_type::block_size,
            "Return the block size.\n\n"
            "\t:returns: The block size i.e. the total size in bytes that this "
            "coder operates on.\n"
        )
        .def("symbol_size", &coder_type::symbol_size,
            "Return the symbol size of a symbol in bytes.\n\n"
            "\t:returns: The symbol size of a symbol in bytes.\n"
        )
        .def("symbols", &coder_type::symbols,
            "Return the number of symbols in this block coder.\n\n"
            "\t:returns: The number of symbols in this block coder.\n"
        )
        .def("rank", &coder_type::rank,
            "Return the rank.\n\n"
            "The rank of a decoder states how many symbols have been "
            "decoded or partially decoded. The rank of an encoder states how "
            "many symbols are available for encoding.\n\n"
            "\t:returns: The rank.\n"
        )
        .def("is_symbol_pivot", &coder_type::is_symbol_pivot,
            arg("symbol_index"),
            "Check if a certain symbol is a pivot.\n\n"
            "A symbol is pivot if it is available to either the encoder or "
            "decoder. A coefficient generator may use this information when "
            "generating coding coefficients.\n\n"
            "\t:param symbol_index: The index of the symbol.\n"
            "\t:returns: True if the symbol is available.\n"
        );

        trace_methods<TraceTag, kodo::has_trace<coder_type>::value, coder_type>
            trace_methods(coder_class);

        return coder_class;
    }
}
