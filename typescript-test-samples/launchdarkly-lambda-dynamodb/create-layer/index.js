const { execSync } = require("node:child_process");
const fs = require("fs");
const archiver = require("archiver");

// install the LaunchDarkly Node SDKs
execSync(
  `npm install --prefix ./nodejs launchdarkly-node-server-sdk launchdarkly-node-server-sdk-dynamodb`
);

// create a zip of the
let output = fs.createWriteStream("../cdk/resources/layers/layer.zip");
let archive = archiver("zip", {
  zlib: { level: 9 },
});

archive.on("warning", function (err) {
  if (err.code === "ENOENT") {
    console.warn(err);
  } else {
    throw err;
  }
});

archive.on("error", function (err) {
  throw err;
});

archive.pipe(output);
archive.directory("./nodejs", false);
archive.finalize();
