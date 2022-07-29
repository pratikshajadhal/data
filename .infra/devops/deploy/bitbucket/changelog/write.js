const path = require("path");
const fs = require("fs");

const { render } = require("mustache")

if (process.argv.length < 4) {
    console.error(`Usage: "node .infra/devops/deploy/bitbucket/changelog/write.js <TEMPLATE_PATH> <CHANGELOG_CONTENT_TEMP_PATH>"`)
    process.exit(1);
}

// parse args
const apiVersion = fs.readFileSync(path.resolve(process.cwd(), 'version')).toString()
const templatePath = process.argv[2];
const changelogContentTempPath = process.argv[3];

// loading changelog data from temporary data file
const changelogContent = fs.readFileSync(path.resolve(process.cwd(), changelogContentTempPath)).toString()

const templateParams = {
    appVersion: apiVersion,
    content: changelogContent,
};

const templateContent = fs.readFileSync(path.resolve(process.cwd(), templatePath)).toString()
const renderedContent = render(templateContent, templateParams)

// create root level changelog file
fs.writeFile(path.resolve(process.cwd(), 'CHANGELOG.md'), renderedContent, (err) => {
    if (err) throw err;
    console.log('CHANGELOG.md file create/update successfully.');
  });

// deleting temp file
fs.unlinkSync(path.resolve(process.cwd(), changelogContentTempPath));
