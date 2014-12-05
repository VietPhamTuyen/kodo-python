// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#include <boost/python.hpp>
#include <boost/python/docstring_options.hpp>

#include <fifi/binary.hpp>
#include <fifi/binary4.hpp>
#include <fifi/binary8.hpp>
#include <fifi/binary16.hpp>

#include <kodo/rlnc/full_vector_codes.hpp>
#include <kodo/rlnc/on_the_fly_codes.hpp>
#include <kodo/rlnc/sliding_window_decoder.hpp>
#include <kodo/rlnc/sliding_window_encoder.hpp>
#include <kodo/rlnc/sparse_full_vector_encoder.hpp>
#include <kodo/disable_trace.hpp>
#include <kodo/enable_trace.hpp>

#include "decoder.hpp"
#include "encoder.hpp"
#include "factory.hpp"
#include "is_encoder.hpp"

#include <string>

namespace kodo_python
{
    template<
        template<class, class> class Coder,
        class Field,
        class TraceTag,
        bool IsEncoder>
    struct create_coder
    {
        create_coder(const std::string& stack, bool trace)
        {
            (void) stack;
            (void) trace;
            assert(0);
        }
    };

    template<
        template<class, class> class Coder,
        class Field,
        class TraceTag>
    struct create_coder<Coder, Field, TraceTag, true>
    {
        create_coder(const std::string& stack, bool trace)
        {
            factory<Coder, Field, TraceTag>(stack, trace, "Encoder");
            encoder<Coder, Field, TraceTag>(stack, trace);
        }
    };

    template<
        template<class, class> class Coder,
        class Field,
        class TraceTag>
    struct create_coder<Coder, Field, TraceTag, false>
    {
        create_coder(const std::string& stack, bool trace)
        {
            factory<Coder, Field, TraceTag>(stack, trace, "Decoder");
            decoder<Coder, Field, TraceTag>(stack, trace);
        }
    };

    template<
        template<class, class> class Coder,
        class Field,
        class TraceTag>
    void create(const std::string& stack, bool trace)
    {
        create_coder<Coder, Field, TraceTag,
            is_encoder<Coder<Field, TraceTag>>::value>coder(stack, trace);
    }

    template<
        template<class, class> class Coder,
        class TraceTag>
    void create_field(const std::string& stack, bool trace)
    {
        create<Coder, fifi::binary, TraceTag>(stack, trace);
        create<Coder, fifi::binary4, TraceTag>(stack, trace);
        create<Coder, fifi::binary8, TraceTag>(stack, trace);
        create<Coder, fifi::binary16, TraceTag>(stack, trace);
    }

    template<
        template<class, class> class Coder>
    void create_trace(const std::string& stack)
    {
        create_field<Coder, kodo::disable_trace>(stack, false);
        create_field<Coder, kodo::enable_trace>(stack, true);
    }

    void create_stacks()
    {
        create_trace<kodo::rlnc::full_vector_encoder>("FullVector");
        create_trace<kodo::rlnc::full_vector_decoder>("FullVector");

        create_trace<kodo::rlnc::sparse_full_vector_encoder>(
            "SparseFullVector");

        create_trace<kodo::rlnc::on_the_fly_encoder>("OnTheFly");
        create_trace<kodo::rlnc::on_the_fly_decoder>("OnTheFly");

        create_trace<kodo::rlnc::sliding_window_encoder>("SlidingWindow");
        create_trace<kodo::rlnc::sliding_window_decoder>("SlidingWindow");
    }

    BOOST_PYTHON_MODULE(kodo)
    {
        boost::python::docstring_options doc_options;
        doc_options.disable_signatures();
        create_stacks();
    }
}
