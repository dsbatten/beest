# BEEST 2 methodology

BEEST 2 turns live network hashrate into Bitcoin's total, mitigated and net emissions, every day. This page sets out every input, every calculation and every assumption behind it, with the source for each. The live chart starts on 1 December 2025, the date of the Cambridge energy-mix survey behind its carbon intensity. The long chart runs the same chain back to September 2019. Last updated 15 November 2026.

## The chain

Three steps, run once a day:

Electricity (TWh a year) = network hashrate (TH/s) × network efficiency (J/TH) × 8,760 hours. The efficiency figure already includes the facility overhead.

Total emissions (MtCO2e a year) = electricity × carbon intensity (gCO2e/kWh).

Net emissions = total emissions less emission mitigation (flare), counted at 91.1% flare destruction efficiency and GWP20.

## Inputs

| Input | Value | Kind | Source and date | Refreshed |
| --- | --- | --- | --- | --- |
| Network hashrate | Live, 7-day moving average of the daily difficulty-implied figure | Live | [mempool.space mining API](https://mempool.space/api/v1/mining/hashrate/3m), no key needed, with blockchain.com and the Coin Metrics community API as fallbacks; `hashrate_feed.py` | Daily |
| Network efficiency at the facility | 19.3 J/TH at November 2026 (range 17.3-22.2); 22.3 J/TH at 1 December 2025; a straight line between | Static, derived | Network efficiency section below; the December 2025 point uses the same formula with the active grid fleet at 20.5 J/TH, the mean of Luxor's 20.2 and Cambridge's 20.8 before the 2026 idling | Luxor's monthly fleet figure, Cambridge survey rounds |
| Carbon intensity of mining electricity | 252 gCO2e/kWh | Static, sourced | Cambridge Digital Mining Industry Report, 2nd edition, preliminary slides, data as of 12 August 2026; implied from the energy mix survey participants reported for December 2025 | Each Cambridge survey round, roughly annual |
| Emission mitigation (flare) | 4.69 MtCO2e a year on the surveyed sample (n = 44) | Static, sourced | Same slides; 91.1% flare efficiency, GWP20 at the IPCC AR6 value | Each Cambridge survey round |
| Bitcoin price (context only) | Live, daily close in USD | Live | Coin Metrics community API, PriceUSD; blockchain.com as fallback. Nothing in the emissions chain depends on it | Daily |

## Hashrate

The daily hashrate figure is implied from difficulty and block times, so single days swing by 10%+ on block luck alone (811-984 EH/s in the week to 15 November 2026). The tracker uses the trailing 7-day average, which is also the window Cambridge uses for its own hashrate figures, so the check values line up. On 15 November 2026 the 7-day average was 894 EH/s against a 30-day average of 1,009. The gap is the fall in hashrate since late October. mempool.space, blockchain.com and Coin Metrics agreed on the 7-day figure to within a fraction of 1% on that date.

## Network efficiency (J/TH)

The Bitcoin network's average efficiency in November 2026 works out at 19.3 joules per terahash measured at the facility meter, somewhere between 17.3 and 22.2 depending on the assumptions. I built the figure from 2026 fleet data from Luxor and Cambridge, an allowance for the older machines running part-time on off-grid power, and a 5% facility overhead. Nobody publishes a measurement of the whole network on current data, so I assembled one from the parts that are measured, and this section says where each number comes from.

### Why a proxy

Each published model covers a slice of the fleet or a past period, and the slices do not add up to the whole. Cambridge's April 2025 industry report gives a hashrate-weighted average for 45 surveyed firms, 48% of the network, as of June 2024. It misses unsurveyed operators and everything that has happened since mid-2024. Cambridge's CBECI index updates daily. But it decides which hardware is running by assuming a flat $0.05/kWh electricity price, it adds a 1.10 facility overhead borrowed from data centres, and its hardware weights are calibrated against the same 2024 survey. Luxor's fleet model, from Hashrate Index, counts every ASIC ever shipped and not yet failed, and infers the active share from difficulty at an average power cost of $0.048/kWh. It is current and monthly. Its blind spot is the machines that run on power far cheaper than that. The listed operators disclose their own fleet efficiency every quarter in SEC filings and monthly updates. That is precise for the large grid-connected industrial miners and silent on private operators, off-grid sites and older machines (together, most of the network).

In short: I use the current-data models for the part of the network they measure well, the grid-connected industrial fleet. I add the part they do not: the older machines on off-grid or stranded power that run only when their power is available or cheap enough. Then I apply a facility overhead that reflects how mining facilities are actually cooled. Each input is marked as sourced, derived or assumed, so the estimate can be redone when any of them changes.

The weighting throughout is by delivered hashrate, the terahashes actually contributing to the observed network total, rather than by machines installed. A machine that runs 30% of the time contributes 30% of its hashrate to the average and 30% of its energy to the total. Uptime therefore enters the calculation by shrinking a segment's share of hashrate; it does not change how many joules a machine draws per terahash while it is running.

### What is left out

Cambridge's 28.2 J/TH is a hashrate-weighted average of 45 survey respondents as of June 2024, published in April 2025 ([Cambridge Digital Mining Industry Report](https://www.jbs.cam.ac.uk/wp-content/uploads/2025/04/2025-04-cambridge-digital-mining-industry-report.pdf)). Cambridge measured a 24% efficiency improvement in the year to June 2024, and the pace has continued. A figure two and a half years old therefore overstates current energy per terahash by a third or more. It appears below only as a historical reference point.

[Spark's energy comparison tool](https://www.spark.money/tools/bitcoin-energy-consumption-comparison) republishes the CBECI central estimate alongside the Cambridge survey's energy mix and adds no measurement of its own. Leaving it out removes a second copy of the 2024 data rather than an independent source.

CoinShares' Q1 and Q2 2026 mining reports ([Q2 2026](https://coinshares.com/insights/research-data/bitcoin-mining-report-q2-2026/)) do not publish a network or fleet-average efficiency. They quote individual operators (Bitdeer 15.8 J/TH, CleanSpark ~16 J/TH) and estimate that 15-20% of the active fleet, the machines older than the S19 XP, was unprofitable at $0.06/kWh in early 2026. A network figure of 17.5 J/TH sometimes attributed to CoinShares could not be traced to any CoinShares publication; 17.5 J/TH happens to be the rated efficiency of a stock Antminer S21. The listed-operator figures used here come straight from the operators' own disclosures.

The CBECI index itself serves only as a cross-check, through its implied efficiency (index power divided by network hashrate). Its hardware selection runs on a fixed $0.05/kWh price and release-date weighting, and its 1.10 overhead is a data-centre convention ([CBECI methodology](https://ccaf.io/cbnsi/cbeci/methodology)).

### Method

The network average is a hashrate-weighted average of two segments, multiplied by a facility overhead. Five steps:

1. Take the 7-day moving average of network hashrate from the difficulty record. This is the denominator every share is measured against.
2. Start from Luxor's fleet model and remove the idle capacity, which Luxor's economics place in the least efficient tier, to get the efficiency of the fleet actually running on grid economics. Check it against the listed operators' disclosed figures.
3. Estimate the share of delivered hashrate coming from older machines on off-grid, stranded or near-free power, where grid economics would mark them idle but cheap power keeps them running. Build it from installed capacity multiplied by an uptime factor set for each kind of power source, and give the segment an efficiency drawn from the machine generations that populate it.
4. Multiply the machine-level average by a power usage effectiveness factor that reflects the current cooling mix.
5. Recompute with each input at its low and high bound to get the range and the sensitivity.

Written out: network J/TH = PUE × [(1 − s) × E_grid + s × E_off], where s is the off-grid and older-machine share of delivered hashrate, E_grid the active grid fleet efficiency and E_off the older-machine efficiency, all measured at the machine's wall plug.

### Inputs to the efficiency figure

| Input | Central value | Low | High | Type | Source |
| --- | --- | --- | --- | --- | --- |
| Network hashrate, 7-day moving average | Live, from the tracker | | | Sourced | Difficulty record via the mempool.space API; the worked figures below use 894 EH/s at 15 November 2026 |
| Luxor total net ASIC capacity | 1,153 EH | | | Sourced | [Luxor Hashrate Lookback, July 2026](https://hashrateindex.com/blog/luxor-hashrate-lookback-series-july-2026/) (published 7 August 2026) |
| Luxor active fleet | 926 EH | | | Sourced | Same; implied by July difficulty |
| Luxor idle capacity | 227 EH | | | Sourced | Same: uneconomic, curtailed, in transit or under maintenance |
| Luxor fleet average efficiency | 20.2 J/TH | | | Sourced | Same |
| Cambridge survey fleet efficiency, December 2025 | 20.8 J/TH | | | Sourced | Cambridge 2nd edition preliminary slides, August 2026; survey respondents, before the 2026 idling |
| Cambridge estimated fleet efficiency, August 2026 | 16.3 J/TH | | | Sourced | Same; Cambridge's estimate, assuming the machines idled since December were the least efficient |
| Efficiency of the idle tier | 30 J/TH | 27 | 33 | Assumed | Midpoint of Luxor's 25-38 J/TH band, which was below breakeven in July and August 2026 |
| Active grid fleet efficiency, E_grid | 17.3 J/TH | 16.3 | 18.5 | Derived | Midpoint of the Luxor-derived 18.2 and Cambridge's 16.3; see the grid-connected fleet below |
| Listed-operator fleet efficiency (cross-check) | 16.1-16.4 J/TH | | | Sourced | CleanSpark 16.07 J/TH at 31 March 2026 ([April 2026 update](https://www.stocktitan.net/news/CLSK/clean-spark-releases-march-2026-operational-fmweqc4h138k.html)); Bitdeer 16.4 J/TH at 31 March 2026 ([Q1 2026 call](https://www.aol.com/articles/bitdeer-btdr-q1-2026-earnings-182451000.html)) |
| Off-grid share of surveyed power | 8.1% (1.23 GW) | | | Sourced | Cambridge 2025, surveyed firms only |
| Off-grid and older-machine share of delivered hashrate, s | 10% | 6% | 15% | Derived and assumed | See off-grid and older machines below |
| Older-machine efficiency, E_off | 28 J/TH | 25 | 32 | Assumed | S19 XP 21.5, S19j Pro and S19 Pro 29.5, M30S++ 31 J/TH; manufacturer ratings |
| Weighted uptime of off-grid and older machines | 66% | | | Derived | See off-grid and older machines below |
| Facility overhead, PUE | 1.05 | 1.03 | 1.08 | Assumed | See facility overhead below; CBECI uses 1.10 with bounds 1.01-1.20 |

J/TH values are at the machine's wall plug, as manufacturers rate them, until the PUE step.

### The grid-connected fleet

Luxor's fleet model counted 1,153 EH of ASIC capacity manufactured and not yet failed in August 2026, of which 926 EH was active and 227 EH idle, and put the fleet average at 20.2 J/TH. The idle capacity sits in the least efficient machines: Luxor's 25-38 J/TH tier earned $45/MWh against a network-average power cost of $48/MWh, so on grid economics it does not run.

The idle capacity is a mixture: machines that cannot cover their power cost, machines curtailed for grid events, machines in transit and machines under maintenance. Treating all of it as the oldest tier slightly flatters the active fleet, since some newer machines are always in transit or down for repair. The effect on the final figure is a fraction of a joule and sits inside the range.

Taking the idle tier out of the fleet average leaves the efficiency of the fleet that is running on grid economics. If the idle machines average 27 J/TH the active fleet comes out at 18.5 J/TH; at 30 J/TH it is 17.8; at 33 J/TH it is 17.1. The Luxor-derived figure is 18.2 J/TH, between the first two.

Cambridge's second-edition survey gives a second reading of the same fleet. Its respondents averaged 20.8 J/TH in December 2025, within 3% of Luxor's 20.2 for the fleet before the 2026 idling, so two independent sources agree on the starting point. For August 2026 Cambridge estimates 16.3 J/TH, reached by assuming that every machine switched off since December was from the least efficient tier. Its base is also weighted toward the large operators who answer surveys, whose fleets are newer than the grid-connected population as a whole. The two methods agree on the fleet before idling and differ only in how much efficiency the idling removed: Luxor's tier economics put the idle machines at 27-33 J/TH, Cambridge's assumption puts them higher. Neither assumption is measured, so the central case takes the midpoint, 17.3 J/TH, with Cambridge's 16.3 as the low bound and the Luxor derivation's 18.5 as the high bound.

The central figure sits above the listed operators' own disclosures (CleanSpark 16.07 and Bitdeer 16.4 J/TH at 31 March 2026). That is the expected relationship: listed miners run the newest fleets, and the grid-connected population includes private operators a generation behind them.

One ambiguity remains in Luxor's wording. If the 20.2 J/TH already describes the active fleet rather than the total, E_grid is 20.2 and the network result rises by 2.7 J/TH. That reading is carried in the range, and a confirmation from Luxor would settle it.

### Off-grid and older machines

This segment is the hashrate that Luxor's grid economics would mark idle but that runs anyway, because its power is near free. It covers flare gas at the wellhead, seasonal or stranded hydro, wind and solar with no grid buyer, and older machines on grid connections that switch on only in cheap hours. Older generations fill it, for two reasons. A machine that is uneconomic at $0.048/kWh is where cheap power creates the most value. And a site with intermittent power cannot justify the capital cost of a new machine it will run a third of the time.

The generations in this segment are rated at 21.5 J/TH (S19 XP), 29.5 J/TH (S19 Pro and S19j Pro) and 31 J/TH (M30S++). A central 28 J/TH with a range of 25-32 covers a mix weighted toward the S19 family, which was the volume machine of 2020-2022 and is now the main stock on the second-hand market.

On the size of the segment: Cambridge's 2025 survey found off-grid power at 8.1% of respondents' total power use, 1.23 GW. At 28 J/TH that is 44 EH/s, 5% of today's hashrate. The survey covers formal operators who answer questionnaires. It does not reach the informal and small-scale off-grid fleet (wellhead operators outside the listed companies, hydro sites in Central Asia, Africa and Latin America, container-scale solar), or the older grid-connected machines run opportunistically in cheap hours. Doubling the surveyed figure for the unsurveyed population and adding the opportunistic grid-connected machines gives the central 10% of delivered hashrate. The low bound is 6% (surveyed off-grid plus a small informal allowance) and the high bound 15%.

Delivered hashrate is installed capacity multiplied by the fraction of time the machines run, and that fraction depends on what powers them. For flare and stranded gas, 40% of the segment's installed capacity, uptime is set at 88%. The gas supply is continuous and generator fleets typically achieve 90-95% availability; the lower figure allows for well shut-ins and moves between pads. For seasonal or stranded hydro, 25% of the segment, uptime is set at 65%. Run-of-river sites deliver through the wet season and part of the dry: Sichuan's wet season runs May to October, and miners there historically ran near-full for 6 months and at a fraction for the rest. For older grid-connected machines that switch on only in cheap hours, 20% of the segment, uptime is set at 50%. These run when the hourly price is below their breakeven, $42/MWh for the 25-38 J/TH tier at current hashprice. In a price-volatile market such as ERCOT, half of all hours clear below that in a normal year, fewer in summer when miners also curtail to avoid transmission charges. For wind and solar without storage, 15% of the segment, uptime is set at 30%. The source's capacity factor is the upper limit: US utility-scale solar averages 24% and onshore wind 34% ([EIA Electric Power Monthly, Table 6.07.B](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_6_07_b)). A miner behind the meter at a curtailed plant can only beat the plant's own capacity factor by drawing grid power the rest of the time, and that moves it to the grid segment.

Weighted across that mix (0.40 × 0.88 + 0.25 × 0.65 + 0.20 × 0.50 + 0.15 × 0.30), the segment's uptime is 66%. The gas, hydro and grid figures are assumptions grounded in the operating pattern of each source; the wind and solar figure follows from measured capacity factors.

The mix itself is an assumption, since no survey breaks the off-grid fleet down by power source, and its effect is bounded. Were the segment all flare gas, uptime would be 88% and the installed base needed to deliver 10% of hashrate a quarter smaller. Were it all wind and solar, uptime would be 30% and the installed base three times larger. Once the delivered share is fixed, the network average does not move with the mix. The mix matters for converting an installed-capacity figure such as Cambridge's 1.23 GW into delivered hashrate, and for judging how much idle legacy capacity sits behind the share that shows up in difficulty.

### Facility overhead

Power usage effectiveness (PUE) is total facility power divided by the power drawn by the machines themselves; the difference is cooling, transformers, lighting and controls. CBECI applies 1.10 as its best guess for every mining facility, with 1.01 and 1.20 as bounds ([CBECI methodology](https://ccaf.io/cbnsi/cbeci/methodology)). That figure is inherited from enterprise data-centre practice, where servers run in conditioned rooms with redundant cooling and power, and it was set when air-cooled containers in warm climates were the norm.

The central value here is 1.05, with 1.03-1.08 as the range. Mining facilities are built differently from data centres. Most of the fleet runs in open-air or evaporatively cooled halls and containers, with no humidity control, no redundant power path and no uninterruptible supply. The overhead that pushes data-centre PUE toward 1.2 and beyond is therefore largely absent. The cooling mix has also moved to liquid. The current efficiency frontier is hydro-cooled (Antminer S23 Hyd ~9.5 J/TH; Bitdeer A4 Ultrahydro 9.45 J/TH), and the listed operators' fleet renewal through 2025 and 2026 has been toward hydro and immersion machines. Liquid cooling takes the fan load out of the overhead and typically runs at 1.02-1.05, while air-cooled halls in temperate climates run near 1.05-1.10. Bitdeer reports ~1.1 at its Tydal site in Norway, where lake water provides the cooling ([Q1 2026 call](https://www.aol.com/articles/bitdeer-btdr-q1-2026-earnings-182451000.html)). A fleet moving from air to liquid moves its average overhead down from the 1.10 convention.

Manufacturers rate J/TH at the wall plug, after the machine's own power-supply losses, so those losses are already in the machine figure and are not counted again in the overhead.

The 1.05 is an assumption rather than a measurement. No operator survey reports PUE across the fleet, and the only disclosed site figure sits at the upper end of the range. The range of 1.03-1.08 brackets a fleet that is mostly liquid-cooled at the low end and mostly air-cooled in warm climates at the high end. The overhead applies to the whole fleet, including the off-grid segment, where containerised air cooling is common and the overhead is if anything higher; the high bound covers that.

### Result

At the machine, the average is 0.90 × 17.3 + 0.10 × 28 = 18.4 J/TH. With the 1.05 overhead it is 19.3 J/TH at the facility meter. This figure is the output of the method. Power and energy follow from it by multiplication with live hashrate, which the tracker does continuously. For example: at the 7-day average of 894 EH/s on 15 November 2026 it is 17.2 GW of continuous draw, 151 TWh a year.

With every input at its low bound the result is 17.3 J/TH; with every input at its high bound, 22.2 J/TH. The reading in which Luxor's 20.2 J/TH already describes the active fleet gives 22.0 J/TH, inside that range. Moving one input at a time, with all others at the central value:

| Input moved | At low bound | At high bound | Swing |
| --- | --- | --- | --- |
| Active grid fleet, E_grid (16.3-18.5 J/TH) | 18.3 | 20.4 | 2.1 |
| Off-grid and older-machine share, s (6-15%) | 18.8 | 19.9 | 1.0 |
| Facility overhead, PUE (1.03-1.08) | 18.9 | 19.8 | 0.9 |
| Older-machine efficiency, E_off (25-32 J/TH) | 19.0 | 19.7 | 0.7 |

The grid-fleet input carries the widest swing, 2.1 J/TH, and the whole of that width is the disagreement between Luxor and Cambridge over how much efficiency the 2026 idling removed. The off-grid share and the overhead each move the result by ~1 J/TH.

Against the figures it replaces: the Cambridge survey's 28.2 J/TH from June 2024 data is 53% higher than this estimate's 18.4 J/TH at the machine. The gap is two and a half years of fleet renewal. Cambridge's own August 2026 estimate of 16.3 J/TH with its 1.10 overhead gives 17.9 J/TH at the facility, 7% below this estimate. The difference is the off-grid and older-machine segment that the survey base does not reach. The CBECI index's implied figure for September 2026, 19.0 J/TH including its 1.10 overhead, is within 2% of this estimate. The two arrive there by different routes: CBECI with a higher overhead on a more efficient fleet, this method with a lower overhead on a fleet that includes older machines.

### The efficiency figure over time

The chart does not hold one efficiency figure across its whole window, because the fleet improved through 2026 as the least efficient machines switched off. On 1 December 2025 the active grid fleet is put at 20.5 J/TH, the mean of Luxor's 20.2 and Cambridge's 20.8 for the fleet before the idling. With the same off-grid allowance and overhead that gives 22.3 J/TH at the facility. On 15 November 2026 the figure is the 19.3 J/TH derived above. Between the two dates the series runs a straight line; after the second date it holds flat until the method is next refreshed. Against Cambridge's own December 2025 point (190 TWh, 48.0 MtCO2e) the series gives 213 TWh and 53.7 Mt, 12% higher. ~7 points of that is the off-grid and older-machine segment the method adds by design. The rest is that the 7-day hashrate on 1 December 2025 (1,089 EH/s) sat above Cambridge's December average.

## Carbon intensity

The 252 gCO2e/kWh is Cambridge's implied figure for December 2025, down 13% from 288 in June 2024. It follows from the mix survey participants reported: low-carbon 59.4% (hydro 36.9, nuclear 9.0, wind 8.6, solar 4.4, other renewables 0.5) and fossil 40.6% (natural gas 32.1, coal 8.0, oil 0.5). Hydro is now the largest single source; natural gas was in June 2024, at 38.2%. Low-carbon here means renewables plus nuclear; the renewable share alone is 50.4%.

Cambridge itself carried the December 2025 intensity unchanged into its August 2026 estimate (35.0 MtCO2e on 138.8 TWh), so holding it static between survey rounds follows the source's own practice.

The figure describes the surveyed industrial fleet. The tracker applies it to the whole network, including the off-grid and older-machine segment, whose mix differs. Flare gas is a fossil fuel at the point of combustion; stranded hydro, wind and solar are not. The segment is a tenth of hashrate and its two halves pull in opposite directions, so no adjustment is made.

## Emission mitigation (flare)

Mining on flare gas is negative-emission mining: the generator burns gas that the operator would otherwise flare, and a generator destroys methane more completely than a flare does. Counted over 20 years, the methane kept out of the air outweighs the carbon dioxide from burning it, so the segment's net contribution is a deduction from network emissions.

Two conventions set the size of the deduction. Flare destruction efficiency is 91.1%, the field-measured average from aircraft surveys of operating flares across the Permian, Eagle Ford and Bakken ([Plant et al. 2022, Science](https://www.science.org/doi/10.1126/science.abq0385)). The 98% often assumed is the EPA's figure from 1980s test-stand work and has not been confirmed in the field, and since US basins are relatively well regulated, 91.1% is conservative as a global figure. The warming potential of methane is GWP20 at the IPCC AR6 value, 82.5 for fossil methane ([Forster et al. 2021, AR6 WG1 Chapter 7, Table 7.15](https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/)). I use AR6 rather than the higher central value in my own recalibration because it is the figure a reader can check against the IPCC without further argument. I use the 20-year horizon because methane does most of its warming within two decades of release, which is the window the climate targets fall in. A 100-year average understates what the methane actually does.

The figure in use is Cambridge's 4.69 MtCO2e a year for the 44 survey respondents mining on flare gas, at 91.1% and GWP20. Cambridge's slide does not state which GWP20 value it applied. The ratio of its GWP20 and GWP100 figures (2.95) is consistent with AR6 values, so the figure is carried as published until Cambridge confirms. If their value turns out higher, the figure is scaled by 82.5 over it. Until the open questions below are answered, the tracker deducts only the surveyed 4.69 Mt, which understates mitigation. Once mitigation is computed from gas volumes rather than taken from a survey, the 91.1% and the AR6 GWP20 enter the arithmetic directly. A second mitigation line, emission mitigation (landfills), is reserved in the chart and the series for when a sourced figure exists.

## History before December 2025

The live chart starts on 1 December 2025 because that is the date of the Cambridge survey behind its carbon intensity. The long chart runs the same chain back to 1 September 2019, where [BEEST 1](https://docs.google.com/spreadsheets/d/1YSsIk2ghvPDHTcfUKkKo9cqg0XI_gSGh/edit?gid=270821339#gid=270821339), the spreadsheet model this tracker replaces, began, and from 1 December 2025 its rows are the live chart's rows, so the two join without a step. Before that date each input is built as follows. Every row carries a note saying which basis it rests on, shown in the hover.

**Hashrate.** The 7-day average of the daily mempool.space figure, the same series the live chart uses, back to 2019.

**Network efficiency.** The same structure as the live method: whole-network J/TH = 1.05 × [0.9 × grid fleet + 0.1 × older machines], with the older segment at 1.366 times the grid fleet. That reduces to 1.088 times the grid-fleet figure. Only the source of the grid-fleet figure changes over the history. From June 2022 to December 2025 it is Cambridge's survey points: 40.7 J/TH (June 2022), 36.9 (June 2023), 28.2 (June 2024) and 20.5 (December 2025, the mean of Cambridge's 20.8 and Luxor's 20.2). Between points the series is interpolated on a log scale, because fleet efficiency improves by a roughly constant proportion a year rather than a constant number of joules. Whole-network figures at those points: 44.3, 40.2, 30.7 and 22.3 J/TH. Before June 2022 no survey exists. Cambridge's CBECI hardware model, the only published series, was unreliable before its August 2023 update: its machine selection followed the bitcoin price, producing swings such as a dip through 2020 that reflect the model rather than the fleet. So it supplies one number only: the September 2019 level, 86.0 J/TH, scaled by the factor that brings CBECI's June 2022 figure onto the survey (40.7 ÷ 48.4 = 0.841), which gives 72.3 J/TH. The grid-fleet figure then runs on a straight log-scale line from 72.3 in September 2019 to 40.7 in June 2022. The improvement that line implies, 19% a year, matches the 18% a year the survey points show for 2022-2025. Blockware's April 2023 estimate of 32.2 J/TH is a check rather than an input. It sits 13% below Cambridge's June 2023 survey, which is the direction expected from a shipment-and-economics model against a survey weighted to large operators, and inside the range the structure puts around that date.

**Carbon intensity.** BEEST 1's Scope 2 series, the gross intensity of mining electricity in gCO2e/kWh, at its dated points from September 2019 (597) to 26 October 2024 (261), with straight lines between points. From 26 October 2024 a straight line runs to Cambridge's 252 at 1 December 2025. CBECI's own intensity series is not used at any date: it was unreliable until the April 2025 industry report. BEEST 1's own forward projection for November 2026, 249 gCO2e/kWh and 58.8% clean, lands within 1% of Cambridge's 252 and 59.4%, which is the strongest corroboration either figure has.

**Emission mitigation (flare).** BEEST 1's net intensity series differs from its Scope 2 series by the methane mitigation per kWh. That difference, times the electricity, is the mitigation in tonnes. It is scaled by 82.5 ÷ 84 to restate BEEST 1's GWP20 of 84 at the AR6 value, which lowers the deduction by 2% and raises net emissions by the same amount. From 26 October 2024 the figure runs on a straight line in tonnes to Cambridge's 4.69 Mt at 1 December 2025. Before 2021 the two BEEST 1 series are identical, so mitigation is zero.

**Clean energy share.** BEEST 1's total sustainable (clean) energy share at its dated points, then a straight line to Cambridge's 59.4% at 1 December 2025, held after. It is carried in the series for a later chart and does not enter the emissions arithmetic, which uses the intensity directly.

**Price.** Coin Metrics' daily PriceUSD from 2019, context only.

Sources for this section: [BEEST 1 spreadsheet](https://docs.google.com/spreadsheets/d/1YSsIk2ghvPDHTcfUKkKo9cqg0XI_gSGh/edit?gid=270821339#gid=270821339) (Daniel Batten, series extracted 15 November 2026, stored at `sources/beest1-emission-intensity.csv`); CBECI hardware-efficiency series (Cambridge Centre for Alternative Finance, read 15 November 2026 from the CBECI chart data, stored at `sources/cbeci-hardware-efficiency-monthly.csv`); Cambridge survey points as in the references; [Blockware Intelligence](https://www.blockwareintelligence.com/) April 2023 network efficiency 32.2 J/TH as recorded in BEEST 1.

## Direction of drift

Each static input is a snapshot of a quantity moving in the direction that lowers net emissions. The fleet gets more efficient month by month. The mix moves toward lower-carbon power (288 to 252 gCO2e/kWh in 18 months). Flare-gas mitigation grows as more wellhead capacity comes on. Between refreshes the tracker therefore overstates net emissions, and by more the longer since the last refresh. The direction is stated with the output so a reader knows which way to expect a correction.

## Limitations, and what would tighten them

Each limit below is also the next measurement that would add a layer of confidence.

The off-grid share is the least measured input. Cambridge's 8.1% covers surveyed firms only, and the informal fleet is estimated rather than counted; the 6-15% range is the width of that uncertainty. A question on off-grid share in the next Cambridge survey round would narrow it more than any further modelling. The uptime split by power source is likewise assumed, since no survey breaks the off-grid fleet down that way, though once the delivered share is set it affects installed-capacity conversions rather than the network average.

The facility overhead rests on one disclosed site figure and an argument from the cooling mix; a PUE question in the same survey round would settle it. Luxor's tier shares are not public, so the active-fleet derivation treats the whole idle capacity as sitting in the 25-38 J/TH tier. Some of it is newer machines in transit or under maintenance, which would lower the active fleet's efficiency slightly and raise the result by a fraction of a joule. A published tier breakdown from Luxor, or Cambridge's final survey figures, would close most of the 2.1 J/TH swing on the grid-fleet input.

Machine ratings are nameplate. Hydro and immersion operators often underclock, which improves J/TH below the rating, while some air-cooled operators overclock, which worsens it; the two pull in opposite directions and are not separately modelled. Difficulty-implied hashrate carries a few percent of error over a 7-day average; the tracker's daily reading inherits that.

The result also moves with hashprice. When hashprice falls the idle tier grows and the active grid fleet becomes more efficient; when it rises, older machines switch back on. The estimate is dated to its inputs and is recomputed when Luxor publishes a new fleet figure, roughly monthly.

Two questions sit with Cambridge on the flare-gas figure: how the 44-respondent sample scales to the network, and how the figure relates to the larger flare offset in Cambridge's pre-release briefing. Either answer would move the mitigation line, and both would move it up.

## References

- Forster, P. et al. (2021), The Earth's Energy Budget, Climate Feedbacks and Climate Sensitivity, in IPCC AR6 WG1 Chapter 7, Table 7.15: methane GWP20 82.5 (fossil) and 79.7 (non-fossil), GWP100 29.8 and 27.0. https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-7/
- Plant, G. et al. (2022), Inefficient and unlit natural gas flares both emit large quantities of methane, Science 377(6614): 1566-1571. Aircraft-measured flare destruction efficiency 91.1% across the Permian, Eagle Ford and Bakken. https://www.science.org/doi/10.1126/science.abq0385
- Cambridge Centre for Alternative Finance (2026), Digital Mining Industry Report, 2nd edition, preliminary slides shared by Alexander Neumueller, data as of 12 August 2026: survey fleet efficiency 20.8 J/TH at December 2025 and estimated 16.3 J/TH at August 2026 with a 1.10 overhead; December 2025 energy mix (59.4% low-carbon, 252 gCO2e/kWh); 138.8 TWh and 35.0 MtCO2e at August 2026; flare-gas mitigation by assumption. Stored at `sources/cambridge-2nd-edition-preliminary-2026-08/`.
- Cambridge Centre for Alternative Finance (2025), Cambridge Digital Mining Industry Report, April 2025: 28.2 J/TH weighted (median 29.5, mean 30.6, range 18.0-71.4, N=45) as of June 2024; off-grid 8.1% of surveyed power, 1.23 GW. https://www.jbs.cam.ac.uk/wp-content/uploads/2025/04/2025-04-cambridge-digital-mining-industry-report.pdf
- Luxor Hashrate Index (2026), Hashrate Lookback Series, July 2026 (published 7 August 2026): total net ASIC capacity 1,153 EH, active fleet 926 EH, idle 227 EH, fleet average 20.2 J/TH, $0.048/kWh average power cost, energy hashprice by efficiency tier. https://hashrateindex.com/blog/luxor-hashrate-lookback-series-july-2026/
- mempool.space mining API, daily difficulty-implied hashrate. https://mempool.space/docs/api/rest#get-mining-hashrate
- Blockchain.com charts API (fallback). https://api.blockchain.info/charts/hash-rate?timespan=1year&format=json
- Coin Metrics community API: PriceUSD (daily bitcoin price, context only) and HashRate (fallback hashrate source). https://docs.coinmetrics.io/api/v4
- Methane GWP Recalibration Note (this project), the record of why the project's own central GWP20 sits above AR6 and why AR6 is used here regardless.
- [Hashrate Index Roundup, 9 November 2026](https://hashrateindex.com/blog/hashrate-index-roundup-november-9-2026/): hashprice $31.89/PH/day, energy hashprice by tier, difficulty 148.36T
- [CoinShares Bitcoin Mining Report, Q2 2026](https://coinshares.com/insights/research-data/bitcoin-mining-report-q2-2026/) (15 September 2026): operator efficiencies, hashrate history, share of fleet below breakeven
- [CleanSpark March 2026 operational update](https://www.stocktitan.net/news/CLSK/clean-spark-releases-march-2026-operational-fmweqc4h138k.html): 16.07 J/TH, 50 EH/s
- [Bitdeer Q1 2026 earnings call](https://www.aol.com/articles/bitdeer-btdr-q1-2026-earnings-182451000.html): fleet 16.4 J/TH at 31 March 2026, Tydal PUE ~1.1
- [CBECI methodology](https://ccaf.io/cbnsi/cbeci/methodology): $0.05/kWh hardware selection, release-date weighting, PUE 1.10 with bounds 1.01 and 1.20
- [Spark, Bitcoin energy consumption comparison](https://www.spark.money/tools/bitcoin-energy-consumption-comparison): republishes CBECI and Cambridge survey figures
- [EIA Electric Power Monthly, Table 6.07.B](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_6_07_b): capacity factors for utility-scale solar and wind
- Manufacturer ratings for the S19 XP (21.5 J/TH), S19 Pro and S19j Pro (29.5 J/TH), M30S++ (31 J/TH), S21 (17.5 J/TH), S23 Hyd (~9.5 J/TH)

## Check values

Cambridge's own points, for testing the chain: 190 TWh and 48.0 MtCO2e at December 2025; 138.8 TWh and 35.0 MtCO2e at August 2026 (885 EH/s, 16.3 J/TH, 1.10 overhead, 252 gCO2e/kWh). Reproducing these with Cambridge's inputs confirms the arithmetic before the tracker's own inputs are substituted.
