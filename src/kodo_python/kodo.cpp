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
        void operator()(const std::string& stack, bool trace)
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
        void operator()(const std::string& stack, bool trace)
        {
            factory<Coder, Field, TraceTag>(stack, trace, "encoder");
            encoder<Coder, Field, TraceTag>(stack, trace);
        }
    };

    template<
        template<class, class> class Coder,
        class Field,
        class TraceTag>
    struct create_coder<Coder, Field, TraceTag, false>
    {
        void operator()(const std::string& stack, bool trace)
        {
            factory<Coder, Field, TraceTag>(stack, trace, "decoder");
            decoder<Coder, Field, TraceTag>(stack, trace);
        }
    };

    template<
        template<class, class> class Coder,
        class Field,
        class TraceTag>
    void create(const std::string& stack, bool trace)
    {
        create_coder<
            Coder,
            Field,
            TraceTag,
            is_encoder<Coder<Field, TraceTag>>::value
        > cc;
        cc(stack, trace);
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
        create_trace<kodo::full_rlnc_encoder>("full_rlnc");
        create_trace<kodo::full_rlnc_decoder>("full_rlnc");

        create_trace<kodo::on_the_fly_encoder>("on_the_fly");
        create_trace<kodo::on_the_fly_decoder>("on_the_fly");

        create_trace<kodo::sliding_window_encoder>("sliding_window");
        create_trace<kodo::sliding_window_decoder>("sliding_window");
    }

    BOOST_PYTHON_MODULE(kodo)
    {
        boost::python::docstring_options doc_options;
        doc_options.disable_signatures();
        create_stacks();
    }
}
