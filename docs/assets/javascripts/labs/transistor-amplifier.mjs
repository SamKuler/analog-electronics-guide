function finite(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}


export function amplifierModel(parameters = {}) {
  const mode = parameters.mode === "mos" ? "mos" : "bjt";
  const transconductanceMilliSiemens = Math.max(
    0.001,
    finite(parameters.transconductanceMilliSiemens, 40),
  );
  const stageResistanceKOhm = Math.max(
    0.001,
    finite(parameters.stageResistanceKOhm, 2),
  );
  const degenerationKOhm = Math.max(
    0,
    finite(parameters.degenerationKOhm, 0),
  );
  const sourceResistanceKOhm = Math.max(
    0,
    finite(parameters.sourceResistanceKOhm, 1),
  );
  const inputResistanceKOhm = Math.max(
    0.001,
    finite(parameters.inputResistanceKOhm, 9),
  );
  const loadResistanceKOhm = Math.max(
    0.001,
    finite(parameters.loadResistanceKOhm, 10),
  );
  const supplyVoltage = Math.max(0.2, finite(parameters.supplyVoltage, 12));
  const quiescentOutputVoltage = Math.min(
    supplyVoltage,
    Math.max(0, finite(parameters.quiescentOutputVoltage, supplyVoltage / 2)),
  );
  const inputPeakVoltage = Math.max(
    0,
    finite(parameters.inputPeakVoltage, 0.1),
  );

  const sourceFactor = inputResistanceKOhm
    / (sourceResistanceKOhm + inputResistanceKOhm);
  const stageGain = -(
    transconductanceMilliSiemens * stageResistanceKOhm
  ) / (
    1 + transconductanceMilliSiemens * degenerationKOhm
  );
  const loadFactor = loadResistanceKOhm
    / (stageResistanceKOhm + loadResistanceKOhm);
  const totalGain = sourceFactor * stageGain * loadFactor;
  const lowerBoundaryVoltage = mode === "bjt" ? 0.2 : 0;
  const lowerHeadroom = Math.max(
    0,
    quiescentOutputVoltage - lowerBoundaryVoltage,
  );
  const upperHeadroom = Math.max(
    0,
    supplyVoltage - quiescentOutputVoltage,
  );

  return {
    mode,
    boundaryModel: "abstract-output-window",
    transconductanceMilliSiemens,
    stageResistanceKOhm,
    degenerationKOhm,
    sourceResistanceKOhm,
    inputResistanceKOhm,
    loadResistanceKOhm,
    supplyVoltage,
    quiescentOutputVoltage,
    inputPeakVoltage,
    sourceFactor,
    stageGain,
    loadFactor,
    totalGain,
    lowerBoundaryVoltage,
    lowerHeadroom,
    upperHeadroom,
  };
}


export function amplifierSample(model, phaseRadians) {
  const phase = finite(phaseRadians, 0);
  const input = model.inputPeakVoltage * Math.sin(phase);
  const candidateSignal = model.totalGain * input;
  const candidateOutputVoltage = model.quiescentOutputVoltage + candidateSignal;
  let outputVoltage = candidateOutputVoltage;
  let clippedRegion = "linear";

  if (candidateOutputVoltage < model.lowerBoundaryVoltage) {
    outputVoltage = model.lowerBoundaryVoltage;
    clippedRegion = "lower";
  } else if (candidateOutputVoltage > model.supplyVoltage) {
    outputVoltage = model.supplyVoltage;
    clippedRegion = "upper";
  }

  return {
    phase,
    input,
    candidateSignal,
    candidateOutputVoltage,
    outputVoltage,
    outputSignal: outputVoltage - model.quiescentOutputVoltage,
    clippedRegion,
  };
}
