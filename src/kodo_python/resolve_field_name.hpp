// Copyright Steinwurf ApS 2011-2013.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <string>
#include <fifi/binary.hpp>
#include <fifi/binary4.hpp>
#include <fifi/binary8.hpp>
#include <fifi/binary16.hpp>
#include <fifi/prime2325.hpp>

namespace kodo_python
{
    template<class Field>
    std::string resolve_field_name()
    {
        assert(0);
    }

    class no_field
    { };

    template<>
    std::string resolve_field_name<no_field>()
    {
        return "";
    }

    template<>
    std::string resolve_field_name<fifi::binary>()
    {
        return "Binary";
    }

    template<>
    std::string resolve_field_name<fifi::binary4>()
    {
        return "Binary4";
    }

    template<>
    std::string resolve_field_name<fifi::binary8>()
    {
        return "Binary8";
    }

    template<>
    std::string resolve_field_name<fifi::binary16>()
    {
        return "Binary16";
    }

    template<>
    std::string resolve_field_name<fifi::prime2325>()
    {
        return "Prime2325";
    }
}
