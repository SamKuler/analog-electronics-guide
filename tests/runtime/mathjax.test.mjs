import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
import test from "node:test";

const script = readFileSync(
  new URL("../../docs/assets/javascripts/mathjax.js", import.meta.url),
  "utf8",
);

function loadMathJaxConfig() {
  const subscribers = [];
  const labels = [
    {
      children: [],
      textContent: "9.1 从平方律推出 \\(g_m\\)",
      replaceChildren(fragment) {
        this.children = fragment.children;
      },
    },
  ];
  const navigations = [
    {},
    {},
  ];
  const context = {
    document$: {
      subscribe(callback) {
        subscribers.push(callback);
      },
    },
    document: {
      querySelectorAll(selector) {
        assert.equal(selector, ".md-nav--secondary");
        return navigations.map(() => ({
          querySelectorAll(innerSelector) {
            assert.equal(innerSelector, ".md-ellipsis");
            return labels;
          },
        }));
      },
      createDocumentFragment() {
        return {
          children: [],
          append(...nodes) {
            this.children.push(...nodes);
          },
        };
      },
      createElement(tagName) {
        return { className: "", tagName, textContent: "" };
      },
      createTextNode(textContent) {
        return { nodeType: 3, textContent };
      },
    },
  };
  context.window = context;
  runInNewContext(script, context);
  return { context, labels, navigations, subscribers };
}

test("one document event produces exactly one MathJax typeset pass", async () => {
  const { context, subscribers } = loadMathJaxConfig();
  let typesetCalls = 0;
  context.MathJax.typesetPromise = async () => {
    typesetCalls += 1;
  };

  assert.equal(context.MathJax.startup.typeset, false);
  assert.equal(subscribers.length, 1);
  await subscribers[0]();
  assert.equal(typesetCalls, 1);
});

test("table-of-contents TeX is wrapped in a dedicated MathJax node", async () => {
  const { context, labels, subscribers } = loadMathJaxConfig();
  context.MathJax.typesetPromise = async () => {};

  await subscribers[0]();

  const formula = labels[0].children.find(
    (child) => child.className === "arithmatex",
  );
  assert.ok(formula);
  assert.equal(formula.textContent, "\\(g_m\\)");
});
