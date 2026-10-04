import sys
import boto3
import config

gid, ver = sys.argv[1], sys.argv[2]
rt = boto3.client("bedrock-runtime", region_name=config.AWS_REGION)

def check(text, source="INPUT"):
    r = rt.apply_guardrail(
        guardrailIdentifier=gid,
        guardrailVersion=ver,
        source=source,
        content=[{"text": {"text": text}}],
    )
    print(r["action"], "|", source, "|", text)

check("How much are 5 items at $29.99 with 10% off?")
check("5 items at $29.99 with 10% off comes to $134.96.", source="OUTPUT")

