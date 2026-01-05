# The Renewable Energy Paradox: Why "Cheaper" Green Power Might Not Lower Your Bills

*How the UK's electricity market creates a hidden cost spiral as we race toward net zero*

---

## The Promise vs The Reality

We've all heard the headlines: renewable energy is now the cheapest form of electricity generation. Solar and wind costs have plummeted. The path to net zero should mean cheaper power for everyone.

But there's a catch. A big one.

As I discovered while researching my dissertation on UK electricity market economics, the very success of renewable energy creates a financial paradox that could keep consumer bills stubbornly high - or even push them higher.

Welcome to the **subsidy spiral**.

---

## How Electricity Prices Actually Work

Before we get to the paradox, you need to understand one crucial thing about how electricity is priced in the UK.

Every half-hour, the National Grid dispatches power plants in order of their running costs - cheapest first. This is called the **merit order**. Solar and wind, with essentially zero fuel costs, always go first. Then nuclear, then biomass, and finally gas.

Here's the key: **the most expensive plant needed to meet demand sets the price for everyone**.

So if we need gas to keep the lights on (and we almost always do), then gas sets the wholesale price - and every generator, including solar and wind, receives that same price.

![Merit Order Diagram]

This system made sense when most plants had similar cost structures. But it creates strange dynamics when you mix zero-cost renewables with expensive gas.

---

## The Cannibalisation Effect

Imagine you're an investor in a new wind farm. You've done your calculations based on current wholesale prices of around £80/MWh. Looks profitable.

But here's what happens as more wind farms get built:

