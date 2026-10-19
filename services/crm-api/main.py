from fastapi import FastAPI

# Création de notre application API CRM
app = FastAPI(
    title="NovaRetail CRM API",
    description="API CRM simulée pour notre plateforme Data Engineering",
    version="1.0.0",
)


# Endpoint permettant de vérifier la disponibilité de l'API
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "novaretail-crm-api"}
