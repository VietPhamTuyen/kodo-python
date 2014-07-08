// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#include <boost/python.hpp>
#include <boost/python/register_ptr_to_python.hpp>
#include <boost/python/docstring_options.hpp>

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
    template<
        template<class, class> class Encoder,
        template<class, class> class Decoder,
        class Field,
        class TraceTag>
    void create(const std::string& stack, const std::string& field, bool trace)
    {
        factory<Encoder<Field, TraceTag>>(stack, field, trace, "encoder");
        encoder<Encoder, Field, TraceTag>(stack, field, trace);
        factory<Decoder<Field, TraceTag>>(stack, field, trace, "decoder");
        decoder<Decoder, Field, TraceTag>(stack, field, trace);
    }

    template<
        template<class, class> class Encoder,
        template<class, class> class Decoder,
        class TraceTag>
    void create_field(const std::string& stack, bool trace)
    {
        create<Encoder, Decoder, fifi::binary, TraceTag>(
            stack, "binary", trace);
        create<Encoder, Decoder, fifi::binary4, TraceTag>(
            stack, "binary4", trace);
        create<Encoder, Decoder, fifi::binary8, TraceTag>(
            stack, "binary8", trace);
        create<Encoder, Decoder, fifi::binary16, TraceTag>(
            stack, "binary16", trace);
    }

    template<
        template<class, class> class Encoder,
        template<class, class> class Decoder>
    void create_trace(const std::string& stack)
    {
        create_field<Encoder, Decoder, kodo::disable_trace>(stack, false);
        create_field<Encoder, Decoder, kodo::enable_trace>(stack, true);
    }

    void create_stacks()
    {
        create_trace<
            kodo::full_rlnc_encoder, kodo::full_rlnc_decoder>("full_rlnc");
        create_trace<
            kodo::on_the_fly_encoder, kodo::on_the_fly_decoder>("on_the_fly");
        create_trace<
            kodo::sliding_window_encoder, kodo::sliding_window_decoder>(
            "sliding_window");
    }

    BOOST_PYTHON_MODULE(kodo)
    {
        boost::python::docstring_options doc_options;
        doc_options.disable_signatures();
        create_stacks();
    }
}
