from pypika.terms import Star

from gamelib.data_models import attribute_index_labels
from gamelib.data_models import skill_index_labels
from lib.core.server_context import Context


async def load_data(context: Context) -> None:
    """
    This function loads skill and attribute labels into cache store
    :param context: server context
    """
    # fetch skill labels from postgres
    skill_query = skill_index_labels.select(Star())
    skill_query = skill_query.get_sql()
    skill_data = await context.ds_connection.fetch(skill_query)

    # store processed data in cachestore
    skill_labels = context.cache_store.get_dictionary("skill_labels")
    skill_labels.clear()
    for skill in skill_data:
        skill_index = skill["skill_index"]
        skill_labels[skill_index] = dict(skill)

    # fetch attribute labels from postgres
    attribute_query = attribute_index_labels.select(Star())
    attribute_query = attribute_query.get_sql()
    attribute_data = await context.ds_connection.fetch(attribute_query)

    # store processed data in cachestore
    attribute_labels = context.cache_store.get_dictionary("attribute_labels")
    attribute_labels.clear()
    for attribute in attribute_data:
        attribute_index = attribute["attribute_index"]
        attribute_labels[attribute_index] = dict(attribute)
