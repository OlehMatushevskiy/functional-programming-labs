"""Public package interface for the functional pipeline."""

from typing import TYPE_CHECKING

if TYPE_CHECKING or "." in (__package__ or ""):
    from .. import core
else:
    import core

Record = core.Record
Stats = core.Stats
pipe = core.pipe
compose = core.compose
juxt = core.juxt
with_total = core.with_total
boost_category = core.boost_category
filter_by_stock = core.filter_by_stock
sort_by_total_desc = core.sort_by_total_desc
take = core.take
reduce_stats = core.reduce_stats
build_pipeline = core.build_pipeline
