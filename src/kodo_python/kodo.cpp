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

#include <sak/storage.hpp>

#include "decoder.hpp"
#include "encoder.hpp"
#include "factory.hpp"

namespace kodo_python
{
    BOOST_PYTHON_MODULE(kodo)
    {
        // Full RLNC
        factory<kodo::full_rlnc_encoder<fifi::binary>>("full_rlnc_encoder_factory_binary");
        encoder<kodo::full_rlnc_encoder<fifi::binary>>("full_rlnc_encoder_binary");
        factory<kodo::full_rlnc_decoder<fifi::binary>>("full_rlnc_decoder_factory_binary");
        decoder<kodo::full_rlnc_decoder<fifi::binary>>("full_rlnc_decoder_binary");

        factory<kodo::full_rlnc_encoder<fifi::binary8>>("full_rlnc_encoder_factory_binary8");
        encoder<kodo::full_rlnc_encoder<fifi::binary8>>("full_rlnc_encoder_binary8");
        factory<kodo::full_rlnc_decoder<fifi::binary8>>("full_rlnc_decoder_factory_binary8");
        decoder<kodo::full_rlnc_decoder<fifi::binary8>>("full_rlnc_decoder_binary8");

        factory<kodo::full_rlnc_encoder<fifi::binary16>>("full_rlnc_encoder_factory_binary16");
        encoder<kodo::full_rlnc_encoder<fifi::binary16>>("full_rlnc_encoder_binary16");
        factory<kodo::full_rlnc_decoder<fifi::binary16>>("full_rlnc_decoder_factory_binary16");
        decoder<kodo::full_rlnc_decoder<fifi::binary16>>("full_rlnc_decoder_binary16");

        // On the fly
        factory<kodo::on_the_fly_encoder<fifi::binary>>("on_the_fly_encoder_factory_binary");
        encoder<kodo::on_the_fly_encoder<fifi::binary>>("on_the_fly_encoder_binary");
        factory<kodo::on_the_fly_decoder<fifi::binary>>("on_the_fly_decoder_factory_binary");
        decoder<kodo::on_the_fly_decoder<fifi::binary>>("on_the_fly_decoder_binary");

        factory<kodo::on_the_fly_encoder<fifi::binary8>>("on_the_fly_encoder_factory_binary8");
        encoder<kodo::on_the_fly_encoder<fifi::binary8>>("on_the_fly_encoder_binary8");
        factory<kodo::on_the_fly_decoder<fifi::binary8>>("on_the_fly_decoder_factory_binary8");
        decoder<kodo::on_the_fly_decoder<fifi::binary8>>("on_the_fly_decoder_binary8");

        factory<kodo::on_the_fly_encoder<fifi::binary16>>("on_the_fly_encoder_factory_binary16");
        encoder<kodo::on_the_fly_encoder<fifi::binary16>>("on_the_fly_encoder_binary16");
        factory<kodo::on_the_fly_decoder<fifi::binary16>>("on_the_fly_decoder_factory_binary16");
        decoder<kodo::on_the_fly_decoder<fifi::binary16>>("on_the_fly_decoder_binary16");
    }
}
