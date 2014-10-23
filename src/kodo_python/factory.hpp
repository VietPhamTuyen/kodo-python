// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <boost/python/args.hpp>

#include <string>

#include "resolve_field_name.hpp"

namespace kodo_python
{
    template<template<class, class> class Coder, class Field, class TraceTag>
    void factory(const std::string& stack, bool trace, const std::string& coder)
    {
        using boost::python::arg;
        using boost::python::args;
        using boost::python::class_;
        using boost::python::init;

        std::string field = resolve_field_name<Field>();

        std::string s = "_";
        std::string kind = coder + s + std::string("factory");
        std::string trace_string = trace ? "_trace" : "";
        std::string name = stack + s + kind + s + field + trace_string;

        typedef typename Coder<Field, TraceTag>::factory factory_type;
        auto factory = class_<factory_type, boost::noncopyable>(
            name.c_str(),
            (std::string("Factory for creating ") + coder + std::string("s.")
                ).c_str(),
            init<uint32_t, uint32_t>(
                args("max_symbols", "max_symbol_size"),
                "Factory constructor.\n\n"
                "\t:param max_symbols: "
                "The maximum symbols the coders can expect.\n"
                "\t:param max_symbol_size: "
                "The maximum size of a symbol in bytes.\n"))
        .def("build", &factory_type::build,
            "Build the actual coder.\n\n"
            "\t:returns: An instantiation of a coder.\n")
        .def("set_symbols", &factory_type::set_symbols, arg("symbols"),
            "Set the number of symbols.\n\n"
            "\t:param symbols: The number of symbols.\n"
        )
        .def("set_symbol_size", &factory_type::set_symbol_size,
            arg("symbol_size"),
            "Set the symbol size.\n\n"
            "\t:param symbols_size: The symbol size.\n"
        )
        .def("max_symbols", &factory_type::max_symbols,
            "Return the maximum number of symbols in a block.\n\n"
            "\t:returns: The maximum number of symbols in a block.\n"
        )
        .def("max_symbol_size", &factory_type::max_symbol_size,
            "Return the maximum symbol size in bytes.\n\n"
            "\t:returns: The maximum symbol size in bytes.\n"
        )
        .def("max_payload_size", &factory_type::max_payload_size,
            "Return the maximum required payload buffer size in bytes.\n\n"
            "\t:returns: The maximum required payload buffer size in bytes.\n"
        );

        std::string max_block_size_desc;
        if (coder == std::string("encoder"))
        {
            max_block_size_desc =
            "Return the maximum amount of data encoded in bytes.\n\n"
            "This is calculated by multiplying the maximum number of symbols "
            "encoded by the maximum size of a symbol.\n\n"
            "\t:returns: The maximum amount of data encoded in bytes\n";
        }
        else if (coder == std::string("decoder"))
        {
            max_block_size_desc =
            "Return the maximum amount of data decoded in bytes.\n\n"
            "This is calculated by multiplying the maximum number of symbols "
            "decoded by the maximum size of a symbol.\n\n"
            "\t:returns: The maximum amount of data decoded in bytes\n";
        }
        factory.def("max_block_size", &factory_type::max_block_size,
            max_block_size_desc.c_str()
        );
        // Enable boost to map from the c++ pointer type to the python coder
        // type. E.g., from std::shared_ptr<Codec> to python [Codec]_encoder.
        boost::python::register_ptr_to_python<typename factory_type::pointer>();
    }
}
