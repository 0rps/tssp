import itertools
import random
import secrets
import string
import uuid
import hashlib

from app.configurator.constants import GameMode
from app.configurator.documents import GameConfig
from app.ssp.constants import (
    BCAT_RATE,
    RANDOM_BANNER_SIZE_PROB,
    SCALED_BANNER_SIZE_PROB,
    get_ssp_settings,
    SSP_ID,
    THE_SAME_USER_ID
)
from app.ssp.fixtures import IAB_CATEGORIES, TOP_100_WEBSITES, TOP_SSP_LIST


def generate_str_id() -> str:
    allowed_chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(allowed_chars) for _ in range(8))


def generate_ads_txt(cfg: GameConfig, ssp_id: string):
    has_ssp_in_ads_txt = True
    if cfg.ads_txt_enabled:
        ssp_settings = get_ssp_settings()
        has_ssp_in_ads_txt = random.random() < ssp_settings.ADSTXT_GENERATION_PROBABILITY

    used = set()

    data = []
    for i in range(5):
        index = random.randint(1, len(TOP_SSP_LIST)) - 1
        ssp_data = TOP_SSP_LIST[index]
        ssp_name, ssp_domain = ssp_data["name"], ssp_data["domain"]

        if ssp_domain in used:
            continue

        data.append(f'{ssp_name}, {hashlib.md5(ssp_domain.encode()).hexdigest()}, DIRECT')
        used.add(ssp_domain)

    if has_ssp_in_ads_txt:
        data = data[:-1]
        data.append(f"ACA SSP, {ssp_id}, DIRECT")

    return has_ssp_in_ads_txt, "\n".join(data)


def website_generator(cfg: GameConfig) -> list[tuple]:
    num_websites = cfg.impressions_total
    sizes = generate_sizes(num_websites)
    probabilities = generate_probabilities(num_websites)
    ssps = generate_ssps(num_websites, cfg.ads_txt_enabled)
    user_ids = generate_user_ids(num_websites, cfg.frequency_capping_enabled)
    bcat = generate_bcats(num_websites, cfg.blocked_categories_enabled and cfg.mode == GameMode.SCRIPT.value)
    websites_cycle = itertools.cycle(TOP_100_WEBSITES)

    website_ads_txt = {}
    ssp_id = SSP_ID

    for i in range(num_websites):
        w, h = sizes[i].split("x")
        click, conv = probabilities[i]

        if i in website_ads_txt:
            has_ssp_in_ads_txt, ads_txt_data = website_ads_txt[i]
        else:
            has_ssp_in_ads_txt, ads_txt_data = generate_ads_txt(cfg, ssp_id)
            website_ads_txt[i] = (has_ssp_in_ads_txt, ads_txt_data)

        yield next(websites_cycle), w, h, click, conv, ssps[i], user_ids[i], bcat[i], has_ssp_in_ads_txt, ads_txt_data


def generate_sizes(num_websites: int) -> list[str]:
    num_websites_scaled = int(num_websites * SCALED_BANNER_SIZE_PROB)
    num_websites_random = int(num_websites * RANDOM_BANNER_SIZE_PROB)
    num_websites_predefined = num_websites - num_websites_scaled - num_websites_random

    sizes_scaled = ["400x400", "450x300", "300x450"]
    sizes_random = [
        "500x100",
        "600x500",
        "200x600",
        "100x400",
        "500x400",
        "300x400",
        "150x250",
        "200x400",
        "100x300",
        "550x450",
    ]
    sizes_predefined = ["200x200", "300x200", "200x300"]

    sizes = (
        pick_random_values(sizes_scaled, num_websites_scaled)
        + pick_random_values(sizes_random, num_websites_random)
        + pick_random_values(sizes_predefined, num_websites_predefined)
    )
    random.shuffle(sizes)
    return sizes


def generate_probabilities(num_websites: int) -> list[tuple]:
    click_choices = [x / 100 for x in range(10, 50)]
    conv_choices = [x / 100 for x in range(1, 25)] + [x / 100 for x in range(1, 50)]

    click_prob = pick_random_values(click_choices, num_websites)
    conv_prob = pick_random_values(conv_choices, num_websites)
    return list(zip(click_prob, conv_prob))


def generate_ssps(num_websites: int, enabled: bool) -> list[str]:
    # TODO(low): IMPLEMENT
    # if enabled:
    #     return ["implement me, I am broken on purpose"]
    # else:
    return [SSP_ID] * num_websites


def generate_user_ids(num_websites: int, enabled: bool) -> list[str]:
    if not enabled:
        return [THE_SAME_USER_ID] * num_websites

    ssp_settings = get_ssp_settings()
    used_user_ids = [uuid.uuid4().hex]
    result = []

    for _ in range(num_websites):
        if random.random() < ssp_settings.USERID_GENERATION_PROBABILITY:
            user_index = int(random.randint(0, len(used_user_ids)-1))
            user_id = used_user_ids[user_index]
            used_user_ids.append(user_id)
        else:
            user_id = uuid.uuid4().hex
        result.append(user_id)

    return result


def generate_bcats(num_websites: int, enabled: bool) -> list[list[str]]:
    available_categories = [
        "IAB1",
        "IAB5",
        "IAB12",
        "IAB14",
        "IAB19",
    ]

    ssp_settings = get_ssp_settings()
    result = [set() for _ in range(num_websites)]

    if enabled:
        for i in range(num_websites):
            if random.random() < ssp_settings.ADD_ONE_BLOCKED_CATEGORY:
                cat = random.randint(1, len(available_categories)) - 1
                result[i].add(available_categories[cat])

            if random.random() < ssp_settings.ADD_SECOND_BLOCKED_CATEGORY:
                cat = random.randint(1, len(available_categories)) - 1
                result[i].add(available_categories[cat])

    return [list(x) for x in result]


def pick_random_values(values: list, number: int) -> list:
    return [random.choice(values) for _ in range(number)]
