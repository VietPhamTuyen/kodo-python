// Copyright Steinwurf ApS 2015.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#include <kodo/nocode/carousel_decoder.hpp>
#include <kodo/nocode/carousel_encoder.hpp>

#include <kodo/pool_factory.hpp>
#include <kodo/rebind_factory.hpp>

#include "create_helpers.hpp"

namespace kodo_python
{
    template<class Field, class TraceTag>
    class carousel_encoder_wrapper : public
        kodo::nocode::carousel_encoder<TraceTag>
    {
    public:
        using factory = kodo::rebind_factory<
            kodo::nocode::carousel_encoder<TraceTag>,
            carousel_encoder_wrapper<Field, TraceTag>>;
    };

    template<class Field, class TraceTag>
    class carousel_decoder_wrapper : public
        kodo::nocode::carousel_decoder<TraceTag>
    {
    public:
        using factory = kodo::rebind_factory<
            kodo::nocode::carousel_encoder<TraceTag>,
            carousel_decoder_wrapper<Field, TraceTag>>;

    public:
        uint32_t symbols_uncoded()
        {
            return kodo::nocode::carousel_decoder<TraceTag>::rank();
        }
    };

    void create_carousel_stacks()
    {
        using namespace kodo;

        create_trace<carousel_decoder_wrapper, no_field>("NoCode");
        create_trace<carousel_encoder_wrapper, no_field>("NoCode");
    }
}
