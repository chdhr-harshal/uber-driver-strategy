# Putting Data in the Driver's Seat: Optimizing Earnings for On-Demand Ride-Hailing

On-demand ride-hailing platforms like Uber and Lyft are helping reshape urban transportation, by enabling car owners to become drivers for hire with minimal overhead. Although there are many studies that consider ride-hailing platforms holistically, e.g., from the perspective of supply and demand equilibria, little emphasis has been placed on optimization for the individual, self-interested drivers that currently comprise these fleets. While some individuals drive opportunistically either as their schedule allows or on a fixed schedule, we show that strategic behavior regarding when and where to drive can substantially increase driver income. In this paper, we formalize the problem of devising a driver strategy to maximize expected earnings, describe a series of dynamic programming algorithms to solve these problems under different sets of modeled actions available to the drivers, and exemplify the models and methods on a large scale simulation of driving for Uber in NYC. In our experiments, we use a newly-collected dataset that combines the NYC taxi rides dataset along with Uber API data, to build time-varying traffic and payout matrices for a representative six-month time period in greater NYC. From this input, we can reason about prospective itineraries and payoffs. Moreover, the framework enables us to rigorously reason about and analyze the sensitivity of our results to perturbations in the input data. Among our main findings is that repositioning throughout the day is key to maximizing driver earnings, whereas 'chasing surge' is typically misguided and sometimes a costly move.

<strong>Paper: </strong>&lt;add link to the paper&gt;

<strong>Github:</strong> <a href="https://github.com/chdhr-harshal/uber_driver_strategy">https://github.com/chdhr-harshal/uber_driver_strategy</a>

<strong>Datasets: </strong>(Please refer to the paper for detailed information about the nature of the data.)
1. NYC taxi trips and zones dataset: <a href="http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml">http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml</a>
2. Uber passenger waiting time dataset: &lt;add link&gt;
3. Uber ride estimates dataset: &lt;add link&gt;

Detailed guide about various attributes in the Uber dataset is available at <a href="https://developer.uber.com/docs/riders/references/api/v1.2">https://developer.uber.com/docs/riders/references/api/v1.2</a>

<strong>Citation: </strong><span>We encourage you to cite our datasets if you have used them in your work. You can use the following BibTeX citation:</span>
<pre style="background-color: #eeeeee; padding: 1px; margin: 1px; font-family: consolas, courier, monospace; overflow-x: scroll; font-size: 13px; line-height: normal;">@misc{uberapicrawl,
  author       = {Chaudhari, Harshal A. and Byers, John W. and Terzi, Evimaria},
  title        = {NYC Uber API dataset},
  howpublished = {\url{https://www.bu.edu/cs/groups/dblab/ride-hailing}},
  month        = Dec,
  year         = 2017
}
</pre>
