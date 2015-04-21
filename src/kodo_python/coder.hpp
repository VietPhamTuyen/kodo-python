// Copyright Steinwurf ApS 2015.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <string>

#include <Python.h>
#include <boost/python/args.hpp>

#include <kodo/trace.hpp>
#include <kodo/has_trace.hpp>
#include <kodo/has_rank.hpp>

#include "has_is_symbol_pivot.hpp"

namespace kodo_python
{
    template<bool HAS_IS_SYMBOL_PIVOT, class Type>
    struct is_symbol_pivot_method
    {
        template<class CoderClass>
        is_symbol_pivot_method(CoderClass& coder_class)
        {
            (void) coder_class;
        }
    };

    template<class Type>
    struct is_symbol_pivot_method<true, Type>
    {
        template<class CoderClass>
        is_symbol_pivot_method(CoderClass& coder_class)
        {
            coder_class
            .def("is_symbol_pivot", &Type::is_symbol_pivot,
                boost::python::arg("symbol_index"),
                "Check if a certain symbol is a pivot.\n\n"
                "A symbol is pivot if it is available to either the encoder or "
                "decoder. A coefficient generator may use this information "
                "when generating coding coefficients.\n\n"
                "\t:param symbol_index: The index of the symbol.\n"
                "\t:returns: True if the symbol is available.\n"
            );
        }
    };

    template<bool HAS_RANK, class Type>
    struct rank_method
    {
        template<class CoderClass>
        rank_method(CoderClass& coder_class)
        {
            (void) coder_class;
        }
    };

    template<class Type>
    struct rank_method<true, Type>
    {
        template<class CoderClass>
        rank_method(CoderClass& coder_class)
        {
            coder_class
            .def("rank", &Type::rank,
                "Return the rank.\n\n"
                "The rank of a decoder states how many symbols have been "
                "decoded or partially decoded. The rank of an encoder states "
                "how many symbols are available for encoding.\n\n"
                "\t:returns: The rank.\n"
            );
        }
    };

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
        );

        (is_symbol_pivot_method<
            has_is_symbol_pivot<coder_type>::value, coder_type> (coder_class));

        (rank_method<
            kodo::has_rank<coder_type>::value, coder_type> (coder_class));

        (trace_methods<TraceTag,
            kodo::has_trace<coder_type>::value, coder_type> (coder_class));

        return coder_class;
    }
}
