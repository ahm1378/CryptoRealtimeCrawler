import os

from config.env import env, BASE_DIR

env.read_env(os.path.join(BASE_DIR, ".env"))

bingx_api_key = env("BINGX_API_KEY")
bingx_api_secrets = env("BINGX_API_SECRET")
xt_api_key = env("XT_API_KEY")
xt_api_secret = env("XT_API_SECRET")
lbank_api_key = env("LBANK_API_KEY")
lbank_api_secret = env("LBANK_API_SECRET")
coinex_api_key = env("COINEX_API_KEY")
coinex_api_secrets = env("COINEX_API_SECRET")


cmc_api_key = env("CMC_API_KEY")

API_KEYS = {"bingx":bingx_api_key, "xt":xt_api_key, "lbank":lbank_api_key, "coinex":coinex_api_key, "cmc":cmc_api_key}
API_SECRETS = {"bingx":bingx_api_secrets, "xt":xt_api_secret, "lbank":lbank_api_secret, "coinex":coinex_api_secrets}