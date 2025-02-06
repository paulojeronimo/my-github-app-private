#!/usr/bin/env bash
set -eou pipefail
cd $(dirname $0)

username=${username:-paulo-oso-sh}
url=http://127.0.0.1:8000/create_repository/${username}
output=$(basename $0 .sh).output.json

curl -s -X POST $url -H "Content-Type: application/json" > $output

echo File $output generated:
jq . $output
