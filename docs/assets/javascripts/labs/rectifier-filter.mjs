function finite(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}


function normalizedParameters(parameters = {}) {
  const topology = ["half", "full", "bridge"].includes(parameters.topology)
    ? parameters.topology
    : "bridge";
  return {
    topology,
    secondaryRmsVoltage: Math.max(
      0,
      finite(parameters.secondaryRmsVoltage, 9),
    ),
    frequencyHz: Math.max(1, finite(parameters.frequencyHz, 50)),
    diodeDropVoltage: Math.max(
      0,
      finite(parameters.diodeDropVoltage, 0.7),
    ),
    capacitanceMicroF: Math.max(
      1,
      finite(parameters.capacitanceMicroF, 1000),
    ),
    loadMilliAmp: Math.max(0, finite(parameters.loadMilliAmp, 100)),
    regulatorVoltage: Math.max(
      0,
      finite(parameters.regulatorVoltage, 5),
    ),
    dropoutVoltage: Math.max(
      0,
      finite(parameters.dropoutVoltage, 2),
    ),
  };
}


export function rectifierModel(parameters) {
  const model = normalizedParameters(parameters);
  const diodeDrops = model.topology === "bridge" ? 2 : 1;
  const rippleFrequencyHz = model.topology === "half"
    ? model.frequencyHz
    : 2 * model.frequencyHz;
  const peakRectifiedVoltage = Math.max(
    0,
    model.secondaryRmsVoltage * Math.SQRT2
      - diodeDrops * model.diodeDropVoltage,
  );
  const loadAmp = model.loadMilliAmp / 1000;
  const capacitanceFarad = model.capacitanceMicroF * 1e-6;
  const rippleEstimateVoltage = loadAmp
    / (rippleFrequencyHz * capacitanceFarad);
  const valleyVoltage = Math.max(
    0,
    peakRectifiedVoltage - rippleEstimateVoltage,
  );
  const regulatorMarginVoltage = valleyVoltage
    - model.regulatorVoltage
    - model.dropoutVoltage;

  return {
    ...model,
    diodeDrops,
    rippleFrequencyHz,
    peakRectifiedVoltage,
    capacitanceFarad,
    rippleEstimateVoltage,
    valleyVoltage,
    regulatorMarginVoltage,
    regulated: regulatorMarginVoltage >= 0,
  };
}


function rectifiedInstant(model, phase) {
  const peakSecondary = model.secondaryRmsVoltage * Math.SQRT2;
  const secondary = peakSecondary * Math.sin(phase);
  const diodeLoss = model.diodeDrops * model.diodeDropVoltage;
  if (model.topology === "half") {
    return {
      secondary,
      rectified: Math.max(0, secondary - diodeLoss),
    };
  }
  return {
    secondary,
    rectified: Math.max(0, Math.abs(secondary) - diodeLoss),
  };
}


export function rectifierSamples(parameters, sampleCount = 401) {
  const model = rectifierModel(parameters);
  const count = Math.max(3, Math.trunc(finite(sampleCount, 401)));
  const durationSeconds = 2 / model.frequencyHz;
  const timeStep = durationSeconds / (count - 1);
  const dischargePerStep = (
    model.loadMilliAmp / 1000
  ) * timeStep / model.capacitanceFarad;
  let capacitorVoltage = 0;

  const advance = (timeSeconds) => {
    const phase = 2 * Math.PI * model.frequencyHz * timeSeconds;
    const instant = rectifiedInstant(model, phase);
    const discharged = Math.max(0, capacitorVoltage - dischargePerStep);
    const charging = instant.rectified > discharged;
    capacitorVoltage = charging ? instant.rectified : discharged;
    const outputVoltage = capacitorVoltage
      >= model.regulatorVoltage + model.dropoutVoltage
      ? model.regulatorVoltage
      : Math.max(0, capacitorVoltage - model.dropoutVoltage);

    return {
      timeSeconds,
      phase,
      secondaryVoltage: instant.secondary,
      rectifiedVoltage: instant.rectified,
      capacitorVoltage,
      outputVoltage,
      charging,
    };
  };

  // The page compares its waveform with steady-state ripple and dropout metrics.
  // Warm the capacitor for several complete source cycles, then expose only the
  // final two cycles so a cold-start transient cannot contradict those metrics.
  const warmupSteps = Math.ceil(
    8 / model.frequencyHz / timeStep,
  );
  for (let index = 0; index < warmupSteps; index += 1) {
    advance((index - warmupSteps) * timeStep);
  }

  return Array.from({ length: count }, (_, index) => (
    advance(index * timeStep)
  ));
}
