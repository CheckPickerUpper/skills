// Writes each changeset as its commit link and its text. The shared GitHub
// formatter also thanks the commit's author, which in a single-maintainer
// repository thanks the maintainer on every line.

async function getReleaseLine(changeset, _type, options) {
  const [first, ...rest] = changeset.summary.trim().split("\n");
  const link = changeset.commit
    ? `[\`${changeset.commit.slice(0, 7)}\`](https://github.com/${options.repo}/commit/${changeset.commit}) `
    : "";
  const body = rest.map((line) => (line.trim() ? `  ${line}` : "")).join("\n");
  return `\n\n- ${link}${first}${body ? `\n${body}` : ""}`;
}

async function getDependencyReleaseLine() {
  return "";
}

module.exports = { getReleaseLine, getDependencyReleaseLine };
