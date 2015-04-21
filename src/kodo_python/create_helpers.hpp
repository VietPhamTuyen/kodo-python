// Copyright Steinwurf ApS 2015.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <string>

#include <boost/python.hpp>
#include <boost/python/args.hpp>

#include <fifi/binary.hpp>
#include <fifi/binary4.hpp>
#include <fifi/binary8.hpp>
#include <fifi/binary16.hpp>

#include <kodo/disable_trace.hpp>
#include <kodo/enable_trace.hpp>

#include "has_is_complete.hpp"

#include "decoder.hpp"
#include "encoder.hpp"
#include "factory.hpp"
#include "resolve_field_name.hpp"

namespace kodo_python
{
    template<template<class, class> class Coder, class Field, class TraceTag,
             bool IsEncoder>
    struct create_coder;

    template<template<class, class> class Coder, class Field, class TraceTag>
    struct create_coder<Coder, Field, TraceTag, true>
    {
        create_coder(const std::string& stack)
        {
            decoder<Coder, Field, TraceTag>(stack);
        }
    };

    template<template<class, class> class Coder, class Field, class TraceTag>
    struct create_coder<Coder, Field, TraceTag, false>
    {
        create_coder(const std::string& stack)
        {
            encoder<Coder, Field, TraceTag>(stack);
        }
    };

    template< template<class, class> class Coder, class Field, class TraceTag>
    void create(const std::string& stack)
    {
        factory<Coder, Field, TraceTag>(stack);
        (create_coder<Coder, Field, TraceTag,
            has_is_complete<Coder<Field, TraceTag>>::value>(stack));
    }

    template<template<class, class> class Coder, class Field>
    void create_trace(const std::string& stack)
    {
        create<Coder, Field, kodo::enable_trace>(stack);
    }

    template<template<class, class> class Coder>
    void create_field(const std::string& stack)
    {
        create_trace<Coder, fifi::binary>(stack);
        create_trace<Coder, fifi::binary4>(stack);
        create_trace<Coder, fifi::binary8>(stack);
        create_trace<Coder, fifi::binary16>(stack);
    }
}
