function finite(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}


function normalizedParameters(parameters = {}) {
  return {
    dcLoopGain: Math.max(0, finite(parameters.dcLoopGain, 1e4)),
    pole1Hz: Math.max(1e-12, finite(parameters.pole1Hz, 10)),
    pole2Hz: Math.max(1e-12, finite(parameters.pole2Hz, 1e5)),
  };
}


export function loopResponse(parameters, frequencyHz) {
  const model = normalizedParameters(parameters);
  const frequency = Math.max(0, finite(frequencyHz, 0));
  const ratio1 = frequency / model.pole1Hz;
  const ratio2 = frequency / model.pole2Hz;
  const magnitude = model.dcLoopGain / Math.sqrt(
    (1 + ratio1 ** 2) * (1 + ratio2 ** 2),
  );
  const magnitudeDb = magnitude > 0
    ? 20 * Math.log10(magnitude)
    : Number.NEGATIVE_INFINITY;
  const phaseDeg = -(
    Math.atan(ratio1) + Math.atan(ratio2)
  ) * 180 / Math.PI;

  return {
    frequencyHz: frequency,
    magnitude,
    magnitudeDb,
    phaseDeg,
  };
}


export function stabilityMetrics(parameters) {
  const model = normalizedParameters(parameters);
  if (model.dcLoopGain <= 1) {
    return {
      hasCrossover: false,
      crossoverHz: null,
      phaseMarginDeg: null,
      dampingRatio: 1,
      status: "无 0 dB 交越",
    };
  }

  let low = Math.min(model.pole1Hz, model.pole2Hz) * 1e-6;
  let high = Math.max(model.pole1Hz, model.pole2Hz) * 1e8;
  if (loopResponse(model, high).magnitude >= 1) {
    return {
      hasCrossover: false,
      crossoverHz: null,
      phaseMarginDeg: null,
      dampingRatio: 0.05,
      status: "交越超出显示范围",
    };
  }

  for (let iteration = 0; iteration < 100; iteration += 1) {
    const middle = Math.sqrt(low * high);
    if (loopResponse(model, middle).magnitude > 1) {
      low = middle;
    } else {
      high = middle;
    }
  }

  const crossoverHz = Math.sqrt(low * high);
  const atCrossover = loopResponse(model, crossoverHz);
  const phaseMarginDeg = 180 + atCrossover.phaseDeg;
  const dampingRatio = Math.min(
    1.2,
    Math.max(0.05, phaseMarginDeg / 100),
  );
  let status = "裕度充足";
  if (phaseMarginDeg <= 0) {
    status = "不稳定";
  } else if (phaseMarginDeg < 30) {
    status = "低裕度";
  } else if (phaseMarginDeg < 60) {
    status = "有振铃";
  }

  return {
    hasCrossover: true,
    crossoverHz,
    phaseMarginDeg,
    dampingRatio,
    status,
  };
}
