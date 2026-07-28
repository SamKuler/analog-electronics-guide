import assert from "node:assert/strict";
import test from "node:test";

import {
  rectifierModel,
  rectifierSamples,
} from "../../docs/assets/javascripts/labs/rectifier-filter.mjs";


const nominal = {
  topology: "bridge",
  secondaryRmsVoltage: 9,
  frequencyHz: 50,
  diodeDropVoltage: 0.7,
  capacitanceMicroF: 1000,
  loadMilliAmp: 100,
  regulatorVoltage: 5,
  dropoutVoltage: 2,
};


test("bridge rectifier uses two diode drops and twice-line ripple frequency", () => {
  const model = rectifierModel(nominal);

  assert.ok(Math.abs(model.peakRectifiedVoltage - (9 * Math.SQRT2 - 1.4)) < 1e-12);
  assert.equal(model.rippleFrequencyHz, 100);
  assert.equal(model.diodeDrops, 2);
});


test("capacitor ripple estimate is load current divided by ripple frequency and capacitance", () => {
  const model = rectifierModel(nominal);

  assert.ok(Math.abs(model.rippleEstimateVoltage - 1) < 1e-12);
  assert.ok(Math.abs(model.valleyVoltage - (9 * Math.SQRT2 - 2.4)) < 1e-12);
  assert.equal(model.regulated, true);
});


test("low secondary voltage exposes dropout at the capacitor valley", () => {
  const model = rectifierModel({
    ...nominal,
    secondaryRmsVoltage: 5,
  });

  assert.equal(model.regulated, false);
  assert.ok(model.regulatorMarginVoltage < 0);
});


test("time samples show charging pulses and bounded regulator output", () => {
  const samples = rectifierSamples(nominal, 401);

  assert.equal(samples.length, 401);
  assert.ok(samples.some((point) => point.charging));
  assert.ok(samples.some((point) => !point.charging));
  assert.ok(samples.every((point) => point.capacitorVoltage >= 0));
  assert.ok(samples.every((point) => point.outputVoltage <= nominal.regulatorVoltage + 1e-12));
});


test("displayed nominal waveform is warmed to the same steady state as the metrics", () => {
  const model = rectifierModel(nominal);
  const samples = rectifierSamples(nominal, 401);

  assert.equal(model.regulated, true);
  assert.ok(samples.every((point) => (
    point.outputVoltage >= nominal.regulatorVoltage - 1e-12
  )));
  assert.ok(samples[0].capacitorVoltage > nominal.regulatorVoltage);
});
