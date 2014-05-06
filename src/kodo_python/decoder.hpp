// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <sak/storage.hpp>
#include <kodo/is_partial_complete.hpp>
#include <kodo/has_partial_decoding_tracker.hpp>
#include <kodo/print_decoder_state.hpp>
#include <kodo/has_print_cached_symbol_coefficients.hpp>
#include <kodo/has_print_cached_symbol_data.hpp>
#include <kodo/print_cached_symbol_coefficients.hpp>
#include <kodo/print_cached_symbol_data.hpp>

#include <Python.h>
#include <bytesobject.h>

namespace kodo_python
{

    template<class Decoder>
    PyObject* copy_symbols(Decoder& decoder)
    {
        std::vector<uint8_t> payload(decoder.block_size());
        auto storage = sak::mutable_storage(payload.data(), decoder.block_size());
        decoder.copy_symbols(storage);
        #if PY_MAJOR_VERSION >= 3
        return PyBytes_FromStringAndSize((char*)payload.data(), decoder.block_size());
        #else
        return PyString_FromStringAndSize((char*)payload.data(), decoder.block_size());
        #endif
    }

    /// @todo: consider removing this method from the python api.
    template<class Decoder>
    PyObject* copy_symbol(Decoder& decoder, uint32_t index)
    {
        std::vector<uint8_t> payload(decoder.block_size());
        auto storage = sak::mutable_storage(payload.data(), decoder.block_size());
        decoder.copy_symbol(index, storage);
        #if PY_MAJOR_VERSION >= 3
        return PyBytes_FromStringAndSize((char*)payload.data(), decoder.block_size());
        #else
        return PyString_FromStringAndSize((char*)payload.data(), decoder.block_size());
        #endif
    }

    template<class Decoder>
    PyObject* recode(Decoder& decoder, const std::string& data)
    {
        std::vector<uint8_t> payload(data.length());
        std::copy(data.c_str(), data.c_str() + data.length(), payload.data());
        decoder.recode(payload.data());
        #if PY_MAJOR_VERSION >= 3
        return PyBytes_FromStringAndSize((char*)payload.data(), data.length());
        #else
        return PyString_FromStringAndSize((char*)payload.data(), data.length());
        #endif
    }

    template<class Decoder>
    PyObject* decode(Decoder& decoder, const std::string& data)
    {
        std::vector<uint8_t> payload(data.length());
        std::copy(data.c_str(), data.c_str() + data.length(), payload.data());
        decoder.decode(payload.data());
        #if PY_MAJOR_VERSION >= 3
        return PyBytes_FromStringAndSize((char*)payload.data(), data.length());
        #else
        return PyString_FromStringAndSize((char*)payload.data(), data.length());
        #endif
    }

    template<class Decoder>
    bool has_partial_decoding_tracker(Decoder& decoder)
    {
        (void) decoder;
        return kodo::has_partial_decoding_tracker<Decoder>::value;
    }

    template<class Decoder>
    bool is_partial_complete(Decoder& decoder)
    {
        return kodo::is_partial_complete(decoder);
    }

    template<class Decoder>
    bool has_print_decoder_state(Decoder& decoder)
    {
        (void) decoder;
        return kodo::has_debug_linear_block_decoder<Decoder>::value;
    }

    template<class Decoder>
    void print_decoder_state(Decoder& decoder)
    {
        kodo::print_decoder_state(decoder, std::cout);
    }

    template<class Decoder>
    bool has_print_cached_symbol_coefficients(Decoder& decoder)
    {
        (void) decoder;
        return kodo::has_print_cached_symbol_coefficients<Decoder>::value;
    }

    template<class Decoder>
    void print_cached_symbol_coefficients(Decoder& decoder)
    {
        kodo::print_cached_symbol_coefficients(decoder, std::cout);
    }

    template<class Decoder>
    bool has_print_cached_symbol_data(Decoder& decoder)
    {
        (void) decoder;
        return kodo::has_print_cached_symbol_data<Decoder>::value;
    }

    template<class Decoder>
    void print_cached_symbol_data(Decoder& decoder)
    {
        kodo::print_cached_symbol_data(decoder, std::cout);
    }

    template<class Coder>
    void decoder(const std::string& name)
    {
        typedef Coder decoder_type;
        boost::python::class_<decoder_type, boost::noncopyable>(name.c_str(),
            boost::python::no_init)
            .def("payload_size", &decoder_type::payload_size)
            .def("block_size", &decoder_type::block_size)
            .def("symbol_size", &decoder_type::symbol_size)
            .def("symbols", &decoder_type::symbols)
            .def("rank", &decoder_type::rank)
            .def("is_symbol_pivot", &decoder_type::is_symbol_pivot)
            .def("recode", &recode<decoder_type>)
            .def("decode", &decode<decoder_type>)
            .def("is_complete", &decoder_type::is_complete)
            .def("copy_symbols", &copy_symbols<decoder_type>)
            .def("copy_symbol", &decoder_type::copy_symbol)
            .def("is_symbol_decoded", &decoder_type::is_symbol_decoded)
            .def("has_partial_decoding_tracker", &has_partial_decoding_tracker<decoder_type>)
            .def("is_partial_complete", &is_partial_complete<decoder_type>)
            .def("has_print_decoder_state", &has_print_decoder_state<decoder_type>)
            .def("print_decoder_state", &print_decoder_state<decoder_type>)
            .def("has_print_cached_symbol_coefficients", &has_print_cached_symbol_coefficients<decoder_type>)
            .def("print_cached_symbol_coefficients", &print_cached_symbol_coefficients<decoder_type>)
            .def("has_print_cached_symbol_data", &has_print_cached_symbol_data<decoder_type>)
            .def("print_cached_symbol_data", &print_cached_symbol_data<decoder_type>)
        ;

        boost::python::register_ptr_to_python<boost::shared_ptr<decoder_type>>();
    }
}


