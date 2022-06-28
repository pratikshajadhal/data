// converts dotfile to JSON format

const fs = require("fs");
const path = require("path");

if (process.argv.length < 4) {
    console.error("Usage 'node .infra/devops/env/tools/conv/conv_json_dot.js <PATH_TO_INPUT_JSON_FILE> <PATH_TO_OUTPUT_DOTFILE>'")
    process.exit(1);
}

// parse input json file
const inputJSON = require(path.resolve(process.cwd(), process.argv[2]));

// create dotenv data
var dotenvData = "";
Object.keys(inputJSON).forEach(key => {
	dotenvData += `${key}='${inputJSON[key]}'\n`;
});

// write dotenv file
fs.writeFileSync(path.resolve(process.cwd(), process.argv[3]), dotenvData);
