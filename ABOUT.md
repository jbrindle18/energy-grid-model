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

## Could Battery Storage Be the Game-Changer?

While this model highlights significant structural problems with renewable-heavy electricity markets, there is one technology that could fundamentally alter this dynamic: **battery storage**.

### The Storage Solution

Battery storage has the potential to address many of the core problems this model reveals:

**1. Reducing Curtailment and Wasted Energy**

When renewable generation exceeds demand (causing prices to crash to zero), batteries can **store the excess energy** instead of it being wasted through curtailment. This captured energy can then be discharged later when demand is high and prices spike. By acting as a "buffer" between supply and demand, batteries transform what would be wasted renewable energy into valuable, dispatchable power.

**2. Smoothing Price Volatility**

The model shows extreme price volatility: zero prices when renewables are abundant, and high prices when they drop. Batteries can **arbitrage these price differences** - buying (charging) when prices are low and selling (discharging) when prices are high. This creates a natural price floor and ceiling, reducing the wild swings that make the market so unstable. The more storage capacity, the smoother prices become.

**3. Restoring Market Functionality**

Perhaps most importantly, batteries could **restore genuine price signals** to the market. When batteries charge during low-price periods and discharge during high-price periods, they respond directly to market prices - unlike CfD-backed renewables that are insulated from price signals. This creates a more functional market where price actually guides behavior, rather than being overridden by government contracts.

**4. Reducing CfD Costs**

If batteries can store excess renewable energy and discharge it during high-price periods, renewable generators would earn more from the wholesale market. This means they would need **fewer CfD top-up payments** to reach their strike price. In scenarios where batteries are abundant, the wholesale price might stay closer to CfD strike prices, dramatically reducing the subsidy burden on consumers.

**5. Reducing Gas Backup Requirements**

Currently, gas plants must maintain high capacity to cover periods when renewables drop. But if batteries can store renewable energy and discharge it during these periods, the need for gas backup capacity decreases. This could reduce the "stranded asset" problem and lower overall system costs.

### The Catch: 

However, there are significant challenges:

- **Cost**: Battery storage is still expensive, though costs are falling rapidly. The economics depend on the price spread between low and high periods - which this model shows can be substantial, but may narrow as more storage enters the market.

- **Scale**: The UK expects 23-27 GW of battery capacity by 2030, but this may still be insufficient to fully address the volatility shown in high-RE scenarios. The model shows curtailment in the hundreds of GWh - storing all of this would require massive battery capacity.

- **Duration**: Most grid-scale batteries today can only store 2-4 hours of energy. For longer periods (overnight, or during extended low-wind periods), longer-duration storage or other solutions would be needed.

- **Market Structure**: Batteries would need appropriate market mechanisms to participate effectively as described here. Current UK markets are still adapting to storage participation.



**This model doesn't include storage, so it may be **overstating the problems** in high-RE scenarios. The future might be less bleak than these simulations suggest - but only if storage deployment keeps pace with renewable growth, and if the economics work out.**

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

**CfD Strike Price Assumptions**: The model uses a portfolio-based approach that reflects the weighted average strike prices of all active CfD contracts in a given year. For 2025, the weighted average strike prices are approximately £69/MWh (solar), £121/MWh (onshore wind), and £149/MWh (offshore wind), with an overall average of £147/MWh. This accounts for the mix of older, more expensive contracts from early allocation rounds (AR1-AR3) and newer, cheaper contracts from recent rounds (AR4-AR6). The model defaults to "Portfolio (Historical)" mode, which uses these weighted averages. Users can switch to "Manual" mode to explore scenarios with different strike price assumptions, such as a system dominated by newer AR6 contracts (£47-59/MWh) or older contracts (£80-140/MWh).

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
- **CfD strike prices**: Low Carbon Contracts Company (LCCC). The model uses portfolio-based weighted average strike prices that reflect the mix of active contracts from all allocation rounds. For 2025, this produces averages of £69/MWh (solar), £121/MWh (onshore wind), and £149/MWh (offshore wind). Users can view historical allocation round prices and switch to manual strike price mode in the visualiser.
- **Capacity factors**: BEIS historical averages (Solar ~11%, Onshore ~27%, Offshore ~40%)
- **Gas costs**: Calibrated to £73/MWh wholesale price for 2025 validation. See VALIDATION_2025.md for calibration details.
- **Scenario presets**: NESO Clean Power 2030, UK Government targets, GlobalData projections

## Model Validation

The model has been validated against 2025 UK electricity market data. With calibrated parameters, the model produces wholesale prices within **£0.15/MWh (0.2%)** of expected values. See `VALIDATION_2025.md` for detailed validation results and calibrated parameters.

*This is an educational model for exploring market dynamics, not a forecasting tool.*

