#include <boost/python.hpp>
#include <boost/python/register_ptr_to_python.hpp>

#include <fifi/default_field.hpp>

#include <kodo/rlnc/full_vector_codes.hpp>
#include <kodo/systematic_operations.hpp>

#include <sak/storage.hpp>

#include "decoder.hpp"
#include "encoder.hpp"
#include "factory.hpp"

namespace kodo_python
{
    BOOST_PYTHON_MODULE(kodo)
    {
        factory<kodo::full_rlnc_encoder<fifi::binary>>("encoder_factory_binary");
        encoder<kodo::full_rlnc_encoder<fifi::binary>>("encoder_binary");
        factory<kodo::full_rlnc_decoder<fifi::binary>>("decoder_factory_binary");
        decoder<kodo::full_rlnc_decoder<fifi::binary>>("decoder_binary");

        factory<kodo::full_rlnc_encoder<fifi::binary8>>("encoder_factory_binary8");
        encoder<kodo::full_rlnc_encoder<fifi::binary8>>("encoder_binary8");
        factory<kodo::full_rlnc_decoder<fifi::binary8>>("decoder_factory_binary8");
        decoder<kodo::full_rlnc_decoder<fifi::binary8>>("decoder_binary8");
    }
}
