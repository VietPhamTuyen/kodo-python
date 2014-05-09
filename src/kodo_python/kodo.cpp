// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#include <boost/python.hpp>
#include <boost/python/register_ptr_to_python.hpp>

#include <fifi/binary.hpp>
#include <fifi/binary4.hpp>
#include <fifi/binary8.hpp>
#include <fifi/binary16.hpp>

#include <kodo/rlnc/full_rlnc_codes.hpp>
#include <kodo/rlnc/on_the_fly_codes.hpp>
#include <kodo/rlnc/sliding_window_encoder.hpp>
#include <kodo/rlnc/sliding_window_decoder.hpp>
#include <kodo/disable_trace.hpp>
#include <kodo/enable_trace.hpp>

#include <sak/storage.hpp>

#include "decoder.hpp"
#include "encoder.hpp"
#include "factory.hpp"

namespace kodo_python
{
    template<template<class, class> class Encoder,template<class, class> class Decoder, class Field, class TraceTag>
    void create(const std::string& kind, const std::string& field, const std::string& trace)
    {
        std::string trace_string = "";
        if (trace != "")
            trace_string = "_" + trace;

        factory<Encoder<Field, TraceTag>>(kind + "_encoder_factory_" + field + trace_string );
        encoder<Encoder, Field, TraceTag>(kind + "_encoder_" + field + trace_string);
        factory<Decoder<Field, TraceTag>>(kind + "_decoder_factory_" + field + trace_string);
        decoder<Decoder, Field, TraceTag>(kind + "_decoder_" + field + trace_string);
    }

    template<template<class, class> class Encoder,template<class, class> class Decoder, class TraceTag>
    void create_field(const std::string& kind, const std::string& trace)
    {
        create<Encoder, Decoder, fifi::binary, TraceTag>(kind, "binary", trace);
        create<Encoder, Decoder, fifi::binary4, TraceTag>(kind, "binary4", trace);
        create<Encoder, Decoder, fifi::binary8, TraceTag>(kind, "binary8", trace);
        create<Encoder, Decoder, fifi::binary16, TraceTag>(kind, "binary16", trace);
    }

    template<template<class, class> class Encoder,template<class, class> class Decoder>
    void create_trace(const std::string& kind)
    {
        create_field<Encoder, Decoder, kodo::disable_trace>(kind, "");
        create_field<Encoder, Decoder, kodo::enable_trace>(kind, "trace");
    }

    void create_coders()
    {
        create_trace<kodo::full_rlnc_encoder, kodo::full_rlnc_decoder>("full_rlnc");
        create_trace<kodo::on_the_fly_encoder, kodo::on_the_fly_decoder>("on_the_fly");
        create_trace<kodo::sliding_window_encoder, kodo::sliding_window_decoder>("sliding_window");
    }

    BOOST_PYTHON_MODULE(kodo)
    {
        create_coders();
    }
}
