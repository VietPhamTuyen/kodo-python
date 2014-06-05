// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <boost/python/args.hpp>

namespace kodo_python
{
    template<class Coder>
    void factory(const std::string& name)
    {
        using namespace boost::python;

        typedef typename Coder::factory factory_type;
        class_<factory_type, boost::noncopyable>(name.c_str(),
            init<uint32_t, uint32_t>())
            .def("build", &factory_type::build, "BUILD")
            .def("set_symbols", &factory_type::set_symbols, arg("symbols"), "SET_SYMBOLS")
            .def("set_symbol_size", &factory_type::set_symbol_size, arg("symbol_size"), "SET_SYMBOL_SIZE")
            .def("max_symbols", &factory_type::max_symbols, "MAX_SYMBOLS")
            .def("max_symbol_size", &factory_type::max_symbol_size, "MAX_SYMBOL_SIZE")
            .def("max_block_size", &factory_type::max_block_size, "MAX_BLOCK_SIZE")
            .def("max_payload_size", &factory_type::max_payload_size, "MAX_PAYLOAD_SIZE")
        ;
    }
}
