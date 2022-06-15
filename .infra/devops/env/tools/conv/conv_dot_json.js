// converts dotfile to JSON format

const fs = require("fs");
const path = require("path");

const dotenv = require("dotenv");

if (process.argv.length < 4) {
    console.error("Usage 'node .infra/devops/env/tools/conv/conv_dot_json.js <PATH_TO_INPUT_DOTFILE> <PATH_TO_OUTPUT_JSON_FILE>'")
    process.exit(1);
}

// parse input dotfile
const inputDotfileConfig = dotenv.config({ path: path.resolve(process.cwd(), process.argv[2]) });

// write output JSON file
fs.writeFileSync(path.resolve(process.cwd(), process.argv[3]), JSON.stringify(inputDotfileConfig.parsed) + "\n");
