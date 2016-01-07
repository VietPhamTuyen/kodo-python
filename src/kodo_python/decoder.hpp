// Copyright Steinwurf ApS 2015.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <algorithm>
#include <string>
#include <vector>

#include <Python.h>
#include <bytesobject.h>
#include <boost/python.hpp>
#include <boost/python/args.hpp>

#include <kodo_core/has_partial_decoding_tracker.hpp>
#include <kodo_core/has_write_payload.hpp>

#include <sak/storage.hpp>

#include "coder.hpp"
#include "resolve_field_name.hpp"

namespace kodo_python
{
    template<class Decoder>
    PyObject* copy_from_symbols(Decoder& decoder)
    {
        std::vector<uint8_t> payload(decoder.block_size());
        auto storage = sak::mutable_storage(
            payload.data(), decoder.block_size());
        decoder.copy_from_symbols(storage);
        #if PY_MAJOR_VERSION >= 3
        return PyBytes_FromStringAndSize(
            (char*)payload.data(), decoder.block_size());
        #else
        return PyString_FromStringAndSize(
            (char*)payload.data(), decoder.block_size());
        #endif
    }

    template<class Decoder>
    PyObject* decoder_write_payload(Decoder& decoder)
    {
        std::vector<uint8_t> payload(decoder.payload_size());
        auto length = decoder.write_payload(payload.data());

        #if PY_MAJOR_VERSION >= 3
        return PyBytes_FromStringAndSize((char*)payload.data(), length);
        #else
        return PyString_FromStringAndSize((char*)payload.data(), length);
        #endif
    }

    template<class Decoder>
    void read_payload(Decoder& decoder, const std::string& data)
    {
        std::vector<uint8_t> payload(data.length());
        std::copy(data.c_str(), data.c_str() + data.length(), payload.data());
        decoder.read_payload(payload.data());
    }

    template<bool HasPartialDecodingTracker>
    struct is_partially_complete_method
    {
        template<class DecoderClass>
        is_partially_complete_method(DecoderClass& decoder_class)
        {
            (void) decoder_class;
        }
    };

    template<>
    struct is_partially_complete_method<true>
    {
        template<class DecoderClass>
        is_partially_complete_method(DecoderClass& decoder_class)
        {
            decoder_class
            .def("is_partially_complete",
                &DecoderClass::wrapped_type::is_partially_complete,
                "Check whether the decoding matrix is partially decoded.\n\n"
                "\t:returns: True if the decoding matrix is partially "
                "decoded.\n");
        }
    };

    template<bool HasWritePayload>
    struct write_payload_method
    {
        template<class DecoderClass>
        write_payload_method(DecoderClass& decoder_class)
        {
            (void) decoder_class;
        }
    };

    template<>
    struct write_payload_method<true>
    {
        template<class DecoderClass>
        write_payload_method(DecoderClass& decoder_class)
        {
            decoder_class
            .def("write_payload",
                &decoder_write_payload<typename DecoderClass::wrapped_type>,
                "Recode symbol.\n\n"
                "\t:returns: The recoded symbol.\n"
            );
        }
    };

    template<template<class, class> class Coder>
    struct extra_decoder_methods
    {
        template<class DecoderClass>
        extra_decoder_methods(DecoderClass& decoder_class)
        {
            (void) decoder_class;
        }
    };

    template<
        template<class, class> class Coder,
        class Field, class TraceTag
    >
    void decoder(const std::string& stack)
    {
        using boost::python::arg;
        using decoder_type = Coder<Field, TraceTag>;

        std::string field = resolve_field_name<Field>();
        std::string kind = "Decoder";
        std::string name = stack + kind + field;

        auto decoder_class = coder<Coder, Field, TraceTag>(name)
        .def("read_payload", &read_payload<decoder_type>, arg("symbol_data"),
            "Decode the provided encoded symbol.\n\n"
            "\t:param symbol_data: The encoded symbol.\n"
        )
        .def("is_complete", &decoder_type::is_complete,
            "Check whether decoding is complete.\n\n"
            "\t:returns: True if the decoding is complete.\n"
        )
        .def("symbols_uncoded", &decoder_type::symbols_uncoded,
            "Returns the number of uncoded symbols currently known.\n\n"
            "Depending on the algorithm used the true number of uncoded\n"
            "symbols may be higher.\n"
            "The reason for this uncertainty is the some algorithms, for\n"
            "performance reasons, choose to not keep track of the exact\n"
            "status of the decoding matrix.\n"
            "It is however guaranteed that at least this amount of uncoded\n"
            "symbols exist.\n"
            "\t:returns: The number of symbols which have been uncoded.\n"
        )
        .def("copy_from_symbols", &copy_from_symbols<decoder_type>,
            "Return the decoded symbols.\n\n"
            "\t:returns: The decoded symbols.\n"
        );

        (write_payload_method<
            kodo_core::has_write_payload<decoder_type>::value>(decoder_class));

        (is_partially_complete_method<
            kodo_core::has_partial_decoding_tracker<decoder_type>::value>(
                decoder_class));

        (extra_decoder_methods<Coder>(decoder_class));
    }
}
