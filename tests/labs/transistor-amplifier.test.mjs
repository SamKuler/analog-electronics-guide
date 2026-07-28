import assert from "node:assert/strict";
import test from "node:test";

import {
  amplifierModel,
  amplifierSample,
} from "../../docs/assets/javascripts/labs/transistor-amplifier.mjs";


const nominal = {
  mode: "bjt",
  transconductanceMilliSiemens: 40,
  stageResistanceKOhm: 2,
  degenerationKOhm: 0.5,
  sourceResistanceKOhm: 1,
  inputResistanceKOhm: 9,
  loadResistanceKOhm: 2,
  supplyVoltage: 12,
  quiescentOutputVoltage: 5,
  inputPeakVoltage: 0.1,
};


test("amplifier model exposes the three gain-chain factors", () => {
  const model = amplifierModel(nominal);

  assert.ok(Math.abs(model.sourceFactor - 0.9) < 1e-12);
  assert.ok(Math.abs(model.stageGain - (-80 / 21)) < 1e-12);
  assert.ok(Math.abs(model.loadFactor - 0.5) < 1e-12);
  assert.ok(Math.abs(model.totalGain - (-12 / 7)) < 1e-12);
});


test("common-emitter and common-source samples invert phase", () => {
  const point = amplifierSample(amplifierModel(nominal), Math.PI / 2);

  assert.ok(point.input > 0);
  assert.ok(point.outputSignal < 0);
  assert.equal(point.clippedRegion, "linear");
});


test("output clipping is asymmetric around an off-center Q point", () => {
  const model = amplifierModel({
    ...nominal,
    degenerationKOhm: 0,
    inputPeakVoltage: 0.2,
    quiescentOutputVoltage: 2,
  });
  const positiveInput = amplifierSample(model, Math.PI / 2);
  const negativeInput = amplifierSample(model, 3 * Math.PI / 2);

  assert.equal(positiveInput.clippedRegion, "lower");
  assert.equal(negativeInput.clippedRegion, "linear");
  assert.ok(Math.abs(positiveInput.outputVoltage - 0.2) < 1e-12);
});


test("MOS mode uses zero as the simplified lower output boundary", () => {
  const model = amplifierModel({ ...nominal, mode: "mos" });

  assert.equal(model.boundaryModel, "abstract-output-window");
  assert.equal(model.lowerBoundaryVoltage, 0);
  assert.equal(model.lowerHeadroom, 5);
  assert.equal(model.upperHeadroom, 7);
});
