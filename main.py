from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from calculs import calcul, P_ATM

app = FastAPI(title="MolecularLab API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionRequest(BaseModel):
    molecule: str
    pressure: float = Field(gt=0)
    unit: str


UNITES = {
    "pa": 1.0,
    "kpa": 1000.0,
    "bar": 100000.0,
    "atm": P_ATM,
    "mmhg": 133.322
}


@app.post("/predict")
def prediction(data: PredictionRequest):

    nom = data.molecule.strip()
    unite = data.unit.lower().strip()

    if not nom:
        raise HTTPException(
            status_code=400,
            detail="Veuillez saisir une molécule."
        )

    if unite not in UNITES:
        raise HTTPException(
            status_code=400,
            detail="Unité non reconnue."
        )

    pression_pa = data.pressure * UNITES[unite]

    resultat, erreur = calcul(nom, pression_pa)

    if erreur:
        raise HTTPException(status_code=404, detail=erreur)

    if resultat["tb"] is None:
        raise HTTPException(
            status_code=422,
            detail="Calcul impossible."
        )

    return {
        "molecule": resultat["nom"],
        "formula": resultat["formule"],
        "cas": resultat["CAS"],
        "tb_kelvin": resultat["tb"],
        "tb_celsius": resultat["tb"] - 273.15,
        "method": resultat["methode"],
        "source": resultat["source_1atm"],
        "pressure_pa": pression_pa,
        "tb_1atm": resultat["tb_1atm"]
    }


# Cette ligne lit directement tous les fichiers du projet
import os

app.mount("/", StaticFiles(directory=".", html=True), name="static")