1. **More wind capacity** means wind generates more of the UK's electricity
2. **When wind is generating**, there's less need for expensive gas
3. **Less gas means lower prices** during those hours
4. **But wind farms all generate at the same time** (when it's windy)
5. **So wind farms increasingly sell power when prices are lowest**

This is **cannibalisation** - renewable generators eating into their own revenues.

I built a model to quantify this. The results are stark:

| Scenario | RE Share | Avg Wholesale Price | RE Capture Price | Capture Rate |
|----------|----------|--------------------:|----------------:|-------------:|
| Current UK | ~35% | £82/MWh | £78/MWh | 95% |
| 2030 Targets | ~65% | £45/MWh | £32/MWh | 71% |
| High RE | ~85% | £18/MWh | £8/MWh | 44% |

That last column is the killer. At high renewable penetration, wind and solar might only capture 44% of the average wholesale price. They're generating power, but increasingly for free.

---

## Enter Contracts for Difference

The government saw this problem coming. Their solution: **Contracts for Difference (CfDs)**.

Here's how they work:

- A renewable generator is guaranteed a **strike price** (say, £50/MWh)
- If the wholesale price is below the strike price, consumers pay the difference
- If the wholesale price is above the strike price, the generator pays back the difference

In theory, this gives investors certainty and should lower costs over time as strike prices fall.

In practice, it creates the subsidy spiral.

---

## The Subsidy Spiral Explained

Let's trace through what happens:

**Today (Low RE Penetration):**
- Wholesale price: ~£80/MWh (gas often sets the price)
- Strike price: ~£50/MWh
- CfD payment: Generator pays BACK £30/MWh
- Consumer benefit: Clawback payments reduce bills

**2030 (High RE Penetration):**
- Wholesale price: ~£30/MWh (RE sets price more often)
- Strike price: ~£50/MWh
- CfD payment: Consumer pays £20/MWh TOP-UP
- Consumer cost: Levy on bills increases

**The Paradox:**
As renewable energy succeeds in driving down wholesale prices, CfD costs to consumers *increase*. The gap between the (falling) wholesale price and the (fixed) strike price grows ever wider.

Wholesale prices fall. Consumer prices don't.

---

## What The Model Shows

Using my simulation of the UK grid, I can model these dynamics in real-time. The key metrics tell the story:

**Wholesale Price** - What generators receive from the market
**Consumer Price** - What you actually pay (wholesale + CfD levy)

Switch from "Current UK" to "2030 Government Targets" in the model and watch:
- Wholesale price drops significantly
- But consumer price stays flat or rises
- CfD levy grows to fill the gap

This isn't a bug in the market design. It's a feature. CfDs were designed to provide revenue certainty for investors - and they do. But that certainty comes at a cost that's passed directly to consumers.

---

## The Caveats

Before you conclude that renewables are a scam, some important context:

### What the model doesn't capture:

1. **Curtailment costs** - When we have too much renewable power and pay generators to switch off (~£3bn/year projected). This means reality may be *worse* than the model suggests.

2. **Storage** - Batteries could absorb excess renewable power and reduce price volatility. The UK expects 23-27 GW of battery capacity by 2030.

3. **Demand flexibility** - Smart tariffs could shift consumption to match renewable output, reducing the need for gas backup.

4. **Grid upgrades** - £24 billion is being invested in "electricity superhighways" to reduce bottlenecks.

### What's changing:

The government is reforming the system. Strike prices have fallen dramatically - offshore wind went from £117/MWh in 2015 to £58/MWh in 2024. New CfD contracts are getting cheaper.

And crucially, the counterfactual matters: what would prices be *without* renewables? If we were still dependent on volatile gas markets, bills would likely be even higher and more unpredictable.

---

## The Uncomfortable Questions

My research doesn't argue against renewable energy. It argues that our current market design has fundamental tensions:

1. **Can marginal pricing work in a zero-marginal-cost world?**
   When most generators have near-zero running costs, who sets the price? What does "competitive" even mean?

2. **Should we pay for capacity, not just energy?**
   We need gas plants available for when the wind doesn't blow. But they can't survive economically if they only run occasionally. The Capacity Market tries to address this, but is it enough?

3. **Is locational pricing inevitable?**
   Currently, electricity costs the same everywhere in Great Britain. But it's much cheaper to generate in Scotland (wind) than to consume in London. Should prices reflect this?

4. **Who bears the transition costs?**
   Decarbonisation is essential. But the costs fall disproportionately on bill-payers, while the benefits (avoided climate damage) are diffuse. Is this fair?

---

## Try It Yourself

I've built an interactive tool that lets you explore these dynamics. Adjust renewable capacity, change strike prices, compare scenarios.

**[Link to visualiser]**

Watch how wholesale prices, consumer prices, and CfD costs interact. See the subsidy spiral in action.

---

## Conclusion

The UK's electricity market is undergoing the biggest transformation since privatisation. Renewable energy is not just an environmental necessity - it's increasingly an economic one.

But the transition isn't free, and the costs aren't always visible. The subsidy spiral means that the success of renewables in driving down wholesale prices doesn't automatically translate to lower consumer bills.

This isn't an argument against decarbonisation. It's an argument for honest accounting about transition costs, and for continued market reform to ensure those costs are distributed fairly.

The question isn't whether we can afford to decarbonise. It's whether we can afford a market design that obscures the true economics of the transition.

---

*This analysis is based on my dissertation research at the University of Sheffield. The interactive model is available at [link]. All models are simplifications - see the "About" tab for caveats and assumptions.*

---

## Key Terms Glossary

| Term | Definition |
|------|------------|
| **Merit Order** | Dispatching generators cheapest-first; the most expensive needed sets the price |
| **Wholesale Price** | The market clearing price for electricity |
| **Cannibalisation** | Renewable generators earning less as RE penetration increases |
| **CfD (Contract for Difference)** | Government scheme guaranteeing generators a fixed "strike price" |
| **Strike Price** | The guaranteed price per MWh under a CfD contract |
| **LCCC** | Low Carbon Contracts Company - manages CfD payments |
| **Capture Rate** | What RE generators actually earn vs the average wholesale price |
| **Curtailment** | Paying generators to reduce output when supply exceeds demand |

