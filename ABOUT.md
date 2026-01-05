# About This Model

> **⚠️ Beta Version**: This model is currently in beta. While it accurately captures core market dynamics, it is a simplified representation with known limitations. Results should be interpreted with caution and not used for investment or policy decisions. Feedback and bug reports welcome.

## Note from the Author

This interactive tool simulates the UK wholesale electricity market to explore price dynamics under different renewable energy scenarios. It was developed by me, **Joe Brindle** ([www.joebrindle.uk](https://www.joebrindle.uk/)), as a project of interest, after writing my undergraduate dissertation *"Profit vs the Planet: Is the UK's market-based electricity decarbonisation strategy feasible?"*, largely inspired by Brett Christophers' book [*The Price is Wrong*](https://www.versobooks.com/en-gb/products/3069-the-price-is-wrong).

**Contact**: [joe@joebrindle.uk](mailto:joe@joebrindle.uk)

---

## Energy "Markets"

There is a lot this model doesn't do - it's ridiculously oversimplified compared to the actual energy grid - but it is here to prove an ultimately simple point: **the future of our energy markets just don't make sense.**

As renewable energy penetration increases, the revenue from generating will fall, often hitting zero; energy prices will be incredibly volatile. So why on earth would anyone want to invest in renewables, especially considering they may have to guarantee returns for 2+ decades in order to make profits? Fortunately, the government has introduced agreements called **Contracts for Difference (CfD)**, which assure renewable generators a set price when their energy is bought - regardless of the "spot" price at that moment. These CfD prices are essentially set by the government, and allocated related to a calculated need for buildout in that year. In the past, they were allocated through a reverse auction, but this was judged to negatively drive down prices and disincentivise adequate renewable investment.

In this model you can see that at greater renewable penetrations, the wholesale "spot" prices for energy are often really low, especially when renewable generation is high - but renewable energy generators are still compensated lots of money because of their CfDs. In short, the bulk of energy prices in this "market" will be set by centralised government decision; by shifting from a system of energy prices driven by fuel costs to one driven by capital investment, we have effectively made the traditional market mechanism redundant.

### The Death of the Price Signal

In a healthy market, price serves as a signal: high prices encourage production, and low prices discourage it. However, under the **Contract for Difference (CfD)** model, this signal is severed.

Because the government guarantees a "strike price," the renewable generator is insulated from the reality of the wholesale market. When the sun is shining and the wind is blowing, the "spot" price may crash to zero - or even turn negative, something I've not modelled here - but the generator continues to produce because their income is locked in. The market is no longer "clearing" based on supply and demand; it is simply a pass-through entity for a predetermined government contract.


### The Worst of Both Worlds

This leaves us in a precarious middle ground: a **pseudo-market** that requires heavy-handed government control but lacks the efficiency of a truly planned system. We are left with several systemic failures:

- **Crude Capacity Planning:** Instead of the market identifying where and when energy is needed, we rely on civil servants to "guess" the required buildout for the next decade. If the government miscalculates the "strike price" or the volume required, we end up with either an energy shortfall or an expensive surplus.

- **The Privatization of Upside:** Under this model, the government provides the ultimate safety net, effectively underwriting the entire industry. However, while the public assumes the long-term risk of these price guarantees, the financial rewards flow directly into the **private purse**. We have socialised the risk of the energy transition while privatizing the returns from our natural resources.

- **The Inefficiency of Private Debt:** Funding a national grid through private loans is inherently more expensive than public investment. Private lenders demand higher interest rates to account for perceived risks and the 20-year repayment window. If the state used its ability to borrow at lower sovereign rates to fund infrastructure directly, the total cost to the taxpayer would be significantly lower. Instead, we pay a "private capital premium" that inflates the price of every megawatt-hour.

- **Decoupled Incentives:** In a planned system, the state could strategically place infrastructure to minimize grid congestion. In our current "zombie market," private companies build wherever they can secure a CfD, often forcing the government to pay even more "constraint payments" to turn generators off when the grid can't handle the load.

### A Necessity for Control Without the Benefits

Ultimately, we have created a system of **necessity-driven government control**. We cannot allow the market to set the price, because at high renewable penetration, the market price would be so low and volatile that no rational investor would ever build a wind farm.

Thus, the state is forced to step in and fix prices to ensure survival. We have ended up with a system that has all the **rigidity of a planned economy** - where prices are set by decree and investment is directed by central quotas - but with none of the **coordination or cost-integration** that a fully nationalised, planned grid might offer. We are paying the premium for a market that, for all intents and purposes, no longer exists.

*P.S. There are plenty more reasons why this system is going to get messy. The risk of stranded gas assets (needed to maintain high capacity in case of renewable drop, but rarely generating) is an important one of these.*

---

## Model Strengths

This model accurately captures several key dynamics of the UK electricity market:

- **Merit order dispatch**: Correctly models how generators are dispatched cheapest-first
- **Price formation**: Accurately shows how the marginal generator sets wholesale price
- **Time-varying RE output**: (Reasonably) realistic solar and wind patterns (hourly/seasonal variation)
- **Demand profiles**: UK-typical demand patterns (weekday/weekend, seasonal)
- **Cannibalisation effect**: Correctly shows RE generators earning less as RE grows
- **Price volatility**: Captures price spikes and collapses
- **CfD mechanics**: Properly calculates top-up and clawback payments
- **Parameter sensitivity**: Can test impact of gas prices, carbon prices, CfD strike prices

---

## Model Weaknesses & Limitations

This model is a **simplified representation** and does not include several important factors:

### ⚠️ Critical Missing Elements

**CfD Strike Price Assumptions**: The model's default CfD strike prices (£58-71/MWh) reflect Allocation Round 6 (2024) prices for new projects. However, existing renewable energy capacity has much higher strike prices from earlier allocation rounds. The weighted average of active CfDs in 2025 was approximately £151/MWh. This means the model may **understate CfD costs** for scenarios representing the current UK system, where older, more expensive contracts still dominate. Users can adjust strike prices in the visualiser to explore different contract mixes.

**Curtailment Costs**: The model tracks curtailment volume but not costs. In reality, curtailed generators (especially older Renewables Obligation farms) receive compensation payments, estimated at ~£3bn/year at peak. This is not modelled because curtailment compensation varies, and is sometimes part of CfD sometimes not. This means the model may significantly **understate costs** in high-RE scenarios where renewables are generating above demand.

**Capacity Markets**: The model does not include capacity market payments (~£1.4bn/year in 2025, approximately £5/MWh spread across all generation). These payments ensure gas plants remain available for grid stability, even when not generating. This understates consumer costs and gas plant economics, as capacity markets subsidize the cost of maintaining backup generation.

**Balancing Costs**: While the model tracks curtailment volume, it does not include the full balancing cost (£2.5bn in 2024, £4.3-5.2bn projected for 2025, or £9-18/MWh). Most of this is from network constraints forcing generators to switch off when the grid cannot handle the load. Combined with capacity markets, this adds £14-23/MWh to consumer bills that the model does not capture, and these costs increase with renewable penetration.

**Battery Storage**: The model assumes no storage. The UK expects 23-27 GW of battery capacity by 2030, which would significantly reduce curtailment and price volatility. This means the model may **overstate costs** in high-RE scenarios where storage would help.

**Network Constraints**: Transmission bottlenecks (especially Scotland to England) cause additional curtailment not captured here. Real curtailment is higher than model suggests.

### 📊 Market Structure Simplifications

**Forward Markets**: This model uses spot prices only. In reality, most electricity is sold in forward markets (days/weeks/months ahead), which smooths price volatility. Generators with forward contracts experience less cannibalisation than shown here.

**Balancing Mechanism**: Real-time grid balancing and the Balancing Mechanism are not modelled. This affects price formation during periods of supply/demand imbalance.

**Interconnector Dynamics**: Interconnectors are modelled as simple imports with fixed prices. In reality, they can flow both ways and prices vary with European market conditions.

**Negative Pricing**: The model sets a price floor at zero. Real markets can have negative prices when there's excess supply and generators pay to stay online.

### 🔧 Technical Limitations

**Demand-Side Response**: No modelling of flexible demand (smart tariffs, EV charging, heat pumps). This could absorb excess renewable power and reduce the need for gas backup.

**Generator Outages**: All dispatchable generators are assumed available at full capacity. Real plants have planned maintenance and unplanned outages.

**Start-up Costs**: Gas plants have start-up costs not included in marginal cost calculations. This affects dispatch decisions for short periods.

**Network Losses**: Transmission losses are not modelled. Real generation must exceed demand to account for losses.



---

## Data Sources & References

- **Capacity data**: BEIS/DESNZ Energy Statistics 2024
- **CfD strike prices**: Low Carbon Contracts Company (LCCC). Default values reflect Allocation Round 6 (2024) prices for new projects. Historical allocation round prices are available in the visualiser.
- **Capacity factors**: BEIS historical averages (Solar ~11%, Onshore ~27%, Offshore ~40%)
- **Gas costs**: Typical 2024/25 fuel + UK ETS carbon prices
- **Scenario presets**: NESO Clean Power 2030, UK Government targets, GlobalData projections

*This is an educational model for exploring market dynamics, not a forecasting tool.*

