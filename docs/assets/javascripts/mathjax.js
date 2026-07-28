window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
  },
  startup: {
    typeset: false,
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex",
  },
};

function prepareTableOfContentsMath(navigation) {
  const formulaPattern = /\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]/g;

  navigation.querySelectorAll(".md-ellipsis").forEach((label) => {
    const source = label.textContent;
    const fragment = document.createDocumentFragment();
    let cursor = 0;
    let match;

    while ((match = formulaPattern.exec(source)) !== null) {
      fragment.append(document.createTextNode(source.slice(cursor, match.index)));
      const formula = document.createElement("span");
      formula.className = "arithmatex";
      formula.textContent = match[0];
      fragment.append(formula);
      cursor = match.index + match[0].length;
    }

    if (cursor > 0) {
      fragment.append(document.createTextNode(source.slice(cursor)));
      label.replaceChildren(fragment);
    }
  });
}

document$.subscribe(() => {
  document
    .querySelectorAll(".md-nav--secondary")
    .forEach(prepareTableOfContentsMath);
  return MathJax.typesetPromise();
});
