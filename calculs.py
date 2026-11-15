from math import log, log10

from chemicals.identifiers import search_chemical
from chemicals import Tb, Tc, Pc
from chemicals.phase_change import Riedel

try:
    from thermo.group_contribution.joback import Joback
except Exception:
    Joback = None

R = 8.314
P_ATM = 101325.0


def identifier(nom):
    """Recherche une molécule par nom, formule, CAS ou SMILES."""
    try:
        return search_chemical(nom)
    except Exception:
        return None


def tb_normale(mol):
    """Température d'ébullition à 1 atm."""
    try:
        valeur = Tb(mol.CAS)

        if valeur is not None:
            return valeur, "Valeur mesurée (base de données)", None

    except Exception:
        pass

    try:
        est = Joback(mol.smiles).estimate()

        return (
            est["Tb"],
            "Estimation Joback (approximative)",
            est
        )

    except Exception:
        return None, "Impossible de calculer", None


def tb_antoine(mol, P):
    """Calcul par la méthode d'Antoine."""
    try:
        from chemicals.vapor_pressure import Psat_data_AntoinePoling as D

        ligne = D.loc[mol.CAS]

        A = float(ligne["A"])
        B = float(ligne["B"])
        C = float(ligne["C"])

        T = B / (A - log10(P)) - C

        return T, f"Antoine (A={A:.4f}, B={B:.2f}, C={C:.2f})"

    except Exception:
        return None, None


def tb_clausius(mol, tb1, est, P):
    """Calcul par Clausius-Clapeyron."""
    try:
        tc = Tc(mol.CAS) or (est or {}).get("Tc")
        pc = Pc(mol.CAS) or (est or {}).get("Pc")

        if tc is None or pc is None:
            est = Joback(mol.smiles).estimate()
            tc, pc = est["Tc"], est["Pc"]

        hvap = Riedel(tb1, tc, pc)

        T2 = 1.0 / (
            1.0 / tb1 - R * log(P / P_ATM) / hvap
        )

        methode = (
            f"Clausius-Clapeyron "
            f"(Hvap = {hvap / 1000:.1f} kJ/mol, Riedel)"
        )

        return T2, methode

    except Exception:
        return None, None


def calcul(nom, P=P_ATM):
    """Fonction principale de calcul."""

    mol = identifier(nom)

    if mol is None:
        return None, "Molécule introuvable (essayez le nom anglais)."

    tb1, source1, est = tb_normale(mol)

    resultat = {
        "nom": mol.common_name,
        "formule": mol.formula,
        "CAS": mol.CAS,
        "tb_1atm": tb1,
        "source_1atm": source1
    }

    if abs(P - P_ATM) < 1:
        resultat["tb"] = tb1
        resultat["methode"] = source1

        return resultat, None

    T, methode = tb_antoine(mol, P)

    if T is None and tb1 is not None:
        T, methode = tb_clausius(mol, tb1, est, P)

    resultat["tb"] = T
    resultat["methode"] = methode

    return resultat, None