
import pandas as pd
from tree.node import Node, SymlinkNode

df = pd.read_csv(__file__.replace('example.py', 'inputs.csv'))
df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True)
df = df.set_index('date')

iuk_flows = Node('iuk_flows', curve='aasdasdas',formula='MAX(MIN((0.1 * (nbp_ttf - full_iuk)), 1), 0) * (iuk_technical_capacity - iuk_booked_capacity) + MAX(MIN(0.3 * (nbp_ttf - sunk_iuk), 1), 0) * (iuk_booked_capacity - bacton_booked_capacity) + MAX(MIN(0.5 * (nbp_ttf - sunk_bacton), 1), 0) * bacton_booked_capacity')

nbp_ttf = Node('nbp_ttf', formula='nbp - ttf * fx * 100 / 34.121416', parent=iuk_flows)
nbp = Node('nbp', parent=nbp_ttf, series=df['nbp'])
ttf = Node('ttf', parent=nbp_ttf, series=df['ttf'])
fx = Node('fx', parent=nbp_ttf, series=df['fx'])
iuk_technical_capacity = Node('iuk_technical_capacity', parent=iuk_flows, series=df['iuk_technical_capacity'])
iuk_booked_capacity = Node('iuk_booked_capacity', parent=iuk_flows, series=df['iuk_booked_capacity'])

# Reference: https://pandas.pydata.org/docs/reference/api/pandas.Series.combine.html
bacton_booked_capacity = Node('bacton_booked_capacity', formula='MIN(bacton_booked_entry, iuk_booked_capacity)')
bacton_booked_capacity_iuk_flows = SymlinkNode(bacton_booked_capacity, parent=iuk_flows)
iuk_booked_capacity = Node('iuk_booked_capacity', parent=bacton_booked_capacity, series=df['iuk_booked_capacity'])
iuk_booked_capacity_iuk_flows = SymlinkNode(iuk_booked_capacity, parent=iuk_flows)
bacton_booked_entry = Node('bacton_booked_entry', parent=bacton_booked_capacity, series=df['bacton_booked_entry'])
bacton_booked_entry = SymlinkNode(bacton_booked_capacity, parent=iuk_flows)

full_iuk = Node('full_iuk', formula='sunk_iuk + iuk_be_uk')
full_iuk_iuk_flows = SymlinkNode(full_iuk, parent=iuk_flows)
iuk_be_uk = Node('iuk_be_uk', parent=full_iuk, series=df['iuk_be_uk'])

sunk_iuk = Node('sunk_iuk', formula='sunk_bacton + bacton_entry')
sunk_iuk_full_iuk = SymlinkNode(sunk_iuk, parent=full_iuk)
sunk_iuk_iuk_flows = SymlinkNode(sunk_iuk, parent=iuk_flows)
bacton_entry = Node('bacton_entry', desc='Bacton Entry', parent=sunk_iuk, series=df['bacton_entry'])


sunk_bacton = Node('sunk_bacton', formula='national_grid_commodity_entry + iuk_commodity_be_uk + gts_exit + fluxys_nl_zee_ocuc + fluxys_commodity')
sunk_bacton_sunk_iuk = SymlinkNode(sunk_bacton, parent=sunk_iuk)
sunk_bacton_iuk_flows = SymlinkNode(sunk_bacton, parent=iuk_flows)

national_grid_commodity_entry = Node('national_grid_commodity_entry', parent=sunk_bacton, series=df['national_grid_commodity_entry'])
iuk_commodity_be_uk = Node('iuk_commodity_be_uk', parent=sunk_bacton, series=df['iuk_commodity_be_uk'])
gts_exit = Node('gts_exit', parent=sunk_bacton, series=df['gts_exit'])
fluxys_nl_zee_ocuc = Node('fluxys_nl_zee_ocuc', parent=sunk_bacton, series=df['fluxys_nl_zee_ocuc'])
fluxys_commodity = Node('fluxys_commodity', parent=sunk_bacton, series=df['fluxys_commodity'])

from anytree.iterators import PostOrderIter
for node in PostOrderIter(iuk_flows):
    try:
        node.calculate()
    except TypeError:
        pass

import pdb
pdb.set_trace()


    """
    Gas
        Fundamental
            Price Chart
    Power
        Fundamental
            Price Chart

    version, auto asign
    user, auto asign
    created_at, asuto
    start_effective_date, user input
    end_effective_date (optional default equal to start_effective_date),
    start_point_date, user input
    end_point_date (optional default equal to start_point_date),
    point_value, uer inpuyt
    frequency, user input
    reason, required user input
    curve, required, userinput, weather the curve name stored in database or not, it has to be the same curve

    * flag to the dataset on the front end to informa user the manula changes
    * custom resample rule, Seasonal, winter and summer, Gas year, 1/ October to 30 Sep
    * Gas resample: daily, weekly non iso week, monthly, quarterly, seasonal, gas year, annual

    1. netback config
    2. lng price spread original configs from Liam
    """
