# converte sua private key para o formato TOML correto

with open("/home/akel/Downloads/barulhodebelem-0d43bd5da9ee.json", "r") as f:
    import json
    data = json.load(f)

private_key = data["private_key"]

# substitui quebras de linha por \n
private_key_toml = private_key.replace("\n", "\\n")

print(private_key_toml)
