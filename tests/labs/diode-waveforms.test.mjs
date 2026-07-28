import assert from "node:assert/strict";
import test from "node:test";

import {
  diodeSample,
  diodeWaveform,
} from "../../docs/assets/javascripts/labs/diode-waveforms.mjs";


test("half-wave rectifier blocks a negative half-cycle", () => {
  const point = diodeSample(
    { mode: "rectifier", amplitude: 5, offset: 0, drop: 0.7, reference: 0 },
    3 * Math.PI / 2,
  );

  assert.equal(point.output, 0);
  assert.equal(point.conducting, false);
});


test("half-wave rectifier subtracts the forward drop while conducting", () => {
  const point = diodeSample(
    { mode: "rectifier", amplitude: 5, offset: 0, drop: 0.7, reference: 0 },
    Math.PI / 2,
  );

  assert.ok(Math.abs(point.output - 4.3) < 1e-12);
  assert.equal(point.conducting, true);
});


test("upper limiter clamps above reference plus diode drop", () => {
  const point = diodeSample(
    { mode: "limiter", amplitude: 5, offset: 0, drop: 0.7, reference: 2 },
    Math.PI / 2,
  );

  assert.equal(point.output, 2.7);
  assert.equal(point.conducting, true);
});


test("steady-state positive clamper pins the negative peak", () => {
  const point = diodeSample(
    { mode: "clamper", amplitude: 4, offset: 1, drop: 0.6, reference: 0 },
    3 * Math.PI / 2,
  );

  assert.ok(Math.abs(point.output - 0.6) < 1e-12);
  assert.equal(point.conducting, true);
});


test("finite clamp time constant produces more droop than a large one", () => {
  const fast = diodeWaveform(
    { mode: "clamper", amplitude: 4, offset: 0, drop: 0.7, reference: 0, rcPeriods: 1 },
    241,
  );
  const slow = diodeWaveform(
    { mode: "clamper", amplitude: 4, offset: 0, drop: 0.7, reference: 0, rcPeriods: 20 },
    241,
  );
  const positivePeakIndex = 60;

  assert.ok(fast[positivePeakIndex].output < slow[positivePeakIndex].output);
});
