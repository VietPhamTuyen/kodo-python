// Copyright Steinwurf ApS 2015.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#include <kodo/rlnc/sliding_window_encoder.hpp>
#include <kodo/rlnc/sliding_window_decoder.hpp>

#include "create_helpers.hpp"

namespace kodo_python
{
    template<class Type>
    struct extra_encoder_methods<kodo::rlnc::sliding_window_encoder, Type>
    {
        template<class EncoderClass>
        extra_encoder_methods(EncoderClass& encoder_class)
        {
            encoder_class
            .def("feedback_size", &Type::feedback_size,
                "Return the required feedback buffer size in bytes.\n\n"
                "\t:returns: The required feedback buffer size in bytes.\n"
                )
            .def("read_feedback", &read_feedback<Type>,
                "Return the feedback information.\n\n"
                "\t:returns: The feedback information.\n");
        }
    };

    template<class Type>
    struct extra_decoder_methods<kodo::rlnc::sliding_window_decoder, Type>
    {
        template<class DecoderClass>
        extra_decoder_methods(DecoderClass& decoder_class)
        {
            decoder_class
            .def("feedback_size", &Type::feedback_size,
                "Return the required feedback buffer size in bytes.\n\n"
                "\t:returns: The required feedback buffer size in bytes.\n"
                )
            .def("write_feedback", &write_feedback<Type>,
                "Return a buffer containing the feedback.\n\n"
                "\t:returns: A buffer containing the feedback.\n");
        }
    };

    void create_sliding_window_stacks()
    {
        using namespace kodo::rlnc;

        create_encoder<sliding_window_encoder>("SlidingWindow");
        create_decoder<sliding_window_decoder>("SlidingWindow");
    }
}
