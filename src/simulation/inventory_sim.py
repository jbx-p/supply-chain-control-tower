"""
inventory_sim.py
A simpy-based inventory simulation for one product: daily demand
consumption, a reorder-point policy, and a supplier delivery process
with randomized disruption risk (extra delay) and demand shocks.
"""

import simpy
import random


class InventorySimulation:
    def __init__(self, env, product_id, initial_inventory,
                 daily_demand_mean, daily_demand_std,
                 reorder_point, order_quantity,
                 base_lead_time, risk_score,
                 disruption_prob=0.10, demand_spike_prob=0.05,
                 sim_days=180):
        self.env = env
        self.product_id = product_id
        self.inventory = initial_inventory
        self.daily_demand_mean = daily_demand_mean
        self.daily_demand_std = max(daily_demand_std, 0.01)  # avoid zero-std edge case
        self.reorder_point = reorder_point
        self.order_quantity = order_quantity
        self.base_lead_time = base_lead_time
        self.risk_score = risk_score
        self.disruption_prob = disruption_prob
        self.demand_spike_prob = demand_spike_prob
        self.sim_days = sim_days

        self.total_stockout_units = 0.0
        self.total_demand = 0.0
        self.orders_placed = 0
        self.disruption_events = 0
        self.daily_log = []

        self.action = env.process(self.run())

    def supplier_delivery(self, qty):
        """
        Runs as its own simpy process once triggered by a reorder.
        Lead time is risk-adjusted (as in Phase 5), and has a chance
        of an additional disruption delay — mirroring Phase 1's
        injected disruption events, but stochastic here instead of
        pre-scripted.
        """
        lead_time = self.base_lead_time * (1 + (self.risk_score / 100) * 0.5)

        if random.random() < self.disruption_prob:
            lead_time *= random.uniform(1.5, 3.0)
            self.disruption_events += 1

        yield self.env.timeout(lead_time)
        self.inventory += qty

    def run(self):
        for day in range(self.sim_days):
            demand = max(0, random.gauss(self.daily_demand_mean, self.daily_demand_std))

            if random.random() < self.demand_spike_prob:
                demand *= random.uniform(1.5, 3.0)

            self.total_demand += demand

            if demand > self.inventory:
                stockout = demand - self.inventory
                self.total_stockout_units += stockout
                self.inventory = 0
            else:
                self.inventory -= demand

            if self.inventory <= self.reorder_point:
                self.env.process(self.supplier_delivery(self.order_quantity))
                self.orders_placed += 1

            self.daily_log.append({"day": day, "inventory": round(self.inventory, 1)})
            yield self.env.timeout(1)

    @property
    def service_level(self):
        if self.total_demand == 0:
            return 1.0
        return 1 - (self.total_stockout_units / self.total_demand)


if __name__ == "__main__":
    random.seed(42)
    env = simpy.Environment()
    sim = InventorySimulation(
        env, product_id="TEST",
        initial_inventory=500,
        daily_demand_mean=100, daily_demand_std=15,
        reorder_point=300, order_quantity=1500,
        base_lead_time=20, risk_score=50,
        sim_days=180,
    )
    env.run(until=180)

    print(f"Service level: {sim.service_level:.1%}")
    print(f"Total stockout units: {sim.total_stockout_units:.1f}")
    print(f"Orders placed: {sim.orders_placed}")
    print(f"Disruption events hit: {sim.disruption_events}")