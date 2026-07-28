function finite(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}


function normalizedParameters(parameters = {}) {
  return {
    mode: ["rectifier", "limiter", "clamper"].includes(parameters.mode)
      ? parameters.mode
      : "rectifier",
    amplitude: Math.max(0, finite(parameters.amplitude, 5)),
    offset: finite(parameters.offset, 0),
    drop: Math.max(0, finite(parameters.drop, 0.7)),
    reference: finite(parameters.reference, 0),
    rcPeriods: Math.max(0.05, finite(parameters.rcPeriods, 10)),
  };
}


export function diodeSample(parameters, phaseRadians) {
  const model = normalizedParameters(parameters);
  const phase = finite(phaseRadians, 0);
  const input = model.offset + model.amplitude * Math.sin(phase);

  if (model.mode === "limiter") {
    const threshold = model.reference + model.drop;
    const conducting = input > threshold;
    return {
      phase,
      input,
      output: conducting ? threshold : input,
      conducting,
      threshold,
    };
  }

  if (model.mode === "clamper") {
    const targetMinimum = model.reference + model.drop;
    const inputMinimum = model.offset - model.amplitude;
    const storedShift = targetMinimum - inputMinimum;
    const output = input + storedShift;
    const distanceFromNegativePeak = Math.abs(
      Math.atan2(Math.sin(phase - 1.5 * Math.PI), Math.cos(phase - 1.5 * Math.PI)),
    );
    return {
      phase,
      input,
      output,
      conducting: distanceFromNegativePeak < 1e-9,
      threshold: targetMinimum,
      storedShift,
    };
  }

  const threshold = model.drop;
  const conducting = input > threshold;
  return {
    phase,
    input,
    output: conducting ? input - model.drop : 0,
    conducting,
    threshold,
  };
}


export function diodeWaveform(parameters, sampleCount = 241) {
  const model = normalizedParameters(parameters);
  const count = Math.max(3, Math.trunc(finite(sampleCount, 241)));

  if (model.mode !== "clamper") {
    return Array.from({ length: count }, (_, index) => {
      const phase = (index / (count - 1)) * 2 * Math.PI;
      return diodeSample(model, phase);
    });
  }

  const targetMinimum = model.reference + model.drop;
  const inputMinimum = model.offset - model.amplitude;
  const storedShift = targetMinimum - inputMinimum;
  return Array.from({ length: count }, (_, index) => {
    const phase = (index / (count - 1)) * 2 * Math.PI;
    const input = model.offset + model.amplitude * Math.sin(phase);
    const timeSinceNegativePeak = (
      phase - 1.5 * Math.PI + 2 * Math.PI
    ) % (2 * Math.PI);
    const retainedShift = storedShift * Math.exp(
      -timeSinceNegativePeak / (2 * Math.PI * model.rcPeriods),
    );
    const angularStep = 2 * Math.PI / (count - 1);
    return {
      phase,
      input,
      output: input + retainedShift,
      conducting: timeSinceNegativePeak < angularStep,
      threshold: targetMinimum,
      storedShift: retainedShift,
    };
  });
}
