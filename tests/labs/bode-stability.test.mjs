import assert from "node:assert/strict";
import test from "node:test";

import {
  loopResponse,
  stabilityMetrics,
} from "../../docs/assets/javascripts/labs/bode-stability.mjs";


test("one dominant pole contributes minus 3.0103 dB at its corner", () => {
  const response = loopResponse(
    { dcLoopGain: 1, pole1Hz: 100, pole2Hz: 1e15 },
    100,
  );

  assert.ok(Math.abs(response.magnitudeDb - (-3.0102999566)) < 1e-8);
  assert.ok(Math.abs(response.phaseDeg - (-45)) < 1e-8);
});


test("two poles approach minus 180 degrees above both corners", () => {
  const response = loopResponse(
    { dcLoopGain: 1000, pole1Hz: 10, pole2Hz: 100 },
    1e7,
  );

  assert.ok(response.phaseDeg < -179.99);
});


test("lowering the second pole reduces phase margin", () => {
  const highSecondPole = stabilityMetrics({
    dcLoopGain: 1e4,
    pole1Hz: 10,
    pole2Hz: 1e7,
  });
  const lowSecondPole = stabilityMetrics({
    dcLoopGain: 1e4,
    pole1Hz: 10,
    pole2Hz: 1e3,
  });

  assert.equal(highSecondPole.hasCrossover, true);
  assert.equal(lowSecondPole.hasCrossover, true);
  assert.ok(lowSecondPole.phaseMarginDeg < highSecondPole.phaseMarginDeg);
  assert.ok(lowSecondPole.dampingRatio < highSecondPole.dampingRatio);
});


test("loop below unity reports no zero-decibel crossover", () => {
  const metrics = stabilityMetrics({
    dcLoopGain: 0.5,
    pole1Hz: 10,
    pole2Hz: 100,
  });

  assert.equal(metrics.hasCrossover, false);
  assert.equal(metrics.crossoverHz, null);
  assert.equal(metrics.status, "无 0 dB 交越");
});


test("loop exactly at unity has no positive-frequency crossover", () => {
  const metrics = stabilityMetrics({
    dcLoopGain: 1,
    pole1Hz: 10,
    pole2Hz: 100,
  });

  assert.equal(metrics.hasCrossover, false);
  assert.equal(metrics.crossoverHz, null);
  assert.equal(metrics.status, "无 0 dB 交越");
});
