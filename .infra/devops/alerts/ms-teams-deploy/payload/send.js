const path = require("path");

const axios = require('axios');
const parse = require("json-templates");

if (process.argv.length < 11) {
    console.error(`Usage: "node .infra/devops/alerts/ms-teams-deploy/payload/send.js <ENV_NAME> <BITBUCKET_REPO_NAME> <BITBUCKET_PIPELINE_URL> <AWS_REGION> <AWS_ACCOUNT_ID> <SERVICE_ECR_NAME> <IMG_SHA_256> <IMG_TAG> <SERVICE_URL>"`)
    process.exit(1);
}


const templateParams = {
    webhookUrl: process.argv[2],
    envName: process.argv[3],
    bitbucketRepoName: process.argv[4],
    bitbucketPipelineUrl: process.argv[5],
    awsRegion: process.argv[6],
    awsAccountId: process.argv[7],
    serviceEcrName: process.argv[8],
    imgSha256: process.argv[9],
    imgTag: process.argv[10],
    healthCheckUrl: process.argv[11],
};
// console.error('params: ', templateParams);

var fileContents = require(path.resolve(process.cwd(), ".infra/devops/alerts/ms-teams-deploy/payload/template-message-card.json"));

const template = parse(fileContents);
const payload = JSON.stringify(template(templateParams));

// send request
(async function makeGetRequest() {
    let res;
    try {
        res = await axios.post(templateParams.webhookUrl, payload);
    } catch(err) {
        console.error('\nRequest failed: ', err.response.data);
        process.exit(1);
    }
    
    let data = res.data;
    console.log(data);
})();
