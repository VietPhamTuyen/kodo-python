// Copyright Steinwurf ApS 2011-2012.
// Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
// See accompanying file LICENSE.rst or
// http://www.steinwurf.com/licensing

#pragma once

#include <sak/storage.hpp>
#include <kodo/systematic_operations.hpp>
#include <cstdint>

namespace kodo_python
{
    template<class T>
    class encoder : public T
    {

    public:

        bool is_systematic() const
        {
            return kodo::is_systematic_encoder(*this);
        }

        bool is_systematic_on() const
        {
            return kodo::is_systematic_on(*this);
        }

        void set_systematic_on()
        {
            kodo::set_systematic_on(*this);
        }

        void set_systematic_off()
        {
            kodo::set_systematic_on(*this);
        }

        void set_symbols(const uint8_t* data, uint32_t size)
        {
            auto storage = sak::const_storage(data, size);
            T::set_symbols(storage);
        }
    };
}
